
import paramiko
import create_tunnel
import random


# [ip of DUT, ip of VC where DUT is connected to]

result_file = open("output.txt", "w")

dut = [
    ["10.255.138.26", "10.255.127.161"],
    ["10.255.138.59", "10.255.127.162"],
    ["10.255.138.96", "10.255.127.163"],
    ["10.255.138.131", "10.255.127.164"],
    ["10.255.138.174", "10.255.127.165"],
    ["10.255.138.205", "10.255.127.166"],
]


starting_vlan = 400
starting_bvlan = 4000
username = "admin"
password = "switch"

success = 0


for _ in range(100):
    try:
        vlan+=1
    except:
        vlan = starting_vlan

    try:
        if bvlan >= 4002:
            bvlan = 4000
        else:
            bvlan += 1
    except:
        bvlan = starting_bvlan
    
    test_ips = random.sample(dut, 2)
    print(test_ips[0][0],test_ips[1][0])


    #### Creating tunnel between VCs
    create_tunnel.create(test_ips[0][1], "1/1/1", test_ips[1][1], "1/1/1", bvlan, vlan)


    #### Testing ping
        # On 2nd switch
    with paramiko.SSHClient() as ssh:
        # This script doesn't work for me unless the following line is added!
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh.connect(test_ips[0][0], username=username, password=password, port=22)


        last_bit = dut.index(test_ips[1]) + 1
        inp, out, err = ssh.exec_command("ping 10.10.99.{}".format(last_bit))
        error = err.readlines()
        if len(error) == 0:
            success += 1
            try:
                result_file.write("Success\n")
            except:
                result_file.close()
            print("+")
        else:
            try:
                result_file.write("Error\n")
                result_file.write(str(error))
                result_file.write("\n")
            except:
                result_file.close()
            print(error)


result_file.close()