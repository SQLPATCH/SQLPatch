'''
Description: Statistical tools
LastEditTime: 2021-10-21 12:56:34
'''
# !/usr/bin/env python
import os


def get_file_content(filepath):
    '''
    description: Get file content and split by line
    param {
        filepath
    }
    return {
        line_list
    }
    ''' 
    
    with open(filepath, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    line_list = content.split('\n')
    return line_list


def filter_file(project_path, file_list):
    '''
    description: Filter files
    param {
        project_path
        file_list
    }
    return {
        file_list
    }
    '''   
    for file in os.listdir(project_path):
        file_path = os.path.join(project_path, file)
        if os.path.isdir(file_path):
            filter_file(file_path, file_list)
        elif (file_path.endswith('.c') or file_path.endswith('.cpp')) and file.find('test') == -1:
            file_list.append(file_path)
    return file_list


