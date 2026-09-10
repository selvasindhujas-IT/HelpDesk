"""
tools/system_tools.py
-----------------------
Safe, predefined diagnostic tools that the AI Agent may call.

SECURITY RULE (IMPORTANT):
This module NEVER executes arbitrary commands supplied by a user. Every
function below performs one specific, hardcoded, read-only diagnostic
operation. There is no code path that accepts free-form shell/PowerShell
text from user input. This is intentional and must not be changed.

Allowed operations: reading system info via `platform`/`psutil`, opening a
socket to test connectivity, and running a small fixed set of read-only
subprocess calls (ping) with fully hardcoded arguments.
"""

import socket
import platform
import subprocess
import shutil
from typing import Dict

import psutil

from config.config import Config


def get_system_information() -> Dict:
    """Return general operating system and machine information."""
    try:
        return {
            "status": "success",
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_hostname() -> Dict:
    """Return the machine's network hostname."""
    try:
        return {"status": "success", "hostname": socket.gethostname()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_local_ip() -> Dict:
    """
    Return the machine's local (LAN) IP address.

    Uses a UDP socket "connect" (no data is actually sent) to determine
    which local interface would be used to reach the public internet.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        finally:
            s.close()
        return {"status": "success", "local_ip": ip_address}
    except Exception as exc:
        return {"status": "error", "message": str(exc), "local_ip": "unavailable"}


def check_internet_connection(timeout: float = 3.0) -> Dict:
    """Check basic internet reachability by opening a TCP socket to a known host."""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((Config.PING_TARGET_HOST, 53))
            connected = True
        finally:
            s.close()
        return {"status": "success", "internet_connected": connected}
    except OSError:
        return {"status": "success", "internet_connected": False}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def check_dns_resolution() -> Dict:
    """Check whether DNS resolution is working by resolving a known hostname."""
    try:
        resolved_ip = socket.gethostbyname(Config.DNS_TEST_HOST)
        return {
            "status": "success",
            "dns_working": True,
            "resolved_host": Config.DNS_TEST_HOST,
            "resolved_ip": resolved_ip,
        }
    except socket.gaierror:
        return {
            "status": "success",
            "dns_working": False,
            "resolved_host": Config.DNS_TEST_HOST,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def ping_public_host() -> Dict:
    """
    Ping a fixed, hardcoded public host (Config.PING_TARGET_HOST) to check
    basic network reachability. The target host and ping arguments are
    entirely predefined - no user input is ever passed to subprocess.
    """
    try:
        target = Config.PING_TARGET_HOST
        is_windows = platform.system().lower() == "windows"
        count_flag = "-n" if is_windows else "-c"
        command = ["ping", count_flag, "2", "-w" if is_windows else "-W", "2000" if is_windows else "2", target]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )
        reachable = result.returncode == 0
        return {
            "status": "success",
            "target": target,
            "reachable": reachable,
            "output": result.stdout[-500:] if result.stdout else result.stderr[-500:],
        }
    except FileNotFoundError:
        return {"status": "error", "message": "ping utility not found on this system."}
    except subprocess.TimeoutExpired:
        return {"status": "success", "target": Config.PING_TARGET_HOST, "reachable": False, "output": "Request timed out."}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_cpu_usage() -> Dict:
    """Return current CPU usage percentage."""
    try:
        usage = psutil.cpu_percent(interval=0.5)
        return {"status": "success", "cpu_usage_percent": usage}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_memory_usage() -> Dict:
    """Return current memory (RAM) usage statistics."""
    try:
        mem = psutil.virtual_memory()
        return {
            "status": "success",
            "memory_usage_percent": mem.percent,
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def get_disk_usage() -> Dict:
    """Return current disk usage statistics for the system drive."""
    try:
        anchor = "C:\\" if platform.system().lower() == "windows" else "/"
        total, used, free = shutil.disk_usage(anchor)
        percent_used = round((used / total) * 100, 1) if total else 0.0
        return {
            "status": "success",
            "disk_usage_percent": percent_used,
            "total_gb": round(total / (1024 ** 3), 2),
            "free_gb": round(free / (1024 ** 3), 2),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def run_full_diagnostics() -> Dict:
    """Convenience function that runs every safe diagnostic tool at once."""
    return {
        "system_information": get_system_information(),
        "hostname": get_hostname(),
        "local_ip": get_local_ip(),
        "internet_connection": check_internet_connection(),
        "dns_resolution": check_dns_resolution(),
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage(),
        "disk_usage": get_disk_usage(),
    }
