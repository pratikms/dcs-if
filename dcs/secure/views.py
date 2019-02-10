from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
import logging
import json
import subprocess
import tarfile
import sys
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../",)))
import debian_parser as db
import vulners
import linuxScanner as scanner


logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return render(request, 'blank-page.html', { 'nav_active': 'blank' })

def dashboard(request):
    total_number_of_images = total_images()
    total_number_of_containers = total_containers()
    total_compliance_score = compliance_score()
    logger.error(total_number_of_containers)
    return render(request, 'dashboard.html', { 'total_images': total_number_of_images, 'total_containers': total_number_of_containers, 'total_compliance_score': total_compliance_score, 'nav_active': 'dashboard' })

def images(request):
    command = "docker image list --format 'table {{.Repository}},{{.Tag}},{{.ID}},{{.CreatedAt}},{{.Size}}'"
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
    # error = proc.stderr.read()
    if output:
        logger.error (output)
        return str(output.decode('utf-8').rstrip())
    return None

def containers(request):
    command = "docker container list --format 'table {{.ID}},{{.Image}},{{.Status}},{{.Command}},{{.CreatedAt}},{{.Names}},{{.Labels}}'"
    container_list = subprocess.check_output(command, shell=True).decode('utf8').splitlines()
    data = [d.split(",") for d in container_list[1:]]
    # image_dict = {i:v.split(",") for i, v in enumerate(image_list[1:])}
    logger.error(data[0])
    # return JsonResponse({'data': image_dict})
    return render(request, 'containers.html', { 'data': data, 'nav_active': 'containers' })

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
            return render(request, 'compliance.html', { 'total': total, 'score':count,'results':compresults, 'nav_active': 'compliance_check' })
        except yaml.YAMLError as exc:
            logger.error(exc)

def get_total(identifier):
    command = 'docker ' + identifier + ' list'
    wc_command = 'wc -l'
    command_op = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    wc_command_op = subprocess.check_output(wc_command, shell=True, stdin=command_op.stdout)
    total = int(wc_command_op) - 1
    return total

def total_images():
    total_images = get_total('image')
    return total_images

def total_containers():
    total_containers = get_total('container')
    return total_containers

def save_docker_tar(image_name):
    if "/" in image_name:
        image_name = image_name.replace("/", "_")
    if "-" in image_name:
        image_name = image_name.replace("-", "_")
    tar_name = "../extract_dumping_area/"+ image_name + ".tar"
    image_save_command = 'docker image save ' + image_name + " -o " + tar_name
    img_save_command_op = subprocess.Popen(image_save_command, shell=True, stdout=subprocess.PIPE)
    # logger.error(img_save_command_op.stdout.read())
    # total_containers_command_op = subprocess.check_output(total_containers_command, shell=True, stdin=containers_command_op.stdout)
    if os.path.exists(tar_name):
        return tar_name
    else:
        return None 

def vulscan_images(request, img_id='',img_name=''):
    image_name = img_name
    tarname = save_docker_tar(img_id)
    vulners_api = vulners.Vulners(api_key="EZHMSESQ6PEL7AJVF8LWUE5P7EDHYXXAJ2DN86B42DD7BVFZODZSWGK5QRUWNZCX")
    if tarname:
        package_list = db.main(tarname)
        total_packages = len(package_list)
        for pkg in package_list:
            # results = vulners_api.softwareVulnerabilities(pkg['Package'] , pkg['Version'])
            cpe_results = vulners_api.cpeVulnerabilities('"'+'cpe:/a:'+pkg['Package'].lower()+':debian:'+ pkg['Version'] +'"')
            logger.error(cpe_results)

        return render(request, 'vulscan.html', { 'data': package_list, 'total_packages':total_packages , 'image_name':image_name})
    else:
        return HttpResponse("cannot save image, failed failed failed")

def vulscan_containers_view(request, cont_id='', cont_name=''):
    return render(request, 'vulscan_container.html', { 'cont_name': cont_name, 'cont_id': cont_id })

def vulscan_images_view(request, image_id='', image_name=''):
    return render(request, 'vulscan_image.html', { 'img_id': image_id, 'img_name': image_name })

def vulscan_containers(request, cont_id='', cont_name=''):
    scannerInstance = scanner.scannerEngine()
    cont_scan_results = scannerInstance.scan(dockerID=cont_id, dockerImage=cont_name, checkDocker=True)
    # logger.error(json.dumps(cont_scan_results))
    return JsonResponse(cont_scan_results, safe=False)
    # return render(request, 'vulscan_container.html', { 'cont_name': cont_name, 'cont_scan_results': cont_scan_results })


def compliance_score():
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
            return { 'total': total, 'score':count}
        except yaml.YAMLError as exc:
            logger.error(exc)


def image_vulscan(request, img_id=''):
    import random
    docker_nm = "container_" + str(random.randint(1,101))
    command = "docker run -it --name=" + docker_nm + " -d "+ str(img_id)
    logger.error("Running command : " + command)
    proc = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stdout.read()
    cmd_cntnr_id = "docker ps -aqf \"name=" + docker_nm.strip() + '"'
    running_cntnr_id = subprocess.check_output(cmd_cntnr_id, shell=True).decode('utf8').splitlines()[0]
    scannerInstance = scanner.scannerEngine()
    image_scan_results = scannerInstance.scan(dockerID=running_cntnr_id, dockerImage=docker_nm, checkDocker=True)
    logger.error(image_scan_results)
    # error = proc.stderr.read()
    command = "docker kill " + docker_nm 
    proc = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    kill_output = proc.stdout.read()
    logger.error ('Before o/p')
    if output:
        logger.error (output)
        # return HttpResponse(output)
        #return str(output.decode('utf-8').rstrip())
        return JsonResponse(image_scan_results, safe=False)
        #return render(request, 'vulscan_images.html', { 'data': image_scan_results })
    logger.error ('After o/p')
