import subprocess
import tempfile
import sys
import pathlib


def html_to_pdf(html_file_path):
    command = [
        "google-chrome-stable",
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        "--print-to-pdf=" + "hoge.pdf",
        html_file_path,
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()


if __name__ == "__main__":
    html_file_path = sys.argv[1]
    if not pathlib.Path(html_file_path).exists():
        raise FileNotFoundError("File not found: " + html_file_path)
    html_to_pdf(html_file_path)
