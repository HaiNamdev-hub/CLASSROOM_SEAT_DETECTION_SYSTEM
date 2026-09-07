from src.file_handler import get_file_info
from config.config import PROJECT_NAME
from config.logger import setup_logger
from src.image_handler import (
    read_image,
    get_image_info,
    show_image,
    resize_image,
    convert_to_gray,
    save_image
)
from src.video_handler import play_video
from src.video_handler import play_video, show_webcam

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

        resized_image = resize_image(image, width=800)

        gray_image = convert_to_gray(resized_image)

        output_path = save_image(
            gray_image,
            "data/output/classroom_gray.jpg"
        )

        print(f"Đã lưu ảnh xử lý tại: {output_path}")

        show_image(
            gray_image,
            "Processed Image"
        )

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

        play_video("data/input/classroom.mp4")

        show_webcam()

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