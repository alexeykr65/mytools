#!/usr/bin/env python3

# import asyncio
# import telnetlib3

# host, port, username, password, command = '192.168.180.11', 10018, 'root', 'cisco', 'show interface summary'


# @asyncio.coroutine
# def shell(reader, writer):

#     while True:

#         outp = yield from reader.read(1024)
#         writer.write(username + '\n')
#         writer.write(password + '\n')
#         writer.write(command + '\n')
#         print(outp)
#         if not outp:
#             break
#         elif 'Number of Interfaces' in outp:
#             break

#     print(outp)


# loop = asyncio.get_event_loop()
# coro = telnetlib3.open_connection(host, port, shell=shell)
# reader, writer = loop.run_until_complete(coro)
# loop.run_until_complete(writer.protocol.waiter_closed)


import telnetlib
import time

HOST = '192.168.180.11'
user = "root"
password = "cisco"
command = "show interface summary"

tn = telnetlib.Telnet(HOST, 10018)
tn.interact()
print(tn.read_all())
tn.close()

# def write_raw_sequence(tn, seq):
#     sock = tn.get_socket()
#     if sock is not None:
#         sock.send(seq)

# write_raw_sequence(tn, telnetlib.IAC + telnetlib.WILL + telnetlib.SGA)

# tn.write(user.encode('ascii') + b"\n")
# tn.write(password.encode('ascii') + b"\n")
# tn.write(command.encode('ascii') + b"\n")
# time.sleep(1)
# data = tn.read_very_eager().decode('ascii')

# print(data)
