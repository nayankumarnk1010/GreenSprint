from pathlib import Path

from huggingface_hub import hf_hub_download


MODEL_REPO_ID = "Daksh159/plant-disease-mobilenetv2"

MODEL_DIR = Path("models/plant_disease")
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def download_file(
    filename: str,
) -> None:
    print(f"Downloading {filename}...")

    downloaded_path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=filename,
        local_dir=str(MODEL_DIR),
        local_dir_use_symlinks=False,
    )

    print(f"Saved: {downloaded_path}")


def main() -> None:
    download_file("mobilenetv2_plant.pth")
    download_file("class_names.json")

    print("\nPlant disease model downloaded successfully.")
    print(f"Model folder: {MODEL_DIR.resolve()}")


if __name__ == "__main__":
    main()