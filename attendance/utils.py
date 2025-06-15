import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import logging

from attendance.monthly_sheet import update_monthly_attendance

logger = logging.getLogger(__name__)
load_dotenv()

def update_google_sheet(name):
    """Update attendance in Google Sheet."""
    try:
        update_monthly_attendance(name)
        logger.debug(f"Called update_monthly_attendance for {name}")

        # Custom logic to replace removed snippet
        # Example: Append to a simple log (replace with your desired logic)
        with open("attendance_log.txt", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            f.write(f"{name},{timestamp}\n")
        logger.debug(f"Logged attendance for {name} at {timestamp}")

    except Exception as e:
        logger.error(f"Error in update_google_sheet: {str(e)}")
        raise