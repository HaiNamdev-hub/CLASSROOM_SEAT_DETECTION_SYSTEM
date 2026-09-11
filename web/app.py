from pathlib import Path

import subprocess
import threading
import time
import uuid

import cv2
import imageio_ffmpeg

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    Response
)

from src.image_handler import (
    read_image
)
from src.webcam_processor import (
    process_dynamic_webcam_frame
)

from src.main import (
    process_frame
)

from src.person_detector import (
    load_model
)

from src.seat_config import (
    load_seats
)

from src.visualizer import (
    draw_statistics
)

from database.db import (
    init_database,
    save_analysis_session,
    save_seat_results,
    get_history,
    get_session_detail,
    get_latest_statistics
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# BASE PATH
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# =========================================================
# UPLOAD PATHS
# =========================================================

UPLOAD_IMAGE_DIR = (
    BASE_DIR
    / "uploads"
    / "images"
)

UPLOAD_VIDEO_DIR = (
    BASE_DIR
    / "uploads"
    / "videos"
)


# =========================================================
# RESULT PATHS
# =========================================================

RESULT_IMAGE_DIR = (
    BASE_DIR
    / "results"
    / "screenshots"
)

RESULT_VIDEO_DIR = (
    BASE_DIR
    / "results"
    / "videos"
)


# =========================================================
# SEAT CONFIG PATHS
# =========================================================

SEAT_IMAGE_CONFIG = (
    BASE_DIR
    / "config"
    / "seats_image.json"
)

SEAT_VIDEO_CONFIG = (
    BASE_DIR
    / "config"
    / "seats_video.json"
)

SEAT_WEBCAM_CONFIG = (
    BASE_DIR
    / "config"
    / "seats_webcam.json"
)


# =========================================================
# CREATE DIRECTORIES
# =========================================================

UPLOAD_IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

UPLOAD_VIDEO_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULT_IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULT_VIDEO_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# DATABASE INIT
# =========================================================

init_database()


# =========================================================
# YOLO MODEL
# =========================================================

model = load_model()


# =========================================================
# VIDEO JOB STORAGE
# =========================================================

video_jobs = {}


# =========================================================
# WEBCAM STATE
# =========================================================

webcam_state = {
    # User has requested camera to run
    "running": False,

    # Camera was actually opened successfully
    "stream_active": False,

    # Latest processed frame information
    "last_statistics": None,
    "last_occupancy": None,
    "last_mappings": None,
    "last_persons": 0,
    "last_fps": 0.0,

    # Prevent duplicate history records
    "saved": False,
    "session_id": None,

    # Error information
    "error": None
}


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok",
        "system":
            "Classroom Seat Detection"
    })


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.route(
    "/api/statistics",
    methods=["GET"]
)
def statistics():

    return jsonify(
        get_latest_statistics()
    )


# =========================================================
# IMAGE ANALYSIS
# =========================================================

@app.route(
    "/api/analyze/image",
    methods=["POST"]
)


