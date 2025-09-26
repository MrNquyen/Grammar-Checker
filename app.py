# app.py
import openpyxl
import pandas as pd
import os
from flask import Flask, render_template, url_for, request, send_file, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from icecream import ic
from datetime import timedelta
from io import BytesIO

from utils.excel_utils import load_excel_wb

# Configuration
save_dir = "save/upload"

# Flask app
app = Flask(__name__)
app.secret_key = "supersecret"  # required for session to work


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

#-- Upload files
@app.route("/upload", methods=["POST"])
def upload():
    #~ Get upload file
    file = request.files["file"]
    filename = file.filename

    #~ Load and save
    error_message = None
    if not file or not file.filename:
        error_message = "Please upload the file first"
    else:
        save_path = os.path.join(save_dir, file.filename)
        file.save(save_path)
        wb = load_excel_wb(path=save_path)

        #~ Save to session
        session["current_excel_file_path"] = save_path
        session["sheet_names"] = wb.sheetnames
    return render_template("index.html", error_message=error_message)


#-- Show Excel Files on Web
@app.route("/show_excel", methods=["GET", "POST"])
def show_excel():
    if "current_excel_file_path" not in session:
        error_message = "Please upload the file first"
        return render_template("index.html", error_message=error_message)
    return render_template("show_excel.html", sheets=session["sheet_names"])

#-- Show sheet
#---- Serve for SpreadJS
@app.route("/download_excel")
def download_excel():
    return send_file(session["current_excel_file_path"], as_attachment=True)


#---- Serve for SpreadJS
# @app.route("/show_sheet", methods=["GET"])
# def show_sheet():
#     # sheet_name = request.form.get("sheet")
#     sheet_name = request.args.get("sheet")
#     ic(sheet_name)
#     if "current_excel_file_path" not in session:
#         return "Please upload the file first"

#     #~ Show sheet
#     wb = load_excel_wb(path=session["current_excel_file_path"])
#     sheet = wb[sheet_name]

#     return render_template("show_sheet.html", sheet_name=sheet_name)
    


if __name__=="__main__":
    app.run(debug=True)
