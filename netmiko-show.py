#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Configure S-Terra
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs
import argparse
import paramiko
import time
import datetime
import re
import os
import sys
import socket
import getpass
import multiprocessing as mp
import netmiko as nm
from functools import partial
from akarlibs.akarlogging import AkarLogging
import akarlibs.openstack as ops
import logging

description_argument_parser = "netmiko-show: Get commands from Cisco , v1.0"
epilog_argument_parser = "Alexey: alexeykr@gmail.ru"

timeout_ssh = 1
log_level = logging.INFO


def check_argument_parser():
    logger.debug("Analyze options ... ")
    parser = argparse.ArgumentParser(description=description_argument_parser, epilog=epilog_argument_parser)
    parser.add_argument("-c", "--command", help="List commands to run", dest="command_run", default="")
    parser.add_argument("-hi", "--hostip", help="IP address of Hosts", dest="host_ip", default="")
    parser.add_argument("-tm", "--sshtimeout", help="SSH timeout in sec", dest="ssh_timeout", default=10)
    parser.add_argument("-l", "--lab", help="Name of labs in openstack", dest="lab", default="")
    parser.add_argument('-n', '--netid', help='Openstack stack network name', action="store", dest="netid", default="wan0")
    parser.add_argument("-ps", "--passwords", help="Set passwords", dest="passwords", default="")
    parser.add_argument("-np", "--numproc", help="Number processes", dest="number_proc", default=0)
    parser.add_argument("-p", "--print", help="Output on screen ", dest="print_onscreen", action="store_true")
    parser.add_argument("-d", "--debug", help="Debug information view(1 - standart, 2 - more verbose)", dest="debug", default=0)
    return parser.parse_args()


def get_date():
    """
    This function returns a tuple of the year, month and day.
    """
    # Get Date
    now = datetime.datetime.now()
    day = str(now.day)
    month = str(now.month)
    year = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)

    if len(day) == 1:
        day = "0" + day
    if len(month) == 1:
        month = "0" + month
    return year, month, day, hour, minute


def write_to_file_result(pre_name_file, namehost, iphost, write_messsage, flagNewFile=True):
    year, month, day, hour, minute = get_date()
    output_dir = "./output/"
    list_names = [pre_name_file, namehost, iphost, day, month, year, hour, minute + ".txt"]
    file_name = "_".join(list_names)
    with open(output_dir + file_name, "w") as id_config_file:
        id_config_file.write(write_messsage)
        id_config_file.write("\n\n")


def get_routers_from_openstack(name_lab, netid_lab):
    logger.debug("Get list servers with ip addresses ... ")
    ops_server = ops.Servers(name=name_lab, dbg=logging.ERROR)
    rt = ops_server.get_srv_nets(netid_lab)
    hosts = list()
    for r in rt:
        if re.search(r'[^R]*(R\d+)', r):
            hosts.append(rt[r]['ipv4'])
    # logger.info(srv_ips)
    return hosts


def connect_to_host(user, passw, list_commands, list_devices):
    proc = os.getpid()
    logger = AkarLogging(log_level, f'process:{proc}').get_color_logger()
    dict_netmiko = dict()
    dict_netmiko["ip"] = list_devices["ip"]
    dict_netmiko["device_type"] = list_devices["device_type"]
    dict_netmiko["timeout"] = list_devices["timeout"]
    dict_netmiko["username"] = user
    dict_netmiko["global_delay_factor"] = list_devices["global_delay_factor"]
    dict_netmiko["password"] = passw
    hostname = "noname"
    logger.debug(f'{dict_netmiko}')
    ret = dict()
    return_message = ""
    try:
        id_ssh = nm.ConnectHandler(**dict_netmiko)
        id_ssh.read_channel()
        find_hostname = id_ssh.find_prompt()
        hostname = re.match("([^#]*)#", find_hostname).group(1).strip()

        return_message += "!**************** {} : {} ****************\n".format(hostname, list_devices["ip"])
        logger.info("Connected to hostname: {} with Ip : {} ... OK".format(hostname, dict_netmiko["ip"]))
        for cmd in list_commands:
            return_message += "====>>>> {:30s} <<<<====\n".format(cmd)
            cmd_return = id_ssh.send_command(cmd)
            return_message += "{}\n".format(cmd_return)
    except Exception as error:
        return_message += "!#host_error:{}:{}\n".format(list_devices["ip"], hostname)
        return_message += "{}\n".format(error)
        if re.search("timed-out", str(error)):
            return return_message
        else:
            return_message += "!#host_error:{}:{}\n".format(list_devices["ip"], hostname)
            return_message += "{}\n".format(error)
    ret[hostname] = return_message
    return ret


if __name__ == "__main__":
    mp.freeze_support()
    start_time = time.time()
    listComm = list()
    device_type = "cisco_ios_ssh"
    username_ssh = "root"
    list_dict_hosts_ssh = []
    list_comm = []
    logger = AkarLogging(log_level, "Main Process").get_color_logger()

    arg = check_argument_parser()
    timeout_ssh = int(arg.ssh_timeout)
    num_proc_ssh = int(arg.number_proc)
    if num_proc_ssh == 0:
        num_proc_ssh = int(mp.cpu_count()) * 2
    logger.info("Maximum of processes ssh allow : {}".format(num_proc_ssh))
    pass_ssh = "cisco"
    hosts = list()
    if arg.host_ip:
        hosts = arg.host_ip.split(",")
    if arg.lab:
        hosts = get_routers_from_openstack(arg.lab, arg.netid)
    #        exit(0)
    if hosts:
        for hh in hosts:
            data = dict()
            data["ip"] = hh.strip()
            data["host"] = hh.strip()
            data["timeout"] = timeout_ssh
            data["device_type"] = device_type
            data["global_delay_factor"] = 2
            list_dict_hosts_ssh.append(data)

    if len(list_dict_hosts_ssh) < 1:
        logger.error("No hosts ip ....")
        exit(1)
    logger.debug(f'{list_dict_hosts_ssh}')
    if arg.command_run:
        list_comm = arg.command_run.split(",")
        logger.info(f"List commands to run: {list_comm}")
    if len(list_comm) == 0:
        list_comm.append("show run")
    # for l in list_dict_hosts_ssh:
    #     result = connect_to_host(username_ssh, pass_ssh, list_comm, l)
    #     print(result)
    # logger.info("Running time: {0:.2f} secunds".format(time.time() - start_time))
    # exit()
    pool = mp.Pool(processes=num_proc_ssh)
    mp_short_connect = partial(connect_to_host, username_ssh, pass_ssh, list_comm)
    result = pool.map(mp_short_connect, list_dict_hosts_ssh)
    pool.close()
    pool.join()
    # print(result)
    res_sorted = dict()
    for res in result:
        for hst in res:
            res_sorted[hst] = res[hst]
    for res in sorted(res_sorted):
        # print(res_sorted[res])
        logger.info(res_sorted[res])
    # print(f"{sorted(res_sorted)}")

    logger.info("Script complete successful!")
    logger.info("Running time: {0:.2f} secunds".format(time.time() - start_time))
    sys.exit(0)
