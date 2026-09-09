import unittest

from src.seat_mapper import (
    get_person_position,
    point_inside_roi,
    map_person_to_seat
)


class TestSeatMapping(unittest.TestCase):

    def test_person_position(self):
        person = {
            "bbox": [100, 100, 300, 400],
            "confidence": 0.90
        }

        position = get_person_position(
            person
        )

        self.assertEqual(
            position,
            (200, 400)
        )

    def test_point_inside_roi(self):
        point = (150, 300)

        roi = [
            100,
            200,
            300,
            400
        ]

        self.assertTrue(
            point_inside_roi(
                point,
                roi
            )
        )

    def test_point_outside_roi(self):
        point = (500, 500)

        roi = [
            100,
            200,
            300,
            400
        ]

        self.assertFalse(
            point_inside_roi(
                point,
                roi
            )
        )

    def test_map_person_to_seat(self):
        person = {
            "bbox": [
                100,
                100,
                300,
                400
            ],
            "confidence": 0.90
        }

        seats = [
            {
                "seat_id": "S01",
                "roi": [
                    100,
                    300,
                    300,
                    450
                ]
            }
        ]

        seat_id = map_person_to_seat(
            person,
            seats
        )

        self.assertEqual(
            seat_id,
            "S01"
        )


if __name__ == "__main__":
    unittest.main()