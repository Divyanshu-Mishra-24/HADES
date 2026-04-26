import tkinter as tk
from tkinter import font, scrolledtext
import socket
import requests
import threading
import paramiko
import time
import queue
import sys
import os
import subprocess
import tempfile

# -----------------------------
# Configuration
# -----------------------------
TARGET_IP = "127.0.0.1"
PORTS = {
    "SSH": 2222,
    "FTP": 2121,
    "HTTP": 8081,
    "DNS": 5354,
    "SMTP": 2525
}

# -----------------------------
# Cyberpunk Theme Colors
# -----------------------------
CP_BG = "#050505"
CP_CYAN = "#00f3ff"
CP_YELLOW = "#f3ec19"
CP_RED = "#ff003c"
CP_GREEN = "#00ff9f"
CP_MAGENTA = "#ff00ff"
CP_WHITE = "#ffffff"

# -----------------------------
# Terminal UI Class
# -----------------------------
class AttackerTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("| HADES |")
        self.root.geometry("950x650")
        self.root.configure(bg=CP_BG)

        # Set font
        self.terminal_font = font.Font(family="Consolas", size=11, weight="bold")
        
        # UI Components
        self.output_area = scrolledtext.ScrolledText(
            root, 
            bg=CP_BG, 
            fg=CP_CYAN, 
            insertbackground=CP_YELLOW,
            font=self.terminal_font,
            borderwidth=0,
            highlightthickness=0,
            padx=15,
            pady=15
        )
        self.output_area.pack(expand=True, fill="both")
        
        # Tags for styling (Cyberpunk Palette)
        self.output_area.tag_config("prompt", foreground=CP_YELLOW)
        self.output_area.tag_config("error", foreground=CP_RED)
        self.output_area.tag_config("success", foreground=CP_GREEN)
        self.output_area.tag_config("info", foreground=CP_MAGENTA)
        self.output_area.tag_config("warning", foreground=CP_YELLOW)
        self.output_area.tag_config("neutral", foreground=CP_CYAN)

        # Session state
        self.current_session = None
        self.input_queue = queue.Queue()
        
        # Bindings
        self.output_area.bind("<Return>", self.process_input)
        self.output_area.bind("<Control-c>", self.interrupt_session)
        self.output_area.bind("<BackSpace>", self.handle_backspace)
        self.output_area.bind("<Delete>", self.handle_backspace)
        self.output_area.bind("<Left>", self.handle_left)
        self.output_area.bind("<Home>", self.handle_home)
        self.output_area.bind("<Key>", self.handle_typing)
        self.output_area.bind("<<Cut>>", self.handle_cut)
        
        # Start prompt
        self.print_banner()
        self.show_prompt()
        
        self.output_area.focus_set()

    def print_banner(self):
        banner = """
 ██╗  ██╗ █████╗ ██████╗ ███████╗███████╗
 ██║  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
 ███████║███████║██║  ██║█████╗  ███████╗
 ██╔══██║██╔══██║██║  ██║██╔══╝  ╚════██║
 ██║  ██║██║  ██║██████╔╝███████╗███████║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝
 >>> SYSTEM INITIALIZED | HADES NEURAL INTERFACE v2.0.7
 >>> WARNING: UNTRUSTED CONNECTION DETECTED
 >>> STATUS: [READY FOR EXPLOITATION]
"""
        self.write(banner, "info")

    def show_prompt(self):
        if self.current_session:
            prompt = f"{self.current_session.prompt_prefix} "
        else:
            prompt = "netrunner@hades:~$ "
        self.write(prompt, "prompt")
        self.output_area.mark_set("input_start", "end-1c")
        self.output_area.mark_gravity("input_start", "left")
        self.output_area.see(tk.END)

    def write(self, text, tag="neutral"):
        self.output_area.insert(tk.END, text, tag)
        self.output_area.see(tk.END)

    def handle_backspace(self, event):
        try:
            sel_start = self.output_area.index(tk.SEL_FIRST)
            if self.output_area.compare(sel_start, "<", "input_start"): return "break"
        except tk.TclError:
            if self.output_area.compare(tk.INSERT, "<=", "input_start"): return "break"

    def handle_cut(self, event):
        try:
            sel_start = self.output_area.index(tk.SEL_FIRST)
            if self.output_area.compare(sel_start, "<", "input_start"): return "break"
        except tk.TclError: return "break"

    def handle_left(self, event):
        if self.output_area.compare(tk.INSERT, "<=", "input_start"): return "break"

    def handle_home(self, event):
        self.output_area.mark_set(tk.INSERT, "input_start")
        return "break"

    def handle_typing(self, event):
        if self.output_area.compare(tk.INSERT, "<", "input_start"):
            self.output_area.mark_set(tk.INSERT, "end-1c")

    def process_input(self, event):
        input_text = self.output_area.get("input_start", "end-1c").strip()
        if self.current_session:
            p = self.current_session.prompt_prefix
            if p and input_text.startswith(p): input_text = input_text[len(p):].strip()
        self.write("\n")
        self.output_area.mark_set("input_start", tk.END)
        if self.current_session: self.input_queue.put(input_text)
        else:
            if input_text: self.execute_local_command(input_text)
            else: self.show_prompt()
        return "break"

    def interrupt_session(self, event):
        if self.current_session:
            self.write("\n^C KILL SIGNAL SENT...\n", "warning")
            self.current_session.stop(); self.current_session = None; self.show_prompt()
        return "break"

    def execute_local_command(self, cmd_line):
        parts = cmd_line.split()
        if not parts: self.show_prompt(); return
        cmd, args = parts[0].lower(), parts[1:]
        if cmd == "help": self.show_help(); self.show_prompt()
        elif cmd == "clear": self.output_area.delete("1.0", tk.END); self.show_prompt()
        elif cmd == "exit": self.root.destroy(); os._exit(0)
        elif cmd == "ssh": self.start_ssh_session(args)
        elif cmd == "ftp": self.start_ftp_session(args)
        elif cmd == "smtp": self.start_smtp_session(args)
        elif cmd == "python": self.run_python_cmd(args)
        elif cmd.startswith("$") or cmd in ["powershell", "pwsh"]: self.run_powershell_cmd(cmd_line)
        elif cmd in ["curl", "wget"]: self.run_http_attack(args)
        elif cmd == "nmap": self.run_nmap_scan(args)
        elif cmd == "sqlmap": self.run_sqlmap_sim(args)
        elif cmd == "whois": self.run_whois_sim(args)
        else: self.run_powershell_cmd(cmd_line)

    def show_help(self):
        help_text = """
>>> CRYPTIC-LINK AVAILABLE COMMANDS:
  ssh <user>@<ip>  - Secure Shell Infiltration
  ftp <ip>         - File Transfer Hijack
  smtp <ip>        - Mail Relay Exploitation
  curl <url>       - Web Endpoint Request
  nmap <ip>        - Neural Network Scan
  sqlmap <url>     - DB Injection Simulation
  python -c "..."  - Direct Script Execution
  $ <command>      - Host PowerShell Bridge
  clear / exit     - Terminal Control
"""
        self.write(help_text, "info")

    def start_ssh_session(self, args):
        if not args: self.write("Usage: ssh <user>@<ip>\n", "warning"); self.show_prompt(); return
        user_host = args[0]
        port = PORTS["SSH"]
        if "-p" in args:
            try: port = int(args[args.index("-p")+1])
            except: pass
        username, host = user_host.split("@") if "@" in user_host else ("root", user_host)
        self.write(f"[!] INITIATING SECURE SHELL HANDSHAKE TO {host}:{port}...\n", "warning")
        self.write(f"[?] Confirm establish link? (y/n): ", "warning")
        self.output_area.mark_set("input_start", "end-1c")
        self.current_session = InteractiveSession(self, host, port, "")
        def handle():
            if self.input_queue.get().strip().lower() == 'y':
                self.write(f"[>] {username}@{host}'s ACCESS KEY: ")
                self.output_area.mark_set("input_start", "end-1c")
                pwd = self.input_queue.get().strip()
                session = SSHSession(self, host, port, username, pwd)
                self.current_session = session; session.run()
            else: self.write("[-] Connection Aborted.\n", "error"); self.current_session = None; self.root.after(0, self.show_prompt)
        threading.Thread(target=handle, daemon=True).start()

    def start_ftp_session(self, args):
        host = args[0] if args else TARGET_IP
        port = PORTS["FTP"]
        self.write(f"[!] ATTEMPTING FTP HANDSHAKE TO {host}:{port}...\n", "warning")
        self.write(f"[?] Confirm establish link? (y/n): ", "warning")
        self.output_area.mark_set("input_start", "end-1c")
        self.current_session = InteractiveSession(self, host, port, "")
        def handle():
            if self.input_queue.get().strip().lower() == 'y':
                self.write(f"[>] Name ({host}:netrunner): ")
                self.output_area.mark_set("input_start", "end-1c")
                u = self.input_queue.get().strip()
                self.write("[>] Access Key: ")
                self.output_area.mark_set("input_start", "end-1c")
                p = self.input_queue.get().strip()
                session = FTPSession(self, host, port, u, p)
                self.current_session = session; session.run()
            else: self.write("[-] Connection Aborted.\n", "error"); self.current_session = None; self.root.after(0, self.show_prompt)
        threading.Thread(target=handle, daemon=True).start()

    def start_smtp_session(self, args):
        host = args[0] if args else TARGET_IP
        port = PORTS["SMTP"]
        self.write(f"[!] ESTABLISHING SMTP RELAY TO {host}:{port}? (y/n): ", "warning")
        self.output_area.mark_set("input_start", "end-1c")
        self.current_session = InteractiveSession(self, host, port, "")
        def handle():
            if self.input_queue.get().strip().lower() == 'y':
                session = SMTPSession(self, host, port)
                self.current_session = session; session.run()
            else: self.write("[-] Aborted.\n", "error"); self.current_session = None; self.root.after(0, self.show_prompt)
        threading.Thread(target=handle, daemon=True).start()

    def run_python_cmd(self, args):
        if "-c" in args:
            code = " ".join(args[args.index("-c")+1:])[1:-1]
            def exec_p():
                import io
                from contextlib import redirect_stdout, redirect_stderr
                out = io.StringIO()
                try:
                    with redirect_stdout(out), redirect_stderr(out):
                        exec(code, {"socket": socket, "requests": requests, "time": time})
                    self.write(out.getvalue())
                except Exception as e: self.write(f"SYNTAX ERROR: {e}\n", "error")
                self.root.after(0, self.show_prompt)
            threading.Thread(target=exec_p, daemon=True).start()
        else: self.write("Usage: python -c \"<code>\"\n", "warning"); self.show_prompt()

    def run_powershell_cmd(self, script):
        self.write("[!] BRIDGING TO HOST POWER-SHELL CORE...\n", "info")
        def ex_ps():
            fd, path = tempfile.mkstemp(suffix=".ps1")
            try:
                with os.fdopen(fd, 'w') as tmp: tmp.write(script)
                p = subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", path], stdout=subprocess.PIPE, text=True)
                stdout, _ = p.communicate()
                if stdout: self.write(stdout)
            finally:
                if os.path.exists(path): os.remove(path)
            self.root.after(0, self.show_prompt)
        threading.Thread(target=ex_ps, daemon=True).start()

    def run_http_attack(self, args):
        if not args: self.show_prompt(); return
        url = args[0] if args[0].startswith("http") else f"http://{args[0]}"
        def do():
            try:
                r = requests.get(url, headers={"User-Agent": "CYBER-NETRUNNER/1.0"}, timeout=5)
                self.write(f"LINK STATUS: {r.status_code}\nDATA: {r.text[:200]}...\n", "success")
            except: self.write("[-] LINK FAILURE\n", "error")
            self.root.after(0, self.show_prompt)
        threading.Thread(target=do, daemon=True).start()

    def run_nmap_scan(self, args):
        self.write(f"[!] SCANNING NEURAL NODES AT {args[0] if args else TARGET_IP}...\n", "info")
        for s, p in PORTS.items(): self.write(f"NODE {p}/TCP [{s}] -> STATUS: UNPROTECTED\n", "success")
        self.show_prompt()

    def run_sqlmap_sim(self, args):
        self.write("[!] INJECTING MALFORMED PACKETS...\n[+] DATA LEAK DETECTED: 'id' parameter exposed.\n", "success")
        self.show_prompt()

    def run_whois_sim(self, args):
        self.write(f"[!] TRACING OWNER OF {args[0] if args else 'node.net'}...\n>>> REGISTRAR: NIGHT-CITY INFRASTRUCTURE\n", "info")
        self.show_prompt()

