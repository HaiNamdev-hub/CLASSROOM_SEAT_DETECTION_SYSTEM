import unittest

from src.occupancy import (
    determine_occupancy
)


class TestOccupancy(unittest.TestCase):

    def test_occupied_and_empty(self):

        seats = [
            {
                "seat_id": "S01",
                "roi": [0, 0, 100, 100]
            },
            {
                "seat_id": "S02",
                "roi": [100, 0, 200, 100]
            },
            {
                "seat_id": "S03",
                "roi": [200, 0, 300, 100]
            }
        ]

        mappings = [
            {
                "seat_id": "S01"
            },
            {
                "seat_id": "S03"
            }
        ]

        results = determine_occupancy(
            seats,
            mappings
        )

        self.assertEqual(
            results[0]["status"],
            "Occupied"
        )

        self.assertEqual(
            results[1]["status"],
            "Empty"
        )

        self.assertEqual(
            results[2]["status"],
            "Occupied"
        )


if __name__ == "__main__":
    unittest.main()