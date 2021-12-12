'''
Description: Scan the project and output detailed vulnerability report
LastEditTime: 2021-11-28 18:44:43
'''

import os
from util.frontend import *
from util.err_extract import *
from time import time

def analysis(folder_path):
    '''
    description: Scan the project and output detailed vulnerability report
    param {
        file_path: Path of the project to be scanned
    }
    return {
        analysis_time:  Time of analysis
        json_path:      Path of report.json
        txt_path:       Path of report.txt
    }
    '''    

    start = time()
    cur_path = os.path.abspath(os.getcwd())
    os.chdir(folder_path)#Enter the unzipped folder

    os.system('./configure')
    os.system('make clean')
    os.system('infer run -- make --keep-going')

    end = time()
    analysis_time = (end - start)*1000

    json_path = os.path.join(os.getcwd(), 'infer-out', 'report.json')
    txt_path = os.path.join(os.getcwd(), 'infer-out', 'report.txt')  
    
      

    os.chdir(cur_path)

    return analysis_time, json_path, txt_path


def analysis_afterfix(folder_path, fixed_list, output_path, log_path):


    start = time()
    cur_path = os.path.abspath(os.getcwd())
    os.chdir(folder_path)#Enter the fixed folder
    df_list=[]
    for file_path in fixed_list:
        if(file_path.find('/')!=-1):
                filename=file_path.split('/')[-1]
        else:
            filename=file_path


        line = 'infer -- gcc -c '+file_path
        print(line)
        os.system(line)
        json_path = os.path.join(os.getcwd(), 'infer-out', 'report.json')
        txt_path = os.path.join(os.getcwd(), 'infer-out', 'report.txt')  
        if(os.path.exists(json_path) == False):
            print_to_log('[ERROR]Part of the default patch may affect the original function of the program,\nplease check the patch that has been applied, \nadd some batch templates \nand fix it again', log_path)
            exit(1)
        df=single_version_extract(json_path, txt_path, output_path, filename+'_after_fix')
        df_list.append(df)
        print(len(df))
    dfout = pd.concat(df_list)
    print(len(dfout))
    end = time()
    analysis_time = (end - start)*1000
    os.chdir(cur_path)
    return dfout, analysis_time

    
    
      


