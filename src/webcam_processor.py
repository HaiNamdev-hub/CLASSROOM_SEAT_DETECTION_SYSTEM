from src.person_detector import (
    detect_persons_and_chairs,
    extract_person_and_chair_detections
)

from src.dynamic_occupancy import (
    determine_dynamic_occupancy
)

from src.person_detector import (
    draw_person_detections
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
    # 1. YOLO: PERSON + CHAIR
    # =========================================

    results = (
        detect_persons_and_chairs(
            model,
            frame
        )
    )


    persons, chairs = (
        extract_person_and_chair_detections(
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
            frame.shape
        )
    )


    occupied_count = sum(
        1
        for seat
        in occupancy_results
        if seat["status"]
        == "Occupied"
    )


    total_seats = len(
        occupancy_results
    )


    empty_count = (
        total_seats
        - occupied_count
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

        "empty_seats":
            empty_count,

        "occupancy_rate":
            occupancy_rate
    }


    # =========================================
    # 3. DRAW PERSON
    # =========================================

    output = (
        draw_person_detections(
            frame,
            persons
        )
    )


    # =========================================
    # 4. DRAW CHAIR STATUS
    # =========================================

    output = (
        draw_dynamic_seat_status(
            output,
            occupancy_results
        )
    )


    # =========================================
    # 5. DRAW STATISTICS
    # =========================================

    output = (
        draw_statistics(
            output,
            statistics,
            fps
        )
    )


    return (
        output,
        persons,
        chairs,
        occupancy_results,
        statistics
    )