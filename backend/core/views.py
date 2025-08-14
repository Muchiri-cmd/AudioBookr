from django.shortcuts import render
from django.http import HttpResponse,JsonResponse

# Create your views here.
def main_view(request):
    return render(request,'core/upload.html')

def convert_view(request):
    if request.method != 'POST':
         return HttpResponse(status=405)
    return JsonResponse({"ok":True, "message":"Wiring works"})

def result_view(request,job_id):
    return HttpResponse(f"Result for job {job_id}")