import os
import shutil
import tempfile
from io import BufferedIOBase
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
ALLOWED_EXTENSIONS = {
    ".xlsx",
    ".xls",
    ".csv",
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}
INVALID_FILENAME_CHARS = '<>:"/\\|?*'
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def validate_filename(name: str) -> str:
    if not name or name in {".", ".."} or name != Path(name).name:
        raise ValueError("Nombre de archivo inválido.")
    if any(character in INVALID_FILENAME_CHARS or ord(character) < 32 for character in name):
        raise ValueError("El nombre contiene caracteres no permitidos.")
    if name.endswith((" ", ".")) or name.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError("Ese nombre no está permitido en Windows.")
    if Path(name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Tipo de archivo no admitido.")
    return name


def file_path(name: str, storage_dir: Path = STORAGE_DIR) -> Path:
    return storage_dir / validate_filename(name)


def save_file(file_object: BufferedIOBase, name: str, storage_dir: Path = STORAGE_DIR, *, replace: bool = False) -> Path:
    storage_dir.mkdir(parents=True, exist_ok=True)
    destination = file_path(name, storage_dir)
    if destination.exists() and not replace:
        raise FileExistsError(f'Ya existe un archivo llamado "{name}".')

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=storage_dir, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            file_object.seek(0)
            shutil.copyfileobj(file_object, temporary, length=1024 * 1024)
        os.replace(temporary_path, destination)
    except Exception:
        if temporary_path:
            temporary_path.unlink(missing_ok=True)
        raise
    return destination


def rename_file(old_name: str, new_name: str, storage_dir: Path = STORAGE_DIR) -> Path:
    source = file_path(old_name, storage_dir)
    destination = file_path(new_name, storage_dir)
    if source.suffix.lower() != destination.suffix.lower():
        raise ValueError("El nuevo nombre debe conservar la extensión.")
    if destination.exists() and source != destination:
        raise FileExistsError(f'Ya existe un archivo llamado "{new_name}".')
    source.rename(destination)
    return destination


def replace_file(name: str, replacement: BufferedIOBase, replacement_name: str, storage_dir: Path = STORAGE_DIR) -> Path:
    source = file_path(name, storage_dir)
    destination = file_path(replacement_name, storage_dir)
    if not source.exists():
        raise FileNotFoundError(name)
    same_path = os.path.normcase(source.absolute()) == os.path.normcase(destination.absolute())
    if destination.exists() and not same_path:
        raise FileExistsError(f'Ya existe un archivo llamado "{replacement_name}".')

    saved = save_file(replacement, replacement_name, storage_dir, replace=same_path)
    if not same_path:
        try:
            source.unlink()
        except Exception:
            saved.unlink(missing_ok=True)
            raise
    return saved


def delete_file(name: str, storage_dir: Path = STORAGE_DIR) -> None:
    file_path(name, storage_dir).unlink()


def stored_files(storage_dir: Path = STORAGE_DIR) -> list[Path]:
    storage_dir.mkdir(parents=True, exist_ok=True)
    return sorted(
        (path for path in storage_dir.iterdir() if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS),
        key=lambda path: path.name.casefold(),
    )
