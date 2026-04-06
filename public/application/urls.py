from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('questions.urls', namespace='questions')),
    path('', include('core.urls', namespace='core')),
]
