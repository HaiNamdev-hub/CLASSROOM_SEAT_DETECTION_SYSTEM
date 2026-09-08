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


def configure_seats(image_path):
    image = read_image(image_path)

    seats = []

    seat_number = 1

    while True:
        print(
            f"\nKhoanh vùng cho ghế S{seat_number:02d}"
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

        seat_id = f"S{seat_number:02d}"

        seat = {
            "seat_id": seat_id,
            "roi": [
                int(x),
                int(y),
                int(x + w),
                int(y + h)
            ]
        }

        seats.append(seat)

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
            (x, max(y - 10, 20)),
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

if __name__ == "__main__":
    # image_path = "data/input/classroom.jpg"

    # seats = configure_seats(
    #     image_path
    # )

    # if seats:
    #     save_seats(seats)

    #     print(
    #         f"\nTổng số ghế: {len(seats)}"
    #     )

    # else:
    #     print(
    #         "Chưa cấu hình ghế nào."
    #     )

    image = read_image(
        "data/input/classroom.jpg"
    )

    seats = load_seats()

    output_image = draw_seats(
        image,
        seats
    )

    cv2.imshow(
        "Seat ROI Test",
        output_image
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()