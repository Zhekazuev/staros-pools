# StarOS Pools

Get IPv4 and IPv6 pools from StarOS devices 

  - Get pools
  - Write pools to csv
  - Push pools to Netbox - Update/Delete

### Installation

Git clone from repo
```sh
git clone https://github.com/Zhekazuev/staros-pools.git staros-pools
```

Install the dependencies from requirements.txt. 
```sh
cd staros-pools
cat requirements.txt
source install.sh
```

Start script reading IPv4 pools
```sh
python read/read_pools_v4.py
```
Output - files/allpoolsv4.csv


Start script reading IPv6 pools
```sh
python read/read_pools_v6.py
```
Output - files/allpoolsv6.csv

Example:
```console
[user@server1 staros-pools]# python read/read_pools_v4.py
Pools getting from brest is start
10-30-2020 16:56:46 | INFO: 
INPUT: 1.1.1.1: ['context Gi\n', 'show ip pool\n']
OUTPUT:
....
10-30-2020 16:56:57 | INFO: 
INPUT: 1.1.1.2: ['context SG\n', 'show ip pool\n']
OUTPUT:
...
	Pools getting from mog1server1 is end
Pools getting from mogilev is end
File successfully create
[user@server1 staros-pools]#
```

License
----
Free Software
