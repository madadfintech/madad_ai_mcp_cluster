# ============================================================================
# USAGE EXAMPLES
# ============================================================================

# FILE: examples/usage_example.py
"""
Complete usage examples for the production FastMCP system
"""
import asyncio
import httpx
import json

async def test_system():
    """Test the complete MCP system"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Agent-Orchestrated FastMCP Tool System\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check system status
        print("=" * 70)
        print("🔍 CHECKING SYSTEM STATUS")
        print("=" * 70)
        
        try:
            status_response = await client.get(f"{base_url}/status")
            status = status_response.json()
            print(f"✓ System Status: {status['initialized']}")
            print(f"✓ Total Requests Processed: {status['total_requests_processed']}")
            print(f"✓ Health Status:")
            for server, healthy in status['health_status'].items():
                print(f"  - {server}: {'✓ healthy' if healthy else '✗ unhealthy'}")
            print()
        except Exception as e:
            print(f"✗ Failed to get status: {e}\n")
        
        # Get available tools
        print("=" * 70)
        print("🛠️  AVAILABLE TOOLS")
        print("=" * 70)
        
        try:
            tools_response = await client.get(f"{base_url}/tools")
            tools_data = tools_response.json()
            print(f"✓ Total Tools Available: {tools_data['total_count']}\n")
            
            # Group tools by server
            from collections import defaultdict
            tools_by_server = defaultdict(list)
            for tool in tools_data['tools']:
                server_name = tool['function']['name'].split('.')[0]
                tools_by_server[server_name].append(tool['function']['name'])
            
            for server, tools in tools_by_server.items():
                print(f"📦 {server}:")
                for tool in tools:
                    print(f"   - {tool}")
                print()
        except Exception as e:
            print(f"✗ Failed to get tools: {e}\n")
        
        # Test queries
        print("=" * 70)
        print("💬 TESTING QUERIES")
        print("=" * 70)
        
        test_queries = [
            "Get me information about our company",
            "Show me all users in the system",
            "Search for electronics products under $1000",
            "Create an order: user 1, product 2, quantity 5",
            "What's our current product inventory status?",
            "Search the web for 'artificial intelligence trends 2024'",
            "What's the weather like in San Francisco?",
            "Get the latest technology news",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'─' * 70}")
            print(f"Query {i}/{len(test_queries)}: {query}")
            print(f"{'─' * 70}")
            
            try:
                response = await client.post(
                    f"{base_url}/query",
                    json={"query": query},
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success: {result['success']}")
                    print(f"📊 Metadata:")
                    print(f"   - Request ID: {result['request_id']}")
                    print(f"   - Iterations: {result['metadata']['iterations']}")
                    print(f"   - Execution Time: {result['metadata']['execution_time_seconds']:.2f}s")
                    print(f"   - Tools Used: {len(result['metadata']['tools_used'])}")
                    
                    if result['metadata']['tools_used']:
                        print(f"\n   🔧 Tool Calls:")
                        for tool_info in result['metadata']['tools_used']:
                            status = "✓" if tool_info['success'] else "✗"
                            print(f"      {status} {tool_info['tool']} ({tool_info.get('execution_time_ms', 'N/A')}ms)")
                    
                    print(f"\n💬 Response:\n{result['response']}\n")
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}\n")
                    
            except Exception as e:
                print(f"❌ Exception: {e}\n")
            
            # Small delay between queries
            await asyncio.sleep(1)
        
        # Final health check
        print("=" * 70)
        print("🏥 FINAL HEALTH CHECK")
        print("=" * 70)
        
        try:
            health_response = await client.get(f"{base_url}/health")
            health = health_response.json()
            print(f"✓ Overall Status: {health['status']}")
            for server, healthy in health['servers'].items():
                status_icon = "✓" if healthy else "✗"
                print(f"  {status_icon} {server}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION FASTMCP SYSTEM TEST SUITE")
    print("=" * 70 + "\n")
    asyncio.run(test_system())
    print("\n" + "=" * 70)
    print("✅ TEST SUITE COMPLETED")
    print("=" * 70 + "\n")