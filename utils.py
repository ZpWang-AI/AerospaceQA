import datetime
import time
import os
import sys
import traceback
import threading 
import torch
import random

from typing import *
from pathlib import Path as path

from data_utils import dump_data


def get_cur_time(time_zone_hours=8, return_str=True):
    time_zone = datetime.timezone(offset=datetime.timedelta(hours=time_zone_hours))
    cur_time = datetime.datetime.now(time_zone)
    return cur_time.strftime('%Y-%m-%d_%H:%M:%S') if return_str else cur_time


def sleep_random_time(sleep_time):
    time.sleep(random.random()*sleep_time*2)
    

def exception_handling(
    target_func,
    args=(),
    kwargs=None,
    
    display_message='',
    error_file='',
    error_return=None,
    
    exception_handle_methods=None,
    
    retry_time=3,
    sleep_time=2.5,
):
    if kwargs is None:
        kwargs = {}
    if exception_handle_methods is None:
        exception_handle_methods = []
        
    retry_cnt = 0
    while 1:
        retry_cnt += 1
        try:
            # ====================
            result = target_func(*args, **kwargs)
            return result
            # ====================
        except BaseException as err:
            for error_type, handle_func in exception_handle_methods:
                if type(err) == error_type:
                    handled_return = handle_func()
                    if handled_return:
                        retry_cnt += handled_return
                    break
            else:
                if retry_cnt == 1:
                    error_s = '\n'.join([
                        '=='*10,
                        display_message,
                        '-'*10,
                    ])
                    print(error_s)
                    if error_file:
                        dump_data(error_file, error_s, 'a')
                error_s = '\n'.join([
                    traceback.format_exc(),
                    f'>> retry {retry_cnt} <<',
                    f'>> error {str(err)} <<',
                    '-'*10, 
                ])
                print(error_s)
                if error_file:
                    dump_data(error_file, error_s, 'a')
        finally:
            if retry_cnt >= retry_time:
                return error_return
            else:
                sleep_random_time(sleep_time)


if __name__ == '__main__':
    def f1(a):
        print(a)
        1/0
        
    res = exception_handling(
        f1,
        # args=('input',),
        kwargs={'a':'input'},
        display_message='display',
        error_file='./error.txt',
        error_return='error return',
        exception_handle_methods=(
            [KeyboardInterrupt, lambda:print('hh')],
            [ZeroDivisionError, lambda:3],   
        ),
        retry_time=2,
        sleep_time=1,
    )
    print(res)