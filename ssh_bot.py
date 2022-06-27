from sys import argv
import paramiko
import socket
import os 
import sched
import time

from urdecorators import trap

# script, job_file = argv

host = "spydur.richmond.edu"
ssh_username = "gflanagi"
ssh_password = "xxxxxxxxxxxxxxxxxx"

@trap
def ssh_bot (hostname, username, password, commands):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.load_system_host_keys()
    print("host keys loaded.")
    result_flag = True
    try:
        ssh.connect (
            hostname=host,
            username=ssh_username,
            password=ssh_password)

        # Added for loop here but didn't work
        print(f"{commands=}")
        stdin, stdout, stderr = ssh.exec_command(commands, timeout=10)         

        ssh_output = stdout.readlines()
        ssh_err = stderr.read()
        if ssh_err:
            print ("Problem occured while running command:" + commands + "Error:" + ssh_err)
            result_flag = False
        else:
            print("No error. Here is the output")
            print(''.join(ssh_output))
            result_flag = False
        ssh.close()

    except socket.timeout as e:
        print ("command timed out.", commands)
        ssh.client.close()
        result_flag = False

    except paramiko.SSHException:
        print("Falid to execute the command!", commands)
        ssh.client.close()
        result_flag = False

@trap
def gaussian_job (job_file):

    project_folder = input ("Name of project folder:> ") or None
    sub_folder_1 = input ("Name of 1st subfolder folder:> ") or None
    sub_folder_2 = input ("Name of 2nd subfolder folder:> ") or None
    jobs = open(job_file, 'r')
    
    for job in jobs:
        if project_folder == None:
            commands = (f'cd work && qg16 {job}')
        if project_folder != None:
            if sub_folder_1 == None:
                commands = (f'cd work && cd {project_folder} && qg16 {job}')
            if (sub_folder_1 != None) and (sub_folder_2 == None):
                commands = (f'cd work && cd {project_folder} && cd {sub_folder_1} && qg16 {job}')
            if (sub_folder_1 != None) and (sub_folder_2 != None):
                commands = (f'cd work && cd {project_folder} && cd {sub_folder_1} && cd {sub_folder_2} && qg16 {job}')
    return commands


# commands = gaussian_job(job_file)

ssh_bot ("coltrane", "demouser", "x", "echo 'hello world'")
