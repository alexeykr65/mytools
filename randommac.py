#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Utils
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs
import random
import argparse

description = "Generate MAC address"
epilog = "AKarpov"


def cmdArgsParser():
    # logger.info("Parsing arguments ...")
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--xen', help='XEN type mac address', action="store_true")
    parser.add_argument('--qemu', help='QEMU type mac address', action="store_true")
    return parser.parse_args()


def randomMAC(type="xen"):

    ouis = {'xen': [0x00, 0x16, 0x3E], 'qemu': [0x52, 0x54, 0x00]}
    try:
        oui = ouis[type]
    except KeyError:
        oui = ouis['xen']
    mac = oui + [
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


if __name__ == '__main__':
    cmd_args = cmdArgsParser()
    mac_type = 'xen'
    if cmd_args.qemu:
        mac_type = 'qemu'
    print(randomMAC(mac_type))
