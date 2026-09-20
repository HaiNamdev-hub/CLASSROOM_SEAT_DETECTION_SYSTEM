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


# =========================================================
# PERSON POSITION
# =========================================================

def get_person_bottom_center(
    person_bbox
):
    x1, y1, x2, y2 = person_bbox

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


# =========================================================
# OBJECT CENTER
# =========================================================

def get_box_center(
    bbox
):
    x1, y1, x2, y2 = bbox

    center_x = int(
        (x1 + x2) / 2
    )

    center_y = int(
        (y1 + y2) / 2
    )

    return (
        center_x,
        center_y
    )


# =========================================================
# EXPAND CHAIR FOR PERSON
# =========================================================

def expand_chair_box(
    chair_bbox,
    frame_width,
    frame_height
):
    """
    Mở rộng vùng chair để dễ xác định
    person đang ngồi trên chair.

    Chair thường bị người che nên box
    YOLO có thể nhỏ.
    """

    x1, y1, x2, y2 = chair_bbox

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


# =========================================================
# EXPAND CHAIR FOR OBJECT
# =========================================================

def expand_chair_for_object(
    chair_bbox,
    frame_width,
    frame_height
):
    """
    Mở rộng nhẹ vùng chair để kiểm tra
    backpack, laptop, phone, book...
    """

    x1, y1, x2, y2 = chair_bbox

    width = x2 - x1
    height = y2 - y1


    new_x1 = int(
        x1 - width * 0.20
    )

    new_x2 = int(
        x2 + width * 0.20
    )

    new_y1 = int(
        y1 - height * 0.35
    )

    new_y2 = int(
        y2 + height * 0.20
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


# =========================================================
# OBJECT / CHAIR OVERLAP
# =========================================================

def calculate_overlap_ratio(
    object_bbox,
    chair_bbox
):
    """
    Tính tỷ lệ diện tích object
    nằm bên trong vùng chair.

    Giá trị:
    0.0 -> không giao nhau
    1.0 -> object hoàn toàn nằm trong chair
    """

    ox1, oy1, ox2, oy2 = object_bbox
    cx1, cy1, cx2, cy2 = chair_bbox


    intersection_x1 = max(
        ox1,
        cx1
    )

    intersection_y1 = max(
        oy1,
        cy1
    )

    intersection_x2 = min(
        ox2,
        cx2
    )

    intersection_y2 = min(
        oy2,
        cy2
    )


    intersection_width = max(
        0,
        intersection_x2
        - intersection_x1
    )

    intersection_height = max(
        0,
        intersection_y2
        - intersection_y1
    )


    intersection_area = (
        intersection_width
        *
        intersection_height
    )


    object_width = max(
        0,
        ox2 - ox1
    )

    object_height = max(
        0,
        oy2 - oy1
    )


    object_area = (
        object_width
        *
        object_height
    )


    if object_area <= 0:
        return 0.0


    return (
        intersection_area
        /
        object_area
    )


# =========================================================
# DYNAMIC OCCUPANCY
# =========================================================

def determine_dynamic_occupancy(
    persons,
    chairs,
    frame_shape,
    objects=None
):
    """
    Xác định trạng thái chair:

    Occupied:
        Có person ngồi trên chair.

    Blocked:
        Không có person,
        nhưng có object nằm trên chair.

    Empty:
        Không có person
        và không có object.
    """

    if objects is None:
        objects = []


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


        # =====================================
        # VÙNG KIỂM TRA PERSON
        # =====================================

        person_area = (
            expand_chair_box(
                chair_bbox,
                frame_width,
                frame_height
            )
        )


        # =====================================
        # VÙNG KIỂM TRA OBJECT
        # =====================================

        object_area = (
            expand_chair_for_object(
                chair_bbox,
                frame_width,
                frame_height
            )
        )


        matched_person = None

        matched_object = None


        # =====================================
        # 1. ƯU TIÊN PERSON
        # =====================================

        for person in persons:

            person_point = (
                get_person_bottom_center(
                    person["bbox"]
                )
            )


            if point_inside_box(
                person_point,
                person_area
            ):

                matched_person = (
                    person
                )

                break


        # =====================================
        # 2. NẾU KHÔNG CÓ PERSON
        #    THÌ KIỂM TRA OBJECT
        # =====================================

        if matched_person is None:

            best_overlap = 0.0


            for obj in objects:

                object_bbox = (
                    obj["bbox"]
                )


                object_center = (
                    get_box_center(
                        object_bbox
                    )
                )


                center_inside = (
                    point_inside_box(
                        object_center,
                        object_area
                    )
                )


                overlap_ratio = (
                    calculate_overlap_ratio(
                        object_bbox,
                        object_area
                    )
                )


                # Object được coi là nằm
                # trên ghế nếu:
                #
                # - tâm nằm trong chair
                # hoặc
                # - ít nhất 30% object
                #   giao với chair

                if (
                    center_inside
                    or
                    overlap_ratio >= 0.30
                ):

                    if (
                        overlap_ratio
                        >= best_overlap
                    ):

                        best_overlap = (
                            overlap_ratio
                        )

                        matched_object = (
                            obj
                        )


        # =====================================
        # 3. XÁC ĐỊNH STATUS
        # =====================================

        if matched_person is not None:

            status = (
                "Occupied"
            )


        elif matched_object is not None:

            status = (
                "Blocked"
            )


        else:

            status = (
                "Empty"
            )


        # =====================================
        # 4. SAVE RESULT
        # =====================================

        result = {

            "seat_id":
                f"Chair-{index:02d}",

            "roi":
                chair_bbox,

            "status":
                status,

            "chair_confidence":
                chair[
                    "confidence"
                ],

            "person":
                matched_person,

            "object":
                matched_object
        }


        results.append(
            result
        )


    return results