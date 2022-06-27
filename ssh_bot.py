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
import sched
import time

import paramiko


def ssh_bot (myargs:argparse.Namespace) -> int:
    """
    Execute a few commands using Paramiko.
    """
    commands = gaussian_job(myargs)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    result_flag = True
    try:
        ssh.connect (
            hostname=myargs.host,
            username=myargs.netid,
            password=myargs.password
            )

    except socket.timeout as e:
        print ("command timed out.", commands)
        ssh.client.close()
        result_flag = False

    except paramiko.SSHException:
        print("Falid to execute the command!", commands)
        ssh.client.close()
        result_flag = False

    except Exception as e:
        print(f"Unknown exception: {e}")
        return os.EX_IOERR

    try:
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(commands, timeout=10) 
            ssh_output = stdout.readlines()
            if (ssh_err := stderr.read()):
                print (f"Problem occured while running command: {command}\nError: {ssh_err}")
                return os.EX_IOERR

            print(f"Submitted {command}")
    finally:
        ssh.close()

    return os.EX_OK


def gaussian_job (myargs:argparse.Namespace) -> list:

    lines = open(myargs.job_file).split("\n")
    return tuple( f"cd {myargs.dir} && qg16 {line}" for line in lines )
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='gaussian_job',
        description='gaussian_job: Launch gaussian job on the cluster')

    parser.add_argument('-u', '--netid', type=str, default=getpass.getuser(),
        help="User id for submitting the job. Defaults to the user running this program.")
    parser.add_argument('-p', '--password', type=str, required=True,
        help="Password for the user id.")
    parser.add_argument('-h', '--host', type=str, default=socket.gethostname(),
        help="Name of CPU where job will be submitted. Defaults to *this* CPU.")
    parser.add_argument('-d', '--dir', type=str, default="",
        help="Name of directory under /work that contains the data.")

    parser.add_argument('job_file', type=str, required=True,
        help="Name of the file containing the job to be submitted.")

    sys.exit(ssh_bot(parser.parse_args()))

