#!/usr/bin/env python3

import subprocess



SSHKEYGEN = '/usr/bin/ssh-keygen'

def ssh_keygen(*args):
    cmdline = [SSHKEYGEN] + list(args)
    subprocess.check_call(cmdline)


if __name__ == "__main__":
    for i in range (1, 254):
        ssh_keygen('-R', f'192.168.30.{i}')
