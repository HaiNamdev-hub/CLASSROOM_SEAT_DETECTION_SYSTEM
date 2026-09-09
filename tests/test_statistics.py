import unittest

from src.statistics import (
    calculate_statistics
)


class TestStatistics(unittest.TestCase):

    def test_statistics(self):

        occupancy = [
            {
                "seat_id": "S01",
                "status": "Occupied"
            },
            {
                "seat_id": "S02",
                "status": "Empty"
            },
            {
                "seat_id": "S03",
                "status": "Occupied"
            },
            {
                "seat_id": "S04",
                "status": "Empty"
            }
        ]

        result = calculate_statistics(
            occupancy
        )

        self.assertEqual(
            result["total_seats"],
            4
        )

        self.assertEqual(
            result["occupied_seats"],
            2
        )

        self.assertEqual(
            result["empty_seats"],
            2
        )

        self.assertEqual(
            result["occupancy_rate"],
            50.0
        )


if __name__ == "__main__":
    unittest.main()