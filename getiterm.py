#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Run ssh to connect to Openstack labs
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

description = "openstack-iterm: Run iterm to connect to openstack labs"
epilog = "Alexey Karpov "


eveng_host = "lab.lanhome.org"
iterm_profile = "Main"

apple_script_template = '''
tell application "iTerm2"
    activate
    set new_window to (create window with profile "{{ prof }}")
    delay 1
    tell new_window
        delay 2
{% for rt in routers %}
        create tab with profile "{{ prof }}"
        tell current session
            delay 1
            write text "ssh -o 'UserKnownHostsFile=/dev/null' -o 'StrictHostKeyChecking=no' -l {{ routers[rt]['user'] }} {{ routers[rt]['ipv4'] }}"
            set name to "{{ rt | upper }}"
            delay 1
        end tell
{% endfor %}
    end tell
end tell
'''

apple_script_template_current_window = '''
tell application "iTerm2"
    activate
    delay 1
    tell current window
        delay 2
{% for rt in routers %}
        create tab with profile "{{ prof }}"
        tell current session
            delay 1
            write text "ssh -o 'UserKnownHostsFile=/dev/null' -o 'StrictHostKeyChecking=no' -l {{ routers[rt]['user'] }} {{ routers[rt]['ipv4'] }}"
            set name to "{{ rt | upper }}"
            delay 1
        end tell
{% endfor %}
    end tell
end tell
'''


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('-o', '--openstack', help='Openstack stack name', action="store", dest="name", default="", required=True)
    parser.add_argument('-n', '--netid', help='Openstack stack network name', action="store", dest="netid", default="wan0")
    parser.add_argument('-i', '--iterm', help='Run ssh in iterm', action="store_true")
    parser.add_argument('-a', '--ansible', help='Create hosts.yml file', action="store_true")
    parser.add_argument('-w', '--window', help='Create new window for ssh', action="store_true")
    parser.add_argument('--list', help='Generate dynamic ansible inventory', action="store_true")
    return parser.parse_args()


def run_applescript(lab_routers):
    logger.info("Create and run applescript ... ")
    if cmd_args.window:
        env = Environment(loader=BaseLoader).from_string(apple_script_template)
    else:
        env = Environment(loader=BaseLoader).from_string(apple_script_template_current_window)
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.rstrip_blocks = True
    apple_script = env.render(routers=lab_routers, eveng_host=eveng_host, prof=iterm_profile)
    logger.debug(apple_script)

    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(apple_script)


def get_routers_from_openstack():
    logger.info("Get list servers with ip addresses ... ")
    ops_server = ops.Servers(name=cmd_args.name, dbg=logging.INFO)
    if cmd_args.ansible:
        ops_server.create_ansible_hosts(cmd_args.netid)
    if cmd_args.list:
        ops_server.create_dynamic_inventory(cmd_args.netid)
    # logger.info(srv_ips)
    return ops_server.get_srv_nets(cmd_args.netid)


def main():
    lab_routers = ""
    if cmd_args.name != '':
        lab_routers = get_routers_from_openstack()
    if lab_routers:
        logger.debug(f'{lab_routers}')
        if cmd_args.iterm:
            run_applescript(lab_routers)


if __name__ == '__main__':
    # print(f'Modules path: {sys.path}')
    logger = AkarLogging(logging.INFO, "run_iterm").get_color_logger()
    cmd_args = cmdArgsParser()
    main()
