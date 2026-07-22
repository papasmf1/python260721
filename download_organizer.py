from pathlib import Path
import shutil

# Source download folder (fixed as requested)
DOWNLOADS_DIR = Path(r"C:\Users\student\Downloads")

# Destination folders under current working directory
DESTINATIONS = {
    "images": {".jpg", ".jpeg", ".png"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip", ".exe"},
}


def get_unique_destination_path(dest_dir: Path, file_name: str) -> Path:
    """Return a non-conflicting destination file path."""
    candidate = dest_dir / file_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = dest_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def organize_downloads() -> None:
    if not DOWNLOADS_DIR.exists():
        print(f"다운로드 폴더가 존재하지 않습니다: {DOWNLOADS_DIR}")
        return

    base_dir = Path.cwd()

    # Create destination folders if they do not exist
    for folder_name in DESTINATIONS:
        (base_dir / folder_name).mkdir(parents=True, exist_ok=True)

    moved_count = 0

    for item in DOWNLOADS_DIR.iterdir():
        if not item.is_file():
            continue

        ext = item.suffix.lower()

        target_folder = None
        for folder_name, extensions in DESTINATIONS.items():
            if ext in extensions:
                target_folder = folder_name
                break

        if target_folder is None:
            continue

        destination_dir = base_dir / target_folder
        destination_path = get_unique_destination_path(destination_dir, item.name)

        shutil.move(str(item), str(destination_path))
        moved_count += 1
        print(f"이동: {item.name} -> {destination_path}")

    print(f"완료: 총 {moved_count}개 파일 이동")


if __name__ == "__main__":
    organize_downloads()
