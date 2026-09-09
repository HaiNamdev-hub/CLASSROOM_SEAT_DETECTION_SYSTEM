import cv2
import json

from pathlib import Path

from src.image_handler import read_image


DEFAULT_SEAT_CONFIG = "config/seats.json"


def save_seats(
    seats,
    output_path=DEFAULT_SEAT_CONFIG
):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            seats,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Đã lưu Seat Config tại: "
        f"{output_path}"
    )


def load_seats(
    config_path=DEFAULT_SEAT_CONFIG
):
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy Seat Config: "
            f"{config_path}"
        )

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def configure_seats(image):
    image = image.copy()

    seats = []

    seat_number = 1

    while True:
        print(
            f"\nKhoanh vùng cho ghế "
            f"S{seat_number:02d}"
        )

        print(
            "Kéo chuột chọn vùng ghế."
        )

        print(
            "ENTER/SPACE: xác nhận"
        )

        print(
            "ESC: kết thúc"
        )

        x, y, w, h = cv2.selectROI(
            "Seat ROI Configuration",
            image,
            showCrosshair=True,
            fromCenter=False
        )

        if w == 0 or h == 0:
            break

        seat_id = (
            f"S{seat_number:02d}"
        )

        seat = {
            "seat_id": seat_id,
            "roi": [
                int(x),
                int(y),
                int(x + w),
                int(y + h)
            ]
        }

        seats.append(
            seat
        )

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

        cv2.putText(
            image,
            seat_id,
            (
                x,
                max(y - 10, 20)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

        print(
            f"Đã tạo {seat_id}: "
            f"{seat['roi']}"
        )

        seat_number += 1

    cv2.destroyAllWindows()

    return seats

def draw_seats(image, seats):
    output_image = image.copy()

    for seat in seats:
        seat_id = seat["seat_id"]

        x1, y1, x2, y2 = seat["roi"]

        cv2.rectangle(
            output_image,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            output_image,
            seat_id,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

    return output_image

def get_video_frame(
    video_path,
    frame_number=0
):
    video = cv2.VideoCapture(
        video_path
    )

    if not video.isOpened():
        raise ValueError(
            f"Không thể mở video: {video_path}"
        )

    video.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number
    )

    success, frame = video.read()

    video.release()

    if not success:
        raise ValueError(
            f"Không thể đọc frame {frame_number} "
            f"từ video."
        )

    return frame

def get_webcam_frame(
    camera_index=0
):
    camera = cv2.VideoCapture(
        camera_index
    )

    if not camera.isOpened():
        raise RuntimeError(
            f"Không thể mở webcam index "
            f"{camera_index}"
        )

    success, frame = camera.read()

    camera.release()

    if not success:
        raise RuntimeError(
            "Không thể lấy frame từ webcam."
        )

    return frame

if __name__ == "__main__":
    print("=" * 50)
    print("SEAT ROI CONFIGURATION")
    print("=" * 50)

    print("1. Image")
    print("2. Video")
    print("3. Webcam")

    choice = input(
        "Chọn nguồn để cấu hình Seat ROI: "
    ).strip()

    if choice == "1":
        image = read_image(
            "data/input/classroom.jpg"
        )

        seats = configure_seats(
            image
        )

        config_path = "config/seats_image.json"

        if seats:
            save_seats(
                seats,
                config_path
            )

            print(
                f"\nTổng số ghế: {len(seats)}"
            )

            output_image = draw_seats(
                image,
                seats
            )

            cv2.imshow(
                "Seat ROI - Image",
                output_image
            )

            cv2.waitKey(0)
            cv2.destroyAllWindows()

    elif choice == "2":
        frame = get_video_frame(
            "data/input/classroom.mp4",
            frame_number=0
        )

        seats = configure_seats(
            frame
        )

        config_path = "config/seats_video.json"

        if seats:
            save_seats(
                seats,
                config_path
            )

            print(
                f"\nTổng số ghế: {len(seats)}"
            )

            output_frame = draw_seats(
                frame,
                seats
            )

            h, w = output_frame.shape[:2]

            display_width = 960
            ratio = display_width / w
            display_height = int(h * ratio)

            display_frame = cv2.resize(
                output_frame,
                (display_width, display_height)
            )

            cv2.imshow(
                "Seat ROI - Video",
                display_frame
            )

            cv2.waitKey(0)
            cv2.destroyAllWindows()

    elif choice == "3":
        frame = get_webcam_frame(
            camera_index=0
        )

        seats = configure_seats(
            frame
        )

        config_path = "config/seats_webcam.json"

        if seats:
            save_seats(
                seats,
                config_path
            )

            print(
                f"\nTổng số ghế: {len(seats)}"
            )

            output_frame = draw_seats(
                frame,
                seats
            )

            cv2.imshow(
                "Seat ROI - Webcam",
                output_frame
            )

            cv2.waitKey(0)
            cv2.destroyAllWindows()

    else:
        print(
            "Lựa chọn không hợp lệ."
        )