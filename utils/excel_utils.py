from openpyxl import load_workbook

def load_excel_wb(path):
    return load_workbook(path, data_only=True)