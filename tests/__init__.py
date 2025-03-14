import os
import urllib.request


def download_large_file(url, local_filename):
    """Downloads the file from the specified URL if it doesn't already exist locally."""
    if not os.path.exists(local_filename):
        print(f"Downloading {url} to {local_filename}...")
        urllib.request.urlretrieve(url, local_filename)
        print(f"Downloaded {local_filename}.")
    else:
        print(f"{local_filename} already exists, skipping download.")


def download_test_video():
    """Ensures that the test video 'arcjet_test.mp4' is downloaded."""
    base_url = "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/tests/"
    file_to_download = "arcjet_test.mp4"

    download_large_file(
        base_url + file_to_download,
        os.path.join(os.path.dirname(__file__), file_to_download),
    )


# Automatically download the video when the function is called
download_test_video()
