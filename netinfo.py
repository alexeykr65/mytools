#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Configure S-Terra
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs
import argparse
import akarlibs.alexnornir as mynor
import akarlibs.ciscocfg as cfg
import logging
from akarlibs.akarlogging import AkarLogging


def check_argument_parser():
    description_argument_parser = ""
    epilog_argument_parser = ""
    parser = argparse.ArgumentParser(description=description_argument_parser, epilog=epilog_argument_parser)
    parser.add_argument('-p', '--ping', help='Ping hosts', dest="ping", action="store_true")
    parser.add_argument('-io', '--info_ospf', help='Get information from OSPF', dest="info_ospf", action="store_true")
    parser.add_argument('-o', '--ospf', help='OSPF Configure Standart ', dest="ospf", action="store_true")
    parser.add_argument('-g', '--getconf', help='Get running Configuration', dest="getconf", action="store_true")
    parser.add_argument('-l2', '--int_l2', help='Get L2 Interfaces Configuration', dest="int_l2", action="store_true")
    parser.add_argument('-l3', '--int_l3', help='Get L3 Interfaces Configuration', dest="int_l3", action="store_true")
    parser.add_argument('-vl', '--vlan', help='Get Vlan Configuration', dest="vlan", action="store_true")
    parser.add_argument('-cdp', '--cdp', help='Get CDP Information', dest="cdp", action="store_true")
    parser.add_argument('-c', '--cmd', help='Run command on Routers', dest="cmd", default='')
    parser.add_argument('-fr', '--froles', help='Filter hosts by roles', dest="froles", default='')
    parser.add_argument('-fh', '--fhosts', help='Filter hosts by name', dest="fhosts", default='')
    parser.add_argument('-fo', '--fospf', help='Filter for output information in ospf', dest="fospf", default='')
    parser.add_argument('-r', '--regex', help='Regex output filter', dest="regex", default='.*')
    return parser.parse_args()


def main():
    ag = check_argument_parser()
    # nr = mynor.AlexNornir(data_file="src_cfg/dmvpn_data.yaml", filter_hosts=ag.fhosts, filter_roles=ag.froles, output_dir="output_cfg")
    ## nr = mynor.AlexNornir(data_file="src_cfg/dmvpn_data.yaml")
    regex_filter = ag.regex
    # if ag.ping:
    #     # nr.ping()
    #     pass
    # elif ag.cmd:
    #     if ag.regex:
    #         #nr.run_cmds(ag.cmd, regex_filter)
    #         pass
    # elif ag.getconf:
    #     # nr.get_config()
    #     pass
    # elif ag.cdp:
    #     print("Get CDP Information")
    #     # nr.get_cdp("conf_cdp")
    #     print("Analyze CDP Information")
    #     lst_devices = cfg.ListDevices("./configs/*.txt", path_to_cdp="conf_cdp_05102019/*.txt")
    #     lst_devices.create_csv_cdp("out_cdp")
    #     lst_devices.create_csv_cdp_all("output")
    if ag.int_l3:
        logger.info('Get information about L3 interfaces')
        lst_devices = cfg.ListDevices(dir_cfg, flag_l3_int=True, dbg=dbg)
        lst_devices.create_csv_l3_int(out_dir=dir_l3)
        lst_devices.create_csv_l3_int_all(out_dir=dir_reports)
        lst_devices.create_csv_l3_int_network(out_dir=dir_reports)
    if ag.int_l2:
        logger.info('Get information about L2 interfaces')
        lst_devices = cfg.ListDevices(dir_cfg, flag_l3_int=False, flag_l2_int=True, dbg=dbg)
        lst_devices.create_csv_l2_int(out_dir=dir_l2)
        lst_devices.create_csv_l2_int_all(out_dir=dir_reports)
    if ag.vlan:
        logger.info('Get information about VLANs')
        lst_devices = cfg.ListDevices(dir_cfg, flag_l3_int=False, flag_vlans=True, flag_l2_int=False, dbg=dbg)
        lst_devices.create_csv_vlans(dir_vlans)
        lst_devices.create_csv_vlans_all(dir_reports)
    # elif ag.ospf:
    #     if ag.fospf:
    #         nr.ospf_filter = ag.fospf
    #     nr.ospf_info()


if __name__ == '__main__':
    dbg = logging.INFO
    logger = AkarLogging(dbg, "netinfo").get_color_logger()
    logger.info("Begin netinfo ")
    dbg = logging.INFO
    dir_reports = 'output'
    dir_l2 = f'{dir_reports}/l2-int'
    dir_l3 = f'{dir_reports}/l3-int'
    dir_vlans = f'{dir_reports}/vlans'
    dir_cfg = "./configs/*.txt"
    main()
