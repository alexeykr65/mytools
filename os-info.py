#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Run wireshark for vm interfaces in openstack via ssh
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs

import argparse
import logging
import sys
import telnetlib
import akarlibs.openstack as ops
from termcolor import colored
from akarlibs.akarlogging import AkarLogging
from subprocess import Popen, PIPE
from rich.console import Console
from rich.table import Table
from rich.progress import track


description = "os-info: View information abount instances in openstack"
epilog = "Alexey Karpov "


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-n", "--name", help="Name vm in openstack", dest="name", action="store", default="")
    parser.add_argument("-hst", "--host", help="Name host in openstack", dest="host", action="store", default="osc")
    parser.add_argument("-x", "--xml", help="Dump xml instance", dest="xml", action="store_true")
    parser.add_argument("-v", "--vnc", help="Run vnc instance", dest="vnc", action="store_true")
    parser.add_argument("-s", "--serial", help="Run telnet serial instance", dest="serial", action="store_true")
    return parser.parse_args()


def main():
    lab_host = cmd_args.name
    logger.info(f"host: {lab_host}")
    ops_server = ops.Servers(name=lab_host, dbg=logging.WARNING)
    # console.log(ops_server)
    for srv in ops_server.servers:
        console.rule(characters="=", style='white')
        console.print(
            f'[orange1 bold]{srv.name:17s}[/] [green1]{srv.instance:19s}[/] : [blue1]{srv.image_name:15s}[/] : [white]{srv.host:5s}[/] : [white2]{srv.time_created}'
        )
        # console.rule(
        #     title=f'[magenta]{srv.name}([bold]{srv.instance}) : [bold green]{srv.image_name} [white]: {srv.host} : {srv.time_created}',
        #     characters="*",
        #     style='white',
        # )
        console.rule(characters="=", style='white')

        console.print(
            f'[green]Flavor: [red][i]{srv.flavor}[/i]([magenta]vcpu:{srv.kvminfo.vm_vcpus},mem:{srv.kvminfo.vm_memory},disk:{srv.kvminfo.vm_disk})',
            f'[green]VNC Port: {srv.kvminfo.vm_vnc_port} Serial Port: {srv.kvminfo.vm_serial_port}',
        )

        table = Table("Network", "ipv4/ipv6", "IntName", "mac", "NameTap", "NameQbr", "MTU", "Model")
        ii = 0
        for nt in track(srv.nets, description="Get all interfaces.."):
            intr = srv.kvminfo.interfaces[f'net{ii}']
            ipv6_addr = ""
            ipv4_addr = ""
            if 'ipv6' in srv.nets[nt]:
                ipv6_addr = srv.nets[nt]["ipv6"]
            if 'ipv4' in srv.nets[nt]:
                ipv4_addr = srv.nets[nt]["ipv4"]
            table.add_row(
                f'[blue]{nt}',
                f'[magenta1]{ipv4_addr} / {ipv6_addr}',
                f'[magenta]{intr.name}',
                f'[cyan]{intr.mac_addr}',
                f'[bright_green]{intr.dev}',
                f'[yellow]{intr.bridge}',
                f'{intr.mtu}',
                f'{intr.model}',
            )
            ii += 1
        console.print(table)
        if cmd_args.xml:
            print(f'{srv.kvminfo.xml}')
        if cmd_args.vnc:
            p_ssh = Popen(['/Applications/VNC Viewer.app/Contents/MacOS/vncviewer', f'{srv.host}:{str(srv.kvminfo.vm_vnc_port)}'])
        if cmd_args.serial:
            tn = telnetlib.Telnet(srv.host, srv.kvminfo.vm_serial_port)
            tn.interact()
        logger.info(f"{srv.image_name}")
        logger.info(f"{srv.name} : {srv.instance}")


if __name__ == "__main__":
    logger = AkarLogging(logging.WARNING, "OS Info").get_color_logger()
    cmd_args = cmdArgsParser()
    console = Console()
    main()
