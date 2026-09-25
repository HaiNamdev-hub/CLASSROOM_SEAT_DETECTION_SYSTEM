from ultralytics import YOLO

from src.image_handler import read_image
import cv2
from pathlib import Path
import time


DEFAULT_MODEL = "yolo11n.pt"
PERSON_CLASS_ID = 0
CHAIR_CLASS_ID = 56


BLOCKING_OBJECT_CLASS_IDS = {
    24: "backpack",
    26: "handbag",
    28: "suitcase",
    39: "bottle",
    63: "laptop",
    67: "cell phone",
    73: "book",
}

def load_model(model_name=DEFAULT_MODEL):
    try:
        print(f"Đang load model: {model_name}")

        model = YOLO(model_name)

        print(f"Load model thành công: {model_name}")

        return model

    except Exception as e:
        raise RuntimeError(
            f"Không thể load YOLO model: {e}"
        )


def detect_persons(model, image):
    """
    Detect person trong một ảnh.
    """

    results = model(
        image,
        classes=[PERSON_CLASS_ID]
    )

    return results


def detect_persons_and_chairs(
    model,
    image
):
    """
    Detect Person và Chair
    dùng cho webcam dynamic.
    """

    results = model(
        image,
        classes=[
            PERSON_CLASS_ID,
            CHAIR_CLASS_ID
        ]
    )

    return results

def detect_classroom_objects(
    model,
    image
):
    class_ids = [
        PERSON_CLASS_ID,
        CHAIR_CLASS_ID,
        *BLOCKING_OBJECT_CLASS_IDS.keys()
    ]

    results = model(
        image,
        classes=class_ids,
        conf=0.15,
        iou=0.45
    )

    return results


def extract_classroom_detections(
    results
):
    persons = []
    chairs = []
    objects = []

    for result in results:

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            confidence = float(
                box.conf[0]
            )

            detection = {
                "bbox": [
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                ],

                "confidence":
                    confidence,

                "class_id":
                    class_id
            }

            # PERSON
            if class_id == PERSON_CLASS_ID:

                detection["class"] = "person"

                persons.append(
                    detection
                )

            # CHAIR
            elif class_id == CHAIR_CLASS_ID:

                detection["class"] = "chair"

                chairs.append(
                    detection
                )

            # OBJECT
            elif class_id in BLOCKING_OBJECT_CLASS_IDS:

                detection["class"] = (
                    BLOCKING_OBJECT_CLASS_IDS[
                        class_id
                    ]
                )

                objects.append(
                    detection
                )

    return (
        persons,
        chairs,
        objects
    )


def extract_person_and_chair_detections(
    results
):
    persons = []
    chairs = []

    for result in results:

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            confidence = float(
                box.conf[0]
            )

            detection = {
                "bbox": [
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                ],
                "confidence":
                    confidence
            }

            if (
                class_id
                == PERSON_CLASS_ID
            ):
                persons.append(
                    detection
                )

            elif (
                class_id
                == CHAIR_CLASS_ID
            ):
                chairs.append(
                    detection
                )

    return persons, chairs


def extract_person_detections(results):
    detections = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            confidence = float(box.conf[0])

            detection = {
                "bbox": [
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                ],
                "confidence": confidence
            }

            detections.append(detection)

    return detections

