import socket
import threading
import logging
import time
from database import HoneypotDatabase


class TelnetHoneypot:
    def __init__(self, host='0.0.0.0', port=23):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()

        # Telnet option negotiation bytes
        self.IAC  = bytes([255])
        self.DONT = bytes([254])
        self.DO   = bytes([253])
        self.WONT = bytes([252])
        self.WILL = bytes([251])
        self.SB   = bytes([250])
        self.SE   = bytes([240])

        # Telnet options
        self.OPT_ECHO            = bytes([1])
        self.OPT_SUPPRESS_GA     = bytes([3])
        self.OPT_TERMINAL_TYPE   = bytes([24])
        self.OPT_NAWS            = bytes([31])

    # ------------------------------------------------------------------ #
    #  Low-level helpers                                                   #
    # ------------------------------------------------------------------ #

    def _send(self, conn, data: bytes):
        try:
            conn.sendall(data)
        except Exception:
            pass

    def _recv_line(self, conn, timeout=30) -> str:
        """Read bytes until CRLF or LF, strip Telnet IAC sequences."""
        conn.settimeout(timeout)
        buf = b""
        try:
            while True:
                ch = conn.recv(1)
                if not ch:
                    break
                if ch == self.IAC:
                    opt = conn.recv(2)   # command + option byte
                    # Refuse all option requests gracefully
                    if opt and opt[0:1] in (self.DO, self.DONT):
                        self._send(conn, self.IAC + self.WONT + opt[1:2])
                    elif opt and opt[0:1] in (self.WILL, self.WONT):
                        self._send(conn, self.IAC + self.DONT + opt[1:2])
                    continue
                if ch in (b'\r', b'\n'):
                    if buf:
                        break
                    continue
                buf += ch
        except socket.timeout:
            pass
        return buf.decode('utf-8', errors='ignore').strip()

    def _negotiate(self, conn):
        """Send initial Telnet option negotiations."""
        # Ask client to suppress go-ahead and echo
        self._send(conn, self.IAC + self.WILL + self.OPT_SUPPRESS_GA)
        self._send(conn, self.IAC + self.WILL + self.OPT_ECHO)
        self._send(conn, self.IAC + self.DO   + self.OPT_TERMINAL_TYPE)
        self._send(conn, self.IAC + self.DO   + self.OPT_NAWS)
        time.sleep(0.1)

    # ------------------------------------------------------------------ #
    #  Client handler                                                      #
    # ------------------------------------------------------------------ #

    def handle_client(self, conn, addr):
        client_ip, client_port = addr
        logging.info(f"New Telnet connection from {client_ip}:{client_port}")

        session_id = None
        username   = None

        try:
            self._negotiate(conn)

            # ---- login prompt ---- #
            self._send(conn, b"\r\nDebian GNU/Linux 11\r\n\r\n")
            self._send(conn, b"login: ")
            username = self._recv_line(conn)
            if not username:
                return

            self._send(conn, b"Password: ")
            password = self._recv_line(conn)
            if not password:
                return

            # Log the attempt — honeypot always "succeeds"
            session_id = self.database.log_authentication(
                client_ip, client_port, username, password,
                success=True, service='telnet'
            )
            logging.info(
                f"Telnet fake login: {username}:{password} from {client_ip}"
            )

            # Small delay to feel authentic
            time.sleep(0.5)
            self._send(conn,
                b"\r\nLast login: Mon Apr 14 09:23:11 2025 from 192.168.1.2\r\n"
                b"Linux debian-server 5.10.0-21-amd64 #1 SMP Debian 5.10.162-1 "
                b"(2023-01-21) x86_64\r\n\r\n"
            )

            # ---- fake shell loop ---- #
            prompt = f"{username}@debian-server:~$ ".encode()

            # Fake filesystem for ls
            fake_ls = (
                b"total 32\r\n"
                b"drwxr-xr-x 2 " + username.encode() + b" " + username.encode() + b"  4096 Apr 10 08:00 .\r\n"
                b"drwxr-xr-x 3 root root 4096 Apr 10 07:58 ..\r\n"
                b"-rw-r--r-- 1 " + username.encode() + b" " + username.encode() + b"   220 Apr 10 07:58 .bash_logout\r\n"
                b"-rw-r--r-- 1 " + username.encode() + b" " + username.encode() + b"  3526 Apr 10 07:58 .bashrc\r\n"
                b"-rw-r--r-- 1 " + username.encode() + b" " + username.encode() + b"   807 Apr 10 07:58 .profile\r\n"
            )

            while True:
                self._send(conn, b"\r\n" + prompt)
                raw = self._recv_line(conn)
                if not raw:
                    break

                parts   = raw.split(None, 1)
                cmd     = parts[0].lower()
                args    = parts[1] if len(parts) > 1 else ""

                start = time.time()

                if cmd in ('exit', 'logout', 'quit'):
                    self._send(conn, b"logout\r\n")
                    break
                elif cmd == 'whoami':
                    self._send(conn, username.encode() + b"\r\n")
                elif cmd == 'id':
                    self._send(conn,
                        f"uid=1000({username}) gid=1000({username}) "
                        f"groups=1000({username}),27(sudo)\r\n".encode()
                    )
                elif cmd == 'pwd':
                    self._send(conn, f"/home/{username}\r\n".encode())
                elif cmd == 'hostname':
                    self._send(conn, b"debian-server\r\n")
                elif cmd == 'uname':
                    self._send(conn,
                        b"Linux debian-server 5.10.0-21-amd64 #1 SMP Debian "
                        b"5.10.162-1 x86_64 GNU/Linux\r\n"
                    )
                elif cmd == 'ls':
                    self._send(conn, fake_ls)
                elif cmd == 'cat':
                    if args in ('/etc/passwd', 'passwd'):
                        self._send(conn,
                            b"root:x:0:0:root:/root:/bin/bash\r\n"
                            b"daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\r\n"
                            + username.encode() + b":x:1000:1000::/home/"
                            + username.encode() + b":/bin/bash\r\n"
                        )
                    else:
                        self._send(conn,
                            f"cat: {args}: No such file or directory\r\n".encode()
                        )
                elif cmd == 'echo':
                    self._send(conn, args.encode() + b"\r\n")
                elif cmd == 'ifconfig' or cmd == 'ip':
                    self._send(conn,
                        b"eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\r\n"
                        b"        inet 10.0.2.15  netmask 255.255.255.0  broadcast 10.0.2.255\r\n"
                    )
                elif cmd == 'history':
                    self._send(conn,
                        b"    1  ls\r\n    2  pwd\r\n    3  whoami\r\n    4  history\r\n"
                    )
                elif cmd == '':
                    pass  # blank line — just re-show prompt
                else:
                    self._send(conn,
                        f"-bash: {cmd}: command not found\r\n".encode()
                    )

                duration = time.time() - start
                if session_id:
                    self.database.log_command(
                        session_id, cmd, args, duration, success=True
                    )

        except Exception as e:
            logging.error(
                f"Error handling Telnet client {client_ip}:{client_port} — {e}"
            )
        finally:
            if session_id:
                self.database.end_session(session_id)
            conn.close()
            logging.info(f"Telnet session closed for {client_ip}:{client_port}")

    # ------------------------------------------------------------------ #
    #  Server                                                              #
    # ------------------------------------------------------------------ #

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)

        logging.info(f"Telnet Honeypot listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = server_socket.accept()
                t = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                t.start()
        except KeyboardInterrupt:
            logging.info("Shutting down Telnet honeypot...")
        finally:
            server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    honeypot = TelnetHoneypot()
    honeypot.start()