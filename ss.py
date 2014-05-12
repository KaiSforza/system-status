#!/usr/bin/env python

# import argparse

from __future__ import division

try:
    from subprocess import check_output

    def output(*popenargs, **kwargs):
        return check_output(*popenargs, **kwargs)

except:
    # Python 2.6 also does not have subprocess.check_output, so we're having to
    # reinvent the wheel on this one, too. Code used from the Python 2.7 module
    # once again.
    from subprocess import Popen, PIPE, CalledProcessError

    def output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError(
                'stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output

import socket
import re

try:
    from collections import Counter
except:
    # Python 2.6 does not have the collections.Counter class. This is copied
    # from the Python 2.7 collections module.
    from operator import itemgetter as _itemgetter
    import heapq as _heapq
    from itertools import (
        repeat as _repeat, chain as _chain, starmap as _starmap)

    class Counter(dict):
        def __init__(self, iterable=None, **kwds):
            super(Counter, self).__init__()
            self.update(iterable, **kwds)

        def __missing__(self, key):
            return 0

        def most_common(self, n=None):
            if n is None:
                return sorted(
                    self.iteritems(), key=_itemgetter(1), reverse=True)
            return _heapq.nlargest(n, self.iteritems(), key=_itemgetter(1))

        def elements(self):
            return _chain.from_iterable(_starmap(_repeat, self.iteritems()))

        @classmethod
        def fromkeys(cls, iterable, v=None):
            raise NotImplementedError(
                'Counter.fromkeys() is undefined. \
                Use Counter(iterable) instead.')

        def update(self, iterable=None, **kwds):
            if iterable is not None:
                # if isinstance(iterable, Mapping):
                if hasattr(iterable, 'iteritems'):
                    if self:
                        self_get = self.get
                        for elem, count in iterable.iteritems():
                            self[elem] = self_get(elem, 0) + count
                    else:
                        super(Counter, self).update(iterable)
                else:
                    self_get = self.get
                    for elem in iterable:
                        self[elem] = self_get(elem, 0) + 1
            if kwds:
                self.update(kwds)

        def subtract(self, iterable=None, **kwds):
            if iterable is not None:
                self_get = self.get
                if hasattr(iterable, 'iteritems'):
                    for elem, count in iterable.items():
                        self[elem] = self_get(elem, 0) - count
                else:
                    for elem in iterable:
                        self[elem] = self_get(elem, 0) - 1
            if kwds:
                self.subtract(kwds)

        def copy(self):
            return self.__class__(self)

        def __reduce__(self):
            return self.__class__, (dict(self),)

        def __delitem__(self, elem):
            if elem in self:
                super(Counter, self).__delitem__(elem)

        def __repr__(self):
            if not self:
                return '%s()' % self.__class__.__name__
            items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
            return '%s({%s})' % (self.__class__.__name__, items)

        def __add__(self, other):
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                newcount = count + other[elem]
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count > 0:
                    result[elem] = count
            return result

        def __sub__(self, other):
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                newcount = count - other[elem]
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count < 0:
                    result[elem] = 0 - count
            return result

        def __or__(self, other):
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                other_count = other[elem]
                newcount = other_count if count < other_count else count
                if newcount > 0:
                    result[elem] = newcount
            for elem, count in other.items():
                if elem not in self and count > 0:
                    result[elem] = count
            return result

        def __and__(self, other):
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem, count in self.items():
                other_count = other[elem]
                newcount = count if count < other_count else other_count
                if newcount > 0:
                    result[elem] = newcount
            return result


def dfh():
    return output(['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs'],
                  universal_newlines=True).splitlines()


def dfi():
    return output(['df', '-i', '-x', 'tmpfs', '-x', 'devtmpfs'],
                  universal_newlines=True).splitlines()


def sss():
    return output(['ss', '-s'], universal_newlines=True).splitlines()


def parse_ip_output():
    ip = output(['/sbin/ip', 'a'], universal_newlines=True)
    rawips = re.findall('(inet[ 6].+([0-9]|global ))$', ip, flags=re.M)
    ips = [str.split(x[0]) for x in rawips]
    iplist = []
    for i in ips:
        iplist.append('{0:8}{1}'.format(i[-1], i[1].split('/')[0]))
    return iplist


def format_w():
    w = output(['w'], universal_newlines=True)
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

    with open('/proc/meminfo', 'r') as memfile:
        meminfo = memfile.read()

    meminfo = meminfo.splitlines()
    meminfo = [x.split() for x in meminfo]
    memdict = dict((x[0], x[1]) for x in meminfo)

    total = int(memdict['MemTotal:'])
    free = int(memdict['MemFree:'])
    buffers = int(memdict['Buffers:'])
    cache = int(memdict['Cached:'])

    memused = total - free  # total used memory in kb

    memused = memused - (buffers + cache)  # Remove the buffers and cache

    mempercent = memused / total

    totalmb = total / 1024
    memusedmb = memused / 1024

    if mempercent > 0.7:
        return '{0}{1:,.1f} MB{2:,.1f}/{3} MB'.format(bcolors.RED,
                                                      memusedmb,
                                                      bcolors.S,
                                                      totalmb)
    elif mempercent > 0.5:
        return '{0}{1:,.1f} MB{2}/{3:,.1f} MB'.format(bcolors.YELLOW,
                                                      memusedmb,
                                                      bcolors.S,
                                                      totalmb)
    else:
        return '{0}{1:,.1f} MB{2}/{3:,.1f} MB'.format(bcolors.GREEN,
                                                      memusedmb,
                                                      bcolors.S,
                                                      totalmb)


def __regex_ns(a):
    a = a.split()
    ret = list()
    # if len(a) == 5
    local_port = re.match('.+:(.*)', a[4])
    ret.append(local_port.groups()[0])
    remote_port = re.match('.+:(.*)', a[5])
    ret.append(remote_port.groups()[0])
    return ret


def __parse_netstat():
    ssutn = output(['ss', '-utn'], universal_newlines=True)
    ss = re.findall('tcp.*', ssutn, flags=re.M)
    ss = [__regex_ns(x) for x in ss]
    _nin = [x[0] for x in ss]
    _nout = [x[1] for x in ss]

    return Counter(_nin), Counter(_nout)


def format_ns(n=3):
    a = __parse_netstat()
    if n < (len(a[0]) - 1):
        out = a[0].most_common(n)
    else:
        out = a[0].most_common(len(a[0]) - 1)

    if n < (len(a[1]) - 1):
        nin = a[1].most_common(n)
    else:
        nin = a[1].most_common(len(a[1]) - 1)

    outlist = ['      {0:7<} {1:8>}'.format(y, x) for x, y in out]
    ninlist = ['      {0:7<} {1:8>}'.format(y, x) for x, y in nin]
    return outlist, ninlist


def __format_ss_proc_line(a):
    recv = a[1]
    send = a[2]
    port = a[3]
    try:
        proc = a[5]

        proc = re.sub('^users:\(\(', '', proc)
        proc = re.sub('\)\)$', '', proc)
        proclist = proc.split('),(')
        if len(proclist) > 2:
            procstring = '{0}, {1} (and {2} more)'.format(proclist[0],
                                                          proclist[1],
                                                          len(proclist) - 2)
        elif len(proclist) == 2:
            procstring = '{0}, {1}'.format(proclist[0],
                                           proclist[1])
        else:
            procstring = '{0}'.format(proclist[0])
    except:
        procstring = ''

    return '{0:21}{1:>}{2:>7} {3}'.format(port, recv, send, procstring)


def format_ssntlp(m=2):
    ssntlp = output(['ss', '-plnt'], universal_newlines=True)
    ssntlp = re.sub('"', '', ssntlp)
    ssntlp = re.findall('^LISTEN.*', ssntlp, flags=re.M)
    return [__format_ss_proc_line(x.split()) for x in ssntlp]


if __name__ == '__main__':

    ns = format_ns()

    p = """{sep}
Hostname: {host}
{sep}
{ipaddrs}
{sep}
{wout}
{sep}
{fs}

{inodes}
{sep}
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
                host=socket.gethostname(),
                ipaddrs='\n'.join(parse_ip_output()),
                wout='\n'.join(format_w()),
                fs='\n'.join(dfh()),
                inodes='\n'.join(dfi()),
                memory=parse_mem(),
                sssum='\n'.join(sss()[:2]),
                nsin='\n'.join(ns[0]),
                nsout='\n'.join(ns[1]),
                ssproc='\n'.join(format_ssntlp()))

    print(p)
