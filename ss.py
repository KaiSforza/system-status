#!/usr/bin/env python

# import argparse

from __future__ import division

import subprocess
import socket
import re
import collections


df = subprocess.check_output(['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs'],
                             universal_newlines=True)
dfi = subprocess.check_output(['df', '-i', '-x', 'tmpfs', '-x', 'devtmpfs'],
                              universal_newlines=True)

sss = subprocess.check_output(['ss', '-s'], universal_newlines=True)

hostname = socket.gethostname()


def parse_ip_output():
    ip = subprocess.check_output(['/sbin/ip', 'a'], universal_newlines=True)
    rawips = re.findall('inet[ 6].+[0-9]$', ip, flags=re.M)
    ips = [str.split(x) for x in rawips]
    iplist = []
    for i in ips:
        iplist.append('{:8}{}'.format(i[-1], i[1].split('/')[0]))
    return iplist


def format_w():
    w = subprocess.check_output(['w'], universal_newlines=True)
    lin = w.splitlines()
    lis = lin[2:]
    lis.insert(0, lin[0])
    return lis


def parse_mem():
    class bcolors:
        GREEN = '\033[1;32m'
        YELLOW = '\033[1;33m'
        RED = '\033[1;31m'
        S = '\033[0m'

    mem = subprocess.check_output(['free', '-m'], universal_newlines=True)
    mem = mem.splitlines()
    totals = mem[1].split()
    b_c = mem[2].split()
    maxmem = float(totals[1])
    usedmem = float(b_c[2])
    mempercent = usedmem / maxmem
    if mempercent > 0.7:
        return '{}{} MB{}/{} MB'.format(bcolors.RED,
                                        usedmem,
                                        bcolors.S,
                                        maxmem)
    elif mempercent > 0.5:
        return '{}{} MB{}/{} MB'.format(bcolors.YELLOW,
                                        usedmem,
                                        bcolors.S,
                                        maxmem)
    else:
        return '{}{} MB{}/{} MB'.format(bcolors.GREEN,
                                        usedmem,
                                        bcolors.S,
                                        maxmem)


def regex_ns(a):
    a = a.split()
    r = list()
    local_port = re.match(r'.+:(.*)', a[4])
    r.append(local_port.groups()[0])
    remote_port = re.match(r'.+:(.*)', a[5])
    r.append(remote_port.groups()[0])
    return r


def parse_netstat():
    ssutn = subprocess.check_output(['ss', '-utn'], universal_newlines=True)
    ss = re.findall(r'tcp.*', ssutn, flags=re.M)
    ss = [regex_ns(x) for x in ss]
    _nin = [x[0] for x in ss]
    _nout = [x[1] for x in ss]

    return map(collections.Counter, [_nin, _nout])


def format_ns(n=3):
    a = parse_netstat()
    out = a[0].most_common(n)
    nin = a[1].most_common(n)
    outlist = ['      {:7<} {:8>}'.format(y, x) for x, y in out]
    ninlist = ['      {:7<} {:8>}'.format(y, x) for x, y in nin]
    return outlist, ninlist


def format_ss_proc_line(a):
    recv = a[1]
    send = a[2]
    port = a[3]
    proc = a[5]

    # proc.lstrip('users:((')
    proc = re.sub(r'^users:\(\(', '', proc)
    proc = re.sub(r'\)\)$', '', proc)
    try:
        proclist = proc.split('),(')
        if len(proclist) > 2:
            procstring = '{}, {} (and {} more)'.format(proclist[0],
                                                       proclist[1],
                                                       len(proclist) - 2)
        elif len(proclist) == 2:
            procstring = '{}, {}'.format(proclist[0],
                                         proclist[1])
        else:
            procstring = '{}'.format(proclist[0])
    except:
        procstring = ''

    return '{:21}{:>}{:>7} {}'.format(port, recv, send, procstring)


def format_ssntlp(m=2):
    ssntlp = subprocess.check_output(['ss', '-plnt'], universal_newlines=True)
    ssntlp = re.sub('"', '', ssntlp)
    ssntlp = re.findall(r'^LISTEN.*', ssntlp, flags=re.M)
    return [format_ss_proc_line(x.split()) for x in ssntlp]


ns = format_ns()

p = """{sep}
{host}
{sep}
{ipaddrs}
{sep}
{wout}
{sep}
{fs}
{inodes}{sep}
Memory Used: {memory}
{sep}
Connection Summary:
{sssum}
{sep}
Connection Concentration:
IN (top 3)::
{nsin}
OUT (top 3)::
{nsout}
{sep}
Listening       Recv-Q Send-Q Processes
{ssproc}
{sep}""".format(sep=('-' * 75),
                host=hostname,
                ipaddrs='\n'.join(parse_ip_output()),
                wout='\n'.join(format_w()),
                fs=df,
                inodes=dfi,
                memory=parse_mem(),
                sssum='\n'.join(sss.splitlines()[:2]),
                nsin='\n'.join(ns[0]),
                nsout='\n'.join(ns[1]),
                ssproc='\n'.join(format_ssntlp()))

print(p)
