from django.shortcuts import render
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor
from core.utils.audiobook_pipeline import process_file_to_mp3

#create single-thread executor for TTS tasks
EXECUTOR = ThreadPoolExecutor(max_workers=1)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # core/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # backend/
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
OUTPUTS_DIR = os.path.join(MEDIA_ROOT, 'outputs')
os.makedirs(OUTPUTS_DIR, exist_ok=True)

PIPER_EXE = os.path.join(PROJECT_ROOT, 'piper', 'piper.exe')
PIPER_MODEL_DIR = os.path.join(PROJECT_ROOT, 'piper', 'models')

class DefaultView(APIView):
    def get(self, request):       
        return Response({"message": "Welcome to the Audiobook API!"}, status=status.HTTP_200_OK)

class UploadView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser] #allows DRF to read file uploads

    def post(self,request):
        file = request.FILES.get('file')
        engine = request.data.get('engine', 'piper') # leave room to extend to coqui tts
        voice = request.data.get('voice', '')
        title = request.data.get('title', file.name if file else 'Untitled')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

class StartProcessView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        voice_model = request.data.get('voice', 'en_US-ryan-medium.onnx')

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        # Directories
        output_dir = os.path.join(os.getcwd(), 'media', 'outputs')
        os.makedirs(output_dir, exist_ok=True)

        # Piper paths
        piper_exe = os.path.join(os.getcwd(), 'piper', 'piper.exe')
        piper_model_dir = os.path.join(os.getcwd(), 'piper', 'models')

        # Save uploaded file temporarily
        input_path = os.path.join(output_dir, file.name)
        with open(input_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            final_mp3 = process_file_to_mp3(
                input_path, output_dir, voice_model, piper_exe, piper_model_dir
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        # Return download URL
        mp3_filename = os.path.basename(final_mp3)
        download_url = f"/media/outputs/{mp3_filename}"

        return Response({
            'detail': 'Processing complete',
            'download_url': download_url
        }, status=200)

class VoicesView(APIView):
    def get(self, request):
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'piper', 'models')
        models_dir = os.path.abspath(models_dir)  
        voices = []
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith('.onnx'):
                    voices.append(file)
        return Response({'piper': voices})

class ProgressView(APIView):
    def get(self, request, filename):
        mp3_path = os.path.join(settings.MEDIA_ROOT, 'outputs', f"{filename}.mp3")
        if os.path.exists(mp3_path):
            return Response({'status': 'ready', 'url': f"{settings.MEDIA_URL}outputs/{filename}.mp3"})
        else:
            return Response({'status': 'processing'})