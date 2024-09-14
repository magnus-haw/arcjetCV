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


def ensure_model_files():
    """Ensures that the necessary model files are downloaded."""
    base_url = (
        "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/segmentation/contour/"
    )
    files_to_download = [
        "Unet-xception_25_original.pt",
        "Unet-xception-last-checkpoint.pt",
    ]

    for file in files_to_download:
        download_large_file(
            base_url + file, os.path.join(os.path.dirname(__file__), file)
        )


# Automatically download the files when the package is imported
ensure_model_files()
