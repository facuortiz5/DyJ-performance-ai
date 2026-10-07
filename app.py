import os
import shutil
import tempfile
from io import BufferedIOBase
from pathlib import Path

import streamlit as st


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


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def show_action_result(action, success_message: str) -> None:
    try:
        action()
    except (OSError, ValueError) as error:
        st.session_state["file_feedback"] = ("error", str(error))
    else:
        st.session_state["file_feedback"] = ("success", success_message)
    st.rerun()


@st.dialog("Administrar archivo")
def file_action(name: str, action: str) -> None:
    if action != "Eliminar":
        st.text(name)
    new_name = None
    replacement = None
    if action == "Renombrar":
        new_name = st.text_input("Nuevo nombre", value=name, live=True, on_change="ignore")
    elif action == "Reemplazar":
        replacement = st.file_uploader(
            "Nueva versión",
            type=[extension.removeprefix(".") for extension in sorted(ALLOWED_EXTENSIONS)],
        )
    else:
        st.write(f'¿Seguro que querés eliminar "{name}"?')

    cancel, confirm = st.columns(2)
    if cancel.button("Cancelar", use_container_width=True):
        st.rerun()
    if confirm.button(
        action, type="primary", use_container_width=True,
        disabled=action == "Reemplazar" and replacement is None,
    ):
        if action == "Renombrar":
            show_action_result(lambda: rename_file(name, new_name), "Archivo renombrado correctamente.")
        elif action == "Reemplazar":
            show_action_result(
                lambda: replace_file(name, replacement, replacement.name),
                "Archivo reemplazado correctamente.",
            )
        else:
            show_action_result(lambda: delete_file(name), "Archivo eliminado correctamente.")


def main() -> None:
    st.set_page_config(page_title="Performance AI", page_icon="📁", layout="centered")
    st.title("Performance AI")
    st.caption("Repositorio local de archivos del área de Performance")

    st.subheader("Cargar archivos")
    upload_generation = st.session_state.get("upload_generation", 0)
    uploads = st.file_uploader(
        "Arrastrá archivos aquí o seleccionalos desde tu computadora",
        type=[extension.removeprefix(".") for extension in sorted(ALLOWED_EXTENSIONS)],
        accept_multiple_files=True,
        help="Podés cargar varios archivos a la vez.",
        key=f"uploads-{upload_generation}",
    )
    if st.button("Guardar archivos", type="primary", disabled=not uploads, use_container_width=True):
        saved = 0
        errors = []
        for upload in uploads:
            try:
                save_file(upload, upload.name)
            except (OSError, ValueError) as error:
                errors.append(f"{upload.name}: {error}")
            else:
                saved += 1
        st.session_state["upload_feedback"] = (saved, errors)
        if saved:
            st.session_state["upload_generation"] = upload_generation + 1
        st.rerun()
    if feedback := st.session_state.pop("upload_feedback", None):
        saved, errors = feedback
        for error in errors:
            st.error(error)
        if saved:
            st.success(
                "Archivo guardado correctamente."
                if saved == 1
                else f"{saved} archivos guardados correctamente."
            )

    st.divider()
    files = stored_files()
    st.subheader(f"Archivos almacenados ({len(files)})")
    feedback_area = st.empty()
    if feedback := st.session_state.pop("file_feedback", None):
        if feedback[0] == "success":
            feedback_area.success(feedback[1])
        else:
            feedback_area.error(feedback[1])
    if not files:
        st.info("Todavía no hay archivos almacenados.")
        return

    for path in files:
        with st.container(border=True):
            name_column, size_column, edit_column, replace_column, delete_column = st.columns(
                [6, 2, 1, 1, 1], vertical_alignment="center"
            )
            name_column.text(path.name)
            size_column.caption(format_size(path.stat().st_size))
            for column, action, icon in (
                (edit_column, "Renombrar", "edit"),
                (replace_column, "Reemplazar", "swap_vert"),
                (delete_column, "Eliminar", "delete"),
            ):
                if column.button(
                    "", icon=f":material/{icon}:", help=action,
                    key=f"{action}-{path.name}",
                ):
                    file_action(path.name, action)


if __name__ == "__main__":
    main()
