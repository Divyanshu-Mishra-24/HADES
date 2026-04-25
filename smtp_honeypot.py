import socket
import threading
import base64
import logging
from datetime import datetime
from database import HoneypotDatabase

class SMTPHoneypot:
    def __init__(self, host='0.0.0.0', port=2525):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()
        self.banner = b"220 mail.hades-security.com ESMTP Postfix\r\n"

    def _decode_base64(self, data):
        try:
            return base64.b64decode(data).decode('utf-8', errors='ignore')
        except:
            return data

    def handle_client(self, conn, addr):
        ip = addr[0]
        port = addr[1]
        logging.info(f"SMTP Connection from {ip}:{port}")

        session_data = {
            'ehlo': None,
            'mail_from': None,
            'rcpt_to': [],
            'username': None,
            'password': None,
            'data': "",
            'subject': None
        }

        try:
            conn.send(self.banner)

            # ✅ FIX: line-based reading
            conn_file = conn.makefile('r')

            while True:
                line = conn_file.readline()
                if not line:
                    break

                line = line.strip()
                logging.debug(f"SMTP {ip} >> {line}")

                # ---------------- EHLO / HELO ----------------
                if line.upper().startswith(('EHLO', 'HELO')):
                    session_data['ehlo'] = line.split(' ', 1)[1] if ' ' in line else line
                    conn.send(b"250-mail.hades-security.com Hello " + ip.encode() + b"\r\n")
                    conn.send(b"250-AUTH LOGIN PLAIN\r\n")
                    conn.send(b"250-SIZE 52428800\r\n")
                    conn.send(b"250 8BITMIME\r\n")

                # ---------------- AUTH LOGIN ----------------
                elif line.upper().startswith('AUTH LOGIN'):
                    conn.send(b"334 VXNlcm5hbWU6\r\n")  # Username:

                    user_raw = conn_file.readline().strip()
                    session_data['username'] = self._decode_base64(user_raw)

                    conn.send(b"334 UGFzc3dvcmQ6\r\n")  # Password:

                    pass_raw = conn_file.readline().strip()
                    session_data['password'] = self._decode_base64(pass_raw)

                    logging.info(
                        f"SMTP CREDENTIALS captured from {ip}: "
                        f"{session_data['username']}:{session_data['password']}"
                    )

                    self.database.log_authentication(
                        ip, port,
                        session_data['username'],
                        session_data['password'],
                        success=False,
                        service='smtp'
                    )

                    conn.send(b"535 Authentication failed\r\n")

                # ---------------- MAIL FROM ----------------
                elif line.upper().startswith('MAIL FROM:'):
                    session_data['mail_from'] = line[10:].strip('<>')
                    conn.send(b"250 OK\r\n")

                # ---------------- RCPT TO ----------------
                elif line.upper().startswith('RCPT TO:'):
                    recipient = line[8:].strip('<>')
                    session_data['rcpt_to'].append(recipient)
                    conn.send(b"250 OK\r\n")

                # ---------------- DATA ----------------
                elif line.upper().startswith('DATA'):
                    conn.send(b"354 End data with <CR><LF>.<CR><LF>\r\n")

                    email_body = ""

                    while True:
                        data_line = conn_file.readline()
                        if not data_line:
                            break

                        if data_line.strip() == ".":
                            break

                        email_body += data_line

                        if len(email_body) > 100000:
                            break

                    session_data['data'] = email_body

                    # Extract subject
                    for b_line in email_body.split('\n'):
                        if b_line.lower().startswith('subject:'):
                            session_data['subject'] = b_line[8:].strip()
                            break

                    logging.info(
                        f"SMTP EMAIL captured from {ip} to {session_data['rcpt_to']}"
                    )

                    self.database.log_smtp_event(
                        src_ip=ip,
                        src_port=port,
                        ehlo=session_data['ehlo'],
                        mail_from=session_data['mail_from'],
                        rcpt_to=", ".join(session_data['rcpt_to']),
                        subject=session_data['subject'],
                        data=session_data['data'],
                        username=session_data['username'],
                        password=session_data['password']
                    )

                    conn.send(b"250 Message accepted for delivery\r\n")

                # ---------------- QUIT ----------------
                elif line.upper().startswith('QUIT'):
                    conn.send(b"221 2.0.0 Bye\r\n")
                    break

                # ---------------- RESET ----------------
                elif line.upper().startswith('RSET'):
                    session_data['mail_from'] = None
                    session_data['rcpt_to'] = []
                    session_data['data'] = ""
                    session_data['subject'] = None
                    conn.send(b"250 OK\r\n")

                # ---------------- NOOP ----------------
                elif line.upper().startswith('NOOP'):
                    conn.send(b"250 OK\r\n")

                # ---------------- UNKNOWN ----------------
                else:
                    conn.send(b"500 5.5.1 Command unrecognized\r\n")

        except Exception as e:
            logging.error(f"SMTP Error with {ip}: {e}")
        finally:
            conn.close()
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.host, self.port))
            server.listen(10)
            logging.info(f"SMTP Honeypot listening on {self.host}:{self.port}")

            while True:
                conn, addr = server.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
        except Exception as e:
            logging.error(f"Failed to start SMTP Honeypot: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    honeypot = SMTPHoneypot(port=2525)
    honeypot.start()
