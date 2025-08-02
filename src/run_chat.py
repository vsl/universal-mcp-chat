#!/usr/bin/env python3
"""
CLI script to run MCP Agent Chat with different configurations.
"""

import argparse
import sys
from pathlib import Path
from mcp_chat import MCPChatInterface


def main():
    parser = argparse.ArgumentParser(description="Run MCP Agent Chat Interface")
    parser.add_argument(
        "--config", 
        "-c", 
        default="configs/config.json",
        help="Path to configuration file (default: configs/config.json)"
    )
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available example configurations"
    )
    
    args = parser.parse_args()
    
    if args.list_configs:
        print("Available example configurations:")
        print("  configs/config.json (default) - Ollama configuration")
        print("  configs/config_openai.json - OpenAI configuration")
        print("  configs/config_lmstudio.json - LM Studio configuration")
        return
    
    config_path = args.config
    
    # Check if config file exists
    if not Path(config_path).exists():
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Available configurations:")
        print("  configs/config.json (default)")
        print("  configs/config_openai.json")
        print("  configs/config_lmstudio.json")
        print("\nUse --list-configs to see details.")
        sys.exit(1)
    
    try:
        print(f"Starting MCP Agent Chat with config: {config_path}")
        interface = MCPChatInterface(config_path)
        
        print(f"Model: {interface.config.model_name}")
        print(f"Provider: {interface.config.model_provider}")
        print(f"MCP Servers: {len(interface.config.mcp_servers)}")
        
        interface.launch()
        
    except Exception as e:
        print(f"Error starting interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
