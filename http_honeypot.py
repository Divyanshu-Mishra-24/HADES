from flask import Flask, request, jsonify
import logging
from datetime import datetime
from database import HoneypotDatabase
import threading

class HTTPHoneypot:
    def __init__(self, host='0.0.0.0', port=8081):
        self.host = host
        self.port = port
        self.database = HoneypotDatabase()
        self.app = Flask(__name__)
        self._setup_routes()

    def _log_request(self):
        src_ip = request.remote_addr
        method = request.method
        path = request.path
        headers = dict(request.headers)
        user_agent = request.headers.get('User-Agent')
        
        # Capture payload if any
        payload = None
        if request.is_json:
            payload = request.get_json(silent=True)
        elif request.form:
            payload = request.form.to_dict()
        else:
            payload = request.get_data(as_text=True)

        self.database.log_http_request(
            src_ip=src_ip,
            method=method,
            path=path,
            headers=headers,
            user_agent=user_agent,
            payload=payload
        )
        logging.info(f"HTTP Request: {method} {path} from {src_ip}")

    def _setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        def home():
            self._log_request()
            return "<h1>Welcome to Apache Server</h1>", 200

        @self.app.route("/admin", methods=["GET", "POST"])
        def admin():
            self._log_request()
            return "403 Forbidden", 403

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            self._log_request()
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

        @self.app.route("/wp-admin", methods=["GET", "POST"])
        def wp_admin():
            self._log_request()
            return "<h1>WordPress Login</h1><form><input type='text' name='user'><input type='password' name='pass'></form>", 200

        @self.app.route("/.env", methods=["GET"])
        def env_file():
            self._log_request()
            return "DB_PASSWORD=secret\nAWS_ACCESS_KEY_ID=AKIA...", 200

        @self.app.route("/config.php", methods=["GET"])
        def config_php():
            self._log_request()
            return "<?php define('DB_USER', 'root'); ?>", 200

        @self.app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
        def catch_all(path):
            self._log_request()
            return "404 Not Found", 404

    def start(self):
        logging.info(f"HTTP Honeypot listening on {self.host}:{self.port}")
        # Run Flask without the reloader as it's running in a thread
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    honeypot = HTTPHoneypot()
    honeypot.start()
