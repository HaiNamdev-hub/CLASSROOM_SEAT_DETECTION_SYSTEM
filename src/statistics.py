def calculate_statistics(occupancy_results):
    total_seats = len(occupancy_results)

    occupied_seats = sum(
        1
        for seat in occupancy_results
        if seat["status"] == "Occupied"
    )

    empty_seats = total_seats - occupied_seats

    occupancy_rate = (
        occupied_seats / total_seats * 100
        if total_seats > 0
        else 0.0
    )

    return {
        "total_seats": total_seats,
        "occupied_seats": occupied_seats,
        "empty_seats": empty_seats,
        "occupancy_rate": occupancy_rate
    }

if __name__ == "__main__":
    test_data = [
        {"seat_id": "S01", "status": "Occupied"},
        {"seat_id": "S02", "status": "Empty"},
        {"seat_id": "S03", "status": "Occupied"},
        {"seat_id": "S04", "status": "Empty"},
        {"seat_id": "S05", "status": "Occupied"}
    ]

    statistics = calculate_statistics(test_data)

    print("===== STATISTICS TEST =====")
    print(f"Total Seats: {statistics['total_seats']}")
    print(f"Occupied: {statistics['occupied_seats']}")
    print(f"Empty: {statistics['empty_seats']}")
    print(
        f"Occupancy Rate: "
        f"{statistics['occupancy_rate']:.1f}%"
    )