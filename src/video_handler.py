import cv2

from src.file_handler import check_file


def open_video(file_path):
    """
    Mở file video bằng OpenCV.
    """

    path = check_file(file_path)

    video = cv2.VideoCapture(str(path))

    if not video.isOpened():
        raise ValueError(f"Không thể mở video: {file_path}")

    return video


def play_video(file_path):
    """
    Đọc và hiển thị video từng frame.
    Nhấn q để thoát.
    """

    video = open_video(file_path)

    try:
        while True:
            success, frame = video.read()

            if not success:
                break

            cv2.imshow("Classroom Video", frame)

            if cv2.waitKey(25) & 0xFF == ord("q"):
                break

    finally:
        video.release()
        cv2.destroyAllWindows()


def open_webcam(camera_index=0):
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        raise RuntimeError(
            f"Không thể mở webcam index {camera_index}"
        )

    return camera


def show_webcam(camera_index=0):
    camera = open_webcam(camera_index)

    try:
        while True:
            success, frame = camera.read()

            if not success:
                raise RuntimeError(
                    "Không thể đọc frame từ webcam"
                )

            cv2.imshow("Classroom Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()