'''
Description: 
LastEditTime: 2021-12-12 15:12:17
'''

import json
from pandas import DataFrame
from time import time
from util.frontend import *
from util.err_extract import *
import pandas as pd

def fix_DS(fix_path, line, qualifier, log_path):
    '''
    description: Default repair method for dead store
    param {
        fix_path：  Path of the file to be repaired
        line：      Patch location
        qualifier： Error line
        log_path：  Path of log 
    }
    return： num of patch
    '''    
    with open(fix_path) as f:
        cfile=f.readlines()
    f.close()

    flag = 0

    line = line - 1

    variable_name = qualifier.split('&')[1].split(' ')[0]

    if ((variable_name == 'noptargs') and (cfile[line].find('--noptargs') != -1)) :
        cfile[line] = 'noptargs = noptargs - 1;if(!noptargs){/*patch*/// if (!--noptargs) {' + '\n'
        flag = 1

    elif ((cfile[line].find(variable_name) != -1) and (cfile[line].find(';') != -1)):
        cfile[line] = cfile[line][:-1] + 'printf("%d", ' + variable_name + ');/*patch*/' + '\n'
        flag = 1

    if flag == 1 :

        fixed = ''.join(cfile)

        fp = open(fix_path, mode='w')
        fp.write(fixed)
        fp.close()

        index = fix_path.find('vul/')
        if index!= -1:
            fix_path = fix_path[index + 4:]

        print_to_log('[Fixing DS]  ' + fix_path + '   line:' + str(line + 1), log_path)

    return flag # num of patch


def fix_ND(fix_path, line, qualifier, log_path):
    '''
    description: Default repair method for null dereference
    param {
        fix_path：  Path of the file to be repaired
        line：      Patch location
        qualifier： Error line
        log_path：  Path of log 
    }
    return： num of patch
    '''    
    
    with open(fix_path) as f:
        cfile=f.readlines()
    f.close()
    pointer_name = qualifier.split('`')[1]

    line = line - 1

    cfile[line] ='if (' + pointer_name + ' == NULL) exit;/*patch*/' + cfile[line]
    
    fixed = ''.join(cfile)

    fp = open(fix_path, mode='w')
    fp.write(fixed)
    fp.close()

    index = fix_path.find('vul/')
    if index!= -1:
        fix_path = fix_path[index + 4:]

    print_to_log('[Fixing ND]  ' + fix_path + '   line:' + str(line + 1), log_path)

    return 1 # num of patch



def fix_ND_by_temp(fix_path, temp, log_path):
    '''
    description: Repair according to patch template, which provided by developers
    param {
        fix_path：  Path of the file to be repaired 
        temp：      Patch template
        log_path：  Path of log 
    }
    return： num of patch
    '''     
    
    with open(fix_path) as f:
        cfile=f.readlines()
    f.close()

    if temp["strategy"] == 'offset':
        line = temp["line"] - 1 - temp["offset"]

        cfile[line] ='if (' + temp["poniter_name"] + ' == NULL) exit;/*patch*/' + cfile[line]
        
        fixed = ''.join(cfile)
        fp = open(fix_path, mode='w')
        fp.write(fixed)
        fp.close()

        index = fix_path.find('vul/')
        if index!= -1:
            fix_path = fix_path[index + 4:]

        print_to_log('[Fixing ND]  ' + fix_path + '   line:' + str(temp["line"]), log_path)

        return 1
    
    if temp["strategy"] == 'skip':

        index = fix_path.find('vul/')
        if index!= -1:
            fix_path = fix_path[index + 4:]

        print_to_log('[Skip ND]  ' + fix_path + '   line:' +str(temp["line"]), log_path)
        return 0

    return 0




def get_patch_template(temp_path, name):
    '''
    description: Get the patch template of the specified project
    param {
        temp_path:  Path of batch template file
        name:       Name of project
    }
    return {
        temp_list:  batch template list of the specified project
    }
    '''     

    print(os.getcwd())

    temp_config_file = open(temp_path, 'r')
    all_temp = json.load(temp_config_file)
    temp_config_file.close()

    temp_list = []
    for temp in all_temp:
        if temp["project_name"] == name:
            temp_list.append(temp)

    return temp_list



