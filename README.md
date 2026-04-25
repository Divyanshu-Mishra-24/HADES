# HADES – Honeypot based Attack Detection and Exploitation System

HADES is a **cyber-deception and threat monitoring framework** designed to attract, observe, and analyze attacker behaviour by emulating vulnerable network services.

The system currently implements an **SSH honeypot , FTP honeypot , DNS honeypot , HTTP honeypot and SMTP honeypot** that records login attempts, captures attacker commands, and logs malicious activity for further analysis. The captured data is processed through analytics modules and visualized via a **Blue-Team monitoring dashboard**.

This project is developed for **cybersecurity research, academic experimentation, and attacker behaviour analysis**.

---

# Features

### 🪤 Multi-Protocol Honeypots

Emulates five real-world network services simultaneously to attract and deceive attackers:

- **SSH** — Full fake Ubuntu shell via Paramiko. Accepts all password logins, simulates `ls`, `whoami`, `id`, `uname`, `netstat`, and more while silently logging every command
- **FTP** — Accepts any credentials and responds to standard FTP commands (`SYST`, `FEAT`, `PWD`, `TYPE`)
- **HTTP** — Flask-based web server with irresistible fake endpoints:

  | Path | What it Serves |
  |---|---|
  | `/wp-admin` | Fake WordPress login form |
  | `/.env` | Fake environment file with DB credentials |
  | `/config.php` | Fake PHP config with database credentials |
  | `/admin` | 403 Forbidden response |
  | `/login` | 401 Invalid credentials response |

- **SMTP** — Emulates a Postfix ESMTP server; captures decoded credentials and full email bodies from relay attempts
- **DNS** — Responds to UDP queries with a dummy IP to keep probers engaged while logging every queried hostname

### 🧠 Threat Intelligence Engine

Deep behavioural analysis powered by the `ThreatProfiler`:

- **Brute Force Detection** — IPs with 10+ attempts per day, escalated to `high` above 100 attempts
- **Credential Stuffing Detection** — Usernames targeted from 5+ unique IPs within 24 hours
- **Privilege Escalation Detection** — Regex matching for `sudo su`, `chmod 777`, `/etc/shadow`, and more
- **Data Exfiltration Detection** — Flags patterns like `curl | sh`, `base64 >`, and `tar czf /tmp`

### 📊 Blue-Team Dashboard

The React monitoring dashboard provides:

- **Operations Center** — Live stat cards, traffic velocity line chart, threat origin bar chart, and donut charts for top usernames, passwords, commands, DNS queries, HTTP paths, and SMTP senders
- **Intel Logs** — Tabbed raw log viewer across all five protocols with timestamps, source IPs, and decoded credentials
- **Network Mesh** — Interactive graph visualizing attacker IP connections and lateral movement
- **Auto-Refresh** — Polls every 5 seconds for live telemetry
- **Dark / Light Mode** — Full theme support across the entire UI

### 🎨 3D Particle Background

An animated Three.js particle system that assembles from a scattered field into a glowing shield/fingerprint shape and disperses — cycling continuously in the background.

### 📤 Data Export & API

Full REST API with 11 endpoints covering all log types, threat intelligence reports, per-IP behavioural profiles, and bulk JSON export.

### 🐳 Containerized Deployment

- Fully Dockerized infrastructure
- Isolated honeypot environment
- Easy reproducibility and testing

---

# Technology Stack

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td><b>🖥️ Frontend</b></td>
    <td>
      <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
      <img src="https://img.shields.io/badge/Ant_Design-0170FE?style=flat-square&logo=antdesign&logoColor=white" />
      <img src="https://img.shields.io/badge/Three.js-000000?style=flat-square&logo=threedotjs&logoColor=white" />
      <img src="https://img.shields.io/badge/Recharts-22b5bf?style=flat-square" />
      <img src="https://img.shields.io/badge/Axios-5A29E4?style=flat-square&logo=axios&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td><b>⚙️ Backend</b></td>
    <td>
      <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
      <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" />
      <img src="https://img.shields.io/badge/Paramiko-FF6F00?style=flat-square" />
      <img src="https://img.shields.io/badge/dnslib-4CAF50?style=flat-square" />
    </td>
  </tr>
  <tr>
    <td><b>🗄️ Database</b></td>
    <td>
      <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td><b>🐳 Infrastructure</b></td>
    <td>
      <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
      <img src="https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td><b>🔒 Honeypot Protocols</b></td>
    <td>SSH &nbsp;·&nbsp; FTP &nbsp;·&nbsp; HTTP &nbsp;·&nbsp; SMTP &nbsp;·&nbsp; DNS</td>
  </tr>
  <tr>
    <td><b>📡 API</b></td>
    <td>
      <img src="https://img.shields.io/badge/REST_API-FF6C37?style=flat-square&logo=postman&logoColor=white" />
      <img src="https://img.shields.io/badge/Flask--CORS-000000?style=flat-square&logo=flask&logoColor=white" />
    </td>
  </tr>
</table>

---

# Project Structure

```
HADES/
│
├── ssh_honeypot.py          # SSH honeypot & fake interactive shell
├── ftp_honeypot.py          # FTP honeypot
├── http_honeypot.py         # HTTP honeypot with fake endpoints
├── smtp_honeypot.py         # SMTP honeypot with credential capture
├── dns_honeypot.py          # DNS honeypot (UDP)
│
├── api_server.py            # Flask REST API (11 endpoints)
├── analytics.py             # ThreatProfiler & risk scoring engine
├── database.py              # SQLite ORM (HoneypotDatabase)
├── honeypot.db              # SQLite database (auto-created at runtime)
│
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main dashboard UI (Ant Design + Recharts)
│   │   ├── Background.js    # Three.js particle shield animation
│   │   ├── NetworkMesh.js   # Attacker network graph
│   │   └── index.js         # React entry point
│   └── package.json
│
├── docker/
│   └── docker-compose.yml
│
├── docs/
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
| FTP Honeypot | `localhost:2121`                               |
| DNS Honeypot | `localhost:5354`                               |
| HTTP Honeypot | `localhost:8081`                               |
| SMTP Honeypot | `localhost:2525`                               |


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
- 🗺️ Geolocation-based attack mapping
- 🧠 Threat intelligence enrichment
- 🤖 Machine learning based attack clustering
- ☸️ Kubernetes orchestration

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
