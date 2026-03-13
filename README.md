# HADES – Honeypot based Attack Detection and Exploitation System

HADES is a **cyber-deception and threat monitoring framework** designed to attract, observe, and analyze attacker behaviour by emulating vulnerable network services.

The system currently implements an **SSH honeypot** that records login attempts, captures attacker commands, and logs malicious activity for further analysis. The captured data is processed through analytics modules and visualized via a **Blue-Team monitoring dashboard**.

This project is developed for **cybersecurity research, academic experimentation, and attacker behaviour analysis**.

---

# Architecture

```
             ┌───────────────┐
             │    Attacker   │
             └───────┬───────┘
                     │
                     ▼
          ┌────────────────────┐
          │ Honeypot Services  │
          │  SSH (Implemented) │
          │  FTP (Planned)     │
          │  HTTP (Planned)    │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │   Log Collector    │
          │ Structured Events  │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │      Database      │
          │  Attack Telemetry  │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │   Analytics Engine │
          │ Threat Intelligence│
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Blue Team Dashboard│
          │ Monitoring Console │
          └────────────────────┘
```

---

# Project Status

| Module                           | Status      |
| -------------------------------- | ----------- |
| SSH Honeypot                     | ✅ Implemented |
| Dockerized Deployment            | ✅ Implemented |
| Authentication Logging           | ✅ Implemented |
| Command Capture                  | ✅ Implemented |
| Blue-Team Dashboard              | ✅ Implemented |
| Cloud Deployment                 | ⏳ Pending     |
| FTP Honeypot                     | 🔜 Planned     |
| HTTP Honeypot                    | 🔜 Planned     |
| Multi-Service Honeypot Framework | 🔜 Planned     |

---

# Features

## SSH Honeypot

- Simulates an SSH server environment
- Captures attacker login attempts
- Logs usernames and passwords
- Records attacker commands
- Generates unique session IDs
- Stores attacker activity logs

## Attack Telemetry

The system records:

- Source IP address
- Username and password attempts
- Login success or failure
- Session ID
- Command execution history
- Attack timestamps

This allows analysis of:

- Brute-force attacks
- Credential dictionaries
- Attacker behaviour
- Command execution patterns

## Blue-Team Dashboard

The monitoring dashboard provides:

- Real-time attack logs
- Session tracking
- Attack frequency visualization
- Command execution monitoring
- Credential attempt analysis

## Containerized Deployment

- Fully Dockerized infrastructure
- Isolated honeypot environment
- Easy reproducibility and testing

---

# Technology Stack

| Layer          | Technology                                      |
| -------------- | ----------------------------------------------- |
| Backend        | Python, Paramiko / Twisted (SSH emulation), REST API |
| Infrastructure | Docker, Docker Compose                          |
| Database       | SQLite (current), Elasticsearch / MongoDB (future) |
| Frontend       | React Dashboard                                 |
| Analytics      | Python data processing                          |

---

# Project Structure

```
HADES
│
├── honeypots
│   ├── ssh
│   │   └── ssh_honeypot.py
│   ├── ftp        (planned)
│   └── http       (planned)
│
├── api
│   └── api_server.py
│
├── analytics
│   └── analytics.py
│
├── dashboard
│   └── React frontend
│
├── database
│   └── database.py
│
├── docker
│   └── docker-compose.yml
│
├── docs
│   ├── SRS.md
│   └── DesignDoc.md
│
└── README.md
```

---

# Running the Project

## Start the System (Docker)

Run the following command to start all services:

```bash
docker compose up --build -d
```

This will start the honeypot services and supporting components.

---

# Access the Services

Once the containers start successfully:

| Service      | URL                                            |
| ------------ | ---------------------------------------------- |
| Dashboard    | [http://localhost:3000](http://localhost:3000) |
| API Server   | [http://localhost:5000](http://localhost:5000) |
| SSH Honeypot | `localhost:2222`                               |

---

# Testing the Honeypot (Attack Simulation)

To simulate an attacker connecting to the honeypot, open a new terminal and run:

```bash
ssh test@127.0.0.1 -p 2222
```

Example login attempt:

```
username: test
password: anything
```

The honeypot will:

1. Capture the login attempt
2. Log username and password
3. Create a session ID
4. Record commands executed in the session

These logs can be viewed in the **dashboard interface**.

> **Note:** The honeypot uses **port 2222 instead of port 22** to avoid conflicts with the host system SSH service.

---

# Stopping the System

To stop all running containers:

```bash
docker compose down
```

---

# Troubleshooting

**Check running containers:**

```bash
docker ps
```

**View container logs:**

```bash
docker compose logs
```

**Restart services:**

```bash
docker compose restart
```

---

# Example Attack Scenario

1. An attacker attempts to connect to the SSH service.
2. The honeypot captures login attempts.
3. If login succeeds, a fake shell environment is provided.
4. All commands executed are recorded.
5. Attack logs are stored and visualized through the dashboard.

This allows security researchers to analyze attacker behaviour and attack patterns.

---

# Security Design

The honeypot is designed with strict containment to prevent compromise of the host system.

Security measures include:

- Docker container isolation
- Non-root service execution
- Simulated shell environment
- No access to real system files
- Restricted outbound network connectivity

---

# Planned Enhancements

Future development goals:

- ☁️ Cloud deployment (AWS / Azure / GCP)
- 🔀 Multi-service honeypot architecture
- 📂 FTP honeypot implementation
- 🌐 HTTP honeypot implementation
- 🗺️ Geolocation-based attack mapping
- 🧠 Threat intelligence enrichment
- 🤖 Machine learning based attack clustering
- ☸️ Kubernetes orchestration

---

# Research Applications

This project can be used for:

- Studying brute-force attacks
- Analysing credential stuffing
- Attacker behaviour research
- Cybersecurity education
- Deception-based defence research

---

# Team

**HADES Development Team**

Divyanshu Mishra, Pulkit Jain, Harsh Vishwakarma, Amartya Sharma

---

# Disclaimer

> ⚠️ This project is intended **strictly for cybersecurity research and educational purposes**.
>
> Deploy honeypots only in **controlled environments with proper authorization**.
>
> Users are responsible for complying with applicable laws and regulations.

---