def fixall(df, file_path, folder_path, version, temp_path, name, log_path):
    '''
    description: Repair the project based on the scan results
    param {
        df:             Information about all bugs, including type,location and etc.
        file_path:      Path of the project to be repaired
        folder_path:    Save path of the repaired project
        version:        version number
        temp_path:      Path of batch template file
        name:           Name of project
        log_path:       Path of log
    }
    return {
        patched_path：  Path of fixed project
        cnt:            num of patch
        fix_time:       time of fixing
    }
    '''    

    print_to_log('-------------------------------------fixing start-------------------------------------', log_path)
    
    
    temp_path= os.path.abspath(temp_path)#!!!!!!!

    folder_path = os.path.join(folder_path, 'patched-v' + str(version))

    patched_path, decompress_time = decompress(file_path, folder_path, log_path)    

    vul_path = os.path.abspath(os.path.join(folder_path, 'vul'))
    if os.path.isdir(vul_path):
        pass
    else:
        os.mkdir(vul_path)


    cur_path = os.path.abspath(os.getcwd())#remember to back
    print_to_log('cur_path      '+cur_path, log_path)
    os.chdir(patched_path)#Enter the unzipped folder
    print_to_log('change to make      '+os.path.abspath(os.getcwd()), log_path)
    
    # make
    os.system('./configure')
    os.system('make')


    # # file need fix
    df_group = df.groupby(by = 'file')
    file_list = list(df_group.groups.keys())
    print(file_list)
    for file_path in file_list:
        line = 'cp '+file_path+' ../vul/'
        os.system(line)
        print_to_log(line, log_path)

    start = time()
    cnt = 0
    
    # ======================= Fixing according to patch template ======================= 


    temp_list = get_patch_template(temp_path, name)

    
    for temp in temp_list :
        if(temp["file"].find('/')!=-1):
                filename=temp["file"].split('/')[-1]
        else:
            filename=temp["file"]


        fix_path = os.path.join(vul_path, filename)

        
        if temp["bug_type"] == 'NULL_DEREFERENCE':
            cnt = cnt + fix_ND_by_temp(fix_path, temp, log_path)

            # Remove the Fixed bug from the summary list
            df.drop(df[
                        (df["file"] == temp["file"]) 
                        & (df["line"] == temp["line"]) 
                        & (df["bug_type"] == temp["bug_type"])

                      ].index, 
                    inplace = True)

    # # ======================= Default fixing ======================= 

        
    
    for i in range(len(df)):
        if(df.iloc[i]["file"].find('/')!=-1):
                filename=df.iloc[i]["file"].split('/')[-1]
        else:
            filename=df.iloc[i]["file"]
        fix_path = os.path.join(vul_path, filename)

        if df.iloc[i]["bug_type"] == 'DEAD_STORE':
            cnt = cnt + fix_DS(fix_path,
                                df.iloc[i]["line"],
                                df.iloc[i]["qualifier"],
                                log_path)

        if df.iloc[i]["bug_type"] == 'NULL_DEREFERENCE':
            cnt = cnt + fix_ND(fix_path,
                                df.iloc[i]["line"],
                                df.iloc[i]["qualifier"], 
                                log_path)
    print_to_log("\nthe number of patch is ：" + str(cnt), log_path)

    end = time()

    # =============================================================

    for file_path in file_list:
        file_name = file_path.split('/')[-1]
        line = 'cp '+'../vul/'+file_name+' '+file_path
        os.system(line)
        print_to_log(line,log_path)

    fix_time = (end - start)*1000

    print_to_log('-------------------------------------fixing end-------------------------------------', log_path)
    print_to_log('fixing costed %.2f milliseconds.\n' % fix_time, log_path)
    print_to_log('current path      '+os.path.abspath(os.getcwd()), log_path)
    return patched_path, cnt, fix_time, file_list








