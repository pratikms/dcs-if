from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'blank-page.html', { 'nav_active': 'blank' })

def dashboard(request):
    return render(request, 'dashboard.html', { 'nav_active': 'dashboard' })

def hosts(request):
    return render(request, 'hosts.html', { 'nav_active': 'hosts' })