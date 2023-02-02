from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('test/', views.home_test, name="test/"),
]
