'''
Description: 
LastEditTime: 2021-12-12 15:18:00
'''
'''
Description: Validate
LastEditTime: 2021-11-28 15:14:07
'''

import multiprocessing
import os
from re import L
import sys
from collections import Counter

from numpy import log
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from multiprocessing import Pool
from time import time
import tarfile
import urllib.request as ur
import json
# from util.patch import *
from util.sqlpatch import *
from util.frontend import *
from util.analysis import *


def get_test_result(test_log_path):
    
    with open(test_log_path) as f:
        txt = f.readlines()
    f.close()
    res = {}
    for i in range(len(txt)):
        line = len(txt)-1-i

        if(txt[line].find(' re-run tests:')!=-1):
            res['re-run'] = int(txt[line][:txt[line].find('re-run tests:')])
        if(txt[line].find(' tests skipped:')!=-1):
            res['skipped'] = int(txt[line][:txt[line].find(' tests skipped:')])
        if(txt[line].find(' tests failed:')!=-1):
            res['failed'] = int(txt[line][:txt[line].find(' tests failed:')])
        if(txt[line].find(' tests OK.')!=-1):
            res['ok'] = int(txt[line][:txt[line].find(' tests OK.')])
            break
    
    return(res)

def make_test(folder_path):
    start = time()
    os.chdir(folder_path)#Enter the folder
    print('os.getcwd():' + os.getcwd())

    os.system('./configure')
    os.system('make')
    os.system('make test > maketestlog.txt')


    end = time()
    test_time = (end - start)*1000

    test_log_path = os.path.join(os.getcwd(), 'maketestlog.txt')
    res = get_test_result(test_log_path)


    return test_time, res


def validate(before_fix_path, after_fix_path, log_path):
    start = time()

# ==============================================
    p = Pool(2)

    t1, before_fix = p.apply_async(make_test, args = (before_fix_path))
    t2, after_fix = p.apply_async(make_test, args = (after_fix_path))
    p.close()
    p.join()
# ==============================================================   
    print_to_log('making test for original code cost %.2f milliseconds' % t1, log_path)
    print_to_log('[test result]', log_path)
    print_to_log(before_fix, log_path)

    print_to_log('making test for patched code cost %.2f milliseconds' % t2, log_path)
    print_to_log('[test result]', log_path)
    print_to_log(after_fix, log_path)

    validate_result = dict(Counter(after_fix) - Counter(before_fix))

    if (validate_result['ok'] >= 0):
        print_to_log('Validation successfully passed. The patches did not destroy the functionality of the project', log_path)
    else:
        print_to_log('Validation failed. Please check the patches', log_path)


    end = time()
    validate_time = (end - start) * 1000
    print_to_log('Validation cost %.2f milliseconds' % validate_time, log_path)

    return validate_time, validate_result




