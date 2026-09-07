from src.file_handler import get_file_info
from config.config import PROJECT_NAME
from config.logger import setup_logger
from src.image_handler import read_image, get_image_info, show_image

logger = setup_logger()


def main():
    print("=" * 50)
    print(PROJECT_NAME)
    print("=" * 50)

    logger.info("Application started")

    try:
        file_path = input("Nhập đường dẫn file input: ")

        file_info = get_file_info(file_path)

        image = read_image(file_path)

        image_info = get_image_info(image)

        print("\nThông tin hình ảnh:")
        print(f"Chiều rộng: {image_info['width']} px")
        print(f"Chiều cao: {image_info['height']} px")
        print(f"Số kênh màu: {image_info['channels']}")

        show_image(image)

        logger.info("Input file checked successfully")

        print("\nFile hợp lệ.")
        print(f"Tên file: {file_info['name']}")
        print(f"Định dạng: {file_info['extension']}")
        print(f"Kích thước: {file_info['size']} bytes")
        print(f"Đường dẫn: {file_info['path']}")

    except FileNotFoundError as e:
        logger.error(e)

    except ValueError as e:
        logger.error(e)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

    finally:
        logger.info("Application finished")


if __name__ == "__main__":
    main()