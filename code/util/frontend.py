'''
Description: Acquisition and pretreatment of source files according the configuration provided by users. 
LastEditTime: 2021-12-12 16:56:02
'''
import os
import hashlib
from time import time
import tarfile
import json

def config(config_file):
    '''
    description: Read configuration file
    param {
        config_file ： Path of configuration file
    }
    return {
        download_url：Download link
        project_name：Name of project
    }
    '''    
    project_name = []
    download_url = []
    md5_list = []
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg_list = json.load(f)
    for cfg in cfg_list:
        project_name.append(cfg['project_name'])
        download_url.append(cfg['download_url'])
        md5_list.append(cfg['md5'])
    return download_url, project_name, md5_list


def md5_verify(file_path, md5, log_path):
    with open(file_path, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    fp.close()
    if file_md5 == md5 :
        print_to_log('MD5 verification passed', log_path)
        return 1
    else:
        print_to_log('MD5 verification failed', log_path)
        return 0


def download(url, folder_path, log_path):
    """
    Download the source file according to the given URL
    Parameter:
        url:            Download link
        folder_path：   Path to save downloaded file
        log_path:       Path to save log.txt
        
    """

    start = time()

    print_to_log('download from:  ' + url, log_path)
    filename = url.split('/')[-1]
    file_path = os.path.join(folder_path, filename)
    
    link = 'wget -P ' + folder_path + ' ' + url
    
    os.system(link)

    end = time()

    download_time = (end - start)*1000
        
    print_to_log(filename + '   successfully downloaded, cost %.2f milliseconds.' % download_time, log_path)
    print_to_log('downloaded file path:  ' + file_path, log_path)

    return file_path, download_time



def decompress(file_path, folder_path, log_path):
    '''
    description: Unzip the project package, according to the specified path
    param {
        file_path:      Path of project package
        folder_path:    Path to save decompressed file
        log_path:       Path of log file
    }
    return {
        abs_path:           Absolute path of file
        decompress_time:    Time of decompression        
    }
    '''    
    start = time()

    filename = file_path.split('/')[-1]
    tar = tarfile.open(file_path)
    tar.extractall(folder_path)

    t = tarfile.open(file_path)
    t.extractall(path = folder_path) 
    
    t.close()

    end = time()

    decompress_time = (end - start) * 1000

    print_to_log(filename + '   successfully decompressed, cost %.2f milliseconds.' % decompress_time, log_path)
    abs_path = os.path.abspath(os.path.join(folder_path, filename.split('/')[-1].split('.')[0]))

    return abs_path, decompress_time



def print_to_log(str, log_path):
    '''
    description: Output to log file
    param {
       str:         something to record 
       log_path :   Path of log file
    }
    '''    
    f = open(log_path,'a')
    print(str, file = f)
    f.close()
