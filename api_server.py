from flask import Flask, jsonify, request
from flask_cors import CORS
from database import HoneypotDatabase
from analytics import ThreatProfiler
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
db = HoneypotDatabase()
profiler = ThreatProfiler()

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        analytics = db.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth-logs', methods=['GET'])
def get_auth_logs():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        logs = db.get_authentication_logs(limit, offset)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/command-logs', methods=['GET'])
def get_command_logs():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        logs = db.get_command_logs(limit, offset)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        sessions = db.get_sessions(limit, offset)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        analytics = db.get_analytics()
        
        recent_auth = db.get_authentication_logs(10)
        recent_commands = db.get_command_logs(10)
        recent_sessions = db.get_sessions(10)
        
        dashboard_data = {
            'summary': {
                'total_auth_attempts': analytics.get('total_auth_attempts', 0),
                'successful_logins': analytics.get('successful_logins', 0),
                'failed_logins': analytics.get('total_auth_attempts', 0) - analytics.get('successful_logins', 0),
                'total_sessions': analytics.get('successful_logins', 0)
            },
            'top_source_ips': analytics.get('top_source_ips', []),
            'top_usernames': analytics.get('top_usernames', []),
            'top_passwords': analytics.get('top_passwords', []),
            'top_commands': analytics.get('top_commands', []),
            'daily_attempts': analytics.get('daily_attempts', []),
            'recent_auth': recent_auth,
            'recent_commands': recent_commands,
            'recent_sessions': recent_sessions
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        export_type = request.args.get('type', 'json')
        
        if export_type == 'json':
            auth_logs = db.get_authentication_logs(10000)
            command_logs = db.get_command_logs(10000)
            sessions = db.get_sessions(10000)
            
            export_data = {
                'authentication_logs': auth_logs,
                'command_logs': command_logs,
                'sessions': sessions,
                'export_timestamp': datetime.now().isoformat()
            }
            
            return jsonify(export_data)
        
        return jsonify({'error': 'Unsupported export type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threat-intelligence', methods=['GET'])
def get_threat_intelligence():
    try:
        threat_intel = profiler.generate_threat_intelligence()
        return jsonify(threat_intel)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session-risk/<session_id>', methods=['GET'])
def get_session_risk(session_id):
    try:
        risk_analysis = profiler.analyze_command_sequences(session_id)
        return jsonify(risk_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ip-analysis/<src_ip>', methods=['GET'])
def get_ip_analysis(src_ip):
    try:
        analysis = profiler.analyze_source_ip_behavior(src_ip)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attack-patterns', methods=['GET'])
def get_attack_patterns():
    try:
        patterns = {
            'brute_force': profiler.detect_brute_force_patterns(),
            'credential_stuffing': profiler.detect_credential_stuffing()
        }
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
