#!/usr/bin/env python3
"""
MCP Agent System Demo Launcher

Cross-platform launcher for all available demonstrations.
Supports Windows, macOS, and Linux.
"""

import asyncio
import sys
import os
from typing import Dict, Callable

def show_demo_menu():
    """Display available demo options"""
    
    print("🤖 FINANCEAI PRO™ - PROPRIETARY MCP SYSTEM")
    print("=" * 55)
    print("🏆 Cutting-Edge Investment Banking AI Platform")
    print("🌐 Cross-Platform: Windows | macOS | Linux")
    print("💰 Solving $2B+ Industry Problems with Proprietary AI")
    print()
    
    demos = {
        "1": {
            "name": "Investment Banking Showcase",
            "file": "investment_banking_showcase.py",
            "description": "Complete technical interview demonstration"
        },
        "2": {
            "name": "5-Agent System Orchestration", 
            "file": "multi_agent_demo.py",
            "description": "Live multi-agent workflow execution"
        },
        "3": {
            "name": "MCP Server (Claude Desktop Style)",
            "file": "mcp_server_demo.py", 
            "description": "Financial data MCP server demonstration"
        },
        "4": {
            "name": "Simple AI Agent Demo",
            "file": "simple_agent_demo.py",
            "description": "Basic AI agent workflow showcase"
        },
        "5": {
            "name": "FastAPI Integration",
            "file": "fastapi_integration_demo.py",
            "description": "Sliding window analytics integration"
        },
        "6": {
            "name": "🎯 M&A Advisory Graph Intelligence",
            "file": "ma_advisory_graph_intelligence.py", 
            "description": "Neo4j Graph Data Science for M&A advisory - $375M fee potential"
        }
    }
    
    print("📋 AVAILABLE DEMONSTRATIONS:")
    for key, demo in demos.items():
        print(f"   {key}. {demo['name']}")
        print(f"      └─ {demo['description']}")
    
    print("\n   0. Exit")
    print()
    
    return demos

async def run_demo(demo_file: str):
    """Run selected demonstration"""
    
    demo_path = os.path.join("demos", demo_file)
    
    if not os.path.exists(demo_path):
        print(f"❌ Demo file not found: {demo_path}")
        return
    
    print(f"🚀 Launching: {demo_file}")
    print("-" * 50)
    
    # Import and run the demo
    try:
        # Add demos directory to path
        sys.path.insert(0, "demos")
        
        # Import the demo module
        module_name = demo_file.replace(".py", "")
        demo_module = __import__(module_name)
        
        # Run the main function if it exists
        if hasattr(demo_module, "main"):
            await demo_module.main()
        elif hasattr(demo_module, "run_multi_agent_system"):
            await demo_module.run_multi_agent_system()
        elif hasattr(demo_module, "run_mcp_server_demo"):
            await demo_module.run_mcp_server_demo()
        elif hasattr(demo_module, "demonstrate_integration"):
            await demo_module.demonstrate_integration()
        elif hasattr(demo_module, "run_wow_demo"):
            await demo_module.run_wow_demo()
        elif hasattr(demo_module, "run_ma_intelligence_demo"):
            await demo_module.run_ma_intelligence_demo()
        else:
            print("⚠️  Demo module loaded but no main function found")
            
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("💡 Make sure all dependencies are installed")
    finally:
        # Clean up path
        if "demos" in sys.path:
            sys.path.remove("demos")

def get_platform_info():
    """Get cross-platform information"""
    
    platform_info = {
        "OS": sys.platform,
        "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Architecture": "64-bit" if sys.maxsize > 2**32 else "32-bit"
    }
    
    return platform_info

async def main():
    """Main demo launcher"""
    
    # Show platform compatibility
    platform = get_platform_info()
    print(f"💻 Platform: {platform['OS']} | Python {platform['Python']} | {platform['Architecture']}")
    print()
    
    while True:
        demos = show_demo_menu()
        
        try:
            choice = input("🎯 Select demo (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye! Thanks for exploring the MCP Agent System!")
                break
            elif choice in demos:
                demo = demos[choice]
                print(f"\n🎬 Starting: {demo['name']}")
                await run_demo(demo["file"])
                
                print("\n" + "=" * 55)
                input("Press Enter to return to menu...")
                print()
            else:
                print("❌ Invalid choice. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo launcher interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")