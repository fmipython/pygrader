import os
import zipfile
from multiprocessing import Queue

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from web.utils import run_grader, convert_result
from grader.checks.abstract_check import CheckResult


def run_app() -> None:
    st.title("PyGrader Web Interface")
    st.write("Welcome to the PyGrader web application.")

    st.divider()
    # Additional UI components and logic would go here

    project = st.file_uploader("Upload a project", type=["zip"])

    if project is not None:
        with st.spinner("Grading project..."):
            handle_upload(project)
            queue = Queue()  # type: ignore
            run_grader(queue)

            results = queue.get()
            queue.close()
            st.success("Project graded successfully!")
            st.dataframe(convert_result(results))
    else:
        st.info("Please upload a project to get started.")


def handle_upload(file_obj: UploadedFile) -> None:
    staging_dir = "staging"

    os.makedirs(staging_dir, exist_ok=True)

    zip_file_path = os.path.join(staging_dir, "uploaded_project.zip")
    extract_path = os.path.join(staging_dir, "project")
    with open(zip_file_path, "wb") as f:
        f.write(file_obj.getbuffer())

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_file_path)
