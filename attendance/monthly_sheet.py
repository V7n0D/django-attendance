import os
import json
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *


def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = os.getenv("GOOGLE_CREDS_JSON")

    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Credentials.json'))
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

    return gspread.authorize(creds)


def create_or_get_monthly_sheet():
    now = datetime.now()
    title = f"Vinod - {now.strftime('%B %Y')}"
    client = get_gspread_client()

    try:
        spreadsheet = client.open(title)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(title)
        sheet = spreadsheet.sheet1
        sheet.update("A1:D1", [["Date", "Day", "Status", "Time In"]])

        # Fill month with 'A' for Absent
        day = datetime(now.year, now.month, 1)
        rows = []

        while day.month == now.month:
            rows.append([
                day.strftime("%Y-%m-%d"),
                day.strftime("%A"),
                "A",
                "—"
            ])
            day += timedelta(days=1)

        sheet.append_rows(rows)

        # Add total row with working COUNTIF formula
        # Add total row with working COUNTIF formula
        sheet.update_acell("B33", "Total Present")
        sheet.update_acell("C33", '=COUNTIF(C2:C32, "P")')


        # Format styling
        bold = cellFormat(textFormat=textFormat(bold=True))
        fmt_absent = cellFormat(backgroundColor=color(1, 0.85, 0.85))
        fmt_present = cellFormat(backgroundColor=color(0.8, 1, 0.8))
        fmt_weekend = cellFormat(backgroundColor=color(0.95, 0.95, 0.95))
        center_align = cellFormat(horizontalAlignment='CENTER')

        format_cell_range(sheet, 'A1:D1', bold)
        format_cell_range(sheet, 'A2:D33', center_align)

        for i in range(2, len(rows)+2):
            weekday = sheet.cell(i, 2).value
            if weekday in ["Saturday", "Sunday"]:
                format_cell_range(sheet, f"A{i}:D{i}", fmt_weekend)
            else:
                format_cell_range(sheet, f"C{i}", fmt_absent)

        # Final center formatting for table visibility
        sheet.format('A:D', {
            "horizontalAlignment": "CENTER",
            "wrapStrategy": "WRAP"
        })

        spreadsheet.share('vinodkinpbl@gmail.com', perm_type='user', role='writer', notify=True)

    return client.open(title).sheet1


def update_monthly_attendance(name="Vinod Karri"):
    sheet = create_or_get_monthly_sheet()
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%I:%M %p")

    try:
        cell = sheet.find(today)
        sheet.update_cell(cell.row, 3, "P")  # Mark as Present
        sheet.update_cell(cell.row, 4, time_now)

        # Apply green background to 'P' cell
        fmt_present = cellFormat(backgroundColor=color(0.8, 1, 0.8))
        format_cell_range(sheet, f"C{cell.row}", fmt_present)

    except gspread.exceptions.CellNotFound:
        print("⚠️ Today's row not found in the sheet.")