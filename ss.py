#!/usr/bin/env python

'''
System Status Script

This script is a simple status script that can be run on a server to get some
information about the system. It should generally be run as a root user, though
everything will still function when run as an unprivileged user. It contains
functions for parsing files such a /proc/meminfo, /run/utmp, and others.

There is also a simple test suite distributed with this repository, as well as
a bash version of this script, though it is much shorter and more rudimentary.

When run as a script it will show you a nicely printed output.

This script is compatible with python >= 2.6 and python 3.
'''


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


class bcolors:
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[1;31m'
    S = '\033[0m'


def df(args=[]):
    '''
    Simply returns the output of a 'df' command and splits the lines into a
    list. Uses universal_newlines to write it out into a string, not bytes.
    '''
    dfcmd = ['df']
    dfcmd.extend(args)
    return output(dfcmd, universal_newlines=True).splitlines()


def ss():
    '''
    Get the output of 'ss -utnapss', all of the output used by the functions
    below.
    '''
    return output(['ss', '-utnaps'], universal_newlines=True).splitlines()


def type_df(x):
    x = x.split()
    percent = x[4].strip('%')
    if percent == '-':
        col = ''
    elif int(percent) > 90:
        col = bcolors.RED
    elif int(percent) > 75:
        col = bcolors.YELLOW
    else:
        col = bcolors.GREEN
    return col


def format_df(rawdf):
    cld = ('{0}{1}{2}'.format(type_df(x), x, bcolors.S)
           for x in rawdf if x.startswith('/'))
    header = rawdf[0]
    ret = [header]
    ret.extend(cld)
    return ret


def run_ip(ip='/sbin/ip'):
    return output([ip, 'a'], universal_newlines=True)


def parse_ip_output(ip):
    '''
    Gets the sbin/ip command. On systems where the binary does not reside in
    /sbin/ip, it is almost always available via a symbolic link of /sbin
    /usr/bin.
    '''
    # Grabs either 1 or 2 lines (usually) per interface: one for ipv4 (has a
    # number at the end) and an ipv6 address (has 'global ' at the end).
    rawips = re.findall('(inet[ 6].+([0-9]|global ))$', ip, flags=re.M)
    # Takes each match and splits it on the whitespace.
    ips = (x[0].split() for x in rawips)
    # Run through all of the IP addresses and format them.
    return ('{0:8}{1}'.format(i[-1], i[1].split('/')[0]) for i in ips)


def __strip(x, y='\x00', ign='addr'):
    try:
        if x[0] != ign:
            return x[0], x[1].decode().strip(y)
        else:
            return x[0], x[1]
    except:
        return x[0], x[1]


def parse_utmp(_utmp='/var/run/utmp',
               _fmt="hi32s4s32s256sii2i16s20s",
               _fieldnames=["type", "PID", "Line", "ID", "User",
                            "Hostname", "exit_status", "session",
                            "time_s", "time_ms", "addr", "unused"],
               _force=False,
               _clean=True):
    '''
    Parse the UTMP file.
    This is mostly a test to see that it could be done, and how to do it, so
    use at your own risk. _fmt is set up for linux systems, but can be
    overridden.

    The specific format is outlined below.

    Arguments:
        utmp -- the utmp file to read. Defaults to '/var/run/utmp'
        _fmt -- "hi32s4s32s256sii2i16s20s"
                 ||  | |  |   ||| | |  ^ 20 empty bits that are reserved for
                 ||  | |  |   ||| | |    future use
                 ||  | |  |   ||| | ^--- 4 ints for address, but this does not
                 ||  | |  |   ||| |      seem to work correctly with ints
                 ||  | |  |   ||| ^----- 2 32-byte long ints for time stuffs
                 ||  | |  |   ||^------- Session (32 length int, int32_t)
                 ||  | |  |   |^-------- exit status (unsigned int)
                 ||  | |  |   ^--------- Hostname(UT_HOSTNAMESIZE chars, 256)
                 ||  | |  ^------------- User (UT_NAMESIZE chars, 32)
                 ||  | ^---------------- ID (4 length char)
                 ||  ^------------------ Line (UT_LINESIZE chars, 32)
                 |^--------------------- PID (int)
                 ^---------------------- Type of record (short)
        _filednames -- The field names defined in the _fmt string.
        _force -- Force parsing even if we don't have a sane utmp file or _fmt
                  string
        _clean -- Remove '\x00' from the strings. May create some empty
                  strings. Does not affect the 'addr' field.

    '''
    # Get the length of the format string specified.
    _fmt_len = struct.calcsize(_fmt)
    # Filesize in bytes of the _utmp file. Should be a multiple of _fmt_len.
    _filesize = os.path.getsize(_utmp)

    # We can't reliably parse a file with a length not equal to the format
    # length. Raise an exception if we can't parse it correctly before moving
    # forward.
    if not (_filesize % _fmt_len == 0 and not _force):
        raise Exception(
            "{0} is either corrupt or the format string is wrong.".format(
                _utmp)
        )

    # Read the utmp file and write it into a variable so we can close the file
    # as fast as possible.
    with open(_utmp, 'rb') as utmpfile:
        utmp = utmpfile.read()

    # Get a number of entries in the utmp file.
    _entries = _filesize // _fmt_len

    # Initialize the users list.
    users = []

    # Walk through the utmp file, unpacking as we go.
    for ind in range(_entries):
        # When we unpack we are going to create a dictionary from the output,
        # using the values defined in the _fieldnames variable.
        _raw_fields = zip(_fieldnames,
                          struct.unpack(_fmt, utmp[
                              (_fmt_len * ind):(_fmt_len * (ind + 1))]))
        # Build the dictionary using dictionary comprehension.
        if _clean:
            _raw_fields = map(__strip, _raw_fields)
        user_dict = dict((x, y) for x, y in _raw_fields)
        # Add the dictionary to the users list
        users.append(user_dict)

    # The uses list is going to be what is used, so return it.
    return users


def __get_file(f):
    with open(f, 'r') as xf:
        return xf.read()


def format_w(loadavg, uptime, utmp):
    loadavg = loadavg.split()
    uptime = uptime.split()
    hruptime = str(timedelta(seconds=int(uptime[0].split('.')[0])))

    # Uses utmp to find the logged in users
    # utmpvalues = parse_utmp('/var/run/utmp')
    utmpvalues = [x for x in utmp if x['type'] == 7]

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

    # cut off w's uptime and stuff
    w = output(['w'], universal_newlines=True)
    lin = w.splitlines()
    finallist.extend(lin[1:])
    return finallist


def parse_mem(m):
    '''
    Parse /proc/meminfo and print out the memory used.
    Creates a dictionary with the /proc/meminfo names as keys and the values as
    values.
    '''
    m = m.splitlines()
    # Split on whitespace. Gives us 3 fields for almost everything except for
    # the HubePages counts.
    meminfo = (x.split() for x in m)
    # Create a dictionary
    return dict((x[0][0:-1], x[1]) for x in meminfo)


def format_mem(memdict, memerr=0.7, memwarn=0.5):
    '''
    Format the memory we get from parse_mem(). Two optional arguments, memerr
    and memwarn set the threshold for error and warning colors.
    '''
    total = int(memdict['MemTotal'])
    free = int(memdict['MemFree'])
    buffers = int(memdict['Buffers'])
    cache = int(memdict['Cached'])

    memused = total - free  # total used memory in kb

    memused = memused - (buffers + cache)  # Remove the buffers and cache

    mempercent = memused / total

    totalmb = total / 1024
    memusedmb = memused / 1024

    if mempercent > memerr:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.RED,
                                                    memusedmb,
                                                    bcolors.S,
                                                    totalmb)
    elif mempercent > memwarn:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.YELLOW,
                                                    memusedmb,
                                                    bcolors.S,
                                                    totalmb)
    else:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.GREEN,
                                                    memusedmb,
                                                    bcolors.S,
                                                    totalmb)


