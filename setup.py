#!/usr/bin/env python3
"""
Complete setup and fix script for FastMCP system
This script will:
1. Check all dependencies
2. Create missing __init__.py files
3. Validate directory structure
4. Check environment variables
5. Test imports
6. Provide fix instructions
"""

import sys
import os
from pathlib import Path
import subprocess

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

# Get project root
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

issues_found = []
fixes_applied = []

def check_directory_structure():
    """Check and create necessary directories"""
    print_header("CHECKING DIRECTORY STRUCTURE")
    
    required_dirs = [
        "shared",
        "servers",
        "servers/query_server",
        "servers/transactional_server",
        "servers/external_api_server",
        "agent_host",
        "examples",
        ".pids",
        "logs"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            print_warning(f"Creating missing directory: {dir_path}")
            full_path.mkdir(parents=True, exist_ok=True)
            fixes_applied.append(f"Created directory: {dir_path}")
            all_good = False
        else:
            print_success(f"Directory exists: {dir_path}")
    
    return all_good

def create_init_files():
    """Create __init__.py files"""
    print_header("CHECKING __init__.py FILES")
    
    init_files = [
        "shared/__init__.py",
        "servers/__init__.py",
        "servers/query_server/__init__.py",
        "servers/transactional_server/__init__.py",
        "servers/external_api_server/__init__.py",
        "agent_host/__init__.py",
        "examples/__init__.py"
    ]
    
    all_good = True
    for init_file in init_files:
        full_path = PROJECT_ROOT / init_file
        if not full_path.exists():
            print_warning(f"Creating missing {init_file}")
            full_path.touch()
            fixes_applied.append(f"Created {init_file}")
            all_good = False
        else:
            print_success(f"Exists: {init_file}")
    
    return all_good

def check_dependencies():
    """Check required dependencies"""
    print_header("CHECKING DEPENDENCIES")
    
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "httpx": "httpx",
        "openai": "openai",
        "dotenv": "python-dotenv",
        "tenacity": "tenacity",
        "structlog": "structlog",
        "psutil": "psutil",
        "requests": "requests"
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name.replace("-", "_"))
            print_success(f"{package_name}")
        except ImportError:
            print_error(f"{package_name} - NOT INSTALLED")
            missing.append(package_name)
            issues_found.append(f"Missing package: {package_name}")
    
    # Check pydantic-settings separately
    try:
        from pydantic_settings import BaseSettings
        print_success("pydantic-settings (v2)")
    except ImportError:
        try:
            from pydantic import BaseSettings
            print_warning("Using pydantic.BaseSettings (v1) - consider upgrading")
        except ImportError:
            print_error("pydantic-settings - NOT INSTALLED")
            missing.append("pydantic-settings")
            issues_found.append("Missing package: pydantic-settings")
    
    if missing:
        print(f"\n{Colors.RED}Missing packages detected!{Colors.ENDC}")
        print(f"\nRun this command to install:")
        print(f"{Colors.GREEN}pip install {' '.join(missing)}{Colors.ENDC}\n")
        return False
    
    return True

