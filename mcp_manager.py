"""
Complete server management script for FastMCP system
Usage:
    python mcp_manager.py start    # Start all servers
    python mcp_manager.py stop     # Stop all servers
    python mcp_manager.py restart  # Restart all servers
    python mcp_manager.py status   # Check server status
    python mcp_manager.py logs     # Show recent logs
"""

import subprocess
import sys
import time
import os
import signal
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file FIRST
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
load_dotenv(PROJECT_ROOT / ".env")

print(f"✓ Loaded .env file")
print(f"✓ OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print()

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Install with: pip install psutil")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. Install with: pip install requests")

# Server configurations
SERVERS = [
    {
        "name": "Query Server",
        "port": 8001,
        "command": [sys.executable, "-m", "servers.query_server.main"],
        "health_endpoint": "http://localhost:8001/health",
        "pid_file": ".pids/query_server.pid",
        "log_file": "logs/query_server.log",
        "env": {}
    },
    {
        "name": "Transactional Server",
        "port": 8002,
        "command": [sys.executable, "-m", "servers.transactional_server.main"],
        "health_endpoint": "http://localhost:8002/health",
        "pid_file": ".pids/transactional_server.pid",
        "log_file": "logs/transactional_server.log",
        "env": {}
    },
    {
        "name": "External API Server",
        "port": 8003,
        "command": [sys.executable, "-m", "servers.external_api_server.main"],
        "health_endpoint": "http://localhost:8003/health",
        "pid_file": ".pids/external_api_server.pid",
        "log_file": "logs/external_api_server.log",
        "env": {}
    },
    {
        "name": "Agent Host",
        "port": 8000,
        "command": [sys.executable, "-m", "agent_host.main"],
        "health_endpoint": "http://localhost:8000/health",
        "pid_file": ".pids/agent_host.pid",
        "log_file": "logs/agent_host.log",
        "env": {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")}
    }
]

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def ensure_directories():
    """Ensure required directories exist"""
    Path(".pids").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

def read_pid_file(pid_file: str) -> Optional[int]:
    """Read PID from file"""
    try:
        if Path(pid_file).exists():
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
    except (ValueError, IOError):
        pass
    return None

def write_pid_file(pid_file: str, pid: int):
    """Write PID to file"""
    with open(pid_file, 'w') as f:
        f.write(str(pid))

def remove_pid_file(pid_file: str):
    """Remove PID file"""
    try:
        if Path(pid_file).exists():
            Path(pid_file).unlink()
    except OSError:
        pass

def is_process_running(pid: int) -> bool:
    """Check if process is running"""
    if not HAS_PSUTIL:
        # Fallback method
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def is_port_in_use(port: int) -> bool:
    """Check if port is in use"""
    if not HAS_PSUTIL:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False

def kill_process_on_port(port: int) -> bool:
    """Kill process using specific port"""
    if not HAS_PSUTIL:
        print_warning("Cannot kill process on port without psutil")
        return False
    
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                    return True
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        process.kill()
                        return True
                    except:
                        pass
    except Exception as e:
        print_error(f"Failed to kill process on port {port}: {e}")
    return False

def check_health(endpoint: str, timeout: int = 2) -> Tuple[bool, str]:
    """Check server health endpoint"""
    if not HAS_REQUESTS:
        return False, "requests not installed"
    
    try:
        response = requests.get(endpoint, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return True, data.get('status', 'unknown')
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def start_server(server: Dict) -> bool:
    """Start a single server"""
    print_info(f"Starting {server['name']}...")
    
    # Check if already running
    pid = read_pid_file(server['pid_file'])
    if pid and is_process_running(pid):
        print_warning(f"{server['name']} is already running (PID: {pid})")
        return True
    
    # Check if port is in use
    if is_port_in_use(server['port']):
        print_warning(f"Port {server['port']} is in use. Attempting to free it...")
        if kill_process_on_port(server['port']):
            print_success(f"Freed port {server['port']}")
            time.sleep(1)
        else:
            print_error(f"Failed to free port {server['port']}")
            return False
    
    # Prepare environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(PROJECT_ROOT)
    env.update(server.get('env', {}))
    
    # Start the server
    try:
        log_file = open(server['log_file'], 'a')
        log_file.write(f"\n\n{'='*70}\n")
        log_file.write(f"Starting {server['name']} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"{'='*70}\n\n")
        log_file.flush()
        
        process = subprocess.Popen(
            server['command'],
            stdout=log_file,
            stderr=log_file,
            env=env,
            cwd=PROJECT_ROOT,
            start_new_session=True
        )
        
        # Write PID file
        write_pid_file(server['pid_file'], process.pid)
        
        # Wait for server to start
        print_info(f"Waiting for {server['name']} to start (PID: {process.pid})...")
        max_retries = 30
        for i in range(max_retries):
            time.sleep(1)
            
            # Check if process died
            if not is_process_running(process.pid):
                print_error(f"{server['name']} process died unexpectedly")
                print_info(f"Check log file: {server['log_file']}")
                
                # Show last 20 lines of log
                try:
                    with open(server['log_file'], 'r') as lf:
                        lines = lf.readlines()
                        if lines:
                            print_info("Last lines from log:")
                            for line in lines[-20:]:
                                print(f"  {line.rstrip()}")
                except:
                    pass
                
                remove_pid_file(server['pid_file'])
                return False
            
            # Check health
            is_healthy, status = check_health(server['health_endpoint'])
            if is_healthy:
                print_success(f"{server['name']} started successfully (PID: {process.pid}, Port: {server['port']})")
                return True
        
        print_error(f"{server['name']} failed to become healthy within {max_retries} seconds")
        print_info(f"Check log file: {server['log_file']}")
        return False
        
    except Exception as e:
        print_error(f"Failed to start {server['name']}: {e}")
        import traceback
        traceback.print_exc()
        return False

def stop_server(server: Dict, force: bool = False) -> bool:
    """Stop a single server"""
    print_info(f"Stopping {server['name']}...")
    
    pid = read_pid_file(server['pid_file'])
    if not pid:
        print_warning(f"{server['name']} is not running (no PID file)")
        if is_port_in_use(server['port']):
            if kill_process_on_port(server['port']):
                print_success(f"Killed process on port {server['port']}")
        return True
    
    if not is_process_running(pid):
        print_warning(f"{server['name']} is not running (PID {pid} not found)")
        remove_pid_file(server['pid_file'])
        return True
    
    try:
        if not HAS_PSUTIL:
            if force:
                os.kill(pid, signal.SIGKILL)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                if is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
            print_success(f"{server['name']} stopped (PID: {pid})")
            remove_pid_file(server['pid_file'])
            return True
        
        process = psutil.Process(pid)
        
        if force:
            process.kill()
            print_success(f"{server['name']} killed forcefully (PID: {pid})")
        else:
            process.terminate()
            try:
                process.wait(timeout=10)
                print_success(f"{server['name']} stopped gracefully (PID: {pid})")
            except psutil.TimeoutExpired:
                print_warning(f"{server['name']} didn't stop gracefully, killing...")
                process.kill()
                print_success(f"{server['name']} killed (PID: {pid})")
        
        remove_pid_file(server['pid_file'])
        return True
        
    except Exception as e:
        print_error(f"Failed to stop {server['name']}: {e}")
        return False

def get_server_status(server: Dict) -> Dict:
    """Get status of a single server"""
    pid = read_pid_file(server['pid_file'])
    
    status = {
        "name": server['name'],
        "port": server['port'],
        "pid": pid,
        "running": False,
        "healthy": False,
        "health_status": "unknown"
    }
    
    if pid and is_process_running(pid):
        status["running"] = True
        is_healthy, health_status = check_health(server['health_endpoint'])
        status["healthy"] = is_healthy
        status["health_status"] = health_status
    
    return status

def start_all_servers():
    """Start all servers"""
    print_header("STARTING ALL SERVERS")
    ensure_directories()
    
    success_count = 0
    total = len(SERVERS)
    
    for server in SERVERS:
        if start_server(server):
            success_count += 1
        print()
    
    print_header("STARTUP SUMMARY")
    if success_count == total:
        print_success(f"All {total} servers started successfully!")
    else:
        print_warning(f"{success_count}/{total} servers started successfully")
        print_info("Check individual log files in logs/ directory for details")
    
    return success_count == total

def stop_all_servers(force: bool = False):
    """Stop all servers"""
    action = "FORCE STOPPING" if force else "STOPPING"
    print_header(f"{action} ALL SERVERS")
    
    success_count = 0
    total = len(SERVERS)
    
    for server in reversed(SERVERS):
        if stop_server(server, force):
            success_count += 1
        print()
    
    print_header("SHUTDOWN SUMMARY")
    if success_count == total:
        print_success(f"All {total} servers stopped successfully!")
    else:
        print_warning(f"{success_count}/{total} servers stopped successfully")
    
    return success_count == total

def show_status():
    """Show status of all servers"""
    print_header("SERVER STATUS")
    
    all_running = True
    all_healthy = True
    
    for server in SERVERS:
        status = get_server_status(server)
        
        status_line = f"{status['name']:<25} Port: {status['port']:<5}"
        
        if status['running']:
            status_line += f" PID: {status['pid']:<7}"
            if status['healthy']:
                status_line += f" [{Colors.OKGREEN}HEALTHY{Colors.ENDC}] ({status['health_status']})"
            else:
                status_line += f" [{Colors.FAIL}UNHEALTHY{Colors.ENDC}] ({status['health_status']})"
                all_healthy = False
        else:
            status_line += f" [{Colors.FAIL}STOPPED{Colors.ENDC}]"
            all_running = False
        
        print(status_line)
    
    print()
    print_header("OVERALL STATUS")
    
    if all_running and all_healthy:
        print_success("All servers are running and healthy ✓")
    elif all_running:
        print_warning("All servers are running but some are unhealthy ⚠")
    else:
        print_error("Some servers are not running ✗")
    
    return all_running and all_healthy

def show_logs(lines: int = 50):
    """Show recent logs from all servers"""
    print_header("RECENT LOGS")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print_warning("No logs directory found")
        return
    
    for server in SERVERS:
        log_file = Path(server['log_file'])
        if log_file.exists():
            print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
            print(f"{Colors.BOLD}{server['name']} - Last {lines} lines{Colors.ENDC}")
            print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
            
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    for line in all_lines[-lines:]:
                        print(line.rstrip())
            except Exception as e:
                print_error(f"Failed to read log: {e}")
        else:
            print_warning(f"Log file not found: {log_file}")

def restart_all_servers():
    """Restart all servers"""
    print_header("RESTARTING ALL SERVERS")
    stop_all_servers()
    time.sleep(2)
    return start_all_servers()

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_manager.py {start|stop|restart|status|force-stop|logs}")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "start":
            success = start_all_servers()
            sys.exit(0 if success else 1)
        
        elif command == "stop":
            success = stop_all_servers()
            sys.exit(0 if success else 1)
        
        elif command == "force-stop":
            success = stop_all_servers(force=True)
            sys.exit(0 if success else 1)
        
        elif command == "restart":
            success = restart_all_servers()
            sys.exit(0 if success else 1)
        
        elif command == "status":
            success = show_status()
            sys.exit(0 if success else 1)
        
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            show_logs(lines)
            sys.exit(0)
        
        else:
            print_error(f"Unknown command: {command}")
            print("Valid commands: start, stop, restart, status, force-stop, logs")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()