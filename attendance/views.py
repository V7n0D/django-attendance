import os
from django.shortcuts import render
from django.core.mail import send_mail
from openpyxl import Workbook, load_workbook
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import update_google_sheet
import io
import pandas as pd
from django.http import HttpResponse
from datetime import datetime
from attendance.monthly_sheet import get_gspread_client
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('mark_attendance')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def mark_attendance(request):
    if request.method == "POST":
        name = "Vinod Karri"
        #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        # ------ 1. Update Google Sheet ------#
        update_google_sheet(name)

        #-------- 2. Send Email --------#
        #send_mail(
            #subject ="Attendance Marked",
            #message = f"Hi, Vinod, your attendance was marked at {timestamp}.",
            #from_email=os.getenv('EMAIL_USER'),
            #recipient_list = [os.getenv('EMAIL_USER')],
            #fail_silently=False,
        #)     


        return render(request, 'attendance/mark_attendance.html',{'message':'Attendance marked successfully!'})
    return render(request,'attendance/mark_attendance.html')  

def download_excel(request):
    now = datetime.now()
    title = f"Vinod - {now.strftime('%B %Y')}"
    client = get_gspread_client()
    sheet = client.open(title).sheet1
    data = sheet.get_all_records()

    # Convert to DataFrame
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')

    excel_buffer.seek(0)
    response = HttpResponse(
        excel_buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=\"{title}.xlsx\"'
    return response