class InteractiveSession:
    def __init__(self, terminal, host, port, p_prefix=""):
        self.terminal, self.host, self.port, self.prompt_prefix = terminal, host, port, p_prefix
        self.running = True
    def stop(self): self.running = False

class SSHSession(InteractiveSession):
    def __init__(self, t, h, p, u, pwd):
        super().__init__(t, h, p, f"netrunner@{h}:#")
        self.u, self.pwd, self.client = u, pwd, paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    def run(self):
        try:
            self.client.connect(self.host, port=self.port, username=self.u, password=self.pwd, timeout=5)
            chan = self.client.invoke_shell()
            self.terminal.write("[+] NEURAL LINK ESTABLISHED.\n", "success")
            def rd():
                while self.running:
                    if chan.recv_ready():
                        d = chan.recv(1024).decode('utf-8', errors='ignore')
                        self.terminal.write(d); self.terminal.output_area.mark_set("input_start", "end-1c")
                    time.sleep(0.01)
            threading.Thread(target=rd, daemon=True).start()
            while self.running:
                try:
                    c = self.terminal.input_queue.get(timeout=0.1)
                    if c.lower() in ["exit", "logout"]: break
                    chan.send(c + "\n")
                except queue.Empty: continue
        except Exception as e: self.terminal.write(f"[-] LINK ERROR: {e}\n", "error")
        finally:
            self.client.close(); self.terminal.current_session = None; self.terminal.root.after(0, self.terminal.show_prompt)

