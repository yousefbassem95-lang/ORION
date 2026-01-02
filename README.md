# ORION: Advanced Red Team Network Resilience Tool v2.1
<img width="492" height="651" alt="Screenshot from 2026-01-02 02-25-15" src="https://github.com/user-attachments/assets/7673f459-8b20-464e-b4b0-fe31d7f5e15d" />

![Orion Banner](https://img.shields.io/badge/Status-Stealth_Active-blueviolet) ![Red Team](https://img.shields.io/badge/Category-Red_Team-red) ![Version](https://img.shields.io/badge/Version-2.1_Supernova-blue)

>**"We are the Protectors of the Door."**

## 🌌 Overview
**ORION** is a high-performance, asynchronous network stress testing tool designed for authorized Red Team operations. Version 2.1 ("Supernova") introduces a **Stealth Engine** with proxy rotation and header randomization, ensuring your operations remain undetected.

## ⚠️ LEGAL DISCLAIMER
> [!IMPORTANT]
> **PLEASE READ CAREFULLY BEFORE USE**
>
> This tool is developed for **EDUCATIONAL PURPOSES** and **AUTHORIZED SECURITY TESTING ONLY**. 
>
> Usage of this tool for attacking targets without prior mutual consent is **ILLEGAL**. The developers assume **NO liability** for any misuse.

## 🚀 Features
- **Berserker Core**: AsyncIO engine capable of thousands of concurrent requests.
- **Stealth Mode** (New):
    - **Proxy Tunneling**: Support for SOCKS4, SOCKS5, and HTTP proxies.
    - **Identity Shifting**: Random User-Agents, Referers, and fake `X-Forwarded-For`.
- **Live Telemetry**: Beautiful "Matrix-style" TUI using `rich`.
- **Mission Reports**: JSON logs generated after every mission.

## 🛠️ Installation

### Prerequisites
- Python 3.8+

### Setup
We recommend using a virtual environment:

```bash
git clone https://github.com/J0J0M0J0/orion-project.git
cd orion-project
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## ⚔️ Usage

### Basic Attack
```bash
python3 orion.py --target http://example.com --mode betelgeuse --time 30
```

### Stealth Attack (Proxy Chain)
Use a single proxy or a list to mask your IP:
```bash
python3 orion.py --target http://example.com --mode betelgeuse --proxylist proxies.txt
```

### Modes
| Mode | Description |
|------|-------------|
| **Betelgeuse** | Async HTTP GET Flood (Layer 7) |
| **Rigel** | Async TCP Connection Stress (Layer 4) |
| **Bellatrix** | Slowloris (Low & Slow) |
| **Mintaka** | UDP Packet Volley (Fire & Forget) |

## 🛡️ License
Released for **Educational Use Only**.

---
*Made with precision by **J0J0M0J0**.*
# ORION
