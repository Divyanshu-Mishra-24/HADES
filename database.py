import sqlite3
import json
from datetime import datetime
import uuid

class HoneypotDatabase:
    def __init__(self, db_path="honeypot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authentication_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                src_ip TEXT NOT NULL,
                src_port INTEGER NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                session_id TEXT,
                user_agent TEXT,
                service TEXT DEFAULT 'ssh'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                command TEXT NOT NULL,
                args TEXT,
                result TEXT,
                duration REAL,
                success BOOLEAN DEFAULT TRUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                src_ip TEXT NOT NULL,
                username TEXT,
                commands_count INTEGER DEFAULT 0,
                duration REAL,
                service TEXT DEFAULT 'ssh'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dns_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                src_ip TEXT NOT NULL,
                src_port INTEGER NOT NULL,
                query_name TEXT NOT NULL,
                query_type TEXT NOT NULL,
                record_class TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS http_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                src_ip TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                headers TEXT,
                user_agent TEXT,
                payload TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_authentication(self, src_ip, src_port, username, password, success=False, user_agent=None, service='ssh'):
        session_id = str(uuid.uuid4()) if success else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO authentication_events 
            (timestamp, src_ip, src_port, username, password, success, session_id, user_agent, service)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), src_ip, src_port, username, password, success, session_id, user_agent, service))
        
        if success:
            cursor.execute('''
                INSERT INTO sessions 
                (session_id, start_time, src_ip, username, service)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, datetime.now().isoformat(), src_ip, username, service))
        
        conn.commit()
        conn.close()
        return session_id
    
    def log_command(self, session_id, command, args=None, result=None, duration=0.0, success=True):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if result column exists, if not add it (for backward compatibility)
        try:
            cursor.execute("SELECT result FROM command_events LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE command_events ADD COLUMN result TEXT")
            conn.commit()

        cursor.execute('''
            INSERT INTO command_events 
            (timestamp, session_id, command, args, result, duration, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), session_id, command, args, result, duration, success))
        
        cursor.execute('''
            UPDATE sessions 
            SET commands_count = commands_count + 1
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()

    def log_dns_query(self, src_ip, src_port, query_name, query_type, record_class='IN'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dns_logs 
            (timestamp, src_ip, src_port, query_name, query_type, record_class)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), src_ip, src_port, query_name, query_type, record_class))
        
        conn.commit()
        conn.close()

    def log_http_request(self, src_ip, method, path, headers=None, user_agent=None, payload=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO http_logs 
            (timestamp, src_ip, method, path, headers, user_agent, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), src_ip, method, path, 
              json.dumps(headers) if headers else None, 
              user_agent, 
              json.dumps(payload) if payload else None))
        
        conn.commit()
        conn.close()
    
    def end_session(self, session_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, 
                duration = (julianday(?) - julianday(start_time)) * 86400
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_authentication_logs(self, limit=100, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM authentication_events 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_command_logs(self, limit=100, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM command_events 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

    def get_dns_logs(self, limit=100, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dns_logs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

    def get_http_logs(self, limit=100, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM http_logs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_sessions(self, limit=100, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions 
            ORDER BY start_time DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_analytics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        analytics = {}
        
        cursor.execute('SELECT COUNT(*) FROM authentication_events')
        analytics['total_auth_attempts'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM authentication_events WHERE success = 1')
        analytics['successful_logins'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT service, COUNT(*) as count FROM authentication_events GROUP BY service')
        analytics['service_breakdown'] = [dict(zip(['service', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT src_ip, COUNT(*) as count FROM authentication_events GROUP BY src_ip ORDER BY count DESC LIMIT 50')
        analytics['top_source_ips'] = [dict(zip(['src_ip', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT username, COUNT(*) as count FROM authentication_events GROUP BY username ORDER BY count DESC LIMIT 50')
        analytics['top_usernames'] = [dict(zip(['username', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT password, COUNT(*) as count FROM authentication_events GROUP BY password ORDER BY count DESC LIMIT 50')
        analytics['top_passwords'] = [dict(zip(['password', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT command, COUNT(*) as count FROM command_events GROUP BY command ORDER BY count DESC LIMIT 50')
        analytics['top_commands'] = [dict(zip(['command', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute("SELECT DATE(timestamp, '+5 hours', '30 minutes') as date, COUNT(*) as count FROM authentication_events GROUP BY DATE(timestamp, '+5 hours', '30 minutes') ORDER BY date DESC LIMIT 30")
        analytics['daily_attempts'] = [dict(zip(['date', 'count'], row)) for row in cursor.fetchall()]
        
        # DNS Analytics
        cursor.execute('SELECT COUNT(*) FROM dns_logs')
        analytics['total_dns_queries'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT query_name, COUNT(*) as count FROM dns_logs GROUP BY query_name ORDER BY count DESC LIMIT 50')
        analytics['top_dns_queries'] = [dict(zip(['query_name', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT query_type, COUNT(*) as count FROM dns_logs GROUP BY query_type ORDER BY count DESC')
        analytics['dns_type_breakdown'] = [dict(zip(['query_type', 'count'], row)) for row in cursor.fetchall()]
        
        # HTTP Analytics
        cursor.execute('SELECT COUNT(*) FROM http_logs')
        analytics['total_http_requests'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT path, COUNT(*) as count FROM http_logs GROUP BY path ORDER BY count DESC LIMIT 50')
        analytics['top_http_paths'] = [dict(zip(['path', 'count'], row)) for row in cursor.fetchall()]
        
        cursor.execute('SELECT user_agent, COUNT(*) as count FROM http_logs GROUP BY user_agent ORDER BY count DESC LIMIT 50')
        analytics['top_user_agents'] = [dict(zip(['user_agent', 'count'], row)) for row in cursor.fetchall()]
        
        conn.close()
        return analytics
