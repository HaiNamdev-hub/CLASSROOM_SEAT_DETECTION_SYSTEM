from src.person_detector import (
    detect_classroom_objects,
    extract_classroom_detections,
    draw_person_detections
)

from src.dynamic_occupancy import (
    determine_dynamic_occupancy
)

from src.visualizer import (
    draw_dynamic_seat_status,
    draw_statistics
)


def process_dynamic_webcam_frame(
    model,
    frame,
    fps=None
):

    # =========================================
    # 1. YOLO:
    # PERSON + CHAIR + OBJECT
    # =========================================

    results = (
        detect_classroom_objects(
            model,
            frame
        )
    )


    persons, chairs, objects = (
        extract_classroom_detections(
            results
        )
    )


    # =========================================
    # 2. DETERMINE OCCUPANCY
    # =========================================

    occupancy_results = (
        determine_dynamic_occupancy(
            persons,
            chairs,
            frame.shape,
            objects
        )
    )


    # =========================================
    # 3. COUNT STATUS
    # =========================================

    occupied_count = sum(
        1
        for seat in occupancy_results
        if seat["status"]
        == "Occupied"
    )


    blocked_count = sum(
        1
        for seat in occupancy_results
        if seat["status"]
        == "Blocked"
    )


    total_seats = len(
        occupancy_results
    )


    empty_count = sum(
        1
        for seat in occupancy_results
        if seat["status"]
        == "Empty"
    )


    occupancy_rate = (
        occupied_count
        / total_seats
        * 100

        if total_seats > 0

        else 0.0
    )


    statistics = {

        "total_seats":
            total_seats,

        "occupied_seats":
            occupied_count,

        "blocked_seats":
            blocked_count,

        "empty_seats":
            empty_count,

        "occupancy_rate":
            occupancy_rate
    }


    # =========================================
    # 4. DRAW PERSON
    # =========================================

    output = (
        draw_person_detections(
            frame,
            persons
        )
    )


    # =========================================
    # 5. DRAW CHAIR STATUS
    # =========================================

    output = (
        draw_dynamic_seat_status(
            output,
            occupancy_results
        )
    )


    # =========================================
    # 6. DRAW STATISTICS
    # =========================================

    output = (
        draw_statistics(
            output,
            statistics,
            fps
        )
    )


    # =========================================
    # 7. RETURN
    # =========================================

    return (
        output,
        persons,
        chairs,
        occupancy_results,
        statistics
    )