def analyze_image():

    # ==========================================
    # 1. KIỂM TRA FILE
    # ==========================================

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message":
                "Không tìm thấy file ảnh."
        }), 400


    image_file = request.files[
        "image"
    ]


    if image_file.filename == "":

        return jsonify({
            "success": False,
            "message":
                "Tên file ảnh không hợp lệ."
        }), 400


    # ==========================================
    # 2. LƯU ẢNH UPLOAD
    # ==========================================

    input_filename = (
        f"{uuid.uuid4().hex}_"
        f"{image_file.filename}"
    )


    input_path = (
        UPLOAD_IMAGE_DIR
        / input_filename
    )


    image_file.save(
        str(input_path)
    )


    try:

        # ======================================
        # 3. ĐỌC ẢNH
        # ======================================

        image = read_image(
            str(input_path)
        )


        # ======================================
        # 4. DYNAMIC PERSON + CHAIR DETECTION
        # ======================================

        (
            output_image,
            persons,
            chairs,
            occupancy_results,
            statistics_result
        ) = process_dynamic_webcam_frame(
            model,
            image,
            fps=None
        )


        # ======================================
        # 5. VẼ STATISTICS
        # ======================================

        output_image = draw_statistics(
            output_image,
            statistics_result,
            fps=None
        )


        # ======================================
        # 6. LƯU ẢNH KẾT QUẢ
        # ======================================

        output_filename = (
            f"image_{uuid.uuid4().hex}.jpg"
        )


        output_path = (
            RESULT_IMAGE_DIR
            / output_filename
        )


        save_success = cv2.imwrite(
            str(output_path),
            output_image
        )


        if not save_success:

            raise RuntimeError(
                "Không thể lưu ảnh kết quả."
            )


        # ======================================
        # 7. LƯU DATABASE
        # ======================================

        session_id = (
            save_analysis_session(
                source_type="image",

                source_name=
                    image_file.filename,

                persons=
                    len(persons),

                statistics=
                    statistics_result,

                output_path=
                    str(output_path),

                fps=None
            )
        )


        # Dynamic detection không có
        # mappings kiểu ROI cố định
        save_seat_results(
            session_id,
            occupancy_results,
            None
        )


        # ======================================
        # 8. TRẢ KẾT QUẢ CHO VUE
        # ======================================

        return jsonify({
            "success":
                True,

            "session_id":
                session_id,

            "persons":
                len(persons),

            "chairs":
                len(chairs),

            "total_seats":
                statistics_result[
                    "total_seats"
                ],

            "occupied":
                statistics_result[
                    "occupied_seats"
                ],

            "empty":
                statistics_result[
                    "empty_seats"
                ],

            "occupancy_rate":
                statistics_result[
                    "occupancy_rate"
                ],

            "seats":
                occupancy_results,

            "output_url":
                (
                    "/results/screenshots/"
                    + output_filename
                )
        })


    except Exception as error:

        print(
            "IMAGE ANALYSIS ERROR:",
            error
        )


        return jsonify({
            "success":
                False,

            "message":
                str(error)
        }), 500


# =========================================================
# CONVERT VIDEO TO H.264
# =========================================================

def convert_video_for_browser(
    input_path,
    output_path
):

    ffmpeg_path = (
        imageio_ffmpeg
        .get_ffmpeg_exe()
    )


    command = [
        ffmpeg_path,
        "-y",

        "-i",
        str(input_path),

        "-c:v",
        "libx264",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        "-an",

        str(output_path)
    ]


    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


    if result.returncode != 0:

        error_text = (
            result.stderr
            .decode(
                "utf-8",
                errors="ignore"
            )
        )

        print(
            "FFMPEG ERROR:",
            error_text
        )

        raise RuntimeError(
            "Không thể convert video sang H.264."
        )


# =========================================================
# VIDEO BACKGROUND JOB
# =========================================================

