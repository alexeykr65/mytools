#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MyTools https://github.com/alexeykr65
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

import os
import argparse
import logging
import akarlibs.yamltoheat as ym
from akarlibs.akarlogging import AkarLogging

description = "openstack: Create heat file from yaml "
epilog = "Alexey Karpov "


def cmdArgsParser():
    logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-l", "--lab", help="File lab in format YAML", action="store", dest="lab", default="", required=True)
    parser.add_argument("-n", "--netid", help="Openstack stack MGMT network name", action="store", dest="netid", default="wan0")
    parser.add_argument("-z", "--zone", help="Openstack stack Availability zone", action="store", dest="zone", default="nova:osc")
    parser.add_argument("-o", "--output", help="Output dir for stack files", action="store", dest="output", default="net-stack")
    parser.add_argument("-d", "--draw", help="Draw map", dest="draw", action="store_true")
    parser.add_argument("-g", "--generate", help="Generate heat stack file", dest="generate", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    logger = AkarLogging(logging.INFO, "gen_heat").get_color_logger()
    logger.info("================ Run gen-heatv3 =================")
    cmd_args = cmdArgsParser()
    name_config_yaml = cmd_args.lab
    logger.info(f'File of lab: {name_config_yaml}')
    ht = ym.DevicesInfo(name_config_yaml, dbg=logging.INFO)
    ym.YamlToHeat(ht, dbg=logging.INFO)
    # print(str(ht))
