# app.py

import os
import sys
import time
import threading
import webbrowser

import xlwings as xw
from flask import (
    Flask, render_template, request,
    send_file, session, jsonify
)
from icecream import ic

from utils.general import clean_local_path, load_yml_to_args, load_yml, resource_path
from utils.excel_utils import load_excel_wb, onedrive_url_to_iframe, finalize, convert_cell_string_to_coor
from utils.logger import Logger
from utils.configs import Config
from utils.registry import registry
from utils.session import switch_current
from utils.chatbot import get_correction_results
from projects.agent.agent_checker import GramCheckerAgent
from utils.history_handler import HistoryHandler


# ===== Basic Config =====
class SystemBase:
    def __init__(self, config_run_path):
        self.args = load_yml_to_args(config_run_path)
        self.build()

    def build(self):
        self.build_logger()
        self.build_config()
        self.build_registry()

    def build_config(self):
        self.config = Config(load_yml(self.args.config))

    def build_logger(self):
        self.writer = Logger(name="general")

    def build_registry(self):
        registry.set_module("writer", name="common", instance=self.writer)
        registry.set_module("args", name=None, instance=self.args)
        self.config.build_registry()

config_run_path = r"config/config_run.yaml"
system = SystemBase(config_run_path)
writer = system.writer

# ===== Helpers =====



# ===== Flask App Setup =====
app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)
app.secret_key = "supersecret"

agent_checker = GramCheckerAgent()
history_handler = HistoryHandler()


# ===== Routes =====

@app.route("/", methods=["GET"])
def index():
    """Render homepage showing uploaded files."""
    all_current_files = history_handler.get_all_current_files()
    return render_template("index.html", all_files=all_current_files)


@app.route("/upload", methods=["POST"])
def upload():
    """Handle Excel file upload and store session data."""
    local_path = clean_local_path(request.form.get("local_path", "").strip())
    excel_url = request.form.get("excel_url", "").strip()

    ic(local_path)
    ic(excel_url)

    error_message = None
    if not local_path:
        error_message = "Please enter a local path file"
    elif not excel_url:
        error_message = "Please enter a OneDrive Excel URL"
    elif not os.path.isfile(local_path):
        error_message = "Please enter a valid local path"
    else:
        wb = load_excel_wb(local_path)
        session.update({
            "current_excel_file_path": local_path,
            "current_excel_url": excel_url,
            "sheet_names": wb.sheetnames,
            "current_sheet_name": wb.sheetnames[0],
            "current_iframe": onedrive_url_to_iframe(
                url=excel_url,
                sheetname=wb.sheetnames[0]
            )
        })
        history_handler.add_file_information(
            local_path=local_path,
            online_url=excel_url,
            iframe=session["current_iframe"],
            sheetnames=wb.sheetnames
        )

    all_current_files = history_handler.get_all_current_files()
    ic(all_current_files)
    return render_template("index.html", error_message=error_message, all_files=all_current_files)


@app.route("/select_file", methods=["PATCH"])
def select_file():
    """Switch session to selected file."""
    request_body = request.get_json()
    selected_local_path = request_body.get("selected_local_path")
    file_info = history_handler.get_file_information(selected_local_path)
    session.update({
        "current_excel_file_path": file_info["local_path"],
        "current_excel_url": file_info["online_url"],
        "sheet_names": file_info["sheetnames"],
        "current_sheet_name": file_info["sheetnames"][0],
        "current_iframe": file_info["iframe"]
    })
    return "", 204


@app.route("/show_excel", methods=["GET"])
def show_excel():
    """Render the sheet viewer page."""
    selected_file = request.args.get("selected_file")
    ic(selected_file)
    if not selected_file:
        return render_template("index.html", error_message="Please select a file first")

    switch_current(history_handler, selected_file)
    return render_template("show_excel.html", sheets=session["sheet_names"], iframe=session["current_iframe"])


@app.route("/show_sheet", methods=["GET"])
def show_sheet():
    """Show a specific sheet in the viewer."""
    current_sheet_name = request.args.get("sheet")
    if "current_excel_file_path" not in session:
        return "Please upload a file first", 400

    session["current_sheet_name"] = current_sheet_name
    session["current_iframe"] = onedrive_url_to_iframe(
        url=session["current_excel_url"],
        sheetname=current_sheet_name
    )

    correction_results = history_handler.get_correction_history_info(
        local_path=session["current_excel_file_path"],
        sheet_name=current_sheet_name
    )
    ic(correction_results)

    return render_template(
        "show_excel.html",
        sheets=session["sheet_names"],
        iframe=session["current_iframe"],
        current_sheet_name=current_sheet_name,
        correction_results=correction_results
    )


