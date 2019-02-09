import subprocess

def get_output(command):
    print("Running command : " + command)
    proc = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stdout.read()
    error = proc.stderr.read()
    if output:
        print (output)
        return str(output.decode('utf-8').rstrip())
    return None

def main():
    count = 0 
    import yaml
    with open("definitions.yaml", 'r') as stream:
        try:
            results = {}
            mydict = (yaml.load(stream))
            command_list = []

    #        for key in mydict.keys():
    #            print (key)
    #            input()
            for group in (mydict['groups']):
                group_description = group['description']
                results[group_description] = []
                for check in group['checks']: 
                    result_dict = {}
                    if 'audit' in check.keys() and 'tests' in check.keys():
                        result_dict[check['id']] = [] 
                        print(check['id'])
                        print(check['description'])
                        result_dict[check['id']].append({'description':check['description']})
                        print("command = " + check['audit'])
                        flag = check['tests']['test_items'][0]['flag']
                        test_items = check['tests']['test_items'][0]
                        if 'compare' in test_items.keys():
                            compare_dict = check['tests']['test_items'][0]['compare']
                            print (compare_dict)
                            if compare_dict is not None and 'op' in compare_dict.keys() :
                                op = compare_dict['op']
                                value = str(compare_dict['value'])
                                output_str = get_output(check['audit'])    
                                if op == 'has':
                                    if output_str is not None and value in output_str:
                                        #result_dict['status'] = 'PASS'
                                        result_dict[check['id']].append({'status':'PASS'})
                                    else:
                                        #result_dict['status'] = 'FAIL'
                                        result_dict[check['id']].append({'status':'FAIL'})
                                elif op == "eq":
                                    if output_str is not None and str(value).lower() == str(output_str).lower():
                                        result_dict[check['id']].append({'status':'PASS'})
                                    else: 
                                        result_dict[check['id']].append({'status':'FAIL'})
                                results[group_description].append(result_dict)
                        else:
                            output_str = get_output(check['audit'])
                        if output_str is not None:
                            print (output_str)
                        else:
                            print('skipped '+ str(check['id']))
            print("\n\n")
            total = 0
            for k, values in results.items():
                print (k)
                for v in values:
                    for key, value in v.items():
                        print (key)
                        for elmnts in value:
                            print (elmnts)
                            for x,y in elmnts.items():
                                total+=1
                                if x == 'status' and y == 'PASS':
                                    count +=1             
            print("\n\n")
            print("Total:{} \tScore: {}".format(total, count))
        except yaml.YAMLError as exc:
            print(exc)
        
        
if __name__ == '__main__':
    
