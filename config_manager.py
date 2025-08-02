import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for MCP Agent."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration from JSON file.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self._config = self._load_config()
        load_dotenv(override=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._config["model"]["name"]
    
    @property
    def model_provider(self) -> str:
        """Get model provider."""
        return self._config["model"].get("provider", "openai")
    
    @property
    def model_url(self) -> Optional[str]:
        """Get model API URL."""
        return self._config["model"].get("url")
    
    @property
    def api_key(self) -> str:
        """Get API key from config or environment."""
        api_key = self._config["model"]["api_key"]
        
        # If api_key is uppercase, treat it as environment variable name
        if api_key.isupper():
            env_key = os.getenv(api_key)
            if not env_key:
                raise ValueError(f"Environment variable {api_key} not found")
            return env_key
        
        return api_key
    
    @property
    def mcp_servers(self) -> List[Dict[str, Any]]:
        """Get MCP servers configuration."""
        return self._config.get("mcp_servers", [])
    
    @property
    def max_turns(self) -> int:
        """Get maximum chat turns."""
        return self._config.get("chat", {}).get("max_turns", 30)
    
    @property
    def agent_name(self) -> str:
        """Get agent name."""
        return self._config.get("chat", {}).get("agent_name", "Assistant")
    
    @property
    def agent_instructions(self) -> str:
        """Get agent instructions."""
        return self._config.get("chat", {}).get("agent_instructions", 
                                                "You are a helpful assistant.")
    
    @property
    def ui_config(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return self._config.get("ui", {})
    
