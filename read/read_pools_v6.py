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
            outgi = ssh.shell(['context Gi\n', 'show ipv6 pool verbose\n'], pause=5, buffer=10000).split("\n\n")
            gipools = []
            for pool in outgi:
                if ('RANGE' or 'NET') in pool:
                    pool_name = re.findall(r'\s+Pool Name:\s+(\S+)', pool)[0]
                    start_prefix = re.findall(r'\s+Start Prefix:\s+(\S+)', pool)[0]
                    end_prefix = re.findall(r'\s+End Prefix:\s+(\S+)', pool)[0]
                    prefix = re.findall(r'\s+Configured Prefix:\s+(\S+)', pool)[0]
                    gipools.append({"device": "",
                                    "context": "Gi",
                                    "name": "",
                                    "poolname": pool_name,
                                    "start": start_prefix,
                                    "end": end_prefix,
                                    "prefix": str(prefix)})

        with RemoteClient(ip, user, secret) as ssh:
            outsg = ssh.shell(['context SG\n', 'show ipv6 pool verbose\n'], pause=5, buffer=10000).split("\n\n")
            sgpools = []
            for pool in outsg:
                if ('RANGE' or 'NET') in pool:
                    pool_name = re.findall(r'\s+Pool Name:\s+(\S+)', pool)[0]
                    start_prefix = re.findall(r'\s+Start Prefix:\s+(\S+)', pool)[0]
                    end_prefix = re.findall(r'\s+End Prefix:\s+(\S+)', pool)[0]
                    prefix = re.findall(r'\s+Configured Prefix:\s+(\S+)', pool)[0]
                    gipools.append({"device": "",
                                    "context": "Gi",
                                    "name": "",
                                    "poolname": pool_name,
                                    "start": start_prefix,
                                    "end": end_prefix,
                                    "prefix": str(prefix)})

    except paramiko.SSHException as sshException:
        print(f'Error: {sshException}')

    return gipools, sgpools


def main():
    with open(f"../files/allpoolsv6.csv", "a", encoding="utf-8") as csv_file:
        csv_file.write('region,site,device,name,context,pool name,start,end,prefix\n')

    for region in hosts.keys():
        print(f"Pools getting from {region} is start")
        for host in hosts.get(region):
            gipools, sgpools = get_pool(host.get('host'))

            with open(f"../files/allpoolsv6.csv", "a", encoding="utf-8") as csv_file:
                for pool in gipools:
                    csv_file.write(f"{host.get('region')},,,"
                                   f"{host.get('hostname')},{str(pool['context'])},"
                                   f"{str(pool['poolname'])},{str(pool['start'])},{str(pool['end'])},"
                                   f"{str(pool['prefix'])}\n")

            with open(f"../files/allpoolsv6.csv", "a", encoding="utf-8") as csv_file:
                for pool in sgpools:
                    csv_file.write(f"{host.get('region')},,,"
                                   f"{host.get('hostname')},{str(pool['context'])},"
                                   f"{str(pool['poolname'])},{str(pool['start'])},{str(pool['end'])},"
                                   f"{str(pool['prefix'])}\n")

            print(f"\tPools getting from {host.get('hostname')} is end")
        print(f"Pools getting from {region} is end")
    print("File successfully create")


if __name__ == '__main__':
    main()
