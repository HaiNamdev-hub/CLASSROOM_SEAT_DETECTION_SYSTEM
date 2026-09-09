def determine_occupancy(
    seats,
    mappings
):
    occupied_seats = set()

    for mapping in mappings:
        seat_id = mapping["seat_id"]

        if seat_id is not None:
            occupied_seats.add(
                seat_id
            )

    results = []

    for seat in seats:
        seat_id = seat["seat_id"]

        status = (
            "Occupied"
            if seat_id in occupied_seats
            else "Empty"
        )

        results.append({
            "seat_id": seat_id,
            "roi": seat["roi"],
            "status": status
        })

    return results

if __name__ == "__main__":
    from src.seat_config import load_seats
    from src.seat_mapper import map_persons_to_seats
    from src.image_handler import read_image
    from src.person_detector import (
        load_model,
        detect_persons,
        extract_person_detections
    )

    model = load_model()

    image = read_image(
        "data/input/classroom.jpg"
    )

    results = detect_persons(
        model,
        image
    )

    detections = extract_person_detections(
        results
    )

    seats = load_seats()

    mappings = map_persons_to_seats(
        detections,
        seats
    )

    occupancy = determine_occupancy(
        seats,
        mappings
    )

    print("\n===== SEAT STATUS =====")

    for seat in occupancy:
        print(
            f"{seat['seat_id']} "
            f"-> {seat['status']}"
        )