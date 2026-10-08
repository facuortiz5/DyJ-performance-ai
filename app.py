import streamlit as st

from file_storage import (
    ALLOWED_EXTENSIONS, delete_file, rename_file, replace_file, save_file, stored_files,
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
