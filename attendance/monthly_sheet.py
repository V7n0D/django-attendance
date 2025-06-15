import os
import json
import gspread
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread_formatting import (
    cellFormat, color, textFormat,
    format_cell_range
)

# ✅ Set up logging
logger = logging.getLogger(__name__)

# ✅ Load .env variables
load_dotenv()

def get_gspread_client():
    """Return a gspread client using service account credentials."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_json = os.getenv("GOOGLE_CREDS_JSON")
        if not creds_json:
            raise ValueError("GOOGLE_CREDS_JSON not found in environment variables")

        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        logger.debug("✅ gspread client initialized")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize gspread client: {str(e)}")
        raise

def create_or_get_monthly_sheet():
    """Create or return the monthly attendance sheet for the current month."""
    now = datetime.now()
    title = f"Vinod - {now.strftime('%B %Y')}"
    client = get_gspread_client()

    try:
        spreadsheet = client.open(title)
        sheet = spreadsheet.sheet1
        logger.debug(f"📄 Opened existing sheet: {title}")
    except gspread.SpreadsheetNotFound:
        logger.info(f"📄 Creating new spreadsheet: {title}")
        spreadsheet = client.create(title)
        sheet = spreadsheet.sheet1
        sheet.update("A1:D1", [["Date", "Day", "Status", "Time In"]])

        # ✅ Fill month with Absent days
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

        # ✅ Add summary
        sheet.update_acell("B33", "Total Present")
        sheet.update_acell("C33", '=COUNTIF(C2:C32, "P")')

        # ✅ Apply formatting
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

        # ✅ Share the spreadsheet
        creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
        spreadsheet.share('vinodkinpbl@gmail.com', perm_type='user', role='writer', notify=True)
        spreadsheet.share(creds_dict['client_email'], perm_type='user', role='writer', notify=False)
        logger.info(f"✅ Spreadsheet created and shared: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit")

    return sheet

def update_monthly_attendance(name="Vinod Karri"):
    """Mark attendance for today as Present."""
    try:
        sheet = create_or_get_monthly_sheet()
        today = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%I:%M %p")

        try:
            cell = sheet.find(today)
        except gspread.exceptions.CellNotFound:
            logger.warning(f"⚠️ Date {today} not found in sheet")
            return

        sheet.update_cell(cell.row, 3, "P")
        sheet.update_cell(cell.row, 4, time_now)

        fmt_present = cellFormat(backgroundColor=color(0.8, 1, 0.8))
        format_cell_range(sheet, f"C{cell.row}", fmt_present)

        logger.info(f"✅ Attendance marked for {name} at {time_now} on {today}")

    except Exception as e:
        logger.error(f"❌ Error in update_monthly_attendance: {str(e)}")
        raise
