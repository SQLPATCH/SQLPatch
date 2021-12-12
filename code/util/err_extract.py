'''
Description: Extract and process vulnerability reports
LastEditTime: 2021-12-12 15:14:14
'''
import json
import pandas as pd
from pandas import DataFrame
import re
import os

from util.frontend import print_to_log


def single_version_extract(jsonpath, txtpath, output_path, name):
    '''
    description: Handle vulnerability report and return dataframe
    param {
        jsonpath:      Path of report.json
        txtpath:       Path of report.txt
        output_path:    Path of processed analysis report
        name:           Name of project
    }
    return {
        df:  Processed analysis report
    }
    '''    

    if os.path.isdir(output_path):
        pass
    else:
        os.mkdir(output_path)


    jsonrecords = [json.loads(line) for line in open(jsonpath)]
    allbug = jsonrecords[0]#All scanned vulnerabilities

    with open(txtpath) as f:
        txt = f.readlines()
    
    f.close()

    # Exclude false positive
    index_to_del = []
    for i in range(len(allbug)):
        if (
            (allbug[i]["bug_type"] == "NULL_DEREFERENCE" and allbug[i]["qualifier"].find('`null`') != -1 )
            or
            (allbug[i]["file"].find("src/")!=-1)
            ):
            index_to_del.append(i)
    index_to_del.sort()
    del_num = 0
    for i in range(len(index_to_del)):
        del allbug[index_to_del[i]-del_num]
        del_num += 1

    i = 0
    for no in range(0, len(allbug)*10, 10):
        # Create a new field to save the error code line
        allbug[i]["error_code_line"] = txt[no+5]
        i = i+1

    pattern = re.compile(r'[a-z_A-Z]+\((.*?)\)')
    count = 0
    other = 0

    for i in range(len(allbug)):
        # Number the detected bug
        allbug[i]["sequence"] = i+1  

        line = allbug[i]["error_code_line"]
        # Create a new field to save the name of the API involved in the vulnerability
        if pattern.search(line):
            APIname = pattern.search(line).group().split('(')[0]
            allbug[i]["API_name"] = APIname

            if(APIname[:3] == '_Py' or APIname[:2] == 'Py'):# Python/C API
                allbug[i]["is_pythonCAPI"] = 1
                count = count+1
            else:
                allbug[i]["is_pythonCAPI"] = 0
                other = other+1
                
        else:
            allbug[i]["API_name"] = ''
            allbug[i]["is_pythonCAPI"] = -1

    df = DataFrame(allbug)

    df.to_csv(output_path + '/' + name + '.csv', index = False)#csv

    df.to_excel(output_path + '/' + name + '.xlsx', index = False)#excel

    return df


# NEW
def single_csv_extract(csvpath, output_path, name):

    if os.path.isdir(output_path):
        pass
    else:
        os.mkdir(output_path)

    csv = pd.read_csv(csvpath)
    allbug = csv.to_dict('records')
    print(len(allbug))

    # Exclude false positive
    index_to_del = []
    for i in range(len(allbug)):
        if (
            (allbug[i]["bug_type"] == "NULL_DEREFERENCE" and allbug[i]["qualifier"].find('`null`') != -1 )
            or
            (allbug[i]["file"].find("src/")!=-1)
            ):
            index_to_del.append(i)
    index_to_del.sort()
    del_num = 0
    for i in range(len(index_to_del)):
        del allbug[index_to_del[i] - del_num]
        del_num += 1

    pattern = re.compile(r'sqlite3_[a-z_A-Z0-9]+\((.*?)')
    count = 0
    other = 0

    for i in range(len(allbug)):
        # Number the detected bug
        allbug[i]["sequence"] = i+1  
        line = allbug[i]["error_code_line"]

        # Create a new field to save the name of the API involved in the vulnerability
        if pattern.search(line):
            APIname = pattern.search(line).group().split('(')[0]
            
            allbug[i]["API_name"] = APIname
            print('API NAME:', APIname, '       ERROR TYPE:    ', allbug[i]['bug_type'])
            allbug[i]["is_sqlCAPI"] = 1
            count = count+1
        else:
            allbug[i]["is_sqlCAPI"] = 0
            other = other + 1

    print(count)
    # print(other)

    df = DataFrame(allbug)

    df.to_csv(output_path + '/' + name + '.csv', index = False)#csv
    # df.to_excel(output_path + '/' + name + '.xlsx', index = False)#excel
    # return df