def check_env_file():
    """Check .env file"""
    print_header("CHECKING ENVIRONMENT CONFIGURATION")
    
    env_file = PROJECT_ROOT / ".env"
    
    if not env_file.exists():
        print_warning(".env file not found. Creating template...")
        with open(env_file, 'w') as f:
            f.write("# FastMCP System Configuration\n")
            f.write("OPENAI_API_KEY=your-openai-api-key-here\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("LOG_FORMAT=console\n")
            f.write("MCP_CLIENT_MAX_RETRIES=3\n")
            f.write("OPENAI_TIMEOUT=30\n")
        print_success("Created .env template")
        fixes_applied.append("Created .env template")
        
        print_warning("⚠  IMPORTANT: Edit .env and add your OPENAI_API_KEY")
        issues_found.append("OPENAI_API_KEY not configured in .env")
        return False
    else:
        print_success(".env file exists")
        
        # Check if OPENAI_API_KEY is set
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=your-openai-api-key-here' in content or 'OPENAI_API_KEY=' not in content:
                print_error("OPENAI_API_KEY not configured in .env")
                issues_found.append("OPENAI_API_KEY not configured")
                return False
            else:
                print_success("OPENAI_API_KEY is configured")
    
    return True

def test_imports():
    """Test if all modules can be imported"""
    print_header("TESTING MODULE IMPORTS")
    
    modules_to_test = [
        ("shared.config", "Configuration module"),
        ("shared.logging_config", "Logging module"),
        ("shared.exceptions", "Exceptions module"),
        ("shared.fastmcp", "FastMCP library"),
        ("servers.query_server.main", "Query Server"),
        ("servers.transactional_server.main", "Transactional Server"),
        ("servers.external_api_server.main", "External API Server"),
    ]
    
    all_good = True
    for module_path, description in modules_to_test:
        try:
            __import__(module_path)
            print_success(f"{description}")
        except Exception as e:
            print_error(f"{description} - {str(e)}")
            issues_found.append(f"Import failed: {module_path} - {str(e)}")
            all_good = False
    
    # Test Agent Host separately (might fail due to missing API key)
    try:
        __import__("agent_host.orchestrator")
        __import__("agent_host.mcp_client")
        print_success("Agent Host modules")
    except Exception as e:
        print_warning(f"Agent Host modules - {str(e)}")
        print_info("This is normal if OPENAI_API_KEY is not set")
    
    return all_good

def check_ports():
    """Check if required ports are available"""
    print_header("CHECKING PORT AVAILABILITY")
    
    required_ports = [8000, 8001, 8002, 8003]
    
    try:
        import socket
        all_available = True
        for port in required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print_warning(f"Port {port} is in use")
                all_available = False
            else:
                print_success(f"Port {port} is available")
        
        return all_available
    except Exception as e:
        print_error(f"Failed to check ports: {e}")
        return False

def run_diagnostic():
    """Run comprehensive diagnostic"""
    print(f"\n{Colors.BOLD}FastMCP System Setup & Diagnostic Tool{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    results = {
        "structure": check_directory_structure(),
        "init_files": create_init_files(),
        "dependencies": check_dependencies(),
        "env": check_env_file(),
        "imports": test_imports(),
        "ports": check_ports()
    }
    
    print_header("DIAGNOSTIC SUMMARY")
    
    if all(results.values()):
        print_success("All checks passed! ✓")
        print_info("\nYour system is ready. Start servers with:")
        print(f"  {Colors.GREEN}python manage_servers.py start{Colors.ENDC}\n")
        return True
    else:
        print_warning("Some issues were found\n")
        
        if fixes_applied:
            print(f"{Colors.GREEN}Fixes applied:{Colors.ENDC}")
            for fix in fixes_applied:
                print(f"  ✓ {fix}")
            print()
        
        if issues_found:
            print(f"{Colors.RED}Issues requiring attention:{Colors.ENDC}")
            for issue in issues_found:
                print(f"  ✗ {issue}")
            print()
        
        print(f"{Colors.YELLOW}Next steps:{Colors.ENDC}")
        
        if not results["dependencies"]:
            print("  1. Install missing dependencies (see above)")
        
        if not results["env"]:
            print("  2. Edit .env file and add your OPENAI_API_KEY")
        
        if not results["imports"]:
            print("  3. Fix import errors (check error messages above)")
        
        if not results["ports"]:
            print("  4. Free up ports 8000-8003 or stop conflicting services")
        
        print(f"\n  5. Run this script again: {Colors.GREEN}python setup.py{Colors.ENDC}\n")
        
        return False

def create_minimal_test():
    """Create a minimal test script"""
    print_header("CREATING TEST SCRIPTS")
    
    test_script = PROJECT_ROOT / "test_server.py"
    with open(test_script, 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Minimal test to check if a single server can start
\"\"\"
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Query Server import...")
try:
    from servers.query_server.main import app
    print("✓ Query Server imported successfully")
    print("✓ Run with: uvicorn servers.query_server.main:app --port 8001")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
""")
    
    print_success(f"Created test_server.py")
    print_info("Test with: python test_server.py")

if __name__ == "__main__":
    try:
        success = run_diagnostic()
        create_minimal_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        