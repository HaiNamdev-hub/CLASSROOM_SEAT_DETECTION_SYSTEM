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