class FTPSession(InteractiveSession):
    def __init__(self, t, h, p, u, pwd):
        super().__init__(t, h, p, "netrunner@ftp#")
        self.u, self.pwd, self.sock = u, pwd, socket.socket()
    def run(self):
        try:
            self.sock.connect((self.host, self.port)); self.sock.settimeout(1.0)
            time.sleep(0.5); self.sock.send(f"USER {self.u}\r\n".encode())
            time.sleep(0.5); self.sock.send(f"PASS {self.pwd}\r\n".encode())
            while self.running:
                try:
                    d = self.sock.recv(4096).decode('utf-8', errors='ignore')
                    if d: self.terminal.write(d); self.terminal.root.after(0, self.terminal.show_prompt)
                except: pass
                try:
                    c = self.terminal.input_queue.get(timeout=0.1)
                    cu = c.upper()
                    if cu == "QUIT": break
                    if cu in ["LIST", "LS", "DIR"]:
                        self.terminal.write(">>> OPENING DATA CHANNEL...\ndrwxr-xr-x  htdocs\n-rw-r--r--  config.php\n226 Success.\n", "success")
                        self.terminal.root.after(0, self.terminal.show_prompt); continue
                    elif cu.startswith("STOR"):
                        self.terminal.write(">>> UPLOADING PAYLOAD...\n226 File transfer successful.\n", "success")
                        self.terminal.root.after(0, self.terminal.show_prompt); continue
                    self.sock.send((c + "\r\n").encode())
                except queue.Empty: continue
        except Exception as e: self.terminal.write(f"[-] FTP ERROR: {e}\n", "error")
        finally: self.sock.close(); self.terminal.current_session = None; self.terminal.root.after(0, self.terminal.show_prompt)

class SMTPSession(InteractiveSession):
    def __init__(self, t, h, p):
        super().__init__(t, h, p, "netrunner@smtp#")
        self.sock = socket.socket()
    def run(self):
        try:
            self.sock.connect((self.host, self.port)); self.sock.settimeout(1.0)
            while self.running:
                try:
                    d = self.sock.recv(4096).decode('utf-8', errors='ignore')
                    if d: self.terminal.write(d); self.terminal.root.after(0, self.terminal.show_prompt)
                except: pass
                try:
                    c = self.terminal.input_queue.get(timeout=0.1)
                    if c.lower() == "quit": break
                    self.sock.send((c + "\r\n").encode())
                except queue.Empty: continue
        except Exception as e: self.terminal.write(f"[-] SMTP ERROR: {e}\n", "error")
        finally: self.sock.close(); self.terminal.current_session = None; self.terminal.root.after(0, self.terminal.show_prompt)

if __name__ == "__main__":
    root = tk.Tk()
    app = AttackerTerminal(root)
    root.mainloop()