def draw_person_detections(image, detections):
    output_image = image.copy()

    for person in detections:
        x1, y1, x2, y2 = person["bbox"]
        confidence = person["confidence"]

        cv2.rectangle(
            output_image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        label = f"Person {confidence:.2f}"

        cv2.putText(
            output_image,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return output_image

def save_detection_image(image, output_path):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise ValueError(
            f"Không thể lưu ảnh: {output_path}"
        )

    return output_path

def detect_video(
    model,
    video_path,
    output_path="results/videos/detection_video.mp4"
):
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError(
            f"Không thể mở video: {video_path}"
        )

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25.0

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"avc1"
    )

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        video.release()

        raise RuntimeError(
            f"Không thể tạo video output: {output_path}"
        )

    try:
        previous_time = time.time()
        while True:
            success, frame = video.read()

            if not success:
                break

            results = detect_persons(
                model,
                frame
            )

            detections = (
                extract_person_detections(
                    results
                )
            )

            output_frame = (
                draw_person_detections(
                    frame,
                    detections
                )
            )

            current_time = time.time()

            elapsed_time = current_time - previous_time

            fps_realtime = (
                1 / elapsed_time
                if elapsed_time > 0
                else 0
            )

            previous_time = current_time

            cv2.putText(
                output_frame,
                f"FPS: {fps_realtime:.1f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )

            # Lưu frame gốc đã có bbox
            writer.write(output_frame)

            # Resize chỉ để hiển thị
            h, w = output_frame.shape[:2]

            display_width = 960
            ratio = display_width / w
            display_height = int(
                h * ratio
            )

            display_frame = cv2.resize(
                output_frame,
                (
                    display_width,
                    display_height
                )
            )

            cv2.imshow(
                "YOLO Person Detection - Video",
                display_frame
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:
        video.release()
        writer.release()
        cv2.destroyAllWindows()

    print(
        f"Đã lưu video YOLO tại: "
        f"{output_path}"
    )

def detect_webcam(
    model,
    camera_index=0,
    output_path="results/videos/detection_webcam.mp4"
):
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        raise RuntimeError(
            f"Không thể mở webcam index {camera_index}"
        )

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    camera_fps = camera.get(cv2.CAP_PROP_FPS)

    if camera_fps <= 0:
        camera_fps = 20.0

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fourcc = cv2.VideoWriter_fourcc(*"avc1")

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        camera_fps,
        (width, height)
    )

    if not writer.isOpened():
        camera.release()

        raise RuntimeError(
            f"Không thể tạo video webcam output: {output_path}"
        )

    previous_time = time.time()

    try:
        while True:
            success, frame = camera.read()

            if not success:
                raise RuntimeError(
                    "Không thể đọc frame từ webcam"
                )

            results = detect_persons(
                model,
                frame
            )

            detections = extract_person_detections(
                results
            )

            output_frame = draw_person_detections(
                frame,
                detections
            )

            # Tính FPS realtime
            current_time = time.time()

            elapsed_time = (
                current_time - previous_time
            )

            fps_realtime = (
                1 / elapsed_time
                if elapsed_time > 0
                else 0
            )

            previous_time = current_time

            # Vẽ FPS
            cv2.putText(
                output_frame,
                f"FPS: {fps_realtime:.1f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2
            )

            # Lưu webcam
            writer.write(output_frame)

            cv2.imshow(
                "YOLO Person Detection - Webcam",
                output_frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        writer.release()
        cv2.destroyAllWindows()

    print(
        f"Đã lưu webcam YOLO tại: {output_path}"
    )

# if __name__ == "__main__":
#     model = load_model()

#     image_path = "data/input/classroom.jpg"

#     image = read_image(image_path)

#     results = detect_persons(
#         model,
#         image
#     )

#     detections = extract_person_detections(
#         results
#     )

#     print("\n===== PERSON DETECTIONS =====")

#     print(f"Số người phát hiện: {len(detections)}")

#     for index, person in enumerate(detections, start=1):
#         print(f"\nPerson {index}")
#         print(f"Bounding Box: {person['bbox']}")
#         print(f"Confidence: {person['confidence']:.2f}")

#     output_image = draw_person_detections(
#     image,
#     detections
#     )

#     saved_path = save_detection_image(
#         output_image,
#         "results/screenshots/classroom.jpg"
#     )

#     print(
#         f"Đã lưu ảnh YOLO tại: {saved_path}"
#     )

#     cv2.imshow(
#         "YOLO Person Detection",
#         output_image
#     )

#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

if __name__ == "__main__":
    model = load_model()

    video_path = "data/input/classroom.mp4"

    detect_video(
        model,
        video_path
    )

# if __name__ == "__main__":
#     model = load_model()

#     detect_webcam(
#         model,
#         camera_index=0
#     )