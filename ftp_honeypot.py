import socket
import threading
import logging
import time
from datetime import datetime
from database import HoneypotDatabase

class FTPHoneypot:
    def __init__(self, host='0.0.0.0', port=2121):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()

    def handle_client(self, conn, addr):
        client_ip, client_port = addr
        logging.info(f"New FTP connection from {client_ip}:{client_port}")
        
        conn.sendall(b"220 Welcome to FTP Server\r\n")
        
        username = None
        password = None
        authenticated = False
        session_id = None
        
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                cmd_line = data.decode('utf-8', errors='ignore').strip()
                if not cmd_line:
                    continue
                    
                parts = cmd_line.split(' ', 1)
                cmd = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""
                
                # Pre-authentication commands
                if cmd == 'USER':
                    username = args
                    conn.sendall(b"331 Please specify the password.\r\n")
                elif cmd == 'PASS':
                    password = args
                    
                    # Log authentication attempt
                    # For a honeypot, we might let them in
                    session_id = self.database.log_authentication(
                        client_ip, client_port, username, password, success=True, service='ftp'
                    )
                    authenticated = True
                    conn.sendall(b"230 Login successful.\r\n")
                    logging.info(f"FTP Fake successful login: {username}@{password} from {client_ip}")
                elif cmd == 'QUIT':
                    conn.sendall(b"221 Goodbye.\r\n")
                    break
                else:
                    if not authenticated:
                        conn.sendall(b"530 Please login with USER and PASS.\r\n")
                    else:
                        start_time = time.time()
                        # Handle basic authenticated commands
                        output = ""
                        if cmd == 'SYST':
                            output = "215 UNIX Type: L8\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'FEAT':
                            output = "211-Features:\r\n EPRT\r\n EPSV\r\n MDTM\r\n PASV\r\n REST STREAM\r\n SIZE\r\n TVFS\r\n211 End\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'PWD':
                            output = "257 \"/\" is the current directory\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'TYPE':
                            output = f"200 Switching to {args} mode.\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'PASV':
                            output = "502 Command not implemented.\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'PORT':
                            output = "502 Command not implemented.\r\n"
                            conn.sendall(output.encode())
                        elif cmd == 'LIST':
                            output = "425 Can't open data connection.\r\n"
                            conn.sendall(output.encode())
                        else:
                            output = "500 Unknown command.\r\n"
                            conn.sendall(output.encode())
                        
                        duration = time.time() - start_time
                        if session_id:
                            self.database.log_command(session_id, cmd, args, output.strip(), duration, success=True)
                            
        except Exception as e:
            logging.error(f"Error handling FTP client {client_ip}:{client_port} - {e}")
        finally:
            if session_id:
                self.database.end_session(session_id)
            conn.close()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        logging.info(f"FTP Honeypot listening on {self.host}:{self.port}")
        
        try:
            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            logging.info("Shutting down FTP honeypot...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    # Basic setup for standalone testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    honeypot = FTPHoneypot()
    honeypot.start()