def process_video_job(
    job_id,
    input_path,
    original_filename
):

    video = None
    writer = None

    try:

        seats = load_seats(
            str(
                SEAT_VIDEO_CONFIG
            )
        )


        video = cv2.VideoCapture(
            str(input_path)
        )


        if not video.isOpened():

            raise RuntimeError(
                "Không thể mở video."
            )


        total_frames = int(
            video.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )


        width = int(
            video.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )


        height = int(
            video.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )


        source_fps = video.get(
            cv2.CAP_PROP_FPS
        )


        if source_fps <= 0:
            source_fps = 25.0


        temp_filename = (
            f"{job_id}_temp.mp4"
        )


        final_filename = (
            f"{job_id}_result.mp4"
        )


        temp_path = (
            RESULT_VIDEO_DIR
            / temp_filename
        )


        final_path = (
            RESULT_VIDEO_DIR
            / final_filename
        )


        fourcc = (
            cv2.VideoWriter_fourcc(
                *"mp4v"
            )
        )


        writer = cv2.VideoWriter(
            str(temp_path),
            fourcc,
            source_fps,
            (
                width,
                height
            )
        )


        if not writer.isOpened():

            raise RuntimeError(
                "Không thể tạo video output."
            )


        processed_frames = 0

        total_processing_time = 0.0

        last_statistics = None

        last_occupancy = None

        last_mappings = None

        last_persons_count = 0


        while True:

            success, frame = (
                video.read()
            )


            if not success:
                break


            start_time = (
                time.perf_counter()
            )


            (
                output_frame,
                detections,
                mappings,
                occupancy_results,
                statistics_result
            ) = process_frame(
                model,
                frame,
                seats,
                draw_stats=False
            )


            processing_time = (
                time.perf_counter()
                - start_time
            )


            total_processing_time += (
                processing_time
            )


            processed_frames += 1


            fps = (
                1 / processing_time
                if processing_time > 0
                else 0
            )


            output_frame = (
                draw_statistics(
                    output_frame,
                    statistics_result,
                    fps
                )
            )


            writer.write(
                output_frame
            )


            last_persons_count = (
                len(detections)
            )


            last_statistics = (
                statistics_result
            )


            last_occupancy = (
                occupancy_results
            )


            last_mappings = (
                mappings
            )


            if total_frames > 0:

                progress = (
                    processed_frames
                    / total_frames
                    * 100
                )

            else:

                progress = 0


            video_jobs[
                job_id
            ][
                "progress"
            ] = min(
                progress,
                99
            )


        video.release()
        video = None


        writer.release()
        writer = None


        if processed_frames == 0:

            raise RuntimeError(
                "Video không có frame hợp lệ."
            )


        video_jobs[
            job_id
        ][
            "status"
        ] = "converting"


        convert_video_for_browser(
            temp_path,
            final_path
        )


        if temp_path.exists():

            temp_path.unlink()


        average_fps = (
            processed_frames
            / total_processing_time

            if total_processing_time > 0

            else 0
        )


        session_id = (
            save_analysis_session(
                source_type="video",

                source_name=
                    original_filename,

                persons=
                    last_persons_count,

                statistics=
                    last_statistics,

                output_path=
                    str(final_path),

                fps=
                    average_fps
            )
        )


        save_seat_results(
            session_id,
            last_occupancy,
            last_mappings
        )


        video_jobs[
            job_id
        ] = {

            "status":
                "completed",

            "progress":
                100,

            "session_id":
                session_id,

            "persons":
                last_persons_count,

            "total_seats":
                last_statistics[
                    "total_seats"
                ],

            "occupied":
                last_statistics[
                    "occupied_seats"
                ],

            "empty":
                last_statistics[
                    "empty_seats"
                ],

            "occupancy_rate":
                last_statistics[
                    "occupancy_rate"
                ],

            "fps":
                average_fps,

            "output_url":
                (
                    "/results/videos/"
                    + final_filename
                )
        }


    except Exception as error:

        print(
            "VIDEO JOB ERROR:",
            error
        )


        video_jobs[
            job_id
        ] = {

            "status":
                "failed",

            "progress":
                0,

            "message":
                str(error)
        }


    finally:

        if video is not None:

            video.release()


        if writer is not None:

            writer.release()


# =========================================================
# START VIDEO ANALYSIS
# =========================================================

@app.route(
    "/api/analyze/video",
    methods=["POST"]
)
def analyze_video():

    if "video" not in request.files:

        return jsonify({
            "success": False,
            "message":
                "Không tìm thấy file video."
        }), 400


    video_file = request.files[
        "video"
    ]


    if video_file.filename == "":

        return jsonify({
            "success": False,
            "message":
                "Tên video không hợp lệ."
        }), 400


    job_id = str(
        uuid.uuid4()
    )


    input_filename = (
        f"{job_id}_"
        f"{video_file.filename}"
    )


    input_path = (
        UPLOAD_VIDEO_DIR
        / input_filename
    )


    video_file.save(
        str(input_path)
    )


    video_jobs[
        job_id
    ] = {

        "status":
            "processing",

        "progress":
            0
    }


    worker = threading.Thread(
        target=
            process_video_job,

        args=(
            job_id,
            input_path,
            video_file.filename
        ),

        daemon=True
    )


    worker.start()


    return jsonify({
        "success": True,
        "job_id": job_id
    })


# =========================================================
# VIDEO PROGRESS
# =========================================================

@app.route(
    "/api/analyze/video/progress/<job_id>",
    methods=["GET"]
)
def video_progress(
    job_id
):

    job = video_jobs.get(
        job_id
    )


    if job is None:

        return jsonify({
            "success": False,
            "message":
                "Không tìm thấy video job."
        }), 404


    return jsonify(
        job
    )


# =========================================================
# WEBCAM HELPER
# =========================================================

def open_webcam():

    # Windows: ưu tiên DirectShow
    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if camera.isOpened():
        return camera

    camera.release()

    # Fallback
    camera = cv2.VideoCapture(
        0
    )

    return camera


# =========================================================
# START WEBCAM
# =========================================================

