import threading
import logging
import time
from ssh_honeypot import HoneypotServer as SSHHoneypotServer
from ftp_honeypot import FTPHoneypot

def start_ssh():
    ssh_server = SSHHoneypotServer(host='0.0.0.0', port=2222)
    ssh_server.start()

def start_ftp():
    ftp_server = FTPHoneypot(host='0.0.0.0', port=2121)
    ftp_server.start()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Starting Multi-Port Honeypot System...")
    
    ssh_thread = threading.Thread(target=start_ssh, daemon=True)
    ftp_thread = threading.Thread(target=start_ftp, daemon=True)
    
    ssh_thread.start()
    ftp_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down Multi-Port Honeypot System...")
