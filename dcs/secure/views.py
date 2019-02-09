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
    return render(request, 'dashboard.html', { 'total_images': total_number_of_images, 'total_containers': total_number_of_containers, 'nav_active': 'dashboard' })

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

def get_output(command):
    logger.error("Running command : " + command)
    proc = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stdout.read()
    error = proc.stderr.read()
    if output:
        logger.error (output)
        return str(output.decode('utf-8').rstrip())
    return None

def compcheck(request):
    count = 0 
    import yaml
    with open("definitions.yaml", 'r') as stream:
        try:
            results = {}
            mydict = (yaml.load(stream))
            # command_list = []
            for group in (mydict['groups']):
                group_description = group['description']
                results[group_description] = []
                for check in group['checks']: 
                    result_dict = {}
                    if 'audit' in check.keys() and 'tests' in check.keys():
                        result_dict[check['id']] = [] 
                        # logger.error(check['id'])
                        temp = {}
                        temp['description'] = check['description']
                        #result_dict[check['id']].append({'description':check['description']})
                        logger.error("command = " + check['audit'])
                        logger.error(check['remediation'])
                        temp['Remediation'] = check['remediation']
                        test_items = check['tests']['test_items'][0]
                        if 'compare' in test_items.keys():
                            compare_dict = check['tests']['test_items'][0]['compare']
                            logger.error (compare_dict)
                            if compare_dict is not None and 'op' in compare_dict.keys() :
                                op = compare_dict['op']
                                value = str(compare_dict['value'])
                                output_str = get_output(check['audit'])    
                                if op == 'has':
                                    if output_str is not None and value in output_str:
                                        #result_dict['status'] = 'PASS'
                                        temp['status'] = 'PASS'
                                        #result_dict[check['id']].append({'status':'PASS'})
                                    else:
                                        temp['status'] = 'FAIL'
                                        #result_dict[check['id']].append({'status':'FAIL'})
                                elif op == "eq":
                                    if output_str is not None and str(value).lower() == str(output_str).lower():
                                        temp['status'] = 'PASS'
                                        #result_dict[check['id']].append({'status':'PASS'})
                                    else: 
                                        temp['status'] = 'FAIL'
                                        #result_dict[check['id']].append({'status':'FAIL'})
                                result_dict[check['id']].append(temp)
                                results[group_description].append(result_dict)
                        else:
                            output_str = get_output(check['audit'])
                        if output_str is not None:
                            logger.error (output_str)
                        else:
                            logger.error('skipped '+ str(check['id']))
            logger.error("\n\n")
            compresults = {}
            total = 0
            for k, values in results.items():
                logger.error (k)
                mylist = []
                for v in values:
                    for key, value in v.items():
                        logger.error (key)
                        for elmnts in value:
                            logger.error (elmnts)
                            mylist.append(elmnts)
                            for x,y in elmnts.items():
                                total+=1
                                if x == 'status' and y == 'PASS':
                                    count +=1
                compresults[k] = mylist                                    
            logger.error("\n\n")
            logger.error("Total:{} \tScore: {}".format(total, count))
            return render(request, 'compliance.html', { 'total': total, 'score':count,'results':compresults })
        except yaml.YAMLError as exc:
            logger.error(exc)

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