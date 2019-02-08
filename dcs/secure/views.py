from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
import logging
import json

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'blank-page.html', { 'nav_active': 'blank' })

def dashboard(request):
    return render(request, 'dashboard.html', { 'nav_active': 'dashboard' })

def hosts(request):
    path = '.'
    files = os.listdir(path)
    return render(request, 'hosts.html', { 'files': files, 'nav_active': 'hosts' })

def perform(request, action='', name=''):
    path = '.'
    files = os.listdir(path)
    filesDict = {i: v for i, v in enumerate(files)}
    filesDict['name'] = name
    filesDict['action'] = action
    return JsonResponse(filesDict)