import socket
import threading
import logging
from dnslib import DNSRecord, QTYPE, RR, A
from database import HoneypotDatabase

class DNSHoneypot:
    def __init__(self, host='0.0.0.0', port=5354):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()
        
    def handle_request(self, data, addr, sock):
        client_ip, client_port = addr
        try:
            request = DNSRecord.parse(data)
            query_name = str(request.q.qname).strip('.')
            query_type = QTYPE[request.q.qtype]
            
            logging.info(f"DNS Query from {client_ip}:{client_port} - {query_name} ({query_type})")
            
            # Log to database
            self.database.log_dns_query(
                src_ip=client_ip,
                src_port=client_port,
                query_name=query_name,
                query_type=query_type,
                record_class='IN'
            )
            
            # Craft a fake response (NXDOMAIN or a dummy IP)
            reply = request.reply()
            # Optionally add a fake answer to keep them interested
            reply.add_answer(RR(query_name, QTYPE.A, rdata=A("1.2.3.4"), ttl=60))
            
            sock.sendto(reply.pack(), addr)
            
        except Exception as e:
            logging.error(f"Error parsing DNS packet from {client_ip}: {e}")

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(("0.0.0.0", self.port))
            logging.info(f"DNS Honeypot listening on {self.host}:{self.port} (UDP)")
        except PermissionError:
            logging.error(f"Permission denied to bind to port {self.port}. Try running with elevated privileges.")
            return
        except Exception as e:
            logging.error(f"Failed to start DNS Honeypot: {e}")
            return

        try:
            while True:
                data, addr = sock.recvfrom(512)
                # Handle each request in a separate thread for concurrency
                thread = threading.Thread(
                    target=self.handle_request,
                    args=(data, addr, sock),
                    daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            logging.info("Shutting down DNS Honeypot...")
        finally:
            sock.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    honeypot = DNSHoneypot()
    honeypot.start()
