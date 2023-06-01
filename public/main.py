import requests
import os
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_DIRECTORY = "downloads"
CHUNK_SIZE = 1024 * 1024  # Kích thước chunk (1MB)
CURRENT_VERSION_FILE = "current_version.txt"


class VersionChecker:
    def __init__(self, version_url: str, download_url: str):
        self.version_url = version_url
        self.download_url = download_url

    def download_file(self, url: str, file_path: str) -> None:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)

    def extract_zip(self, zip_path: str, extract_path: str) -> None:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    def check_version(self) -> None:
        try:
            response = requests.get(self.version_url)
            response.raise_for_status()
            content = response.text
            latest_version = re.search(r'\d+\.\d+\.\d+', content).group(0)

            current_version = self.get_current_version()

            if latest_version > current_version:
                print("Phiên bản mới nhất là:", latest_version)
                print("Đang tải về...")

                download_path = os.path.join(
                    DOWNLOAD_DIRECTORY, f"{latest_version}.zip")
                os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

                with ThreadPoolExecutor() as executor:
                    executor.submit(self.download_file, self.download_url.format(
                        latest_version), download_path)

                print("Đã tải về thành công.")

                extract_directory = os.path.join(
                    DOWNLOAD_DIRECTORY, latest_version)
                os.makedirs(extract_directory, exist_ok=True)

                print("Đang giải nén...")
                self.extract_zip(download_path, extract_directory)
                print("Đã giải nén thành công.")

                self.save_current_version(latest_version)
            else:
                print("Phiên bản hiện tại là phiên bản mới nhất.")

        except Exception as e:
            print("Đã xảy ra lỗi:", str(e))

    def get_current_version(self) -> str:
        if os.path.exists(CURRENT_VERSION_FILE):
            with open(CURRENT_VERSION_FILE, "r") as file:
                current_version = file.read().strip()
            return current_version
        else:
            return ""

    def save_current_version(self, version: str) -> None:
        with open(CURRENT_VERSION_FILE, "w") as file:
            file.write(version)


# Gọi hàm kiểm tra phiên bản và tải về
# Thay đổi URL này bằng URL thật của tệp tin phiên bản
version_url = "http://example.com/version.txt"
# Thay đổi URL này bằng URL thật của tệp tin tải về
download_url = "http://example.com/download/{}.zip"

checker = VersionChecker(version_url, download_url)
checker.check_version()
