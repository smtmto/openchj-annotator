import datetime
import logging
import os
import platform
import re
import zipfile
from pathlib import Path
from typing import Iterator, List
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx

import chardet


def detect_encoding(file_path: str) -> str:
    with open(file_path, "rb") as f:
        raw_data = f.read(4096)
        file_size = os.path.getsize(file_path)
        if file_size > 8192:
            f.seek(file_size // 2 - 2048)
            raw_data += f.read(4096)

        result = chardet.detect(raw_data)
        confidence = result.get("confidence", 0)
        encoding = result.get("encoding")

        if confidence > 0.7 and encoding:
            return encoding

        if raw_data.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if raw_data.startswith(b"\xff\xfe"):
            return "utf-16le"
        if raw_data.startswith(b"\xfe\xff"):
            return "utf-16be"

        if encoding:
            return encoding
        else:
            return "cp932"


def read_text_file(file_path: str, encoding: str = None) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    fallback_encodings = [
        "utf-8",
        "utf-8-sig",
        "cp932",
        "shift_jis",
        "euc_jp",
        "iso2022_jp",
        "latin1",
        "ascii",
        "big5",
        "windows-1250",
        "windows-1251",
        "windows-1252",
    ]

    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
            return content
    except UnicodeDecodeError:
        pass
    except Exception as e:
        logging.warning(f"Unexpected error occurred while reading file: {e}")

    for enc in fallback_encodings:
        if enc != encoding:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logging.warning(
                    f"Unexpected error occurred while reading file with encoding {enc}: {e}"
                )

    logging.warning(
        f"All encodings failed. Using fallback: {os.path.basename(file_path)}"
    )
    with open(file_path, "rb") as f:
        binary_data = f.read()
        return binary_data.decode("utf-8", errors="replace")


def write_text_file(content: str, file_path: str, encoding: str = "utf-8") -> None:
    if encoding.lower() in ["utf8", "utf-8"]:
        encoding = "utf-8"
    elif encoding.lower() in ["shiftjis", "shift-jis", "sjis"]:
        encoding = "cp932"

    content = content.replace("\r\n", "\n")
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    try:
        with open(file_path, "wb") as f:
            content_bytes = content.encode(encoding)
            f.write(content_bytes)
    except UnicodeEncodeError as e:
        logging.error(f"Encoding error ({encoding}): {e}")
        if encoding != "utf-8":
            logging.warning(
                f"Attempting fallback to UTF-8: {os.path.basename(file_path)}"
            )
            with open(file_path, "wb") as f:
                content_bytes = content.encode("utf-8")
                f.write(content_bytes)
        else:
            with open(file_path, "wb") as f:
                content_bytes = content.encode("utf-8", errors="replace")
                f.write(content_bytes)
            logging.warning(
                f"Saved file with replaced characters: {os.path.basename(file_path)}"
            )
    except Exception as e:
        logging.error(f"Error occurred while saving file: {e}")
        raise


def extract_zip_file(zip_path: str, extract_to: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    extracted_dirs = [
        d for d in os.listdir(extract_to) if os.path.isdir(os.path.join(extract_to, d))
    ]
    if extracted_dirs:
        return os.path.join(extract_to, extracted_dirs[0])
    return extract_to


def get_app_config_dir():
    system = platform.system()
    app_name = "OpenCHJAnnotator"

    if system == "Windows":
        app_data = os.getenv("APPDATA")
        if app_data:
            config_dir = Path(app_data) / app_name
        else:
            config_dir = Path.home() / f".{app_name.lower()}"
    elif system == "Darwin":
        config_dir = Path.home() / "Library" / "Application Support" / app_name
    else:
        xdg_config_home = os.getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / app_name.lower()
        else:
            config_dir = Path.home() / ".config" / app_name.lower()

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.warning(f"Failed to create config directory: {config_dir} ({e})")
    return config_dir


def get_files_in_directory(
    directory: str, extension: str = ".txt", recursive: bool = False
) -> List[str]:
    path = Path(directory)
    if not path.exists():
        logging.error(f"Specified directory does not exist: {directory}")
        return []

    if not path.is_dir():
        logging.error(f"Specified path is not a directory: {directory}")
        return []

    try:
        if recursive:
            files = list(path.rglob(f"*{extension}"))
        else:
            files = list(path.glob(f"*{extension}"))

        result = [str(f) for f in files]
        return result
    except Exception as e:
        logging.error(f"Error occurred while searching for files: {e}")
        return []


def generate_output_filename(
    input_path: str,
    suffix: str,
    extension: str = ".txt",
    prefix: str = "",
) -> str:
    suffix = replace_datetime_placeholder(suffix)
    base_path = Path(input_path)
    new_name = f"{prefix}{base_path.stem}{suffix}{extension}"
    return str(base_path.parent / new_name)


def create_directory_if_not_exists(directory: str) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)


def batch_file_iterator(
    file_paths: List[str], batch_size: int = 1
) -> Iterator[List[str]]:
    for i in range(0, len(file_paths), batch_size):
        yield file_paths[i : i + batch_size]


def split_text_by_sentences(text: str) -> List[str]:
    sentences = []
    current_sentence = []

    for char in text:
        current_sentence.append(char)
        if char in "。．！？":
            sentences.append("".join(current_sentence))
            current_sentence = []

    if current_sentence:
        sentences.append("".join(current_sentence))

    return sentences


def normalize_path(path: str) -> str:
    normalized = str(Path(path).resolve())
    return normalized.replace("\\", "/")


def get_file_info(file_path: str) -> dict:
    path = Path(file_path)
    stats = path.stat()

    return {
        "name": path.name,
        "size": stats.st_size,
        "size_formatted": format_file_size(stats.st_size),
        "modified": stats.st_mtime,
        "extension": path.suffix,
    }


def format_file_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def extract_filename_from_path(file_path: str) -> str:
    if not file_path:
        return ""
    return Path(file_path).stem


def get_downloads_directory() -> str:
    if platform.system() == "Windows":
        try:
            with OpenKey(
                HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            ) as key:
                downloads_dir = QueryValueEx(
                    key, "{374DE290-123F-4565-9164-39C4925E467B}"
                )[0]
                return downloads_dir
        except Exception:
            pass

    home_dir = str(Path.home())
    downloads_dir = os.path.join(home_dir, "Downloads")

    if not os.path.exists(downloads_dir):
        downloads_dir = os.path.join(home_dir, "ダウンロード")
        if not os.path.exists(downloads_dir):
            return home_dir

    return downloads_dir


def replace_datetime_placeholder(text: str) -> str:
    now = datetime.datetime.now()

    if re.search(r"YYYY", text, re.IGNORECASE):
        text = re.sub(r"YYYY", now.strftime("%Y"), text, flags=re.IGNORECASE)
    elif re.search(r"YY", text, re.IGNORECASE):
        text = re.sub(r"YY", now.strftime("%y"), text, flags=re.IGNORECASE)

    if re.search(r"MM", text, re.IGNORECASE):
        text = re.sub(r"MM", now.strftime("%m"), text, flags=re.IGNORECASE)

    if re.search(r"DD", text, re.IGNORECASE):
        text = re.sub(r"DD", now.strftime("%d"), text, flags=re.IGNORECASE)

    if re.search(r"HH", text, re.IGNORECASE):
        text = re.sub(r"HH", now.strftime("%H"), text, flags=re.IGNORECASE)

    if re.search(r"MI", text, re.IGNORECASE):
        text = re.sub(r"MI", now.strftime("%M"), text, flags=re.IGNORECASE)

    if re.search(r"SS", text, re.IGNORECASE):
        text = re.sub(r"SS", now.strftime("%S"), text, flags=re.IGNORECASE)

    return text
