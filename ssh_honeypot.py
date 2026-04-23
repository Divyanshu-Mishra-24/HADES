import socket
import threading
import paramiko
import logging
import time
import random
import string
from database import HoneypotDatabase
from datetime import datetime

class SSHHoneypot(paramiko.ServerInterface):
    def __init__(self, client_ip, client_port, database):
        self.client_ip = client_ip
        self.client_port = client_port
        self.database = database
        self.session_id = None
        self.event = threading.Event()
        
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        fake_success = True
        
        self.session_id = self.database.log_authentication(
            self.client_ip, 
            self.client_port, 
            username, 
            password, 
            success=fake_success
        )
        
        if fake_success:
            logging.info(f"Fake successful login: {username}@{password} from {self.client_ip}")
            return paramiko.AUTH_SUCCESSFUL
        else:
            logging.info(f"Failed login attempt: {username}@{password} from {self.client_ip}")
            return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        self.database.log_authentication(
            self.client_ip, 
            self.client_port, 
            username, 
            "public_key_" + key.get_fingerprint().hex(),
            success=False
        )
        return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        return 'password,publickey'
    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

class FakeShell:
    def __init__(self, channel, session_id, database):
        self.channel = channel
        self.session_id = session_id
        self.database = database
        self.running = True
        
    def start(self):
        try:
            self.channel.send("Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-52-generic x86_64)\r\n")
            self.channel.send("Last login: Mon Jan 15 10:23:45 2024 from 192.168.1.100\r\n")
            self.channel.send("$ ")
            
            buffer = ""
            
            while self.running:
                try:
                    data = self.channel.recv(1024).decode('utf-8', errors='ignore')
                    if not data:
                        break
                    
                    buffer += data
                    
                    if '\r' in buffer or '\n' in buffer:
                        command_line = buffer.split('\r')[0].split('\n')[0].strip()
                        buffer = ""
                        
                        if command_line:
                            start_time = time.time()
                            output = self.process_command(command_line)
                            duration = time.time() - start_time
                            
                            parts = command_line.split()
                            command = parts[0] if parts else ""
                            args = ' '.join(parts[1:]) if len(parts) > 1 else ""
                            
                            self.database.log_command(
                                self.session_id, 
                                command, 
                                args, 
                                output,
                                duration, 
                                success=True
                            )
                        
                        self.channel.send("$ ")
                        
                except Exception as e:
                    logging.error(f"Error in shell: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"Shell error: {e}")
        finally:
            self.database.end_session(self.session_id)
    
    def process_command(self, command_line):
        parts = command_line.split()
        command = parts[0].lower() if parts else ""
        output = ""
        
        if command == 'ls':
            output = "Desktop  Documents  Downloads  Music  Pictures  Videos\r\nfile.txt  important.doc  backup.zip\r\n"
            self.channel.send(output)
            
        elif command == 'pwd':
            output = "/home/user\r\n"
            self.channel.send(output)
            
        elif command == 'whoami':
            output = "user\r\n"
            self.channel.send(output)
            
        elif command == 'id':
            output = "uid=1000(user) gid=1000(user) groups=1000(user),4(adm),24(cdrom),27(sudo)\r\n"
            self.channel.send(output)
            
        elif command == 'uname':
            args = parts[1] if len(parts) > 1 else ""
            if args == '-a':
                output = "Linux ubuntu 5.15.0-52-generic #58-Ubuntu SMP Thu Oct 13 08:03:55 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux\r\n"
            else:
                output = "Linux\r\n"
            self.channel.send(output)
                
        elif command == 'cat':
            if len(parts) > 1:
                filename = parts[1]
                if filename == 'file.txt':
                    output = "This is a sample file content.\r\n"
                elif filename == 'important.doc':
                    output = "Important document content here.\r\n"
                else:
                    output = f"cat: {filename}: No such file or directory\r\n"
            else:
                output = "cat: missing file operand\r\n"
            self.channel.send(output)
                
        elif command == 'ps':
            output = "  PID TTY          TIME CMD\r\n 1234 pts/0    00:00:01 bash\r\n 5678 pts/0    00:00:00 ps\r\n"
            self.channel.send(output)
            
        elif command == 'netstat':
            output = "Active Internet connections (servers and established)\r\ntcp        0      0 0.0.0.0:22            0.0.0.0:*               LISTEN\r\ntcp        0      0 127.0.0.1:3306         0.0.0.0:*               LISTEN\r\n"
            self.channel.send(output)
            
        elif command == 'exit' or command == 'logout':
            output = "logout\r\n"
            self.channel.send(output)
            self.running = False
            
        elif command == 'sudo':
            output = "[sudo] password for user: "
            self.channel.send(output)
            try:
                password = self.channel.recv(1024).decode('utf-8', errors='ignore').strip()
                self.channel.send("Sorry, try again.\r\n")
                self.channel.send("[sudo] password for user: ")
                password = self.channel.recv(1024).decode('utf-8', errors='ignore').strip()
                self.channel.send("sudo: 1 incorrect password attempt\r\n")
                output += "****\r\nsudo: 1 incorrect password attempt\r\n"
            except:
                pass
                
        elif command == 'wget' or command == 'curl':
            output = f"{command}: command not found\r\n"
            self.channel.send(output)
            
        elif command == 'rm':
            output = "rm: cannot remove 'file': Permission denied\r\n"
            self.channel.send(output)
            
        elif command == 'mkdir':
            output = "mkdir: cannot create directory 'test': Permission denied\r\n"
            self.channel.send(output)
            
        elif command == 'chmod':
            output = "chmod: changing permissions of 'file': Operation not permitted\r\n"
            self.channel.send(output)
            
        elif command == 'help':
            output = "These shell commands are defined internally. Type `help' to see this list.\r\n"
            self.channel.send(output)
            
        else:
            output = f"{command}: command not found\r\n"
            self.channel.send(output)
            
        return output.strip()

class HoneypotServer:
    def __init__(self, host='0.0.0.0', port=2222):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()
        self.host_key = self.generate_host_key()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def generate_host_key(self):
        host_key = paramiko.RSAKey.generate(2048)
        return host_key
    
    def handle_client(self, client, client_ip, client_port):
        try:
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)
            
            server = SSHHoneypot(client_ip, client_port, self.database)
            
            transport.start_server(server=server)
            
            channel = transport.accept(20)
            if channel is None:
                transport.close()
                return
            
            if server.session_id:
                shell = FakeShell(channel, server.session_id, self.database)
                shell.start()
            
            channel.close()
            transport.close()
            
        except Exception as e:
            logging.error(f"Error handling client {client_ip}:{client_port} - {e}")
            try:
                client.close()
            except:
                pass
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(100)
        
        logging.info(f"SSH Honeypot listening on {self.host}:{self.port}")
        
        try:
            while True:
                client, addr = server_socket.accept()
                client_ip, client_port = addr
                
                logging.info(f"New connection from {client_ip}:{client_port}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, client_ip, client_port),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            logging.info("Shutting down honeypot...")
        finally:
            server_socket.close()

