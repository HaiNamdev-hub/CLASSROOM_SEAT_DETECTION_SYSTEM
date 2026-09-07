import cv2

from src.file_handler import check_file
from pathlib import Path


def read_image(file_path):
    """
    Đọc ảnh từ đường dẫn bằng OpenCV.
    """

    # Kiểm tra file có tồn tại trước
    path = check_file(file_path)

    # Đọc ảnh
    image = cv2.imread(str(path))

    # File tồn tại nhưng không phải ảnh / OpenCV không đọc được
    if image is None:
        raise ValueError(f"Không thể đọc ảnh: {file_path}")

    return image


def get_image_info(image):
    """
    Lấy thông tin kích thước ảnh.
    """

    height, width = image.shape[:2]

    return {
        "width": width,
        "height": height,
        "channels": image.shape[2] if len(image.shape) == 3 else 1
    }


def show_image(image, window_name="Classroom Image"):
    """
    Hiển thị ảnh bằng OpenCV.
    """

    cv2.imshow(window_name, image)

    print("Nhấn phím bất kỳ để đóng ảnh...")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize_image(image, width=800):
    """
    Resize ảnh theo chiều rộng, giữ nguyên tỷ lệ.
    """

    original_height, original_width = image.shape[:2]

    ratio = width / original_width
    new_height = int(original_height * ratio)

    resized_image = cv2.resize(
        image,
        (width, new_height)
    )

    return resized_image


def convert_to_gray(image):
    """
    Chuyển ảnh màu sang ảnh grayscale.
    """

    gray_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return gray_image


def save_image(image, output_path):
    """
    Lưu ảnh kết quả.
    """

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