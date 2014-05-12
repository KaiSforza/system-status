#!/usr/bin/env python

from __future__ import division
from __future__ import with_statement

import struct
import os
import time
import socket
import re
from datetime import timedelta

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


def __parse_utmp(_utmp):
    _fmt = "hi32s4s32s256sii2i4l"  # 20s"
    #       ||  | |  |   ||| | |       ^ 20 byte string for unused portion
    #       ||  | |  |   ||| | |         This doesnt seem to be used, though.
    #       ||  | |  |   ||| | ^--- 4 byte long for address
    #       ||  | |  |   ||| ^---- 2 32-byte long ints for time stuffs
    #       ||  | |  |   ||^------ Session (32 length int, int32_t)
    #       ||  | |  |   |^------- exit status (unsigned int)
    #       ||  | |  |   ^-------- Hostname (UT_HOSTNAMESIZE chars, def 256)
    #       ||  | |  ^------------ User (UT_NAMESIZE chars, defaults to 32)
    #       ||  | ^--------------- ID (4 length char)
    #       ||  ^----------------- Line (UT_LINESIZE chars, defaults to 32)
    #       |^-------------------- PID (int)
    #       ^--------------------- Type of record (short)
    _fieldnames = ["type", "PID", "Line", "ID", "User", "Hostname",
                   "exit_status", "session", "time_s", "time_ms",
                   "addrv4_1", "addrv4_2", "addrv4_3", "addrv4_4"]
    _fmt_len = struct.calcsize(_fmt)
    _filesize = os.path.getsize(_utmp)

    with open(_utmp, 'rb') as utmpfile:
        utmp = utmpfile.read()

    _entries = _filesize // _fmt_len

    users = []

    for ind in range(_entries):
        _raw_fields = zip(_fieldnames,
                          struct.unpack(_fmt, utmp[
                              (_fmt_len * ind):(_fmt_len * (ind + 1))]))
        user_dict = dict((x, y) for x, y in _raw_fields)
        if user_dict['type'] in {7, }:
            user_dict['addrv4'] = '{0}.{1}.{2}.{3}'.format(
                user_dict['addrv4_1'],
                user_dict['addrv4_2'],
                user_dict['addrv4_3'],
                user_dict['addrv4_4'])
            users.append(user_dict)

    return(users)


def format_w():

    # Set up the load average status
    with open('/proc/loadavg', 'r') as loadfile:
        loadavg = loadfile.read().split()

    # Sets up our uptime readings
    with open('/proc/uptime', 'r') as upfile:
        uptime = upfile.read().split()
    hruptime = str(timedelta(seconds=int(uptime[0].split('.')[0])))

    # Uses utmp to find the logged in users
    utmpvalues = __parse_utmp('/var/run/utmp')

    with open('/proc/cpuinfo', 'r') as cpuinfofile:
        cpuinfo = cpuinfofile.read()
    bogomips = re.findall(r'^bogomips.+$', cpuinfo, flags=re.M)
    bogomips = float(bogomips[0].split()[2])

    # Get the time format things
    date = time.strftime(
        '%H:%M:%S', time.localtime(time.time()))

    finallist = []
    finallist.append(
        ' {date} up {_uptime}, {usrs} user, load average: {loadavgs}'.format(
            date=date,
            _uptime=hruptime,
            usrs=len(utmpvalues),
            loadavgs=', '.join(loadavg[0:3])))
    # finallist.append('USER     TTY        LOGIN@    IDLE   JCPU   PCPU WHAT')
    finallist.append('USER     TTY        LOGIN@            WHAT')
    for user in utmpvalues:
        # We need to get data for the user process that is in the utmp file
        with open('/proc/{0}/stat'.format(user['PID'])) as procstatfile:
            procstat = procstatfile.read().split()
        # Get the process start time of the login process
        procstarttime = float(procstat[23])
        logintime = (
            (time.time() - float(uptime[0])) + (procstarttime / bogomips))
        # TODO: Get cpu time for child processes using the proc/PID/stat file

        # Get the first child proc of this login. Should be the first PID to
        # have the tty file open.
        lsof = map('/proc/{0}'.format, range(int(user['PID']), 32768))
        usertty = user['Line'].decode().rstrip('\x00')
        child_pid = None
        # This is so ugly...
        for i in lsof:
            try:
                dirlist = os.listdir('{0}/fd'.format(i))
                for j in dirlist:
                        p = os.path.join(i, 'fd', j)
                        if (os.readlink(p) == os.path.join('/dev', usertty)):
                            child_pid = os.path.split(i)[1]
                            break
            except:
                child_pid = child_pid

        with open('/proc/{0}/comm'.format(child_pid)) as commfile:
            cproc = commfile.readlines()[0]

        finallist.append(
            '{User:9}{Line:11}{login:18}{what}'.format(
                User=user['User'].decode().rstrip('\x00'),
                Line=user['Line'].decode().rstrip('\x00'),
                login=time.strftime('%Y/%m/%d %H:%M',
                                    time.localtime(logintime)),
                what=cproc))

    # w = output(['w'], universal_newlines=True)
    # lin = w.splitlines()
    # lis = lin[2:]
    # lis.insert(0, lin[0])
    # return lis
    return finallist


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
