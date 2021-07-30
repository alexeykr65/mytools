#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Run telnet from EVE_NG
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs
import yaml
import re
import os
import json
import argparse
import graphviz as gv
import logging
from netaddr import IPNetwork, IPAddress
from jinja2 import Template, Environment, FileSystemLoader
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


def ipaddr(input_str, net_cfg):
    ip_net = IPNetwork(input_str)
    ret = ""
    if net_cfg == "address":
        ret = ip_net.ip
    elif net_cfg == "netmask":
        ret = ip_net.netmask
    elif net_cfg == "hostmask":
        ret = ip_net.hostmask
    elif net_cfg == "network":
        ret = ip_net.network
    return ret


def generate_stack_template(input_file, output_file, routers, nets, net_mgmt, vm_conf, srv):
    file_loader = FileSystemLoader(f"{src_dir}/templates")
    env = Environment(loader=file_loader)
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.rstrip_blocks = True
    # env.filters['ipaddr'] = self.ipaddr
    template = env.get_template(input_file)
    output = template.render(routers=routers, nets=nets, srv=srv, net_mgmt=net_mgmt, vm=vm_conf, avail_zone=cmd_args.zone)
    with open(output_file, mode="w") as file_:
        file_.write(output)


def draw_net_ipv4_sorted(grln):
    # doublecircle
    f = gv.Graph("Network Map", engine="neato")
    # format='png',  filename='fsm.png'
    f.attr(fontsize="30", fillcolor="red")
    f.attr("node", shape="doublecircle", len="3.0", style="filled", color="lightgrey", size="20", fixedsize="true", fontsize="10", overlap="false")
    # , fillcolor='red'
    f.attr(labelfontsize="5")
    for ii in grln:
        if len(grln[ii]["routers"]) <= 2:
            f.edge(grln[ii]["routers"][0], grln[ii]["routers"][1], label=grln[ii]["label"], fontsize="10", len="2", width="2.5")
        else:
            for rt in grln[ii]["routers"]:
                f.node(grln[ii]["label"], shape="diamond", width="2.0", fillcolor="yellow", style="rounded,filled")
                f.edge(rt, grln[ii]["label"], len="1.5", width="2.5")
        # f.edge(ii, l, label=jj.ipv4_net_pref, len='10.0', fontsize='10')
    # print(f.source)
    # f.render('aaaa.gv')
    # f.view(filename=out_draw)
    # f.save(filename=out_draw)
    f.render(filename=out_draw, format='png', cleanup=True)


def draw_net_ports(grln):
    # doublecircle
    f = gv.Graph("Network Map", engine="neato")
    print(gr_links)
    # format='png',  filename='fsm.png'
    f.attr(fontsize="30", fillcolor="red")
    f.attr("node", shape="doublecircle", len="3.0", style="filled", color="lightgrey", size="20", fixedsize="true", fontsize="10", overlap="false")
    # , fillcolor='red'
    f.attr(labelfontsize="5")
    for ii in grln:
        # if len(grln[ii]["routers"]) <= 2:
        #     f.edge(grln[ii]["routers"][0], grln[ii]["routers"][1], label=grln[ii]["label"], fontsize="10", len="2", width="2.5")
        # else:
        for rt in grln[ii]["routers"]:
            f.edge(rt, grln[ii]["label"], len="1.5", width="2.5")
            f.node(grln[ii]["label"], shape="oval", width="2.0", style="rounded", fontsize="9")
            # f.node(grln[ii]["label"], shape="plaintext", width="2.0", fillcolor="yellow", style="rounded,filled")
        # f.edge(ii, l, label=jj.ipv4_net_pref, len='10.0', fontsize='10')
    print(f.source)
    # f.render('aaaa.gv')
    print(grln)
    # f.view(filename=out_draw)
    f.save(filename=out_draw)


