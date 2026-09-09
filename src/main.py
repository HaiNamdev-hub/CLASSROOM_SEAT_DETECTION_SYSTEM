import cv2
import time

from pathlib import Path

from src.image_handler import read_image

from src.person_detector import (
    load_model,
    detect_persons,
    extract_person_detections,
    draw_person_detections
)

from src.seat_config import load_seats

from src.seat_mapper import (
    map_persons_to_seats
)

from src.occupancy import (
    determine_occupancy
)

from src.statistics import (
    calculate_statistics
)

from src.visualizer import (
    draw_seat_status,
    draw_statistics
)


def process_frame(
    model,
    frame,
    seats,
    fps=None,
    draw_stats=True
):
    results = detect_persons(
        model,
        frame
    )

    detections = extract_person_detections(
        results
    )

    mappings = map_persons_to_seats(
        detections,
        seats
    )

    occupancy_results = determine_occupancy(
        seats,
        mappings
    )

    statistics = calculate_statistics(
        occupancy_results
    )

    output_frame = draw_person_detections(
        frame,
        detections
    )

    output_frame = draw_seat_status(
        output_frame,
        occupancy_results
    )

    if draw_stats:
        output_frame = draw_statistics(
            output_frame,
            statistics,
            fps
        )

    return (
        output_frame,
        detections,
        mappings,
        occupancy_results,
        statistics
    )

def run_image(
    model,
    seats,
    image_path,
    output_path=
    "results/screenshots/system_image.jpg"
):
    image = read_image(
        image_path
    )

    start_time = time.perf_counter()

    (
        output_image,
        detections,
        mappings,
        occupancy,
        statistics
    ) = process_frame(
        model,
        image,
        seats
    )

    processing_time = (
        time.perf_counter() - start_time
    )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(output_path),
        output_image
    )

    print("\n===== SYSTEM RESULT =====")
    print(
        f"Persons: {len(detections)}"
    )
    print(
        f"Total Seats: "
        f"{statistics['total_seats']}"
    )
    print(
        f"Occupied: "
        f"{statistics['occupied_seats']}"
    )
    print(
        f"Empty: "
        f"{statistics['empty_seats']}"
    )
    print(
        f"Occupancy Rate: "
        f"{statistics['occupancy_rate']:.1f}%"
    )
    print(
        f"Processing Time: "
        f"{processing_time:.3f}s"
    )

    print(
        f"Saved: {output_path}"
    )

    cv2.imshow(
        "Classroom Seat Detection - Image",
        output_image
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def create_video_writer(
    output_path,
    fps,
    width,
    height
):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    for codec in ["avc1", "mp4v"]:
        fourcc = cv2.VideoWriter_fourcc(
            *codec
        )

        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (width, height)
        )

        if writer.isOpened():
            return writer

    raise RuntimeError(
        "Không thể tạo VideoWriter."
    )


def run_video(
    model,
    seats,
    video_path,
    output_path=
    "results/videos/system_video.mp4"
):
    video = cv2.VideoCapture(
        video_path
    )

    if not video.isOpened():
        raise ValueError(
            f"Không thể mở video: {video_path}"
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

    writer = create_video_writer(
        output_path,
        source_fps,
        width,
        height
    )

    try:
        while True:
            success, frame = video.read()

            if not success:
                break

            start_time = time.perf_counter()

            (
                output_frame,
                detections,
                mappings,
                occupancy_results,
                statistics
            ) = process_frame(
                model,
                frame,
                seats,
                draw_stats=False
            )

            processing_time = (
                time.perf_counter() - start_time
            )

            fps = (
                1 / processing_time
                if processing_time > 0
                else 0
            )

            output_frame = draw_statistics(
                output_frame,
                statistics,
                fps
            )

            writer.write(
                output_frame
            )

            display_width = 960

            h, w = output_frame.shape[:2]

            ratio = display_width / w
            display_height = int(
                h * ratio
            )

            display_frame = cv2.resize(
                output_frame,
                (
                    display_width,
                    display_height
                )
            )

            cv2.imshow(
                "Classroom Seat Detection - Video",
                display_frame
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break
    finally:
        video.release()
        writer.release()
        cv2.destroyAllWindows()

    print(
        f"Đã lưu video: {output_path}"
    )


def run_webcam(
    model,
    seats,
    camera_index=0,
    output_path=
    "results/videos/system_webcam.mp4"
):
    camera = cv2.VideoCapture(
        camera_index
    )

    if not camera.isOpened():
        raise RuntimeError(
            "Không thể mở webcam."
        )

    width = int(
        camera.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        camera.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    camera_fps = camera.get(
        cv2.CAP_PROP_FPS
    )

    if camera_fps <= 0:
        camera_fps = 20.0

    writer = create_video_writer(
        output_path,
        camera_fps,
        width,
        height
    )

    try:
        while True:
            success, frame = camera.read()

            if not success:
                break

            # Bắt đầu đo thời gian xử lý frame
            start_time = time.perf_counter()

            (
                output_frame,
                detections,
                mappings,
                occupancy_results,
                statistics
            ) = process_frame(
                model,
                frame,
                seats,
                draw_stats=False
            )

            processing_time = (
                time.perf_counter() - start_time
            )

            fps = (
                1 / processing_time
                if processing_time > 0
                else 0
            )

            # Vẽ statistics + FPS
            output_frame = draw_statistics(
                output_frame,
                statistics,
                fps
            )

            # Lưu frame gốc
            writer.write(
                output_frame
            )

            # Resize chỉ để hiển thị
            h, w = output_frame.shape[:2]

            display_width = 960
            ratio = display_width / w
            display_height = int(
                h * ratio
            )

            display_frame = cv2.resize(
                output_frame,
                (
                    display_width,
                    display_height
                )
            )

            cv2.imshow(
                "Classroom Seat Detection - Webcam",
                display_frame
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:
        camera.release()
        writer.release()
        cv2.destroyAllWindows()

    print(
        f"Đã lưu webcam: {output_path}"
    )

def main():
    print("=" * 50)
    print("A7 - CLASSROOM SEAT DETECTION")
    print("=" * 50)

    print("1. Image")
    print("2. Video")
    print("3. Webcam")

    choice = input(
        "Chọn chế độ: "
    ).strip()

    model = load_model()

    if choice == "1":
        seats = load_seats(
            "config/seats_image.json"
        )

        run_image(
            model,
            seats,
            "data/input/classroom.jpg"
        )

    elif choice == "2":
        seats = load_seats(
            "config/seats_video.json"
        )

        run_video(
            model,
            seats,
            "data/input/classroom.mp4"
        )

    elif choice == "3":
        seats = load_seats(
            "config/seats_webcam.json"
        )

        run_webcam(
            model,
            seats,
            camera_index=0
        )

    else:
        print(
            "Lựa chọn không hợp lệ."
        )

if __name__ == "__main__":
    main()