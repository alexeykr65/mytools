#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Dynamic Inventory Ansible from Openstack
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

from subprocess import Popen, PIPE
from jinja2 import Template, Environment, BaseLoader
import yaml
import argparse
import logging
import coloredlogs
import re
import os
import sys
import akarlibs.openstack as ops
from akarlibs.akarlogging import AkarLogging
from collections import OrderedDict

description = "openstack-inventory: Run dynamic inventory from openstack"
epilog = "Alexey Karpov "


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("--list", help="Generate dynamic ansible inventory - all host", action="store_true")
    parser.add_argument("--host", help="Generate dynamic ansible inventory - only one host", action="store")
    return parser.parse_args()


def main():
    logger.info("Get list servers with ip addresses ... ")
    file_config = "oslabs.yml"
    lab_routers = ""
    wan = "wan0"
    lab = "labv10"
    if cmd_args.host:
        print("{}")
        exit(0)

    if os.path.exists(file_config):
        with open(file_config) as file:
            param_list = yaml.load(file, Loader=yaml.FullLoader)
        wan = param_list["wan"]
        lab = param_list["lab"]
        # print(param_list)

    ops_server = ops.Servers(name=lab, dbg=logging.ERROR)
    ops_server.create_dynamic_inventory(wan)
    # if cmd_args.list:
    #     ops_server.create_dynamic_inventory(wan)


if __name__ == "__main__":
    logger = AkarLogging(logging.ERROR, "os_inventory").get_color_logger()
    cmd_args = cmdArgsParser()
    main()
