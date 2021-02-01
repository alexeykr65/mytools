#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Connect ot lab in openstack
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

from subprocess import Popen, PIPE
from jinja2 import Template, Environment, BaseLoader
import argparse
import logging
import coloredlogs
import re
import os
import sys
import akarlibs.openstack as ops
from akarlibs.akarlogging import AkarLogging
from collections import OrderedDict

description = "openstack-terminal: Run Terminal to connect to openstack LABs"
epilog = "Alexey Karpov "


eveng_host = "lab.lanhome.org"
iterm_profile = "prof_telnet"

apple_script_template = '''
tell application "Terminal"
    if not (exists window 1) then reopen
        activate
{% for rt in routers %}
    do script  "echo \\"\\\\033]0;{{ rt }}\\\\007\\"; ssh -o 'UserKnownHostsFile=/dev/null' -o 'StrictHostKeyChecking=no' -l {{ routers[rt]['user'] }} {{ routers[rt]['ipv4'] }}" in window 1
    tell application "System Events" to keystroke "t" using command down            
    delay 1
{% endfor %}
    tell application "System Events" to keystroke "w" using command down
end tell
'''


def run_applescript(lab_routers):
    logger.info("Create and run applescript ... ")
    env = Environment(loader=BaseLoader).from_string(apple_script_template)
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.rstrip_blocks = True
    apple_script = env.render(routers=lab_routers, eveng_host=eveng_host, prof=iterm_profile)
    logger.info(apple_script)

    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(apple_script)


def get_routers_from_openstack():
    logger.info("Get list servers with ip addresses ... ")
    ops_server = ops.Servers(name=lab_name, dbg=logging.INFO)
    # logger.info(srv_ips)
    return ops_server.get_srv_nets(wan_name)


def main():
    lab_routers = ""
    lab_routers = get_routers_from_openstack()
    if lab_routers:
        logger.debug(f'{lab_routers}')
        run_applescript(lab_routers)


if __name__ == '__main__':
    # print(f'Modules path: {sys.path}')
    wan_name = "wan0"
    lab_name = "labv10"
    logger = AkarLogging(logging.INFO, "run_iterm").get_color_logger()
    # cmd_args = cmdArgsParser()
    if len(sys.argv) > 2:
        lab_name = sys.argv[2]
        wan_name = sys.argv[1]
    elif len(sys.argv) == 2:
        lab_name = sys.argv[1]
    logger.info(f'lab: {lab_name} wan: {wan_name}')
    # print(f'lab: {lab_name} wan: {wan_name}')
    main()