# new
def single_csv_sum(csvpath):
    csv = pd.read_csv(csvpath)
    df = DataFrame(csv)
    dead_store = len(df.loc[(df.bug_type == 'DEAD_STORE')])
    sc_dead_store = len(df.loc[(df.bug_type == 'DEAD_STORE') & (df.is_sqlCAPI == 1)])
    uninitialized_value = len(df.loc[(df.bug_type == 'UNINITIALIZED_VALUE')])
    sc_uninitialized_value = len(df.loc[(df.bug_type == 'UNINITIALIZED_VALUE') & (df.is_sqlCAPI == 1)])
    null_dereference = len(df.loc[(df.bug_type =='NULL_DEREFERENCE')])
    sc_null_dereference = len(df.loc[(df.bug_type =='NULL_DEREFERENCE') & (df.is_sqlCAPI == 1)])
    resource_leak = len(df.loc[(df.bug_type == 'RESOURCE_LEAK')])
    sc_resource_leak = len(df.loc[(df.bug_type == 'RESOURCE_LEAK') & (df.is_sqlCAPI == 1)])
    bug_sum = len(df)
    sc_bug_sum = len(df.loc[df.is_sqlCAPI == 1])
    
    sum = {'Dead_Store': dead_store, 
            'sc_Dead_Store': sc_dead_store,
            'Uninitialized_Value': uninitialized_value,
            'sc_Uninitialized_Value': sc_uninitialized_value,
            'Null_Dereference': null_dereference,
            'sc_Null_Dereference': sc_null_dereference,
            'Resource_Leak': resource_leak,
            'sc_Resource_Leak': sc_resource_leak,
            'BUG_SUM': bug_sum,
            'sc_BUG_SUM': sc_bug_sum
            }
    
    for key in sum:
        print('      ' + str(key) + ': ' + str(sum[key]))
    
    return sum





def single_version_sum(df, log_path):
    '''
    description: Count the number of various types of vulnerabilities
    param {
        df:         Processed analysis report
        log_path:   Path of log file
    }
    return {
        sum: Statistical results
    }
    '''    
    dead_store = len(df.loc[(df.bug_type == 'DEAD_STORE')])
    uninitialized_value = len(df.loc[(df.bug_type == 'UNINITIALIZED_VALUE')])
    null_dereference = len(df.loc[(df.bug_type =='NULL_DEREFERENCE')])
    resource_leak = len(df.loc[(df.bug_type == 'RESOURCE_LEAK')])
    bug_sum = len(df)
    
    sum = {'Dead_Store': dead_store, 
            'Uninitialized_Value': uninitialized_value,
            'Null_Dereference': null_dereference,
            'Resource_Leak': resource_leak,
            'BUG_SUM': bug_sum
            
            }
    
    for key in sum:
        print_to_log('      ' + str(key) + ': ' + str(sum[key]), log_path)
    
    return sum




def all_version_data(data_path, output_path):
    '''
    description: Integrate analysis results of all projects
    param {
        data_path:      Path of result of each project
        output_path:    Path to save total result
    }
    '''    
    dirs = os.listdir(data_path)
    if os.path.isdir(output_path):
        pass
    else:
        os.mkdir(output_path)

    alldata = pd.ExcelWriter(os.path.join(output_path, 'alldata.xlsx'))

    version = []
    dead_store = []
    py_dead_store = []
    uninitialized_value = []
    py_uninitialized_value = []
    null_dereference = []
    py_null_dereference = []
    resource_leak = []
    py_resource_leak = []
    bug_sum = []
    py_bug_sum = []

    for folder in dirs:
        jsonpath = os.path.join(data_path, folder, 'infer-out/report.json')
        txtpath = os.path.join(data_path, folder, 'infer-out/report.txt')
        output = output_path + '/' +folder+'/'

        df= single_version_extract(jsonpath, txtpath, output, 'analysis')

        version.append(folder)
        dead_store.append(len(df.loc[(df.bug_type == 'DEAD_STORE')]))
        uninitialized_value.append(len(df.loc[(df.bug_type == 'UNINITIALIZED_VALUE')]))
        null_dereference.append(len(df.loc[(df.bug_type =='NULL_DEREFERENCE')]))
        resource_leak.append(len(df.loc[(df.bug_type == 'RESOURCE_LEAK')]))
        bug_sum.append(len(df))

        df.to_excel(alldata, sheet_name = folder)

    alldata.close()


    interest = {'version': version,
            'DEAD_STORE': dead_store,
            'UNINITIALIZED_VALUE':uninitialized_value,
            'NULL_DEREFERENCE':null_dereference,
            'RESOURCE_LEAK':resource_leak,
            
            'bug_sum':bug_sum
            }
    dfout = pd.DataFrame(interest)

    dfout.to_excel(output_path + '/version_analyze.xlsx', index = False)#excel
    dfout.to_csv(output_path + '/version_analyze.csv', index = False)#csv
   

