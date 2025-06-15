import os
import json
import gspread
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread_formatting import cellFormat, color, textFormat, format_cell_range
from gspread.exceptions import CellNotFound

# Set up logging
logger = logging.getLogger(__name__)
load_dotenv()


def get_gspread_client():
    """Authenticate and return a gspread client."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if not creds_json:
        raise ValueError("Missing GOOGLE_CREDS_JSON in environment variables")

    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)


def create_or_get_monthly_sheet():
    """Create or open the current month's attendance spreadsheet."""
    now = datetime.now()
    title = f"Vinod - {now.strftime('%B %Y')}"
    client = get_gspread_client()

    try:
        spreadsheet = client.open(title)
        sheet = spreadsheet.sheet1
        logger.info(f"📄 Opened sheet: {title}")
        return sheet

    except gspread.SpreadsheetNotFound:
        logger.info(f"🆕 Creating new sheet: {title}")
        spreadsheet = client.create(title)
        sheet = spreadsheet.sheet1
        sheet.update("A1:D1", [["Date", "Day", "Status", "Time In"]])

        # Fill month with Absent by default
        rows = []
        current = datetime(now.year, now.month, 1)
        while current.month == now.month:
            rows.append([
                current.strftime("%Y-%m-%d"),
                current.strftime("%A"),
                "A",
                "—"
            ])
            current += timedelta(days=1)
        sheet.append_rows(rows)

        # Summary row
        sheet.update_acell("B33", "Total Present")
        sheet.update_acell("C33", '=COUNTIF(C2:C32, "P")')

        # Formatting
        bold = cellFormat(textFormat=textFormat(bold=True))
        fmt_absent = cellFormat(backgroundColor=color(1, 0.85, 0.85))
        fmt_present = cellFormat(backgroundColor=color(0.8, 1, 0.8))
        fmt_weekend = cellFormat(backgroundColor=color(0.95, 0.95, 0.95))
        center_align = cellFormat(horizontalAlignment='CENTER')

        format_cell_range(sheet, 'A1:D1', bold)
        format_cell_range(sheet, 'A2:D33', center_align)

        for i in range(2, len(rows) + 2):
            day_name = sheet.cell(i, 2).value
            if day_name in ["Saturday", "Sunday"]:
                format_cell_range(sheet, f"A{i}:D{i}", fmt_weekend)
            else:
                format_cell_range(sheet, f"C{i}", fmt_absent)

        sheet.format("A:D", {
            "horizontalAlignment": "CENTER",
            "wrapStrategy": "WRAP"
        })

        # Share
        creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
        spreadsheet.share('vinodkinpbl@gmail.com', perm_type='user', role='writer', notify=True)
        spreadsheet.share(creds_dict["client_email"], perm_type='user', role='writer', notify=False)

        logger.info(f"✅ Sheet created: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit")
        return sheet


def update_monthly_attendance(name="Vinod Karri"):
    """Mark current date as Present in the sheet."""
    sheet = create_or_get_monthly_sheet()
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%I:%M %p")

    try:
        cell = sheet.find(today)
    except CellNotFound:
        logger.warning(f"⚠️ Date {today} not found in sheet.")
        return

    sheet.update_cell(cell.row, 3, "P")
    sheet.update_cell(cell.row, 4, time_now)

    fmt_present = cellFormat(backgroundColor=color(0.8, 1, 0.8))
    format_cell_range(sheet, f"C{cell.row}", fmt_present)

    logger.info(f"✅ Attendance marked for {name} at {time_now} on {today}")
