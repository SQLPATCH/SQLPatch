'''
Description: Scan the structure of project
LastEditTime: 2021-12-12 15:14:38
'''
# !/usr/bin/env python



from logging import log
import os
from posix import listdir
from posixpath import abspath
import sys
import pandas as pd
from util.frontend import *


from numpy import DataSource
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
sys.path.append(os.path.join(current_dir, ".."))
import json

from util.file_util import *


def get_file_lines(file):
    count = 0
    f = open(file, "r", encoding='ISO-8859-1')
    for line in f.readlines():
        count = count + 1
    f.close()
    return count


def get_native_code_scale(module, file_count, code_count):
    '''
    description: Get the code size of the module
    param {
        module: module of native code
        file_count: files of native code 
        code_count: lines of native code
    }
    return {*}
    '''   
    for file_name in os.listdir(module):
        file = os.path.join(module, file_name)
        if os.path.isdir(file):
            get_native_code_scale(file, file_count, code_count)
        elif file.endswith('.c') or file.endswith('.cpp') or file.endswith('.h'):
            file_count += 1
            code_count += get_file_lines(file)
    return file_count, code_count


def get_module_scale(module):
    file_count = 0
    code_count = 0

    return get_native_code_scale(module, file_count, code_count)


def get_module(project):
    modules = []
    # print(listdir(project))
    for module_name in os.listdir(project):
        if module_name.startswith('.'):
            continue
        module = os.path.join(project, module_name)
        if os.path.isdir(module):
            modules.append(module)
    return modules

    
def scan_single_project(cfg, log_path=''):
    data = {}

    data['name'] = cfg['project_name']
    project_name = cfg['project_name']
    project_path = cfg['project_path']

    modules = get_module(project_path)
    total_file_count = 0
    total_code_count = 0

    for module in modules:
        # print(module)
        file_count, code_count = get_module_scale(module)
        # print(file_count,code_count)
        total_file_count += file_count
        total_code_count += code_count

        print("module: %s, file count: %d, code count: %d" % (module, file_count, code_count))
        if log_path != '':
            print_to_log("      module: %s, file count: %d, code count: %d" % (module, file_count, code_count),log_path)
        data[module.split('/')[-1] + '  file_count'] = file_count
        data[module.split('/')[-1] + '  code_count'] = code_count

    
    print("%s project total have %d native file, %d lines native code." % (project_name, total_file_count, total_code_count))
    if log_path != '':
        print_to_log("\n      %s project total have %d native file, %d lines native code." % (project_name, total_file_count, total_code_count),log_path)
    data['total_file_count'] = total_file_count
    data['total_code_count'] = total_code_count

    return data


def get_code_size(config_file, output_path):
    '''
    description: Get the number of files and code amount of the projects list
    note:       Ensure that the folder is newly unzipped and the current working directory is in 'code/'
    param {
        config_file: Path of configuration file
    }
    return {
        data_sum: the codesize of each project
    }
    '''    
    
    path = os.getcwd()

    data_list = []
    
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg_list = json.load(f)
    for cfg in cfg_list:
        data = scan_single_project(cfg)        
        data_list.append(data)


    dfout = pd.DataFrame(data_list)
    dfout.to_excel(os.path.join(output_path, 'code_size.xlsx'), index = False)#excel
    dfout.to_csv(os.path.join(output_path, 'code_size.csv'), index = False)#csv
        




if __name__ == '__main__':
    config_file = '../config/configure.json'
    output_path = '../statistics'
    get_code_size(config_file, output_path)
    
