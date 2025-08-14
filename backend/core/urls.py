from django.urls import path
from . import views

app_name='core'

urlpatterns = [
    path('',views.main_view, name='main'),
    path('api/convert',views.convert_view,name='convert'),
    path('result/<uuid:job_id>/',views.result_view,name='result')
]