def format_swap(memdict, swaperr=0.7, swapwarn=0.5):
    total = int(memdict['SwapTotal'])
    free = int(memdict['SwapFree'])

    swapused = total - free  # total used swapory in kb

    try:
        swappercent = swapused / total
    except:
        swappercent = 0

    totalmb = total / 1024
    swapusedmb = swapused / 1024

    if swappercent > swaperr:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.RED,
                                                    swapusedmb,
                                                    bcolors.S,
                                                    totalmb)
    elif swappercent > swapwarn:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.YELLOW,
                                                    swapusedmb,
                                                    bcolors.S,
                                                    totalmb)
    else:
        return '{0}{1:.1f} MB{2}/{3:.1f} MB'.format(bcolors.GREEN,
                                                    swapusedmb,
                                                    bcolors.S,
                                                    totalmb)


def __regex_ss(a):
    '''
    Splits up the ss ports and IP's.
    Return a tuple of (local port, remote port)
    '''
    a = a.split()
    # if len(a) == 5
    local_port = re.match('.+:([^:]*$)', a[4])
    remote_port = re.match('.+:([^:]*$)', a[5])
    return local_port.groups()[0], remote_port.groups()[0]


def __parse_ssutn(sslist, header=12):
    '''
    Private function used by format_ssutn thta actually runs the 'ss' command.
    Does the 'sort | uniq -c' part of the old shell script using the
    collections.Counter class.
    '''
    # Remove the header from the output.
    ss = sslist[header:]
    # Run a list comprehension on the ss list and return a tuple of (in, out).
    ss = [__regex_ss(x) for x in ss if re.match('^(tcp|udp) +ESTAB', x)]
    _nin = (x[0] for x in ss)
    _nout = (x[1] for x in ss)

    return Counter(_nin), Counter(_nout)


