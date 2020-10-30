"""
Read pools from hardware
Save pools to pools.csv
"""
from client import RemoteClient
import ipaddress
import paramiko
import config
import time
import csv
import re


hosts = config.StarOS.hosts
user = config.StarOS.user
secret = config.StarOS.password
port = 22


def get_pool(ip):
    try:
        with RemoteClient(ip, user, secret) as ssh:
            outgi = ssh.shell(['context Gi\n', 'show ip pool\n'], pause=5, buffer=10000).split("\n")
            gipools = []
            name = outgi[-1].replace(r'# ', '').replace('[Gi]', '').replace('[SG]', '')
            for pool in outgi:
                if ('RANGE' or 'NET') in pool:
                    line = re.findall(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+.*', pool)
                    try:
                        prefix = ipaddress.IPv4Network(f"{line[0][2]}/{line[0][3]}")
                    except ipaddress.NetmaskValueError:
                        prefix = list(ipaddress.summarize_address_range(ipaddress.IPv4Address({line[0][2]}),
                                                                        ipaddress.IPv4Address({line[0][3]})))[0]
                    gipools.append({"device": "",
                                    "context": "Gi",
                                    "name": name,
                                    "poolname": f"{line[0][0]} {line[0][1]}",
                                    "pool": line[0][2],
                                    "mask": line[0][3],
                                    "prefix": str(prefix)})

        with RemoteClient(ip, user, secret) as ssh:
            outsg = ssh.shell(['context SG\n', 'show ip pool\n'], pause=5, buffer=10000).split("\n")
            sgpools = []
            name = outsg[-1].replace(r'# ', '').replace('[Gi]', '').replace('[SG]', '')
            for pool in outsg:
                if ('RANGE' or 'NET') in pool:
                    line = re.findall(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+.*', pool)
                    try:
                        prefix = ipaddress.IPv4Network(f"{line[0][2]}/{line[0][3]}")
                    except ipaddress.NetmaskValueError:
                        # prefix = list(ipaddress.summarize_address_range(ipaddress.IPv4Address(line[0][2]),
                        # ipaddress.IPv4Address(line[0][3])))[0]
                        prefix = None

                    sgpools.append({"device": "",
                                    "context": "SG",
                                    "name": name,
                                    "poolname": f"{line[0][0]} {line[0][1]}",
                                    "pool": line[0][2],
                                    "mask": line[0][3],
                                    "prefix": str(prefix)})
    except paramiko.SSHException as sshException:
        print(f'Error: {sshException}')

    return gipools, sgpools


def main():
    # create allpoolsv4.csv MB
    with open(f"../files/allpoolsv4.csv", "a", encoding="utf-8") as csv_file:
        csv_file.write('region,site,device,name,context,pool name,pool,mask,prefix\n')

    for region in hosts.keys():
        print(f"Pools getting from {region} is start")
        for host in hosts.get(region):
            # get pools from SG and Gi contexts
            gipools, sgpools = get_pool(host.get('host'))

            # write Gi pools
            with open(f"../files/allpoolsv4.csv", "a", encoding="utf-8") as csv_file:
                for pool in gipools:
                    csv_file.write(f"{host.get('region')},,,"
                                   f"{str(pool['name'])},{str(pool['context'])},"
                                   f"{str(pool['poolname'])},{str(pool['pool'])},{str(pool['mask'])},"
                                   f"{str(pool['prefix'])}\n")

            # write SG pools
            with open(f"../files/allpoolsv4.csv", "a", encoding="utf-8") as csv_file:
                for pool in sgpools:
                    csv_file.write(f"{host.get('region')},,,"
                                   f"{str(pool['name'])},{str(pool['context'])},"
                                   f"{str(pool['poolname'])},{str(pool['pool'])},{str(pool['mask'])},"
                                   f"{str(pool['prefix'])}\n")

            print(f"\tPools getting from {host.get('hostname')} is end")
        print(f"Pools getting from {region} is end")
    print("File successfully create")


if __name__ == '__main__':
    main()
