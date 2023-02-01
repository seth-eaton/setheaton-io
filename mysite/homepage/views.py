from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.
def home(request):
    return render(request, 'homepage/home.html')

def not_found_view(request, exception):
    if request.path.count('sethtunes/') > 0:
        return render(request, 'homepage/sethtunes_404.html')
    else:
        return render(request, 'homepage/404.html')
