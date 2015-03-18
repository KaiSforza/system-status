#!/usr/bin/env python

'''Simple python scipt for testing our scripts'''

from __future__ import print_function
from __future__ import print_function

import subprocess
import re
import sys
import argparse
import pep8
import os

# For switching versions in the second test
V = {2: 3, 3: 2}
ourver = sys.version_info.major
filename = ['ss.py']


def setup():
    print("==> Saving the un-indexed changes...")
    return subprocess.check_call(
        ['git', 'stash', 'save', '--keep-index', '-q', '__PRECOMMITSTASH__'])


def cleanup():
    print("==> Cleaning up the stash...")
    subprocess.check_call(['git', 'stash', 'pop', '-q'])
    print('=!= Done =!=')


def bad_cleanup():
    print('!!! FAIL !!!')
    subprocess.call(['git', 'stash', 'pop', '-q'])
    return 1


def run_python(both):
    run_python_tests(both)
    run_python_scripts(both)


def run_python_tests(both):
    import test_ss
    print('===> Running tests with python{0}...'.format(ourver))
    test_ss.main()
    if both:
        print('===> Running tests with python{0}...'.format(V[ourver]))
        try:
            subprocess.check_call(['python{v}'.format(v=V[ourver]),
                                   'test_ss.py'], stderr=subprocess.DEVNULL)
        except:
            subprocess.check_call(['python', 'test_ss.py'],
                                  env={'PYENV_VERSION': '2.7.8',
                                       'PATH': os.environ['PATH']})


def run_python_scripts(both):
    import ss
    print('===> Running script with python{0}...'.format(ourver))
    ss.main()
    if both:
        print('===> Running script with python{0}...'.format(V[ourver]))
        try:
            subprocess.check_call(
                ['python{v}'.format(v=V[ourver]), 'ss.py'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            subprocess.check_call(
                ['python', 'ss.py'],
                env={'PYENV_VERSION': '2.7.8',
                     'PATH': os.environ['PATH']},
                stdout=subprocess.DEVNULL)


def run_pep8():
    e = 0
    for f in filename:
        print('===> Checking {0} with pep8...'.format(f))
        p = pep8.Checker(filename=f)
        e = e + p.check_all()
    if e > 0:
        raise(Exception, '{0} pep8 errors in files we care about.'.format(e))


def run_bash():
    print('===> Running ss.sh script...')
    subprocess.check_call(['bash', 'ss.sh'],
                          stdout=subprocess.DEVNULL)


def main(both):
    stat = subprocess.check_output(
        ['git', 'status', '--porcelain']).decode()

    files = re.compile(
        '''
        [MADRCU ]{2}           #  Check the flags are not empty
        [ ]{1}                 #  A single space between status and file
        (ss.(py|ss)|           #  The actual 'ss' scripts
         test_ss.py)           #  The tests
        ''', flags=re.VERBOSE)

    # Check if files have been edited
    if re.search(files, stat):
        # Clean up the working directory
        setup()
        # We need to clean up after ourselves if this failes, so use 'try'
        try:
            if re.search('(ss.py|test_ss.py)', stat):
                run_python(both)
                run_pep8()
            if re.search('ss.sh', stat):
                run_bash()
            cleanup()
        except:
            bad_cleanup()
    else:
        print('=!= Nothing done =!=')

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('-f', help='run checks', action='count')
    a.add_argument('-s', help='stash changes', action='count')
    a.add_argument('--both', help='run on both python3 and python2',
                   action='count', default=0)
    args = a.parse_args()
    if args.f:
        run_python(args.both)
        run_pep8()
        run_bash()
    else:
        main(args.both)
