#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Run wireshark for vm interfaces in openstack via ssh
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

from subprocess import Popen, PIPE
import argparse
import logging
import sys
import akarlibs.openstack as ops
from akarlibs.akarlogging import AkarLogging
import akarlibs.kvmlibvirt as kv

description = "sniff-lab: Run wireshark for vm interfaces in openstack via ssh"
epilog = "Alexey Karpov "


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-n", "--name", help="Name host in openstack", dest="name", action="store", required=True)
    parser.add_argument("-i", "--interface", help="Number of inteface", dest="interface", action="store", required=True, type=int)
    return parser.parse_args()


def main():
    lab_host = cmd_args.name
    host_intrf = f"net{int(cmd_args.interface)-1}"
    logger.info(f"host: {lab_host} interface: {host_intrf}")
    ops_server = ops.Servers(name=lab_host, dbg=logging.WARNING)
    if len(ops_server.servers) > 1:
        logging.error("Exist few elements but need one")
        exit(1)
    else:
        srv = ops_server.servers[0]
    logger.info(f"{srv.name} : {srv.instance}")
    logger.info(f"Interface: {srv.kvminfo.interfaces[host_intrf].dev}")
    os_name = f"root@{srv.host}"
    logger.info(f'os_name: {os_name}')
    p_ssh = Popen(["ssh", os_name, "tcpdump", "-U", "-i", str(srv.kvminfo.interfaces[host_intrf].dev), "-s", "0", "-w", "-"], stdout=PIPE)
    p_wireshark = Popen(["wireshark", "-k", "-i", "-"], stdin=p_ssh.stdout)


if __name__ == "__main__":
    logger = AkarLogging(logging.INFO, "os_inventory").get_color_logger()
    cmd_args = cmdArgsParser()
    main()
