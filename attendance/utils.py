import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from gspread_formatting import *
from gspread_formatting.dataframe import format_with_dataframe
from attendance.monthly_sheet import update_monthly_attendance


load_dotenv()

def update_google_sheet(name):
    update_monthly_attendance(name)
    # Define API scopes
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Load credentials
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Credentials.json'))
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

    client = gspread.authorize(creds)
    sheet_title = "Attendance Sheet"

    try:
        sheet = client.open(sheet_title).sheet1
    except gspread.SpreadsheetNotFound:
        # Create new sheet with headers
        spreadsheet = client.create(sheet_title)
        sheet = spreadsheet.sheet1
        sheet.append_row(["Name", "Timestamp"])

        # Share with your Gmail so it shows in Drive
        spreadsheet.share(
            'vinodkinpbl@gmail.com',
            perm_type='user',
            role='writer',
            notify=True
        )

        #print(f"✅ Sheet created and shared: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit")
    
    # Append new attendance record
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([name, timestamp])
