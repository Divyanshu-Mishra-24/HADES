import threading
import logging
import time
import subprocess
import sys
from ssh_honeypot import HoneypotServer as SSHHoneypotServer
from ftp_honeypot import FTPHoneypot
from telnet_honeypot import TelnetHoneypot
from dns_honeypot import DNSHoneypot
from http_honeypot import HTTPHoneypot
from smtp_honeypot import SMTPHoneypot

def start_ssh():
    ssh_server = SSHHoneypotServer(host='0.0.0.0', port=2222)
    ssh_server.start()

def start_ftp():
    ftp_server = FTPHoneypot(host='0.0.0.0', port=2121)
    ftp_server.start()

def start_telnet():
    # Port 23 requires root/admin privileges.
    # If running as a non-root user, change port to e.g. 2323 and
    # forward with:  sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2323
    telnet_server = TelnetHoneypot(host='0.0.0.0', port=23)
    telnet_server.start()

def start_dns():
    dns_server = DNSHoneypot(host='0.0.0.0', port=5354)
    dns_server.start()

def start_http():
    http_server = HTTPHoneypot(host='0.0.0.0', port=8081)
    http_server.start()

def start_smtp():
    # Use 2525 to avoid needing admin privileges for port 25
    smtp_server = SMTPHoneypot(host='0.0.0.0', port=2525)
    smtp_server.start()

def start_attacker_terminal():
    logging.info("Launching Attacker Terminal...")
    try:
        subprocess.Popen([sys.executable, "attacker_terminal.py"])
    except Exception as e:
        logging.error(f"Failed to launch Attacker Terminal: {e}")

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Starting Multi-Port Honeypot System (SSH / FTP / Telnet / DNS)...")

    ssh_thread    = threading.Thread(target=start_ssh,    daemon=True)
    ftp_thread    = threading.Thread(target=start_ftp,    daemon=True)
    telnet_thread = threading.Thread(target=start_telnet, daemon=True)
    dns_thread    = threading.Thread(target=start_dns,    daemon=True)
    http_thread   = threading.Thread(target=start_http,   daemon=True)
    smtp_thread   = threading.Thread(target=start_smtp,   daemon=True)

    ssh_thread.start()
    ftp_thread.start()
    telnet_thread.start()
    dns_thread.start()
    http_thread.start()
    smtp_thread.start()

    # Launch Attacker Terminal
    start_attacker_terminal()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down Multi-Port Honeypot System...")