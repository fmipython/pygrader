import os
import zipfile
from multiprocessing import Queue, Process

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from web.utils import run_grader, convert_results, generate_run_id


def run_app() -> None:
    """
    Main logic for the streamlit app.
    """
    st.title("Pygrader Web Interface")
    st.write("Welcome to the Pygrader web application.")

    st.divider()
    # Additional UI components and logic would go here

    project = st.file_uploader("Upload a project", type=["zip"])

    if project is not None:
        with st.spinner("Grading project..."):
            handle_upload(project)
            run_id = generate_run_id()
            queue = Queue()  # type: ignore

            grader = Process(target=run_grader, args=(queue, run_id))
            grader.start()
            grader.join()
            results = queue.get()
            queue.close()

            st.success("Project graded successfully!")
            st.dataframe(convert_results(results))
    else:
        st.info("Please upload a project to get started.")


def handle_upload(file_obj: UploadedFile) -> None:
    """
    Handle the uploaded zip file by extracting its contents to a staging directory.
    :param file_obj: The uploaded zip file object.
    """
    staging_dir = "project"

    os.makedirs(staging_dir, exist_ok=True)

    zip_file_path = os.path.join(staging_dir, "uploaded_project.zip")
    with open(zip_file_path, "wb") as f:
        f.write(file_obj.getbuffer())

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(staging_dir)

    os.remove(zip_file_path)
