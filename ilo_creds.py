#!/usr/bin/env python3.6
'''FNA and Edge ILO credentials'''
from subprocess import run, DEVNULL, PIPE
import re
import sys
import socket
import argparse
import click

PARSER = argparse.ArgumentParser(description='Fetch ILO credentials for Edge and FNA')
PARSER.add_argument("ilo_creds.py <host>")
ERRMSG2 = 'I could not seem to get creds for this server.'
ERRMSG1 = 'You must specify a single hostname FNA or Edge host as an argument!'

def check_host(hostname):
    """check hostname if valid and proceed, if not then execute the except block"""
    try:
        socket.gethostbyname(hostname)
        print("[~] Getting ILO credentials....")
    except socket.gaierror:
        print(click.style("[!] Cannot resolve hostname: {}".format(hostname), fg='yellow'))
        sys.exit(1)

def show_net_info(hostname, zline):
    '''get the ilo mac and print the ip/mac/url'''
    fnedge = (zline[1].split('.')[0], zline[1].split('.')[1], zline[1].split('.')[2])
    ilofqdn = '{}-oob.{}.{}.facebook.com'.format(fnedge[0], fnedge[1], fnedge[2])
    mac_cmd = 'serfcli get --fields oob.mac {}'.format(hostname)
    ilo_mac = run(mac_cmd, shell=True, stdout=PIPE, stderr=DEVNULL, encoding='utf-8')
    print("URL: https://{}".format(ilofqdn))
    print("ILO MAC: {}".format(ilo_mac.stdout.strip().split()[2]))
    print("ILO IP: {}".format(socket.gethostbyname(ilofqdn)))

def show_creds(line, hostname):
    '''Print creds and call show_net_info() if Edge'''
    zline = [z for z in line.replace(':', ' ').split()]
    print("{}: {}".format(zline[0], zline[1].replace(',', '')))
    print("{} {}: {}".format(zline[2], zline[3].capitalize(), zline[4].replace(',', '')))
    print("{} {}: {}".format(zline[5], zline[6].capitalize(), zline[7]))
    if list(zline[1].split('.'))[0][2] == 'e':
        show_net_info(hostname, zline)

def get_creds(hostname):
    '''take the hostname as the input and fetch the credentials'''
    cmd = 'ti edge get-ilo-creds {}'.format(hostname)
    creds = run(cmd, shell=True, stdout=PIPE, stderr=DEVNULL, encoding='utf-8')
    for line in creds.stdout.strip().split('\n'):
        if re.search('ERROR', line) or creds.stderr:
            print(("[!] {}".format(ERRMSG2)))
            sys.exit(1)
        elif any(re.findall(r'Higher|skipping|LINUX', line)):
            continue
        else:
            show_creds(line, hostname)

def main():
    '''main function'''
    if len(sys.argv) != 2:
        print(click.style("[!] {}".format(ERRMSG1), fg='yellow'))
        sys.exit(1)
    else:
        PARSER.parse_args()
        check_host(sys.argv[1])
        get_creds(sys.argv[1])

if __name__ == '__main__':
    main()
