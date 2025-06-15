from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
import base64

# Create your views here.

def face_attendance(request):
    if request.method == 'POST':
        data_url = request.POST.get('image')

        if data_url:
            format, imgstr = data_url.split(';base64,')
            image_data = ContentFile(base64.b64decode(imgstr), name='captured.jpg')

            # TODO: Use InsightFace to recognize and mark attendance
            print("Image received from webcam")

            # Placeholder response
            return render(request, 'facify/capture_face.html', {'message': 'Image captured and received.'})

    return render(request, 'facify/capture_face.html')
