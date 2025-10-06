from flask import session

def switch_current(history_handler, current_local_path):
    file_info = history_handler.get_file_information(current_local_path)

    session["current_excel_file_path"] = file_info["local_path"] 
    session["current_excel_url"] = file_info["online_url"] 
    session["sheet_names"] = file_info["sheetnames"] 
    session["current_sheet_name"] = file_info["sheetnames"][0]
    session["current_iframe"] = file_info["iframe"] 