def format_ssutn(sslist, n=3, header=12):
    '''
    Print out the number of out and in sockets that are open in a pair of
    columns, similar to what a '| sort | uniq -n | sort -r' would get you.
    Takes a number, n, as input, defaulting to 3.

    Returns the 'n' most common sockets.
    '''
    a = __parse_ssutn(sslist, header=header)
    if n <= (len(a[0])):
        out = a[0].most_common(n)
    else:
        out = a[0].most_common(len(a[0]) - 1)

    if n <= (len(a[1])):
        nin = a[1].most_common(n)
    else:
        nin = a[1].most_common(len(a[1]) - 1)

    outlist = ['      {0:7<} {1:8>}'.format(y, x) for x, y in out]
    ninlist = ['      {0:7<} {1:8>}'.format(y, x) for x, y in nin]
    return outlist, ninlist


def __format_ss_proc_line(a):
    '''
    Private function to get a pretty formatted 'ss -ntlp' output. Takes a line
    of 'ss -ntlp' output as input, returns a formatted string.
    '''
    recv = a[2]
    send = a[3]
    port = a[4]
    try:
        proc = a[6]

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


def format_ssntlp(sslist, m=2):
    '''
    Gets the 'ss -ntlp' output and formats it correctly, as per the
    __format_ss_proc_line() function. Returns a generator, not a list.
    '''
    ssntlp = (x for x in sslist if re.match('^(tcp|udp) +LISTEN.*', x))
    return (__format_ss_proc_line(x.split()) for x in ssntlp)


if __name__ == '__main__':

    sslist = ss()
    ssutn = format_ssutn(sslist)
    me = __get_file('/proc/meminfo')
    meminfo = parse_mem(me)
    la = __get_file('/proc/loadavg')
    up = __get_file('/proc/uptime')
    ut = parse_utmp('/var/run/utmp')
    dfh = df(args=['-h', '-x', 'tmpfs', '-x', 'devtmpfs'])
    dfi = df(args=['-i', '-x', 'tmpfs', '-x', 'devtmpfs'])

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
Swap status: {swap}
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
                ipaddrs='\n'.join(parse_ip_output(run_ip())),
                wout='\n'.join(format_w(la, up, ut)),
                fs='\n'.join(format_df(dfh)),
                inodes='\n'.join(format_df(dfi)),
                memory=format_mem(meminfo),
                swap=format_swap(meminfo),
                sssum='\n'.join(sslist[:2]),
                nsin='\n'.join(ssutn[0]),
                nsout='\n'.join(ssutn[1]),
                ssproc='\n'.join(format_ssntlp(sslist)))

    print(p)
