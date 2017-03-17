#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################
# name:updatehosts
# author: https://github.com/williezh
# version:1.0
# license:MIT
############################

import urllib2
import platform
import time
import re
import os
import shutil
import ConfigParser
import sys
import socket
from datetime import datetime

conf_file = 'config.ini'
# default setting
hosts_folder = ''
hosts_location = '{}hosts'.format(hosts_folder)

source_list = ['https://raw.githubusercontent.com/vokins/simpleu/master/hosts']
not_block_sites = 0
always_on = 0
# default setting

errorLog = open('errorLog.txt', 'a')


def get_cur_info():
    return (sys._getframe().f_back.f_code.co_name)

def exit_this():
    errorLog.close()
    sys.exit()

def deal_error(e):
    now=datetime.now()
    errorLog.write('{}\nfunction:{}\nerror:{}\n\n'.format(now,get_cur_info(),e))
    exit_this() 
       
def check_connection():
    sleep_seconds = 1200    
    for i in range(sleep_seconds):
        try:
            socket.gethostbyname('www.baidu.com')
            break
        except socket.gaierror:
            time.sleep(1)
    else:
        exit_this()


def check_system():
    global hosts_folder
    global hosts_location
    ps=platform.system()
    if ps == 'Windows':
        hosts_folder = os.environ['SYSTEMROOT'] + '\\System32\\drivers\\etc\\'
    elif ps in ['Linux' ,'Darwin']:
        hosts_folder = '/etc/'
    else:
        exit_this()
    hosts_location = '{}hosts'.format(hosts_folder)


def get_config():
    global source_list
    global not_block_sites
    global always_on
    if os.path.exists(conf_file):
        try:
            # 清除Windows记事本自动添加的BOM
            with open(conf_file, 'r+') as f:
                content = f.read()
                content = re.sub(r'\xfe\xff', '', content)
                content = re.sub(r'\xff\xfe', '', content)
                content = re.sub(r'\xef\xbb\xbf', '', content)
                f.seek(0)
                f.write(content)

            conf = ConfigParser.ConfigParser()
            conf.read(conf_file)
            ss='source_select'
            source_id = conf.get(ss, 'source_id')
            source_list = source_id.split(',')
            for i in range(len(source_list)):
                source_list[i] = conf.get(ss, 'source{}'.format(i + 1))

            not_block_sites = conf.get('function', 'not_block_sites')
            always_on = conf.get('function', 'always_on')
        except BaseException as e:
            deal_error(e)


def backup_hosts():
    origin='{}hosts'.format(hosts_folder)
    backup='{}backup_hosts_original_by_updateHosts'.format(hosts_folder)    
    try:                        
        if os.path.isfile(origin):
            if not os.path.isfile(backup):
                shutil.copy(origin, backup)
            shutil.copy(hf, fn.replace('original','last'))
    except BaseException as e:
        deal_error(e)


def download_hosts():
    try:
        hosts_from_web = open('hosts_from_web', 'a')
        for x in source_list:
            data = urllib2.urlopen(x)
            hosts_from_web.write(data.read())
    except BaseException as e:
        deal_error(e)


def process_hosts():
    try:
        hosts_content = open('hosts', 'w')
        file_from_web = open('hosts_from_web')
        hosts_from_web = file_from_web.read()
        file_user_defined = open('hosts_user_defined.txt')
        hosts_user_defined = file_user_defined.read()
        hosts_content.write('#hosts_user_defined\n')
        hosts_content.write(hosts_user_defined)
        hosts_content.write('\n#hosts_user_defined\n')
        hosts_content.write('\n\n#hosts_by_hostsUpdate\n\n')
        site='127.0.0.1'
        if not_block_sites == '1':
            hosts_from_web = re.sub(site, '#not_block_sites', hosts_from_web)
        hosts_content.write(hosts_from_web)
        hosts_content.write('\n#hosts_by_hostsUpdate')
        hosts_content.close()
        file_from_web.close()
        file_user_defined.close()
        os.remove('hosts_from_web')
    except BaseException as e:
        deal_error(e)


def move_hosts():
    try:
        shutil.move('hosts', hosts_location)
    except BaseException as e:
        deal_error(e)


def main():
    check_connection()
    check_system()
    get_config()
    backup_hosts()
    download_hosts()
    process_hosts()
    move_hosts()
    errorLog.close()


if __name__ == '__main__':
    main()

if always_on == '1':
    while 1:
        time.sleep(3600)
        main()
