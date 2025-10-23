from openpyxl import load_workbook
import xlwings as xw
import re
from urllib.parse import urlparse, parse_qs

def load_excel_wb(path):
    return load_workbook(path, data_only=True)


def onedrive_url_to_iframe(
        url: str, 
        sheetname: str,
        width="100%", 
        height="100%",
        current_cell="A1"
    ) -> str:
    """
    Convert a OneDrive/SharePoint Excel file URL into an embeddable iframe HTML.
    Works for links containing the ?d=... parameter.
    """

    # Lấy query param d=...
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    doc_id = query.get("d", [None])[0]

    if not doc_id:
        raise ValueError("Invalid OneDrive URL: no document ID (?d=...) found")

    # Bỏ ký tự 'w' đầu (nếu có)
    if doc_id.startswith("w"):
        doc_id = doc_id[1:]

    # Chèn dấu gạch để thành GUID chuẩn: 8-4-4-4-12
    guid = f"{{{doc_id[0:8]}-{doc_id[8:12]}-{doc_id[12:16]}-{doc_id[16:20]}-{doc_id[20:]}}}"

    # Tạo base domain
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.split('/Documents')[0]}"

    # Ghép thành iframe src
    iframe_src = (
        f"{base_url}/_layouts/15/Doc.aspx?"
        f"sourcedoc={guid}&action=embedview"
        f"&wdAllowInteractivity=False"
        f"&AllowTyping=True"
        f"&ActiveCell='{sheetname}'!{current_cell}"
        f"&wdHideGridlines=True"
        f"&wdHideHeaders=True"
        f"&wdDownloadButton=True"
        f"&wdDownloadButton=True"
        f"&wdInConfigurator=True"
        f"&wdHideGridlines=True&wdHideHeaders=True&wdDownloadButton=True"
    )

    # Tạo iframe HTML
    iframe_html = (
        f'<iframe width="{width}" height="{height}" frameborder="0" '
        f'scrolling="no" '
        f'allowfullscreen '
        f'loading="lazy" '
        f'referrerpolicy="no-referrer" '
        f'src="{iframe_src}"></iframe>'
    )
    return iframe_html


def convert_coor_to_cell_string(x, y):
    # 1-based index coordinates 
    x = x + 1
    y = y + 1

    # Convert
    y_str = ""
    while y > 0:
        y, remainder = divmod(y - 1, 26)
        y_str = chr(65 + remainder) + y_str
    cell_str = f"{y_str}{x}"
    return cell_str


def convert_cell_string_to_coor(cell_str):
    """
    Convert cell string (like 'A1', 'B2', 'AA10') to coordinates (x, y)
    Returns 0-based index coordinates
    
    Args:
        cell_str (str): Cell string like 'A1', 'B2', etc.
    
    Returns:
        tuple: (x, y) coordinates where x is row (0-based), y is column (0-based)
    """
    # Remove any whitespace and convert to uppercase
    cell_str = cell_str.strip().upper()
    
    # Extract column letters and row number using regex
    match = re.match(r'^([A-Z]+)(\d+)$', cell_str)
    if not match:
        raise ValueError(f"Invalid cell string format: {cell_str}")
    
    col_letters = match.group(1)
    x = int(match.group(2))
    
    # Convert column letters to number (A=1, B=2, ..., Z=26, AA=27, etc.)
    y = 0
    for char in col_letters:
        y = y * 26 + (ord(char) - ord('A') + 1)
    
    x = x - 1
    y = y - 1
    return x, y


def finalize(wb):
    wb.save()
    wb.close()
    # xw.apps.active.quit()