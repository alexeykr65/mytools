#!/bin/bash

ssh root@$1 tcpdump -U -i $2 -s 0 -w - | wireshark -k -i -
