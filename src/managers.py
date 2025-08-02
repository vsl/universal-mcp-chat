from typing import List, Dict, Any
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.mcp import MCPServerStdio, MCPServerStreamableHttp
from config_manager import Config


class MCPServerManager:
    """Manager for MCP servers."""
    
    def __init__(self, config: Config):
        """Initialize MCP server manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.mcp_servers = []
        self._initialize_servers()
    
    def _get_server_name(self, server, server_config):
        """Get a user-friendly name for the server."""
        if hasattr(server, '_params'):
            params = server._params
            if 'command' in params and 'args' in params:
                # For stdio servers, use the script name
                args = params['args']
                if args:
                    script_path = args[-1]  # Last argument is usually the script path
                    return script_path.split('/')[-1].replace('.py', '').replace('_', ' ').title()
                return f"{params['command']} server"
            elif 'url' in params:
                # For HTTP servers, use the URL
                return f"HTTP server ({params['url']})"
        
        # Fallback to server type
        server_type = server_config.get("type", "stdio")
        return f"{server_type.title()} Server"

    def _initialize_servers(self):
        """Initialize MCP servers from configuration."""
        for i, server_config in enumerate(self.config.mcp_servers):
            server_type = server_config.get("type", "stdio")
            timeout = server_config.get("timeout", 120)
            
            if server_type == "stdio":
                command = server_config["command"]
                args = server_config.get("args", [])
                params = {"command": command, "args": args}
                
                server = MCPServerStdio(
                    params=params,
                    client_session_timeout_seconds=timeout
                )
                # Store server config for naming
                server._config = server_config
                self.mcp_servers.append(server)
                
            elif server_type == "http":
                url = server_config["url"]
                params = {"url": url}
                
                server = MCPServerStreamableHttp(
                    params=params,
                    client_session_timeout_seconds=timeout
                )
                # Store server config for naming
                server._config = server_config
                self.mcp_servers.append(server)
    
    async def connect_all(self):
        """Connect to all MCP servers."""
        for server in self.mcp_servers:
            await server.connect()
    
    async def list_all_tools(self):
        """List all available tools from all servers."""
        tools_info = []
        for server in self.mcp_servers:
            await server.connect()
            tools = await server.list_tools()
            
            # Get user-friendly server name
            server_config = getattr(server, '_config', {})
            server_name = self._get_server_name(server, server_config)
            
            for tool in tools:
                tools_info.append({
                    "server": server_name,
                    "tool": tool
                })
        return tools_info
    
    def get_servers(self) -> List:
        """Get list of MCP servers."""
        return self.mcp_servers


class ModelManager:
    """Manager for AI models."""
    
    def __init__(self, config: Config):
        """Initialize model manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.client = self._create_client()
        self.model = self._create_model()
    
    def _create_client(self) -> AsyncOpenAI:
        """Create OpenAI client based on configuration."""
        if self.config.model_url:
            # Custom URL (Ollama, LM Studio, etc.)
            return AsyncOpenAI(
                base_url=self.config.model_url,
                api_key=self.config.api_key
            )
        else:
            # Standard OpenAI
            return AsyncOpenAI(api_key=self.config.api_key)
    
    def _create_model(self) -> OpenAIChatCompletionsModel:
        """Create model instance."""
        return OpenAIChatCompletionsModel(
            model=self.config.model_name,
            openai_client=self.client
        )
    
    def get_model(self) -> OpenAIChatCompletionsModel:
        """Get the model instance."""
        return self.model


class AgentManager:
    """Manager for AI agents."""
    
    def __init__(self, config: Config, model_manager: ModelManager, mcp_manager: MCPServerManager):
        """Initialize agent manager.
        
        Args:
            config: Configuration object
            model_manager: Model manager instance
            mcp_manager: MCP server manager instance
        """
        self.config = config
        self.model_manager = model_manager
        self.mcp_manager = mcp_manager
    
    async def create_agent(self) -> Agent:
        """Create and return an AI agent."""
        agent = Agent(
            mcp_servers=self.mcp_manager.get_servers(),
            name=self.config.agent_name,
            instructions=self.config.agent_instructions,
            model=self.model_manager.get_model()
        )
        return agent
