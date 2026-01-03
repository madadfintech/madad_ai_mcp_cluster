#!/usr/bin/env python3
"""
Complete test suite for the MCP System
Run this to test all servers with real queries
"""

import asyncio
import httpx
import json
from datetime import datetime

# Colors for output
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

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

async def test_system():
    """Test the complete MCP system"""
    base_url = "http://localhost:8000"
    
    print(f"\n{Colors.BOLD}🚀 Testing Agent-Orchestrated FastMCP Tool System{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test 1: Check system status
        print_header("1. CHECKING SYSTEM STATUS")
        try:
            response = await client.get(f"{base_url}/status")
            if response.status_code == 200:
                status = response.json()
                print_success(f"System initialized: {status['initialized']}")
                print_success(f"Total requests processed: {status['total_requests_processed']}")
                print_info("Server health status:")
                for server, healthy in status['health_status'].items():
                    status_icon = "✓" if healthy else "✗"
                    print(f"  {status_icon} {server}")
                print()
            else:
                print_error(f"Status check failed: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to connect: {e}")
            return

        # Test 2: Get available tools
        print_header("2. AVAILABLE TOOLS")
        try:
            response = await client.get(f"{base_url}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                print_success(f"Total tools available: {tools_data['total_count']}")
                
                # Group by server
                from collections import defaultdict
                tools_by_server = defaultdict(list)
                for tool in tools_data['tools']:
                    server_name = tool['function']['name'].split('.')[0]
                    tools_by_server[server_name].append(tool['function']['name'].split('.')[1])
                
                for server, tools in tools_by_server.items():
                    print(f"\n  📦 {server} ({len(tools)} tools):")
                    for tool in tools[:5]:  # Show first 5
                        print(f"     - {tool}")
                    if len(tools) > 5:
                        print(f"     ... and {len(tools) - 5} more")
            else:
                print_error(f"Failed to get tools: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")

        # Test 3: Run actual queries
        print_header("3. TESTING QUERIES")
        
        test_queries = [
            {
                "name": "Get Company Info",
                "query": "Tell me about our company",
                "expected_tools": ["query_server"]
            },
            {
                "name": "List Users",
                "query": "Show me all users in the system",
                "expected_tools": ["query_server"]
            },
            {
                "name": "Search Products",
                "query": "Find electronics products under $1000",
                "expected_tools": ["query_server"]
            },
            {
                "name": "Get System Status",
                "query": "What's our system status?",
                "expected_tools": ["query_server"]
            },
            {
                "name": "Create Order",
                "query": "Create an order for user 1, product 2, quantity 3",
                "expected_tools": ["transactional_server"]
            },
            {
                "name": "Update Inventory",
                "query": "Add 50 units to product 1 inventory with reason 'restocking'",
                "expected_tools": ["transactional_server"]
            },
            {
                "name": "Web Search",
                "query": "Search the web for 'latest AI developments'",
                "expected_tools": ["external_api_server"]
            },
            {
                "name": "Get Weather",
                "query": "What's the weather like in San Francisco?",
                "expected_tools": ["external_api_server"]
            },
            {
                "name": "Multi-Tool Query",
                "query": "Get our company information and list all users",
                "expected_tools": ["query_server"]
            },
            {
                "name": "Analytics",
                "query": "Give me a summary of our analytics data",
                "expected_tools": ["query_server"]
            }
        ]
        
        successful = 0
        failed = 0
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n{Colors.BOLD}Test {i}/{len(test_queries)}: {test['name']}{Colors.ENDC}")
            print(f"{'-'*70}")
            print(f"Query: {test['query']}")
            
            try:
                response = await client.post(
                    f"{base_url}/query",
                    json={"query": test['query']},
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['success']:
                        print_success(f"Success!")
                        print_info(f"Request ID: {result['request_id']}")
                        print_info(f"Iterations: {result['metadata']['iterations']}")
                        print_info(f"Execution time: {result['metadata']['execution_time_seconds']:.2f}s")
                        
                        # Show tools used
                        tools_used = result['metadata']['tools_used']
                        if tools_used:
                            print_info(f"Tools called ({len(tools_used)}):")
                            for tool_info in tools_used:
                                status = "✓" if tool_info['success'] else "✗"
                                tool_name = tool_info['tool']
                                exec_time = tool_info.get('execution_time_ms', 'N/A')
                                print(f"  {status} {tool_name} ({exec_time}ms)")
                        
                        # Show response preview
                        response_preview = result['response'][:200]
                        if len(result['response']) > 200:
                            response_preview += "..."
                        print(f"\n{Colors.BOLD}Response:{Colors.ENDC}")
                        print(f"{response_preview}\n")
                        
                        successful += 1
                    else:
                        print_error(f"Query failed: {result.get('response', 'Unknown error')}")
                        failed += 1
                else:
                    print_error(f"HTTP {response.status_code}: {response.text[:100]}")
                    failed += 1
                    
            except Exception as e:
                print_error(f"Exception: {e}")
                failed += 1
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Test 4: Final health check
        print_header("4. FINAL HEALTH CHECK")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health = response.json()
                print_success(f"Overall status: {health['status']}")
                for server, healthy in health['servers'].items():
                    status_icon = "✓" if healthy else "✗"
                    print(f"  {status_icon} {server}")
            else:
                print_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # Summary
        print_header("TESTING SUMMARY")
        total = len(test_queries)
        print(f"Total queries: {total}")
        print_success(f"Successful: {successful}")
        if failed > 0:
            print_error(f"Failed: {failed}")
        else:
            print_success("All tests passed! 🎉")
        
        success_rate = (successful / total) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MCP SYSTEM TEST SUITE")
    print("="*70 + "\n")
    asyncio.run(test_system())
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70 + "\n")