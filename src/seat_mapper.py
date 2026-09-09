from src.image_handler import read_image
from src.person_detector import (
    load_model,
    detect_persons,
    extract_person_detections
)
from src.seat_config import load_seats

def get_person_position(person):
    x1, y1, x2, y2 = person["bbox"]

    point_x = int(
        (x1 + x2) / 2
    )

    point_y = y2

    return point_x, point_y

def point_inside_roi(
    point,
    roi
):
    px, py = point

    x1, y1, x2, y2 = roi

    return (
        x1 <= px <= x2
        and
        y1 <= py <= y2
    )

def map_person_to_seat(
    person,
    seats
):
    position = get_person_position(
        person
    )

    print(
        f"Person position: {position}"
    )

    for seat in seats:
        if point_inside_roi(
            position,
            seat["roi"]
        ):
            return seat["seat_id"]

    return None

def map_persons_to_seats(
    detections,
    seats
):
    mappings = []

    for person in detections:
        seat_id = map_person_to_seat(
            person,
            seats
        )

        mappings.append({
            "bbox": person["bbox"],
            "confidence": (
                person["confidence"]
            ),
            "seat_id": seat_id
        })

    return mappings

if __name__ == "__main__":
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

    print("\n===== REAL SEAT MAPPING =====")

    for mapping in mappings:
        print(
            f"BBox: {mapping['bbox']} "
            f"-> Seat: {mapping['seat_id']} "
            f"| Confidence: "
            f"{mapping['confidence']:.2f}"
        )