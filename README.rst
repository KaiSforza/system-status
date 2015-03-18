.. image:: https://travis-ci.org/KaiSforza/system-status.svg?branch=master
    :target: https://travis-ci.org/KaiSforza/system-status

System Status
=============

A simple set of scripts in python and bash that will print out some
rudimentary system info by querying commands and files, then formatting into
a human-readable output like::

  ---------------------------------------------------------------------------
  Hostname: wst420
  ---------------------------------------------------------------------------
  wlp3s0  192.168.0.3
  ---------------------------------------------------------------------------
   22:45:29 up 3 days, 4:50:01, 1 user, load average: 0.09, 0.15, 0.21
  USER     TTY        LOGIN@   IDLE   JCPU   PCPU WHAT
  wgiokas  tty1      Wed17   35:05   0.37s  0.37s -zsh
  ---------------------------------------------------------------------------
  Filesystem      Size  Used Avail Use% Mounted on
  /dev/sda1       119G   15G  100G  13% /
  /dev/sda2       244M   11M  233M   5% /boot
  /dev/sda1       119G   15G  100G  13% /home

  Filesystem     Inodes IUsed IFree IUse% Mounted on
  /dev/sda1           0     0     0     - /
  /dev/sda2           0     0     0     - /boot
  /dev/sda1           0     0     0     - /home
  ---------------------------------------------------------------------------
  Memory Used: 2196.0 MB/7872.0 MB
  Swap status: 0.0 MB/0.0 MB
  ---------------------------------------------------------------------------
  Connection Summary:
  Total: 265 (kernel 0)
  TCP:   11 (estab 9, closed 0, orphaned 0, synrecv 0, timewait 0/0), ports 0
  ---------------------------------------------------------------------------
  Connection Concentration:
  IN (top 3)::
        1 39220
        1 33498
        1 39219
  OUT (top 3)::
        3 5127
        3 993
        1 43289
  ---------------------------------------------------------------------------
  Listening       Recv-Q Send-Q Processes
  127.0.0.1:33265      0      5 "weechat",pid=544,fd=14
  :::7700              0    128 "mpd",pid=554,fd=3, "systemd",pid=343,fd=19
  ---------------------------------------------------------------------------

(Currently the ``ss.py`` script is under development and will be getting
new output before ``ss.sh``.)

Development
===========

If you are going to work on this, it must be able to run on python 2.6+ and
python 3+. There are tests for the ``ss.py`` script in the ``test_ss.py``
file, as well as automated pre-commit hooks written in both bash and python.
Any commit should pass these tests unless there is a very good reason, and
any new ``parse_`` functions should get at least one test.
