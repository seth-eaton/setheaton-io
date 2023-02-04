from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.
def home(request):
    if request.user_agent.is_mobile:
        return render(request, 'homepage/mobile_home.html')
    else:
        return render(request, 'homepage/home.html')

def projects(request):
    if request.user_agent.is_mobile:
        return render(request, 'homepage/mobile_projects.html')
    else:
        return render(request, 'homepage/projects.html')

def about(request):
    if request.user_agent.is_mobile:
        return render(request, 'homepage/mobile_about.html')
    else:
        return render(request, 'homepage/about.html')

def home_test(request):
    return render(request, 'homepage/home_test.html')

def not_found_view(request, exception):
    if request.path.count('sethtunes/') > 0:
        return render(request, 'homepage/sethtunes_404.html')
    if request.path.count('test/') > 0:
        return render(request, 'homepage/test_404.html')
    else:
        return render(request, 'homepage/404.html')