def main():
    with open(name_config_yaml) as yml:
        conf_yaml = yaml.load(yml, Loader=yaml.FullLoader)
    logger.debug(f"CONFIG_YAML:\n{json.dumps(conf_yaml, indent=2)}")
    rt_lab = {rt: {"links": {"link_" + str(lnk): "" for lnk in conf_yaml["routers"][rt]["links"]}} for rt in conf_yaml["routers"]}
    rt_nets = {("link_" + str(nt)): conf_yaml["networks"][nt] for nt in conf_yaml["networks"]}
    gr_links = {key: {"routers": list(), "label": rt_nets[key]["ipv4"]} for key in rt_nets}
    vm_conf = {key: val for key, val in conf_yaml["vm"].items()}
    if conf_yaml["servers"]:
        srv_lab = {rt: {"links": {"link_" + str(lnk): "" for lnk in conf_yaml["servers"][rt]["links"]}} for rt in conf_yaml["servers"]}
    else:
        srv_lab = {}
    # srv =
    # logger.info(rt_lab)
    # logger.info(rt_nets)
    # logger.info(vm_conf)
    logger.debug(f"gr_links: {json.dumps(gr_links, indent=2)}")
    logger.debug(f"srv_lab: {json.dumps(srv_lab, indent=2)}")
    for rt_key, rt in rt_lab.items():
        index_router = 100 + int(re.match("^[^\d]*(\d*)", rt_key).group(1))
        rt_lab[rt_key]["type"] = conf_yaml["routers"][rt_key]["type"]
        for ln_key, ln in rt_lab[rt_key]["links"].items():
            # print(f"{ rt_nets[ln_key]['ipv4']}")
            gr_links[ln_key]["routers"].append(rt_key)
            ip = str(IPNetwork(rt_nets[ln_key]["ipv4"])[index_router])
            # print(ip)
            rt_lab[rt_key]["links"][ln_key] = dict()
            rt_lab[rt_key]["links"][ln_key]["ipv4"] = ip
    for rt_key, rt in srv_lab.items():
        index_router = 180 + int(re.match("^[^\d]*(\d*)", rt_key).group(1))
        for ln_key, ln in srv_lab[rt_key]["links"].items():
            # print(f"{ rt_nets[ln_key]['ipv4']}")
            gr_links[ln_key]["routers"].append(rt_key)
            ip = str(IPNetwork(rt_nets[ln_key]["ipv4"])[index_router])
            # print(ip)
            srv_lab[rt_key]["links"][ln_key] = dict()
            srv_lab[rt_key]["links"][ln_key]["ipv4"] = ip

    logger.info("Generate stack template")
    logger.debug(f"rt_lab: {json.dumps(rt_lab, indent=2)}")
    if cmd_args.generate:
        generate_stack_template(heat_template_file, out_stack, rt_lab, rt_nets, cmd_args.netid, vm_conf, srv_lab)
    # print(gr_links)
    logger.debug(f"srv_lab: {json.dumps(srv_lab, indent=2)}")
    logger.debug(f"gr_links: {json.dumps(gr_links, indent=2)}")
    logger.debug(f"rt_lab: {json.dumps(rt_lab, indent=2)}")
    if cmd_args.draw:
        draw_net_ipv4_sorted(gr_links)


if __name__ == "__main__":
    logger = AkarLogging(logging.DEBUG, "gen_heat").get_color_logger()
    cmd_args = cmdArgsParser()
    src_dir = os.path.dirname(os.path.realpath(__file__))
    logger.info(f"Source current dir: {__file__}")
    logger.info(f"Source real dir: {os.path.dirname(os.path.realpath(__file__))}")
    gr_links = dict()
    heat_template_file = "template_stack.j2"
    if not os.path.exists("net-stack"):
        os.makedirs("net-stack")
    name_config_yaml = cmd_args.lab
    out_stack = f"{str(cmd_args.output)}/st_{os.path.basename(name_config_yaml)}"
    out_draw = f"{str(cmd_args.output)}/st_{os.path.splitext(os.path.basename(name_config_yaml))[0]}"
    logger.info(f"lab config file: {name_config_yaml}")
    logger.info(f"output heat file: {out_stack}")
    main()
