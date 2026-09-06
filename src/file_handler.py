from pathlib import Path


def check_file(file_path):
    """
    Kiểm tra file input có tồn tại và hợp lệ hay không.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    if not path.is_file():
        raise ValueError(f"Đường dẫn không phải là file: {file_path}")

    return path


def get_file_info(file_path):
    """
    Lấy một số thông tin cơ bản của file.
    """

    path = check_file(file_path)

    return {
        "name": path.name,
        "extension": path.suffix,
        "size": path.stat().st_size,
        "path": str(path.resolve())
    }