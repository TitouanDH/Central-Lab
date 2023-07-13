import paramiko
import time


username= 'admin'
password='switch'


def create(ip1, port1, ip2, port2, bvlan, service_nbr):
    #bvlan logic

    # On 1st switch
    with paramiko.SSHClient() as ssh:
        # This script doesn't work for me unless the following line is added!
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh.connect(ip1, username=username, password=password, port=22)

        ssh.exec_command("service spb {0} isid {0} bvlan {1}".format(service_nbr, bvlan))
        ssh.exec_command("service {0} pseudo-wire enable".format(service_nbr))
        ssh.exec_command("service l2profile 'spbbackbone' 802.1x tunnel 802.1ab peer".format(service_nbr))
        ssh.exec_command("service access port {0} vlan-xlation enable l2profile 'spbbackbone'".format(port1))
        ssh.exec_command("service {0} sap port {1}:all".format(service_nbr, port1))
        time.sleep(1)


    # On 2nd switch
    with paramiko.SSHClient() as ssh:
        # This script doesn't work for me unless the following line is added!
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh.connect(ip2, username=username, password=password, port=22)

        ssh.exec_command("service spb {0} isid {0} bvlan {1}".format(service_nbr, bvlan))
        ssh.exec_command("service {0} pseudo-wire enable".format(service_nbr))
        ssh.exec_command("service l2profile 'spbbackbone' 802.1x tunnel 802.1ab peer".format(service_nbr))
        ssh.exec_command("service access port {0} vlan-xlation enable l2profile 'spbbackbone'".format(port2))
        ssh.exec_command("service {0} sap port {1}:all".format(service_nbr, port2))
        time.sleep(1)




