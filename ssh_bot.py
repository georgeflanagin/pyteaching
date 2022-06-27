# -*- coding: utf-8 -*-
import typing
from   typing import *

import os 
import sys
min_py = (3, 8)

if sys.version_info < min_py:
    print(f"This program requires at least Python {min_py[0]}.{min_py[1]}")
    sys.exit(os.EX_SOFTWARE)

import argparse
import getpass
import socket

import paramiko

def ssh_bot (myargs:argparse.Namespace) -> int:
    """
    Execute a few commands using Paramiko.
    """
    with open(myargs.job_file) as in_file:
        if not (lines := in_file.read().split("\n")):
            print(f"{myargs.job_file} is empty.")
            return os.EX_NOINPUT

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    try:
        ssh.connect (
            hostname=myargs.host,
            username=myargs.netid,
            password=myargs.password
            )

    except socket.timeout as e:
        print (f"command timed out. {e}")
        return os.EX_IOERR

    except Exception as e:
        print(f"Other exception: {e}")
        return os.EX_IOERR

    try:
        for command in (f"cd {myargs.dir} && qg16 {line}" for line in lines):
            _stdin, _stdout, _stderr = ssh.exec_command(commands, timeout=10) 
            ssh_output = _stdout.readlines()
            if (ssh_err := _stderr.read()):
                print (f"Problem occured while running command: {command}\nError: {ssh_err}")
                return os.EX_IOERR

            print(f"Submitted {command}")
    finally:
        ssh.close()

    return os.EX_OK


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='gaussian_job',
        description='gaussian_job: Launch gaussian job on the cluster')

    parser.add_argument('-u', '--netid', type=str, default=getpass.getuser(),
        help="User id for submitting the job. Defaults to the user running this program.")
    parser.add_argument('-p', '--password', type=str, required=True,
        help="Password for the user id.")
    parser.add_argument('--host', type=str, default=socket.gethostname(),
        help="Name of CPU where job will be submitted. Defaults to *this* CPU.")
    parser.add_argument('-d', '--dir', type=str, default="",
        help="Name of directory under /work that contains the data.")

    parser.add_argument('job_file', type=str,
        help="Name of the file containing the job to be submitted.")

    my_args=parser.parse_args()
    my_args.dir = f"/work/{myargs.dir}"

    sys.exit(ssh_bot(my_args))

