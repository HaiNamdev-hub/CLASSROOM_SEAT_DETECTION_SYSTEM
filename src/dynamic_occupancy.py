def point_inside_box(
    point,
    box
):
    x, y = point

    x1, y1, x2, y2 = box

    return (
        x1 <= x <= x2
        and
        y1 <= y <= y2
    )


def get_person_bottom_center(
    person_bbox
):
    x1, y1, x2, y2 = (
        person_bbox
    )

    center_x = int(
        (x1 + x2) / 2
    )

    bottom_y = int(
        y2
    )

    return (
        center_x,
        bottom_y
    )


def expand_chair_box(
    chair_bbox,
    frame_width,
    frame_height
):
    """
    Mở rộng vùng chair để dễ xác định
    person đang ngồi trên chair.

    Chair thường bị người che nên box
    YOLO của chair có thể nhỏ.
    """

    x1, y1, x2, y2 = (
        chair_bbox
    )

    width = x2 - x1

    height = y2 - y1


    new_x1 = int(
        x1 - width * 0.35
    )

    new_x2 = int(
        x2 + width * 0.35
    )

    new_y1 = int(
        y1 - height * 1.2
    )

    new_y2 = int(
        y2 + height * 0.15
    )


    new_x1 = max(
        0,
        new_x1
    )

    new_y1 = max(
        0,
        new_y1
    )

    new_x2 = min(
        frame_width - 1,
        new_x2
    )

    new_y2 = min(
        frame_height - 1,
        new_y2
    )


    return [
        new_x1,
        new_y1,
        new_x2,
        new_y2
    ]


def determine_dynamic_occupancy(
    persons,
    chairs,
    frame_shape
):
    """
    Tự xác định trạng thái ghế
    từ Person + Chair detection.

    Không dùng seats_webcam.json.
    """

    frame_height = (
        frame_shape[0]
    )

    frame_width = (
        frame_shape[1]
    )


    results = []


    for index, chair in enumerate(
        chairs,
        start=1
    ):

        chair_bbox = (
            chair["bbox"]
        )


        expanded_box = (
            expand_chair_box(
                chair_bbox,
                frame_width,
                frame_height
            )
        )


        occupied = False

        matched_person = None


        for person in persons:

            person_point = (
                get_person_bottom_center(
                    person["bbox"]
                )
            )


            if point_inside_box(
                person_point,
                expanded_box
            ):

                occupied = True

                matched_person = (
                    person
                )

                break


        results.append({
            "seat_id":
                f"Chair-{index:02d}",

            "roi":
                chair_bbox,

            "status":
                (
                    "Occupied"
                    if occupied
                    else
                    "Empty"
                ),

            "chair_confidence":
                chair[
                    "confidence"
                ],

            "person":
                matched_person
        })


    return results