from celery import Celery, shared_task
import paramiko
import time

app = Celery('tasks', broker='pyamqp://guest@localhost//')
username= 'admin'
password='switch'

@shared_task(ignore_result=True)
def change_banner(ip, user):
    text = """
    ***************** CENTRAL LAB RESERVATION SYSTEM ******************
    This switch is reserved by : {}
    If you access this switch without reservation, please contact admin

    """.format(user)
    print("change_banner")
    try:
        with paramiko.SSHClient() as ssh:
            # This script doesn't work for me unless the following line is added!
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            ssh.connect(ip, username=username, password=password, port=22, timeout=1)

            ftp = ssh.open_sftp()
            file=ftp.file('switch/pre_banner.txt', "w", -1)
            file.write(text)
            file.flush()
            ftp.close()
            return True
        
    except Exception as e:
        print(e)
        return False

@shared_task(ignore_result=False)
def delete_tunnel(ip1, port1, service_nbr):
    #bvlan logic
    print("delete_tunnel")
    try:
        # On 1st switch
        with paramiko.SSHClient() as ssh:
            # This script doesn't work for me unless the following line is added!
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            ssh.connect(ip1, username=username, password=password, port=22, timeout=1)

            ssh.exec_command("no service {0} sap port {1}:all".format(service_nbr, port1))
            ssh.exec_command("service spb {0} admin-state disable".format(service_nbr))
            _, stdout, _  = ssh.exec_command("no service spb {0}".format(service_nbr))
            stdout.channel.recv_exit_status() 

        return True
    
    except Exception as e:
        print(e)
        return False

@shared_task(ignore_result=False)
def create_tunnel(ip1, port1, ip2, port2, bvlan, service_nbr):
    #bvlan logic
    print("create_tunnel")
    try:
        # On 1st switch
        with paramiko.SSHClient() as ssh:
            # This script doesn't work for me unless the following line is added!
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            ssh.connect(ip1, username=username, password=password, port=22, timeout=1)

            ssh.exec_command("service spb {0} isid {0} bvlan {1}".format(service_nbr, bvlan))
            ssh.exec_command("service {0} pseudo-wire enable".format(service_nbr))
            ssh.exec_command("service l2profile 'spbbackbone' 802.1x tunnel 802.1ab peer".format(service_nbr))
            ssh.exec_command("service access port {0} vlan-xlation enable l2profile 'spbbackbone'".format(port1))
            _, stdout, _  = ssh.exec_command("service {0} sap port {1}:all".format(service_nbr, port1))
            stdout.channel.recv_exit_status() 


        # On 2nd switch
        with paramiko.SSHClient() as ssh:
            # This script doesn't work for me unless the following line is added!
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            ssh.connect(ip2, username=username, password=password, port=22, timeout=1)

            ssh.exec_command("service spb {0} isid {0} bvlan {1}".format(service_nbr, bvlan))
            ssh.exec_command("service {0} pseudo-wire enable".format(service_nbr))
            ssh.exec_command("service l2profile 'spbbackbone' 802.1x tunnel 802.1ab peer".format(service_nbr))
            ssh.exec_command("service access port {0} vlan-xlation enable l2profile 'spbbackbone'".format(port2))
            _, stdout, _  = ssh.exec_command("service {0} sap port {1}:all".format(service_nbr, port2))
            stdout.channel.recv_exit_status() 

        return True
    
    except Exception as e:
        print(e)
        return False

@shared_task(ignore_result=True)
def clean_dut(ip):
    print("clean_dut")
    try:
        with paramiko.SSHClient() as ssh:
            # This script doesn't work for me unless the following line is added!
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            ssh.connect(ip, username=username, password=password, port=22, timeout=1)

            stdin, stdout,_ = ssh.exec_command("cp -r init/* working")
            stdout.channel.recv_exit_status()
            stdin, stdout,_ = ssh.exec_command("reload from working no rollback-timeout\r\n")
            time.sleep(1)
            stdin.write("Y")
            stdin.write("\n")
            stdin.flush()
            return True

    except Exception as e:
        print(e)
        return False
    
@shared_task(ignore_result=True)
def test():
    print("clean_dut")