#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Run wireshark for vm interfaces in openstack via ssh
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

from statistics import mode
from subprocess import Popen, PIPE
import argparse
import logging
import re
import os
import sys
import time
import akarlibs.yamltoheat as ym
import ipdb
from akarlibs.akarlogging import AkarLogging

description = "net-lab: Run ansible-playbook for net-labsv2"
epilog = "Alexey Karpov "


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-n", "--name", help="Stack name in openstack", dest="name", action="store", required=True)
    parser.add_argument("-s", "--skip", help="Skip create stack", dest="skip", action="store_true")
    parser.add_argument("-d", "--dell", help="Del init_del commands", dest="dell", action="store_true")
    parser.add_argument("-t", "--tags", help="List tags", dest="tags", action="store")
    parser.add_argument("-l", "--list", help="List of Routers", dest="list", action="store")
    return parser.parse_args()


def run_ansible(cmd_run):
    p_ansible = os.system(cmd_run)


def gen_heat_os(name_config_yaml):
    logger.info("================ Run gen-heat-openstack =================")
    cur_cmd = os.getcwd()
    os.chdir('..')
    ht = ym.DevicesInfo(name_config_yaml, dbg=logging.INFO)
    ym.YamlToHeat(ht, dbg=logging.INFO)
    os.chdir(curdir)


if __name__ == "__main__":
    logger = AkarLogging(logging.INFO, "gen_heat").get_color_logger()

    cmd_args = cmdArgsParser()
    stack_name = cmd_args.name
    curdir = str(os.getcwd()).split('/')[-1]
    if os.path.exists(f'{os.getcwd()}/oslabs.yml'):
        os.remove(f'{os.getcwd()}/oslabs.yml')
    with open(f'{os.getcwd()}/oslabs.yml', mode="w") as fn:
        fn.write(f'---\nwan: wan0\nlab: {stack_name}')
    res = re.match(r'^(.*)v\d+$', curdir)
    if not cmd_args.skip:
        gen_heat_os(f'{res.group(1)}.yaml')
    stack_template = f'st_{res.group(1)}.yaml'
    # print(f'Stack template: {stack_template} Stack Name: {stack_name}')
    cmd_run = f'ansible-playbook ans_lab_main.yml  -e stack_template={stack_template} -e stack_name={stack_name}'
    if cmd_args.skip:
        cmd_run += f' -e stack_skip=true'
    if cmd_args.list:
        cmd_run += f' -l {cmd_args.list}'
    if cmd_args.dell:
        cmd_run_del = f'{cmd_run} -t init_del'
        run_ansible(cmd_run_del)
        time.sleep(2)
    if cmd_args.tags:
        cmd_run += f' -t {cmd_args.tags}'
    else:
        cmd_run += f' --skip-tags init_del'
    logger.info(f'{cmd_run}')
    run_ansible(cmd_run)