@app.route(
    "/api/webcam/start",
    methods=["POST"]
)
def start_webcam():

    if webcam_state[
        "running"
    ]:

        return jsonify({
            "success": True,
            "status":
                "running",

            "message":
                "Webcam is already running."
        })


    # Reset state
    webcam_state[
        "running"
    ] = True

    webcam_state[
        "stream_active"
    ] = False

    webcam_state[
        "last_statistics"
    ] = None

    webcam_state[
        "last_occupancy"
    ] = None

    webcam_state[
        "last_mappings"
    ] = None

    webcam_state[
        "last_persons"
    ] = 0

    webcam_state[
        "last_fps"
    ] = 0.0

    webcam_state[
        "saved"
    ] = False

    webcam_state[
        "session_id"
    ] = None

    webcam_state[
        "error"
    ] = None


    return jsonify({
        "success": True,

        "status":
            "starting",

        "message":
            "Starting webcam..."
    })


# =========================================================
# STOP WEBCAM + SAVE DATABASE
# =========================================================

@app.route(
    "/api/webcam/stop",
    methods=["POST"]
)
def stop_webcam():

    webcam_state[
        "running"
    ] = False


    statistics_result = (
        webcam_state[
            "last_statistics"
        ]
    )


    # Không có frame nào được xử lý
    if statistics_result is None:

        webcam_state[
            "stream_active"
        ] = False

        return jsonify({
            "success": True,

            "status":
                "stopped",

            "saved":
                False,

            "message":
                (
                    "Webcam stopped, "
                    "but no processed frame "
                    "was available to save."
                )
        })


    # Đã save trước đó rồi
    if webcam_state[
        "saved"
    ]:

        return jsonify({
            "success": True,

            "status":
                "stopped",

            "saved":
                True,

            "session_id":
                webcam_state[
                    "session_id"
                ],

            "message":
                (
                    "Webcam was already stopped "
                    "and saved to History."
                )
        })


    try:

        session_id = (
            save_analysis_session(
                source_type=
                    "webcam",

                source_name=
                    "camera0",

                persons=
                    webcam_state[
                        "last_persons"
                    ],

                statistics=
                    statistics_result,

                output_path=
                    None,

                fps=
                    webcam_state[
                        "last_fps"
                    ]
            )
        )


        save_seat_results(
    session_id,
    webcam_state[
        "last_occupancy"
    ],
    None
)


        webcam_state[
            "saved"
        ] = True

        webcam_state[
            "session_id"
        ] = session_id

        webcam_state[
            "stream_active"
        ] = False


        return jsonify({
            "success": True,

            "status":
                "stopped",

            "saved":
                True,

            "session_id":
                session_id,

            "message":
                (
                    "Webcam stopped and "
                    "analysis was saved "
                    "to History."
                )
        })


    except Exception as error:

        print(
            "SAVE WEBCAM ERROR:",
            error
        )


        return jsonify({
            "success": False,

            "status":
                "error",

            "saved":
                False,

            "message":
                str(error)
        }), 500


# =========================================================
# WEBCAM STATUS
# =========================================================

@app.route(
    "/api/webcam/status",
    methods=["GET"]
)
def webcam_status():

    statistics_result = (
        webcam_state[
            "last_statistics"
        ]
    )


    if webcam_state[
        "error"
    ]:

        camera_status = (
            "error"
        )

    elif webcam_state[
        "stream_active"
    ]:

        camera_status = (
            "running"
        )

    elif webcam_state[
        "running"
    ]:

        camera_status = (
            "starting"
        )

    else:

        camera_status = (
            "stopped"
        )


    if statistics_result is None:

        return jsonify({
            "status":
                camera_status,

            "running":
                webcam_state[
                    "running"
                ],

            "stream_active":
                webcam_state[
                    "stream_active"
                ],

            "saved":
                webcam_state[
                    "saved"
                ],

            "session_id":
                webcam_state[
                    "session_id"
                ],

            "error":
                webcam_state[
                    "error"
                ],

            "persons":
                0,

            "total_seats":
                0,

            "occupied":
                0,

            "empty":
                0,

            "occupancy_rate":
                0.0,

            "fps":
                0.0
        })


    return jsonify({
        "status":
            camera_status,

        "running":
            webcam_state[
                "running"
            ],

        "stream_active":
            webcam_state[
                "stream_active"
            ],

        "saved":
            webcam_state[
                "saved"
            ],

        "session_id":
            webcam_state[
                "session_id"
            ],

        "error":
            webcam_state[
                "error"
            ],

        "persons":
            webcam_state[
                "last_persons"
            ],

        "total_seats":
            statistics_result[
                "total_seats"
            ],

        "occupied":
            statistics_result[
                "occupied_seats"
            ],

        "empty":
            statistics_result[
                "empty_seats"
            ],

        "occupancy_rate":
            statistics_result[
                "occupancy_rate"
            ],

        "fps":
            webcam_state[
                "last_fps"
            ]
            or 0.0
    })