@app.route("/set_correction_reject_status", methods=["POST"])
def set_correction_reject_status():
    request_body = request.get_json()
    cell = request_body.get("cell")
    status = request_body.get("status")
    coordinates = convert_cell_string_to_coor(cell)

    file_id = history_handler.get_file_id(session["current_excel_file_path"])
    history_handler.set_correction_reject_status(
        file_id=file_id,
        sheet_name=session["current_sheet_name"],
        coordinates=coordinates,
        status=status
    )
    correction_results = history_handler.get_correction_history_info(
        local_path=session["current_excel_file_path"],
        sheet_name=session["current_sheet_name"]
    )

    return jsonify({
        "correction_results": correction_results
    }) 


@app.route("/allow_correction", methods=["PATCH"])
def allow_correction():
    request_body = request.get_json()
    cell = request_body.get("cell")


@app.route("/show_sheet_cell", methods=["POST"])
def show_sheet_cell():
    """Show iframe focused on a specific cell."""
    data = request.get_json()
    cell = data.get("cell")
    if "current_excel_file_path" not in session:
        return "Please upload a file first", 400

    session["current_iframe"] = onedrive_url_to_iframe(
        url=session["current_excel_url"],
        sheetname=session["current_sheet_name"],
        current_cell=cell
    )
    return jsonify({
        "iframe": session.get("current_iframe", ""),
        "current_sheet_name": session.get("current_sheet_name", "")
    })


@app.route("/change_sheet_cell", methods=["POST"])
def change_sheet_cell():
    """Update a cell's value and save."""
    data = request.get_json()
    cell = data.get("cell")
    old_value = data.get("old_value")
    new_value = data.get("new_value")

    if old_value != new_value:
        wb = xw.Book(session["current_excel_file_path"])
        current_sheet = wb.sheets[session["current_sheet_name"]]
        agent_checker.change_sheet_cell(
            sheet=current_sheet,
            cell_address=cell,
            old_value=old_value,
            new_value=new_value
        )
        finalize(wb)

    return jsonify({
        "iframe": session.get("current_iframe", ""),
        "current_sheet_name": session.get("current_sheet_name", "")
    })


@app.route("/download_excel")
def download_excel():
    """Download the currently selected Excel file."""
    return send_file(session["current_excel_file_path"], as_attachment=True)


@app.route("/check_grammar", methods=["POST"])
def check_grammar():
    """Check grammar for the current sheet."""
    writer.LOG_INFO("Start Checking Grammar")

    data = request.get_json()
    request_sheet_name = data["sheet_name"]

    wb = load_excel_wb(path=session["current_excel_file_path"])
    rows = [row for row in wb[request_sheet_name].iter_rows(values_only=True)]
    checked_rows = agent_checker.run_sheet(rows)

    results = get_correction_results(old_rows=rows, new_rows=checked_rows)
    file_id = history_handler.get_file_id(session["current_excel_file_path"])

    # Delete First then add
    history_handler.delete_correction_history(file_id)
    for result in results:
        history_handler.add_correction_history(
            file_id=file_id,
            sheet_name=session["current_sheet_name"],
            coordinates=result["coordinates"],
            old_value=result["old_value"],
            new_value=result["new_value"]
        )

    writer.LOG_INFO("Finish Checking Grammar")
    return jsonify({
        "iframe": session.get("current_iframe", ""),
        "results": results
    })



def run_app():
    # app.run(debug=False, use_reloader=False)
    app.run(debug=True, use_reloader=True)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()  # Mở browser sau 1.5s
    run_app()


# "C:\Users\RGA6HC\OneDrive - Bosch Group\GramCheck\oke.xlsx"
# https://bosch-my.sharepoint.com/:x:/r/personal/rga6hc_bosch_com/Documents/GramCheck/Update_Text_TR_FSM_FaultSystemStateManagement_BL0.4C.xlsx?d=w40424d5c4d654f2b841a31e0b6700f2f&csf=1&web=1&e=4xc0pb