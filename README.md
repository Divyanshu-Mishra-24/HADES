# HADES SSH Honeypot System

A comprehensive SSH honeypot system with real-time dashboard visualization and threat intelligence capabilities.

## Features

- **SSH Honeypot Service**: Emulates SSH server to capture attacker behavior
- **Real-time Logging**: Captures authentication attempts and command execution
- **Threat Profiling**: Advanced analytics for attack pattern detection
- **Interactive Dashboard**: React-based UI for log visualization
- **Containerized Deployment**: Docker support for easy deployment

## Architecture

```
Attacker → SSH Honeypot → Database → Analytics Engine → Dashboard
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for dashboard development)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd HoneyPot
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the services:
- **SSH Honeypot**: `ssh://localhost:2222`
- **Dashboard**: `http://localhost:3000`
- **API**: `http://localhost:5000`

### Local Development

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the SSH honeypot:
```bash
python ssh_honeypot.py
```

3. Start the API server:
```bash
python api_server.py
```

4. Install and start the dashboard:
```bash
cd dashboard
npm install
npm start
```

## Components

### SSH Honeypot (`ssh_honeypot.py`)
- Emulates SSH server on port 2222
- Captures authentication attempts
- Simulates shell environment
- Logs all attacker activities

### Database (`database.py`)
- SQLite database for log storage
- Structured data schema for events
- Query and analytics support

### Analytics Engine (`analytics.py`)
- Threat profiling and risk assessment
- Attack pattern detection
- Behavioral analysis
- Session risk scoring

### API Server (`api_server.py`)
- RESTful API for dashboard
- Real-time data endpoints
- Export functionality
- Threat intelligence endpoints

### Dashboard (`dashboard/`)
- React-based web interface
- Real-time visualization
- Interactive charts and graphs
- Log browsing and filtering

## API Endpoints

- `GET /api/dashboard` - Complete dashboard data
- `GET /api/analytics` - Analytics summary
- `GET /api/auth-logs` - Authentication logs
- `GET /api/command-logs` - Command execution logs
- `GET /api/sessions` - Session information
- `GET /api/threat-intelligence` - Threat intelligence data
- `GET /api/session-risk/<session_id>` - Session risk analysis
- `GET /api/ip-analysis/<src_ip>` - Source IP analysis
- `GET /api/attack-patterns` - Attack pattern detection
- `GET /api/export` - Export data (JSON)

## Security Features

- **Container Isolation**: Runs in isolated Docker container
- **Non-root User**: Container runs as non-privileged user
- **Restricted Shell**: Simulated environment prevents real system access
- **Safe Logging**: Credentials stored securely for research purposes
- **Network Restrictions**: Limited outbound connectivity

## Configuration

Default settings can be modified in the respective files:

- **SSH Port**: Change in `ssh_honeypot.py` (default: 2222)
- **API Port**: Change in `api_server.py` (default: 5000)
- **Dashboard Port**: Change in `docker-compose.yml` (default: 3000)
- **Database**: SQLite file location in `database.py`

## Monitoring

The dashboard provides:

- **Real-time Statistics**: Attack counts, success rates
- **Geographic Analysis**: Source IP distribution
- **Trend Analysis**: Attack patterns over time
- **Threat Intelligence**: Risk scoring and profiling
- **Command Analysis**: Most executed commands
- **Session Details**: Individual attacker sessions

## Data Schema

### Authentication Events
- timestamp, src_ip, src_port, username, password, success, session_id

### Command Events
- timestamp, session_id, command, args, duration, success

### Sessions
- session_id, start_time, end_time, src_ip, username, commands_count, duration

## Export and Analysis

Data can be exported via:
- API endpoint: `/api/export?type=json`
- Direct database access
- Dashboard export functionality

## Legal Notice

This system is designed for **research and educational purposes only**. 
Ensure you have proper authorization before deploying any honeypot system.
Users are responsible for complying with applicable laws and regulations.

## Support

For issues and questions:
1. Check the logs in Docker containers
2. Verify network connectivity
3. Ensure proper port configuration
4. Review system requirements

## License

This project is provided for educational and research purposes.
