"""
scripts/download_datasets.py
Downloads datasets required for the project.
"""
import argparse
import subprocess
import sys

def install(package):
    """Installs a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

def download_celeb_df():
    """Downloads the Celeb-DF v2 dataset using gdown."""
    print("Installing gdown...")
    install("gdown")
    
    print("Downloading Celeb-DF v2...")
    # This is the official file ID for Celeb-DF-v2.zip
    file_id = "1OdsdG5djL9p6sQG33W3OQnE9P9xY2gGN"
    output_path = "data/raw/celeb-df/Celeb-DF-v2.zip"
    
    try:
        subprocess.run(
            ["gdown", file_id, "-O", output_path],
            check=True
        )
        print(f"Celeb-DF v2 downloaded successfully to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading Celeb-DF v2: {e}")
        print("Please ensure you have sufficient disk space and a stable internet connection.")

def main():
    parser = argparse.ArgumentParser(description="Download datasets for the Deepfake Detector project.")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        choices=["celeb-df"],
        help="Dataset to download."
    )
    args = parser.parse_args()

    if args.dataset == "celeb-df":
        download_celeb_df()

if __name__ == '__main__':
    main()
