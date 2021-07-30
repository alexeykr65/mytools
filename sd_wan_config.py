#!/usr/bin/env python3

import akarlibs.viptela as vp
import argparse
from rich.console import Console

description = "SDWAN: Initialize sdwan lab "
epilog = "Alexey Karpov "


def cmdArgsParser():
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("-f", "--config_lab", help="File in format YAML", action="store", dest="config_lab", default="sdwan_config.yaml")
    parser.add_argument("-ic", "--init_cntrl", help="Initialize controllers", action="store_true", dest="init_cntrl")
    parser.add_argument("-iv", "--init_vedges", help="Initialize vedges", action="store_true", dest="init_vedges")
    parser.add_argument("-s", "--serial_file", help="Load serial file", action="store", dest="serial_file", default="")
    parser.add_argument("-t", "--load_templates", help="Initialize templates", action="store_true", dest="load_templates")

    return parser.parse_args()


if __name__ == "__main__":
    cn = Console()
    cmd_args = cmdArgsParser()
    file_config = cmd_args.config_lab
    cn.print(f"Config File: {file_config}")
    viptela = vp.Viptela(file_config)
    if cmd_args.init_cntrl:
        viptela.initialize_controllers()
    if cmd_args.init_vedges:
        viptela.init_auth()
        viptela.push_cert_to_controllers()
        viptela.initialize_vedges()
    if cmd_args.serial_file:
        viptela.init_auth()
        viptela.load_serial_file()
        viptela.push_cert_to_controllers()
    if cmd_args.load_templates:
        viptela.init_auth()
        viptela.import_templates()
