#!/usr/bin/env python3.10

import string
from tenacity import retry
from termcolor import colored
from tokenize import String, group

from nornir import InitNornir
from nornir.core.inventory import Inventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
# from nornir_jinja2.plugins.tasks import template_string
from nornir_scrapli.tasks import get_prompt, send_command, send_configs, send_commands

from pathlib import Path
from nornir.core.filter import F

from akarlibs.akarlogging import AkarLogging
from akarlibs.nornir.inventory.mylabs import MyLabInventory
from akarlibs.gentemplates import GenTemplates

import akarlibs.yamltoheat as ym
import akarlibs.openstack as ops
import ipdb
import time
import logging
import argparse
import re
import os
import bpdb

description = "labgen: Create labs in Openstack"
epilog = "Alexey Karpov"


def cmdArgsParser() -> argparse.Namespace:
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-n", "--name", help="Stack name in openstack", dest="name", action="store", required=True)
    parser.add_argument("-s", "--skip", help="Skip create stack", dest="skip", action="store_true")
    parser.add_argument("-a", "--all", help="All configuration Nornir tasks", dest="all", action="store_true")
    parser.add_argument("-d", "--dl", help="Del del_conf commands", dest="dl", action="store_true")
    parser.add_argument("-i", "--init", help="Push init_conf commands", dest="init", action="store_true")
    parser.add_argument("-g", "--gen", help="Generate heat template for Openstack", dest="gen", action="store_true")
    parser.add_argument("-w", "--wan", help="Wan interface", dest="wan", action="store", default="wan0")
    return parser.parse_args()


def deploy_del_conf(task) -> None:
    # print(f'Host: {task.host}\n{task.host.data["init_conf"]}')
    if 'del_conf' in task.host.data:
        task.run(task=send_configs, configs=task.host.data['del_conf'].split('\n'))


def deploy_init_conf(task) -> None:
    # print(f'Host: {task.host}\n{task.host.data["init_conf"]}')
    if 'init_conf' in task.host.data:
        task.run(task=send_configs, configs=task.host.data['init_conf'].split('\n'))


def deploy_interfaces(task) -> None:
    """
        Deploy interfaces 
    """
    # print(f'Host: {task.host}\n{task.host.data["init_conf"]}')
    template_file = f'interfaces_{task.host.platform}.j2'
    if 'interfaces' in task.host.data:
        gtmp = GenTemplates(template_file=f'{TEMPLATES_DIR}/{template_file}', template_data=task.host.data['interfaces'])
        r = gtmp.generate_template()
        task.run(task=send_configs, configs=r.split('\n'))


def tasks_nornir() -> None:
    cisco_hosts = nr.filter(F(groups__contains='cisco'))
    # bpdb.set_trace()
    if args.dl:
        print_title_host(f'Deploy Del_Conf', flag_center=True)
        result = cisco_hosts.run(task=deploy_del_conf)
        print_result(result)
        time.sleep(1)

    if args.all:
        # ipdb.set_trace()
        print_title_host(f'Deploy Interfaces', flag_center=True)
        result = cisco_hosts.run(task=deploy_interfaces)
        print_result(result)

    if args.init or args.all:
        print_title_host(f'Deploy Init_Conf', flag_center=True)
        result = cisco_hosts.run(task=deploy_init_conf)
        print_result(result)


def print_title_host(title_txt, flag_center=False) -> None:
    print(colored("*" * 83, 'yellow', attrs=['bold']))
    ln = len(title_txt)
    lf = int((80 - ln) / 2)
    rf = int(80 - ln - lf)
    if flag_center:
        print("*" * lf, colored(f' {title_txt}', 'magenta', attrs=['bold', 'underline']), "*" * rf)
    else:
        print(colored(f' {title_txt}', 'magenta', attrs=['bold']))


def print_title_result(title_txt) -> None:
    ln = len(title_txt)
    lf = int((80 - ln) / 2)
    rf = int(80 - lf - ln)
    print("=" * lf, colored(f' {title_txt}', 'green'), "=" * rf)


def print_body_result(body_txt, bg='') -> None:
    # if re.search(regex, body_txt):
    if bg:
        print(colored(body_txt, 'white', bg))
    else:
        print(colored(body_txt, 'white'))


def create_stack(tname, tfile) -> None:
    cur_dir = Path.cwd()
    p_template_file = Path(cur_dir.parent, 'net-stack', tfile)
    if p_template_file.exists():
        logger.info(f'Template: {p_template_file}')
    else:
        logger.error(f'File not exist: {p_template_file}')
        exit(1)
    ops_srvs = ops.Stack(name=tname, template_file=str(p_template_file), dbg=logging.INFO)
    ops_srvs.create_stack()


def check_stack_online(tname) -> None:
    ops_srvs = ops.Servers(name=tname, dbg=logging.INFO)
    ops_srvs.check_hosts_online()


def gen_heat_os(name_config_yaml) -> None:
    logger.info("================ Run gen-heat-openstack =================")
    os.chdir(cur_dir.parent)
    ht = ym.DevicesInfo(name_config_yaml, dbg=logging.INFO)
    ym.YamlToHeat(ht, dbg=logging.INFO)
    os.chdir(cur_dir)


if __name__ == "__main__":
    TEMPLATES_DIR = "/Users/alex/Dropbox/automation/net-labsv2/playbooks/templates"
    logger = AkarLogging(logging.INFO, "Openstack Labs").get_color_logger()
    InventoryPluginRegister.register("LabInventory", MyLabInventory)

    args = cmdArgsParser()
    stack_name = args.name
    stack_wan = args.wan or "wan0"
    cur_dir = Path.cwd()
    cur_name_dir = str(cur_dir.name)
    cur_name_base = (re.match(r'^(.*)v\d+$', cur_name_dir)).group(1)
    stack_template = f'st_{cur_name_base}.yaml'
    # print(f'{cur_name_base} = {stack_template}')
    if not args.skip:
        gen_heat_os(f'{cur_name_base}.yaml')
        create_stack(stack_name, stack_template)
        check_stack_online(stack_name)
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 100,
            },
        },
        inventory={
            'plugin': 'LabInventory',
            'options': {
                'wan': stack_wan,
                'lab_name': stack_name,
            },
        },
    )
    tasks_nornir()
