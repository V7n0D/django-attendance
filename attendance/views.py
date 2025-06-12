import os
from django.shortcuts import render
from django.core.mail import send_mail
from openpyxl import Workbook, load_workbook
from datetime import datetime
# Create your views here.

def mark_attendance(request):
    if request.method == "POST":
        # ------ 1. Update Excel Sheet ------#
        file_path = 'attendance_log.xlsx'
        name = "Vinod Karri"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if os.path.exists(file_path):
            wb = load_workbook(file_path)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Name","Timestamp"])

        ws.append([name,timestamp])
        wb.save(file_path) 

        #-------- 2. Send Email --------#
        print("Before sending mail")
        send_mail(
            subject ="Attendance Marked",
            message = f"Hi, Vinod, your attendance was marked at {timestamp}.",
            from_email=os.getenv('EMAIL_USER'),
            recipient_list = [os.getenv('EMAIL_USER')],
            fail_silently=False,
        )     
        print("After sending mail")


        return render(request, 'attendance/mark_attendance.html',{'message':'Attendance marked successfully!'})
    return render(request,'attendance/mark_attendance.html')  
