import tarfile
import sys
import re
import json
import os
import shutil

# image_tar_file = "test.tar"
tar_obj = None
status_file_dir = os.path.dirname(os.path.realpath(__file__))+ os.sep + "extract_dumping_area"

count = 0     


def find_file(layer_path, tar_obj):
    global count
    status_files = []
    layer_obj = tarfile.open(fileobj=tar_obj.extractfile(layer_path))
    for m in layer_obj.getmembers():
        if "status" in (m.name).lower() and "status-old" not in (m.name).lower():
            count = count + 1  
            layer_obj.extract(m.name, status_file_dir)
            if os.path.exists(status_file_dir + os.sep + m.name):
                print("%s extracted successfully\n\n" %m.name)
                os.rename(status_file_dir+os.sep+m.name, status_file_dir+os.sep+m.name+str(count)) 
                status_files.append(status_file_dir+os.sep+m.name+str(count))
        if "os-release" in m.name:
            layer_obj.extract(m.name)
            if os.path.exists(m.name):
                print("%s extracted successfully\n\n" %m.name)
    return status_files

def main(image_name):
    image_tar_file = image_name
    for root, dirs, files in os.walk(status_file_dir):
        for dir in dirs:
            shutil.rmtree(root + os.sep + dir)
        for f in files:
            if not f.endswith(".tar") :
                os.unlink(root+os.sep+f)
    if not tarfile.is_tarfile(image_tar_file):
        print("%s is not tar file" %image_tar_file)
        sys.exit(1)    
    print("%s is tar file" %image_tar_file)
    print("Untar file")
    status_file = None
    try:
        tar_obj = tarfile.open(name=image_tar_file, mode='r')
    except IOError as e:
        print(e)
    else:
        if tar_obj.extractall('./extract_dumping_area/', members=[m for m in tar_obj.getmembers() if m.name in "manifest.json"]):
            print("manifest.json extracted successfully")
        with open("./extract_dumping_area/manifest.json") as f:
            data = json.load(f)
        layers = data[0]['Layers']
        package_info_list = []
        for layer in layers:
            s_files = find_file(layer, tar_obj)
            #if status_file is not None:
            #    break
            for status_file in s_files:
                with open(status_file)as fd:
                    package_data = fd.read().split('\n\n')
                
                for data in package_data:
                    package_info = {}
                    package_re = re.search('Package:\s+(.*)', data, re.I|re.M)
                    if package_re:
                        package_info['Package'] = package_re.group(1)
                    maintainer_re = re.search('Maintainer: (.*)', data, re.I|re.M)
                    if maintainer_re:
                        package_info['Maintainer'] = maintainer_re.group(1)
                    version_re = re.search('Version: (.*)', data, re.I|re.M)
                    if version_re:
                        package_info['Version'] = version_re.group(1)
                    if package_info:
                        package_info_list.append(package_info)
        for v in package_info_list:
            print(v)
    return package_info_list