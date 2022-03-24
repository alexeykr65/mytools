#!/usr/bin/env python3


from nornir import InitNornir
from nornir.core.inventory import Inventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from akarlibs.nornir.inventory.ansible import AnsibleInventory
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_command
import json
import pprint
import ipdb
import logging

InventoryPluginRegister.register("LabInventory", AnsibleInventory)
# InventoryPluginRegister.register("AnsibleInventory", AnsibleInventory)

nr = InitNornir(
    runner={
        "plugin": "threaded",
        "options": {
            "num_workers": 100,
        },
    },
    inventory={
        'plugin': 'LabInventory',
        'options': {
            'hostsfile': 'hosts.yaml',
        },
    },
)
cisco_hosts = nr.filter(name='R11')
nr.inventory.defaults.username = "root"
nr.inventory.defaults.password = ""
# print(cisco_hosts.inventory.hosts)
# results = cisco_hosts.run(napalm_get, getters=['get_interfaces_ip'], severity_level=logging.DEBUG, ssh_private_key_file="~/.ssh/id_rsa")
send_command_results = cisco_hosts.run(task=send_command, command="show ip interface brief")
print_result(send_command_results)

print(nr.config.inventory.plugin)
print(nr.inventory.hosts)
print(nr.inventory.groups)
ipdb.set_trace()
# pprint.pprint(len(nr.inventory.hosts))
# print(json.dumps(nr.inventory.hosts, indent=4))
