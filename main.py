import argparse
import random
import socket
import time
import typing
from urllib.parse import urlparse

import requests
from pyfiglet import Figlet
from termcolor import colored

from errors import FetchedError

# URL for fetching relays
onion_url = (
    "https://onionoo.torproject.org/details?type=relay"
    "&running=true&fields=fingerprint,or_addresses"
)
# Custom user agent
user_agent = (
    "Mozilla/5.0 (Linux; Android 10; Android SDK built for x86) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 "
)


# Checking a port for bad ports described below
def check_port(addr) -> bool:
    bad_ports = [
        1,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
        20,
        21,
        22,
        23,
        25,
        37,
        42,
        43,
        53,
        69,
        77,
        79,
        87,
        95,
        101,
        102,
        103,
        104,
        109,
        110,
        111,
        113,
        115,
        117,
        119,
        123,
        135,
        137,
        139,
        143,
        161,
        179,
        389,
        427,
        465,
        512,
        513,
        514,
        515,
        526,
        530,
        531,
        532,
        540,
        548,
        554,
        556,
        563,
        587,
        601,
        636,
        989,
        990,
        993,
        995,
        1719,
        1720,
        1723,
        2049,
        3659,
        4045,
        5060,
        5061,
        6000,
        6566,
        6665,
        6666,
        6667,
        6668,
        6669,
        6697,
        10080,
    ]

    return int(addr.split(":")[1]) not in bad_ports


# Check remote port opened/closed(filtered)
def is_socket_open(addr: str = None) -> bool:
    if addr is None:
        return False

    addrs = addr.split(':')
    if len(addrs) < 2:
        return False

    try:
        # Trying open remote socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(2.0)
        result = sock.connect_ex((addrs[0], int(addrs[1])))
        sock.close()

        return result == 0
    except Exception as ex:
        print(f'Unhandled is_socket_open {ex}')
        pass

    return False


# Fetching list of relays from tor website

# proxy_list:
# is the proxy string divided by comma
#
# For example
# fetch_relays(proxy="http://proxy-one.org:8888,http://proxy-two.org:8881", relays_number=30)
def fetch_relays(proxy: str = None, relays_number: typing.Optional[int] = 30, timeout: typing.Optional[int] = 5) -> str:
    random.seed(time.time(), 2)

    if proxy is None:
        try:
            resp = requests.get(onion_url, timeout=timeout, headers={'User-Agent': user_agent})
            if resp.status_code != 200:
                raise FetchedError(f'Fetching error, server response code is {resp.status_code}')

            return parse_relays(resp.json(), relays_number)
        except requests.ConnectionError:
            raise FetchedError(f'Fetching error, server connection error')
        except Exception as com:
            print(com.__str__())
            raise FetchedError(com)

    proxies = dict()
    proxy_list = proxy.split(',')

    for addr in proxy_list:
        url = urlparse(addr)
        proxies[url.scheme] = addr
        try:
            resp = requests.get(url=onion_url, timeout=timeout,
                                headers={'User-Agent': user_agent}, proxies=proxies,
                                verify=False)
            if resp.status_code != 200:
                raise FetchedError(f'Fetching error, server response code is {resp.status_code}')

            return parse_relays(resp.json(), relays_number)
        except (ConnectionError, ConnectionResetError, requests.ConnectionError) as conn:
            print(colored(f'Proxy {url.hostname}:{url.port} is down', 'red'))
            pass
        except Exception as common:
            raise FetchedError(common)

    raise FetchedError(f'Fetching error, bad proxies')


# Parse JSON list of relays
def parse_relays(json: dict, relays_number: int = 30) -> str:
    relays = json

    if 'relays' not in relays:
        raise FetchedError(f'Fetching error, relays not found')

    filtered_relays = []

    # max relays number
    counter = len(relays['relays'])

    # Loop for filling validated relays list
    while counter > 0 and len(filtered_relays) < relays_number:
        rnd = random.randint(0, len(relays['relays']) - 1)
        relay = relays['relays'][rnd]
        for addr in relay['or_addresses']:
            if addr.find("[") == -1 and check_port(addr) and is_socket_open(addr):
                filtered_relays.append(addr + ' ' + relay['fingerprint'])
        counter -= 1

    return '\n'.join(filtered_relays)


parser = argparse.ArgumentParser(description='List the content of a folder')

parser.add_argument('-p',
                    '--proxy',
                    help='pass proxy list')
parser.add_argument('-t',
                    '--timeout',
                    type=int,
                    help='fetch timeout')

parser.add_argument('-c',
                    '--count',
                    type=int,
                    help='relays count')

args = parser.parse_args()

custom_fig = Figlet(font='graffiti')
print(custom_fig.renderText('tor2rel'))
print('Trying to load relays...')

try:
    output = fetch_relays(proxy=args.proxy, relays_number=args.count, timeout=args.timeout)
    print('Load successful\n')
    print(colored(output, 'green'))
except FetchedError as fe:
    print(colored(fe.__str__(), 'red'))
except Exception as e:
    print(colored(f'Unhandled error: {e.__str__()}', 'red'))
