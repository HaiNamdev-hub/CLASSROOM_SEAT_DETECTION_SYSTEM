import cv2

from src.file_handler import check_file


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