# =========================================================
# WEBCAM GENERATOR
# =========================================================

def generate_webcam_frames():

    camera = open_webcam()


    if not camera.isOpened():

        message = (
            "Không thể mở webcam. "
            "Hãy kiểm tra camera hoặc "
            "ứng dụng khác đang sử dụng camera."
        )

        print(
            "WEBCAM ERROR:",
            message
        )

        webcam_state[
            "running"
        ] = False

        webcam_state[
            "stream_active"
        ] = False

        webcam_state[
            "error"
        ] = message

        return


    webcam_state[
        "stream_active"
    ] = True

    webcam_state[
        "error"
    ] = None


    try:


        while webcam_state[
            "running"
        ]:

            success, frame = (
                camera.read()
            )


            if not success:

                message = (
                    "Không đọc được frame "
                    "từ webcam."
                )

                print(
                    "WEBCAM ERROR:",
                    message
                )

                webcam_state[
                    "error"
                ] = message

                webcam_state[
        "running"
    ] = False
                webcam_state[
        "stream_active"
    ] = False

                break


            start_time = (
                time.perf_counter()
            )


            (
    output_frame,
    persons,
    chairs,
    occupancy_results,
    statistics_result
) = process_dynamic_webcam_frame(
    model,
    frame,
    fps=None
)


            processing_time = (
                time.perf_counter()
                - start_time
            )


            fps = (
                1 / processing_time

                if processing_time > 0

                else 0
            )


            # =============================================
            # SAVE LATEST WEBCAM RESULT IN MEMORY
            # =============================================

            webcam_state[
                "last_statistics"
            ] = statistics_result


            webcam_state[
                "last_occupancy"
            ] = occupancy_results


            webcam_state[
                "last_mappings"
            ] = None
    

            webcam_state[
                "last_persons"
            ] = len(
                persons
            )


            webcam_state[
                "last_fps"
            ] = fps


            # =============================================
            # DRAW STATISTICS
            # =============================================

            output_frame = (
                draw_statistics(
                    output_frame,
                    statistics_result,
                    fps
                )
            )


            # =============================================
            # ENCODE JPEG
            # =============================================

            encoded_success, buffer = (
                cv2.imencode(
                    ".jpg",
                    output_frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        80
                    ]
                )
            )


            if not encoded_success:
                continue


            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )


    except Exception as error:

        print(
            "WEBCAM STREAM ERROR:",
            error
        )

        webcam_state[
            "error"
        ] = str(
            error
        )

        webcam_state[
        "running"
    ] = False

        webcam_state[
        "stream_active"
    ] = False


    finally:

        camera.release()


        webcam_state[
            "stream_active"
        ] = False


        print(
            "Webcam released."
        )


# =========================================================
# WEBCAM FEED
# =========================================================

@app.route(
    "/video_feed",
    methods=["GET"]
)
def video_feed():

    return Response(
        generate_webcam_frames(),

        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )


# =========================================================
# SERVE IMAGE RESULT
# =========================================================

@app.route(
    "/results/screenshots/<path:filename>",
    methods=["GET"]
)
def result_image(
    filename
):

    return send_from_directory(
        str(
            RESULT_IMAGE_DIR
        ),
        filename
    )


# =========================================================
# SERVE VIDEO RESULT
# =========================================================

@app.route(
    "/results/videos/<path:filename>",
    methods=["GET"]
)
def result_video(
    filename
):

    return send_from_directory(
        str(
            RESULT_VIDEO_DIR
        ),
        filename
    )


# =========================================================
# HISTORY
# =========================================================

@app.route(
    "/api/history",
    methods=["GET"]
)
def history():

    return jsonify(
        get_history()
    )


# =========================================================
# HISTORY DETAIL
# =========================================================

@app.route(
    "/api/history/<int:session_id>",
    methods=["GET"]
)
def history_detail(
    session_id
):

    result = get_session_detail(
        session_id
    )


    if result is None:

        return jsonify({
            "success": False,
            "message":
                "Không tìm thấy phiên phân tích."
        }), 404


    return jsonify(
        result
    )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        threaded=True
    )