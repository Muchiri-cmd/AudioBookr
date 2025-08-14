from django.urls import path
from .views import *

urlpatterns = [
    path('', DefaultView.as_view(), name='default_view'),            
    path('upload/', UploadView.as_view(), name='upload'),             
    path('start/', StartProcessView.as_view(), name='start-process'),  
    path('voices/', VoicesView.as_view(), name='voices'),              
]