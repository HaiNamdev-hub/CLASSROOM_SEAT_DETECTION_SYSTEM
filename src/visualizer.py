import cv2
from pathlib import Path


def draw_seat_status(
    image,
    occupancy_results
):
    output = image.copy()

    for seat in occupancy_results:

        seat_id = seat["seat_id"]
        status = seat["status"]

        x1, y1, x2, y2 = seat["roi"]

        if status == "Occupied":
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        cv2.rectangle(
            output,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        label = f"{seat_id}: {status}"

        cv2.putText(
            output,
            label,
            (
                x1,
                max(y1 - 10, 20)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    return output


def draw_statistics(
    image,
    statistics,
    fps=None
):
    output = image.copy()

    lines = [
        (
            "Total Seats: "
            f"{statistics['total_seats']}"
        ),
        (
            "Occupied: "
            f"{statistics['occupied_seats']}"
        ),
        (
            "Empty: "
            f"{statistics['empty_seats']}"
        ),
        (
            "Occupancy Rate: "
            f"{statistics['occupancy_rate']:.1f}%"
        )
    ]

    if fps is not None:
        lines.append(
            f"FPS: {fps:.1f}"
        )

    x = 20
    y = 35

    for line in lines:

        cv2.putText(
            output,
            line,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        y += 30

    return output

def draw_dynamic_seat_status(
    image,
    occupancy_results
):
    output = image.copy()

    for seat in occupancy_results:

        x1, y1, x2, y2 = seat["roi"]

        status = seat["status"]
        seat_id = seat["seat_id"]

        # =====================================
        # COLOR BY STATUS
        # =====================================

        if status == "Occupied":

            # Đỏ
            color = (
                0,
                0,
                255
            )

        elif status == "Blocked":

            # Cam
            color = (
                0,
                165,
                255
            )

        else:

            # Xanh
            color = (
                0,
                255,
                0
            )


        # =====================================
        # DRAW CHAIR BOX
        # =====================================

        cv2.rectangle(
            output,
            (x1, y1),
            (x2, y2),
            color,
            2
        )


        # =====================================
        # LABEL
        # =====================================

        label = (
            f"{seat_id}: {status}"
        )


        # Nếu ghế bị vật cản
        if status == "Blocked":

            obj = seat.get(
                "object"
            )

            if obj is not None:

                object_name = obj.get(
                    "class",
                    "object"
                )

                confidence = obj.get(
                    "confidence",
                    0.0
                )

                label = (
                    f"{seat_id}: Blocked - "
                    f"{object_name} "
                    f"{confidence:.2f}"
                )


        # =====================================
        # DRAW LABEL
        # =====================================

        cv2.putText(
            output,
            label,
            (
                x1,
                max(
                    y1 - 10,
                    20
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )


    return output


if __name__ == "__main__":

    image = cv2.imread(
        "data/input/classroom.jpg"
    )

    if image is None:

        raise FileNotFoundError(
            "Không đọc được "
            "data/input/classroom.jpg"
        )


    occupancy_results = [
        {
            "seat_id": "S01",
            "roi": [
                50,
                250,
                220,
                430
            ],
            "status":
                "Occupied"
        },
        {
            "seat_id": "S02",
            "roi": [
                250,
                250,
                420,
                430
            ],
            "status":
                "Empty"
        },
        {
            "seat_id": "S03",
            "roi": [
                450,
                250,
                620,
                430
            ],
            "status":
                "Occupied"
        }
    ]


    statistics = {
        "total_seats": 3,
        "occupied_seats": 2,
        "empty_seats": 1,
        "occupancy_rate": 66.7
    }


    output = draw_seat_status(
        image,
        occupancy_results
    )


    output = draw_statistics(
        output,
        statistics,
        fps=18.5
    )


    output_path = Path(
        "results/screenshots/"
        "visualizer_test.jpg"
    )


    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    success = cv2.imwrite(
        str(output_path),
        output
    )


    if not success:

        raise ValueError(
            f"Không thể lưu ảnh tại: "
            f"{output_path}"
        )


    print(
        f"Đã lưu ảnh test tại: "
        f"{output_path}"
    )


    cv2.imshow(
        "Visualizer Test",
        output
    )


    cv2.waitKey(0)

    cv2.destroyAllWindows()