from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
import logging
import json
import subprocess

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'blank-page.html', { 'nav_active': 'blank' })

def dashboard(request):
    total_number_of_images = total_images()
    total_number_of_containers = total_containers()
    return render(request, 'dashboard.html', { 'total_images': total_number_of_images, 'total_containers': total_containers, 'nav_active': 'dashboard' })

def images(request):
    command = "docker image list --format 'table {{.Repository}},{{.Tag}},{{.ID}},{{.Size}}'"
    image_list = subprocess.check_output(command, shell=True).decode('utf8').splitlines()
    data = [d.split(",") for d in image_list[1:]]
    # image_dict = {i:v.split(",") for i, v in enumerate(image_list[1:])}
    logger.error(data[0])
    # return JsonResponse({'data': image_dict})
    return render(request, 'images.html', { 'data': data, 'nav_active': 'images' })
    
def perform(request, action='', name=''):
    path = '.'
    files = os.listdir(path)
    filesDict = {i: v for i, v in enumerate(files)}
    filesDict['name'] = name
    filesDict['action'] = action
    return JsonResponse(filesDict)

def total_images():
    images_command = 'docker image list'
    total_images_command = 'wc -l'
    images_command_op = subprocess.Popen(images_command, shell=True, stdout=subprocess.PIPE)
    total_images_command_op = subprocess.check_output(total_images_command, shell=True, stdin=images_command_op.stdout)
    total_images = int(total_images_command_op) - 1
    return total_images

def total_containers():
    containers_command = 'docker container list'
    total_containers_command = 'wc -l'
    containers_command_op = subprocess.Popen(containers_command, shell=True, stdout=subprocess.PIPE)
    total_containers_command_op = subprocess.check_output(total_containers_command, shell=True, stdin=containers_command_op.stdout)
    total_containers = int(total_containers_command_op) - 1
    return total_containers