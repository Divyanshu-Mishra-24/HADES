import sqlite3
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import ipaddress

class ThreatProfiler:
    def __init__(self, db_path="honeypot.db"):
        self.db_path = db_path
        self.suspicious_commands = [
            'wget', 'curl', 'nc', 'netcat', 'python', 'perl', 'ruby', 'bash', 'sh',
            'chmod', 'chown', 'passwd', 'sudo', 'su', 'crontab', 'systemctl',
            'iptables', 'ufw', 'firewall', 'ssh', 'scp', 'rsync', 'git', 'docker'
        ]
        self.privilege_escalation_patterns = [
            r'sudo.*su', r'su.*-', r'chmod.*777', r'chown.*root',
            r'passwd.*root', r'echo.*passwd', r'\/etc\/shadow'
        ]
        self.exfiltration_patterns = [
            r'curl.*http.*|', r'wget.*http.*|', r'nc.*-l.*-p', r'base64.*>',
            r'uuencode.*|', r'tar.*czf.*\/tmp', r'zip.*\/tmp'
        ]
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def analyze_source_ip_behavior(self, src_ip):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_attempts,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_logins,
                   COUNT(DISTINCT username) as unique_usernames,
                   COUNT(DISTINCT password) as unique_passwords,
                   MIN(timestamp) as first_seen,
                   MAX(timestamp) as last_seen
            FROM authentication_events 
            WHERE src_ip = ?
        ''', (src_ip,))
        
        auth_stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
        
        cursor.execute('''
            SELECT ce.command, COUNT(*) as count
            FROM command_events ce
            JOIN sessions s ON ce.session_id = s.session_id
            WHERE s.src_ip = ?
            GROUP BY ce.command
            ORDER BY count DESC
        ''', (src_ip,))
        
        command_stats = [dict(zip(['command', 'count'], row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'auth_stats': auth_stats,
            'command_stats': command_stats,
            'threat_score': self.calculate_threat_score(auth_stats, command_stats)
        }
    
    def calculate_threat_score(self, auth_stats, command_stats):
        score = 0
        
        score += min(auth_stats['total_attempts'] * 2, 50)
        score += min(auth_stats['unique_usernames'] * 5, 20)
        score += min(auth_stats['unique_passwords'] * 3, 15)
        
        for cmd_stat in command_stats:
            if cmd_stat['command'] in self.suspicious_commands:
                score += min(cmd_stat['count'] * 10, 30)
        
        if auth_stats['successful_logins'] > 0:
            score += 25
        
        return min(score, 100)
    
    def detect_brute_force_patterns(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT src_ip, 
                   DATE(timestamp) as date,
                   COUNT(*) as attempts,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                   COUNT(DISTINCT username) as unique_usernames
            FROM authentication_events
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY src_ip, DATE(timestamp)
            HAVING attempts >= 10
            ORDER BY attempts DESC
        ''')
        
        patterns = []
        for row in cursor.fetchall():
            src_ip, date, attempts, successes, unique_usernames = row
            patterns.append({
                'src_ip': src_ip,
                'date': date,
                'attempts': attempts,
                'successes': successes,
                'unique_usernames': unique_usernames,
                'pattern_type': 'brute_force' if attempts > 50 else 'high_frequency',
                'severity': 'high' if attempts > 100 else 'medium'
            })
        
        conn.close()
        return patterns
    
    def detect_credential_stuffing(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, COUNT(*) as count, COUNT(DISTINCT src_ip) as unique_ips
            FROM authentication_events
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY username
            HAVING count >= 20 AND unique_ips >= 5
            ORDER BY count DESC
        ''')
        
        stuffing_patterns = []
        for row in cursor.fetchall():
            username, count, unique_ips = row
            stuffing_patterns.append({
                'username': username,
                'attempts': count,
                'unique_ips': unique_ips,
                'pattern_type': 'credential_stuffing',
                'severity': 'high' if unique_ips > 10 else 'medium'
            })
        
        conn.close()
        return stuffing_patterns
    
    def analyze_command_sequences(self, session_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT command, args, timestamp
            FROM command_events
            WHERE session_id = ?
            ORDER BY timestamp
        ''', (session_id,))
        
        commands = cursor.fetchall()
        conn.close()
        
        if not commands:
            return {'risk_level': 'low', 'patterns': []}
        
        risk_score = 0
        patterns = []
        
        command_sequence = [cmd[0] for cmd in commands]
        
        for i, (command, args, timestamp) in enumerate(commands):
            for pattern in self.privilege_escalation_patterns:
                if re.search(pattern, f"{command} {args}", re.IGNORECASE):
                    risk_score += 30
                    patterns.append({
                        'type': 'privilege_escalation',
                        'command': command,
                        'args': args,
                        'timestamp': timestamp
                    })
            
            for pattern in self.exfiltration_patterns:
                if re.search(pattern, f"{command} {args}", re.IGNORECASE):
                    risk_score += 40
                    patterns.append({
                        'type': 'data_exfiltration',
                        'command': command,
                        'args': args,
                        'timestamp': timestamp
                    })
            
            if command in self.suspicious_commands:
                risk_score += 10
        
        if 'wget' in command_sequence or 'curl' in command_sequence:
            risk_score += 20
            patterns.append({
                'type': 'network_activity',
                'description': 'File download or network communication detected'
            })
        
        if len(set(command_sequence)) == 1 and len(command_sequence) > 5:
            risk_score += 15
            patterns.append({
                'type': 'repetitive_behavior',
                'description': f'Repeated execution of {command_sequence[0]} command'
            })
        
        risk_level = 'low'
        if risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'patterns': patterns,
            'command_count': len(commands)
        }
    
    def generate_threat_intelligence(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT src_ip
            FROM authentication_events
            WHERE timestamp >= datetime('now', '-24 hours')
        ''')
        
        recent_ips = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        threat_intelligence = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_active_ips': len(recent_ips),
                'high_risk_ips': 0,
                'medium_risk_ips': 0,
                'low_risk_ips': 0
            },
            'ip_analysis': [],
            'attack_patterns': {
                'brute_force': self.detect_brute_force_patterns(),
                'credential_stuffing': self.detect_credential_stuffing()
            },
            'top_threats': []
        }
        
        for src_ip in recent_ips[:50]:
            analysis = self.analyze_source_ip_behavior(src_ip)
            threat_score = analysis['threat_score']
            
            risk_level = 'low'
            if threat_score >= 70:
                risk_level = 'high'
                threat_intelligence['summary']['high_risk_ips'] += 1
            elif threat_score >= 40:
                risk_level = 'medium'
                threat_intelligence['summary']['medium_risk_ips'] += 1
            else:
                threat_intelligence['summary']['low_risk_ips'] += 1
            
            threat_intelligence['ip_analysis'].append({
                'src_ip': src_ip,
                'threat_score': threat_score,
                'risk_level': risk_level,
                'auth_attempts': analysis['auth_stats']['total_attempts'],
                'successful_logins': analysis['auth_stats']['successful_logins'],
                'unique_usernames': analysis['auth_stats']['unique_usernames']
            })
        
        threat_intelligence['ip_analysis'].sort(key=lambda x: x['threat_score'], reverse=True)
        threat_intelligence['top_threats'] = threat_intelligence['ip_analysis'][:10]
        
        return threat_intelligence
    
    def get_session_risk_analysis(self, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        session_analysis = []
        for session_id in sessions:
            analysis = self.analyze_command_sequences(session_id)
            analysis['session_id'] = session_id
            session_analysis.append(analysis)
        
        return session_analysis
