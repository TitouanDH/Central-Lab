from celery import Celery, shared_task
import paramiko
import time
import requests
from urllib3.exceptions import InsecurePlatformWarning
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Celery('tasks', broker='pyamqp://guest@localhost//')
username= 'admin'
password='switch'

def get_header(ip):
    """
    building the authv2 URL. This method performs login to switch using ip. admin/switch is
    used to login and get an Authv2 header. Authentication Token is stored in header for
    subsequent queries.
    :param ip:
    :return:
    """
    authv2_url = "https://%s?domain=authv2&username=admin&password=switch" % (str(ip))

    # setting the header for the authentication request
    auth_headers = {'ACCEPT': 'application/vnd.alcatellucentaos+json; version=1.0'}

    # sending the authentication request to the switch
    r = requests.get(authv2_url, headers=auth_headers, verify=False)

    if r.status_code == 200:  # OK
        body = r.json()
        if "result" not in body or "data" not in body["result"]:
            print('Invalid response body - data not found')
            exit()

        if "token" not in body["result"]["data"]:
            print('Invalid response body - token not found')
            return False, None

        token = body["result"]["data"]["token"]
        print("Login Token is: " + token)
        query_header = {'ACCEPT': 'application/vnd.alcatellucentaos+json; version=1.0',
                        "Authorization": "Bearer " + token}
        return True, query_header
    else:  # NOT OK
        print('An error has occurred.')
        return False, None

def cli(ip,header, cmd):
    query_url = "https://{}?domain=cli&cmd={}".format(ip, cmd)
    r = requests.get(query_url, headers=header, verify=False)
    if r.status_code == 200:  # OK
        output = r.json()['result']['output']
        error = r.json()['result']['error']

        if len(error)>0:
            raise Exception('Error field')
        else:
            return output

    elif r.status_code == 400 or r.status_code == 401:
        raise Exception('Code 400')

    else:  # NOT OK
        raise Exception('Unknown error code')


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
            ssh.connect(ip, username='admin', password='switch', port=22, timeout=1)
            stdin, stdout,_ = ssh.exec_command("cp -r init/* working")
            stdout.channel.recv_exit_status()

    except Exception as e:
        print(e)
        return False


    header = get_header(ip)
    if header[0] : 
        header = header[1]
    else:
        print('cannot auth to ' + ip)
        return False
    try :
        cli(ip,header, "reload from working no rollback-timeout")
    except Exception as e:
        print(e)
        return False