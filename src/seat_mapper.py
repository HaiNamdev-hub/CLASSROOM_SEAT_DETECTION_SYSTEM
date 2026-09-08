def get_person_center(person):
    x1, y1, x2, y2 = person["bbox"]

    center_x = int(
        (x1 + x2) / 2
    )

    center_y = int(
        (y1 + y2) / 2
    )

    return center_x, center_y

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
    center = get_person_center(
        person
    )

    for seat in seats:
        if point_inside_roi(
            center,
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