import unittest

from src.image_handler import read_image

from src.person_detector import (
    load_model,
    detect_persons,
    extract_person_detections
)


class TestPersonDetection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = load_model()

        cls.image = read_image(
            "data/input/classroom.jpg"
        )

    def test_detection_result_is_list(self):
        results = detect_persons(
            self.model,
            self.image
        )

        detections = extract_person_detections(
            results
        )

        self.assertIsInstance(
            detections,
            list
        )

    def test_detection_has_bbox(self):
        results = detect_persons(
            self.model,
            self.image
        )

        detections = extract_person_detections(
            results
        )

        for person in detections:
            self.assertIn(
                "bbox",
                person
            )

            self.assertEqual(
                len(person["bbox"]),
                4
            )

    def test_detection_has_confidence(self):
        results = detect_persons(
            self.model,
            self.image
        )

        detections = extract_person_detections(
            results
        )

        for person in detections:
            self.assertIn(
                "confidence",
                person
            )

            self.assertGreaterEqual(
                person["confidence"],
                0
            )

            self.assertLessEqual(
                person["confidence"],
                1
            )


if __name__ == "__main__":
    unittest.main()