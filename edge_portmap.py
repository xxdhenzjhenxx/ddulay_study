#!/usr/bin/env python3.6
#dennisdulay@fb.com | 12/19/2019
#****E D G E   P O R T M A P**** 
################################ 
from subprocess import check_output,run, PIPE, DEVNULL
from socket import gethostbyname
from getpass import getpass, getuser
import sys, os, re, click, time
tmp_pass = '/tmp/passwd.txt'
serf_mac = []

def check_pass(tmp_pass):
	'''I am going to ask your email password to login to msw switch. 
	   Then will reuse your password for the current session until you
	   logout of your devserver.
	'''
	if os.path.exists(tmp_pass) and os.path.getsize(tmp_pass) > 0:
		with open(tmp_pass, "r") as file:
			passfile = file.readline().rstrip("\n")
	else:
		file = open(tmp_pass, "w")
		sw_pass = getpass("[!] Please enter your edge switch pass: ")
		file.write(sw_pass)
		print("[~] Password written in {}".format(tmp_pass))
		file.close() ; time.sleep(5)

def check_host(hostname: str) -> bool:
	try:
		gethostbyname(hostname)
		check_pass(tmp_pass)
		os.system('clear')
		table_format = '{:^18} {:^17} {:^17} {:^15} {:^15}  {:^8} {:^14}'
		table_headers = ['Edge Servers','Host MAC', 'ILO MAC', 'HOST IP', 'ILO IP', 'MSW Port', 'Uptime']
		print(click.style(table_format.format(*table_headers),fg='red',bold=True))
	except:
		print(click.style("[!] No such hostname as '{}'".format(hostname), fg='red', blink=True))
		sys.exit(1)

def get_serf_macs(cluster_rack,cluster):
	cmd = 'serfcli get {}.{} --fields name,eth0.mac,eth0.ip,oob.mac,oob.ip --tabular'.format(cluster,cluster_rack[2])
	get_macs = run(cmd, shell=True, stdout=PIPE, stderr=DEVNULL, encoding='utf-8')
	for line in get_macs.stdout.strip().replace("|"," ").split('\n'):
		line = [k for k in filter(None, line.split(" "))]
		if re.search('edge',line[0]): 
			newline = line[0].split(".")[0:3]
			newline = "{}.{}.{}".format(newline[0],newline[1],newline[2])
			serf_mac.append("{} {} {} {} {}".format(newline,''.join(line[1].replace(":","").lower()),\
				''.join(line[3].replace(":","").lower()),line[2],line[4]))

def check_sw_macs(serf_mac,mac_add_table,hostname):
	if mac_add_table.returncode > 0:
		print(click.style("[!] Looks like you entered a wrong switch password?",fg='red'))
		os.system("rm -f {}".format(tmp_pass)) ; sys.exit(1)

	def fix_mac(mac):
		index = 2
		_mac = [x for x in mac.replace(".","")]
		for x in range(5):
			_mac.insert(index, ':')
			index += 3
		return ''.join(_mac)
	
	for line in mac_add_table.stdout.strip().split('\n'):
		line = [j for j in filter(None, line.split(" "))]
		if 'DYNAMIC'.upper() in line:
			for mac in serf_mac:
				if line[1][-4:] in mac:
					newmac = [z for z in filter(None, mac.split(" "))]
					if mac.split()[0] == hostname:
						print(click.style("{:17}  {:17}  {:17}  {:15} {:15} {:7} {:16}".format(newmac[0],fix_mac(newmac[1]),fix_mac(newmac[2]),newmac[3],newmac[4],line[3],\
							''.join(map(str, line[5:8]))),fg='yellow',bold=True,reverse=True))
					else:
						print("{:17}  {:17}  {:17}  {:15} {:15}".format(newmac[0],fix_mac(newmac[1]),fix_mac(newmac[2]),newmac[3],newmac[4]),end="")
						print(click.style(" {:7} {:16}".format(line[3],''.join(map(str, line[5:8]))),fg='cyan'))

def bashrc(_pass):
	with open(('/home/{}/.bashrc').format(getuser()), "r+") as file:
		keyword = any("pass" in line for line in file)
		if not keyword:
			file.seek(0, os.SEEK_END)
			file.write("rm -f {}\n".format(_pass))

def main():
	if len(sys.argv) != 2:
		print(click.style("[!] You must specify a single hostname Edge host as an argument!", fg='red', bold=True))
		sys.exit(1)
	try:
		hostname = sys.argv[1]
		check_host(hostname)
		cluster = hostname.split('.')[2]+"c"+hostname.split('.')[1]
		cluster_rack = check_output("serfcli get {} --regular | grep cluster_rack | head -n1".format(hostname),
		    shell=True,encoding='utf-8',universal_newlines=False).rstrip('\n').split(" ")
		sw_cmd = 'sshpass -f {} ssh msw1{}.{}.{} {}'.format(tmp_pass,cluster_rack[2],hostname.split('.')[1],hostname.split('.')[2],
			'sh mac address-table')
		mac_add_table = run(sw_cmd, shell=True, stdout=PIPE, stderr=DEVNULL, encoding='ascii')

		get_serf_macs(cluster_rack,cluster)
		check_sw_macs(serf_mac,mac_add_table,hostname)
		bashrc(tmp_pass) 
		print(click.style("Switch: msw1{}.{}.{}".format(cluster_rack[2],hostname.split('.')[1],hostname.split('.')[2]),fg='magenta'))
	except KeyboardInterrupt:
		print(click.style("[!] CRTL + C detected!!", fg='red',blink=True))	

if __name__ == '__main__':
    main()