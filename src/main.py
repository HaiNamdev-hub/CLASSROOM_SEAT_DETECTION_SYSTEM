from src.file_handler import get_file_info


def main():
    print("=" * 50)
    print("A7 - CLASSROOM SEAT DETECTION")
    print("=" * 50)

    print("Application started.")

    try:
        file_path = input("Nhập đường dẫn file input: ")

        file_info = get_file_info(file_path)

        print("\nFile hợp lệ.")
        print(f"Tên file: {file_info['name']}")
        print(f"Định dạng: {file_info['extension']}")
        print(f"Kích thước: {file_info['size']} bytes")
        print(f"Đường dẫn: {file_info['path']}")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")

    except ValueError as e:
        print(f"[ERROR] {e}")

    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}")

    finally:
        print("\nApplication finished.")


if __name__ == "__main__":
    main()