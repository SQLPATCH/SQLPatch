'''
Description: Prototype System of SQLPATCH
LastEditTime: 2021-12-12 16:54:25
'''

import os
import sys
import pandas as pd
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from multiprocessing import Pool
from time import time
from util.sqlpatch import *
from util.frontend import *
from util.analysis import *
from util.validate import *
from util.file_struct_scanner import *

config_file = '../config/configure.json'    #Path of configuration file
save_dir = '../corpus/'                    #Path to download and decompress the C project file
output_dir = '../output/'                   #Path to output the repaired C project, report and log
temp_path = '../config/patch_template.json' #Path of patch templates

n = 1   # The number of processes allowed to run at the same time

def SQLPATCH(cfg, save_dir, output_dir, temp_path, sum_path):
    '''
    description: 
        Download, decompress, scan and repair a single project,
         according to the configuration file
    param {
        cfg:        Configuration item
        save_dir:   Save path of the downloaded file
        output_dir: Output path of the log and repaired project
        temp_path:  Path of patch templates
        sum_path:   Path of results
    }
    return {
        result:     Output a dict containing time, scan results, and repair results
    }
    '''     
    url = cfg['download_url']
    name = cfg['project_name']

    cur_dir = os.path.abspath(os.getcwd())

    start = time()

    #Create folders for the current processing version
    # Source code download and save path
    folder_path = os.path.abspath(os.path.join(save_dir, name))
    if os.path.isdir(folder_path):
        pass
    else:
        os.mkdir(folder_path)

    # Path to save log and patched code
    output_path = os.path.abspath(os.path.join(output_dir, name))
    if os.path.isdir(output_path):
        pass
    else:
        os.mkdir(output_path)

    log_path = os.path.join(output_path, 'log.txt')
    f = open(log_path,'w')
    f.write('processing log of ' + name)
    f.close()


    # Package name 
    filename = url.split('/')[-1]
    
    print_to_log('filename:  ' + filename, log_path)
    print_to_log('folder_path:  ' + folder_path, log_path)

# ======================= Download =======================  

    file_path, download_time = download(url, folder_path, log_path)

# ======================= Decompress ======================= 

    original_code_path, decompress_time = decompress(file_path, folder_path, log_path)
    print_to_log('original code path:  ' + original_code_path, log_path)

# ======================= Analysis ======================= 

    print_to_log(name + ' original code analysis start.', log_path)
    original_analysis_time, original_analysis_json_path, original_analysis_txt_path = analysis(original_code_path)


    df = single_version_extract(original_analysis_json_path, original_analysis_txt_path, output_path, 'before_fix')

    print_to_log(name + ' original code analysis costed %.2f milliseconds.' % original_analysis_time, log_path)
    print_to_log('original code analysis report path:  ' + original_analysis_json_path, log_path)
    print_to_log('[original code analysis result]', log_path)
    bug_sum_before_fix = single_version_sum(df, log_path)
# ======================= fix ======================= 

    print_to_log(name + ' fixing start.', log_path)
    
    fixed_code_path, patch_number, fix_time, fixed_list = fixall(df,file_path, output_path, 1, temp_path, name, log_path)
                
# ======================= Validate: Analysis after Fix ======================= 

    print_to_log(name + ' patched code analysis start.', log_path)
    df, fixed_analysis_time = analysis_afterfix(fixed_code_path, fixed_list, output_path, log_path)
    bug_sum_after_fix = single_version_sum(df, log_path)

    print_to_log(name + ' patched code analysis costed %.2f milliseconds.' % fixed_analysis_time, log_path)
    print_to_log('[patched code analysis result]', log_path)
    bug_fixed_num = dict(Counter(bug_sum_before_fix) - Counter(bug_sum_after_fix))

    print_to_log('[Number of vulnerabilities successfully fixed]', log_path)
    for key in bug_fixed_num:
        if(bug_fixed_num[key] > 0):
            print_to_log('      ' + str(key) + ': ' + str(bug_fixed_num[key]), log_path)


# ======================= Output ======================= 

    end = time()

    total_time = (end - start) * 1000

    result = {  'name' : name,
                'download_time' : download_time,
                'decompress_time' : decompress_time,
                'original_analysis_time' : original_analysis_time, 
                'fix_time' : fix_time, 
                'fixed_analysis_time' : fixed_analysis_time, 
                'total_time' : total_time,

                'patch_number' : patch_number, 
                'bug_fixed_num' : bug_fixed_num,
                'fixed_code_path' : fixed_code_path
                }

    print_to_log('\n\n[final result]', log_path)
    for key in result:
        print_to_log('      ' + str(key) + ': ' + str(result[key]), log_path)

    print_to_log('\n END', log_path)

    result = [result]

    dfout = pd.DataFrame(result)
    dfout.to_csv(sum_path, mode = 'a', header = False, index = False)

    os.chdir(cur_dir)

    return result


def multiprocess():    

    start = time()  

    res_path = os.path.abspath(os.path.join(output_dir))
    if os.path.isdir(res_path):
        pass
    else:
        os.mkdir(res_path)

    p = Pool(n)
    res_list = []

    sum_path = os.path.abspath(os.path.join(res_path, 'version_analyze.csv'))

    with open(sum_path, 'w') as f:
        f.write('')
    f.close()

    with open(config_file, 'r', encoding='utf-8') as f:
        cfg_list = json.load(f)
    
    for cfg in cfg_list:
        res = p.apply_async(SQLPATCH, args = (cfg, save_dir, output_dir, temp_path, sum_path))
        res_list.append(res) 

    print('Waiting for all subprocesses done...')
    p.close()
    p.join() 
    

    name = ['name', 'download_time', 'decompress_time', 'original_analysis_time',
            'fix_time', 'fixed_analysis_time', 'total_time',
            'patch_number', 'bug_fixed_num', 'fixed_code_path']
    sum = pd.read_csv(sum_path,names = name)
    sum.to_csv(sum_path, mode='w', index = False)

    end = time()
    print('All subprocesses done, costed %.2f seconds.' % (end - start)) 

def onebyone():    

    start = time()  

    res_path = os.path.abspath(os.path.join(output_dir))
    if os.path.isdir(res_path):
        pass
    else:
        os.mkdir(res_path)

    res_list = []

    sum_path = os.path.abspath(os.path.join(res_path, 'version_analyze.csv'))

    with open(sum_path, 'w') as f:
        f.write('')
    f.close()

    with open(config_file, 'r', encoding='utf-8') as f:
        cfg_list = json.load(f)

    for cfg in cfg_list:
        res = SQLPATCH(cfg, save_dir, output_dir, temp_path, sum_path)
        res_list.append(res) 

    name = ['name', 'download_time', 'decompress_time', 'original_analysis_time',
            'fix_time', 'fixed_analysis_time', 'total_time',
            'patch_number', 'bug_fixed_num', 'fixed_code_path']
    sum = pd.read_csv(sum_path,names = name)
    sum.to_csv(sum_path, mode='w', index = False)

    end = time()
    print('All subprocesses done, costed %.2f seconds.' % (end - start))

if __name__ == '__main__':
    multiprocess()
    # onebyone()

