import asyncio
from typing import List, Dict, Any
import gradio as gr
from agents import Runner, trace

from config_manager import Config
from managers import MCPServerManager, ModelManager, AgentManager


class MCPChatInterface:
    """Chat interface for MCP Agent."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the chat interface.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.mcp_manager = MCPServerManager(self.config)
        self.model_manager = ModelManager(self.config)
        self.agent_manager = AgentManager(self.config, self.model_manager, self.mcp_manager)
        
        # UI components
        self.chat = None
        self.chat_history = None
        self.txt = None
        self.btn = None
        self.clear = None
        self.tools_display = None
        self.ui = None
    
    async def run_chat(self, message: str, history: List[Dict[str, str]]):
        """Handle chat interaction.
        
        Args:
            message: User message
            history: Chat history
        """
        print(f"Running chat with message: {message}")
        
        # Connect to MCP servers
        await self.mcp_manager.connect_all()
        print(f"Connected to MCP servers: {self.mcp_manager.get_servers()}")
        
        # Add user message to history
        history.append({"role": "user", "content": message})
        yield history, ""
        
        # Create agent and run
        agent = await self.agent_manager.create_agent()
        
        with trace("mcp_agent_chat"):
            result = await Runner.run(
                agent,
                history,
                max_turns=self.config.max_turns,
            )
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": result.final_output})
        yield history, ""
    
    async def list_available_tools(self):
        """List all available tools from MCP servers."""
        try:
            await self.mcp_manager.connect_all()
            tools_info = await self.mcp_manager.list_all_tools()
            
            if not tools_info:
                tools_output = "No tools available from MCP servers."
            else:
                tools_list = []
                current_server = None
                for tool_info in tools_info:
                    server_name = tool_info['server']
                    tool_name = tool_info['tool']
                    
                    if server_name != current_server:
                        if current_server is not None:
                            tools_list.append("")  # Add empty line between servers
                        tools_list.append(f"**{server_name}:**")
                        current_server = server_name
                    
                    tools_list.append(f"  • {tool_name}")
                
                tools_output = f"Available MCP Tools:\n\n" + "\n".join(tools_list)
            
            print(f"Listed {len(tools_info)} tools from MCP servers")
            return tools_output
            
        except Exception as e:
            error_msg = f"Error listing tools: {str(e)}"
            print(error_msg)
            return error_msg
    
    def create_ui(self):
        """Create Gradio UI."""
        ui_config = self.config.ui_config
        
        with gr.Blocks(title=ui_config.get("title", "MCP Agent Chat")) as self.ui:
            with gr.Row():
                # Left and center: Chat interface
                with gr.Column(scale=3):
                    self.chat = gr.Chatbot(
                        type="messages",
                        label="Agent Chat",
                        height=ui_config.get("height", 500)
                    )
                    self.chat_history = gr.State([])
                    
                    self.txt = gr.Textbox(
                        placeholder=ui_config.get("placeholder", "Chat with our AI Assistant:"),
                        show_label=False
                    )
                    
                    with gr.Row():
                        self.btn = gr.Button("Run", variant="primary")
                        self.clear = gr.Button("Clear")
                
                # Right side: Tools panel
                with gr.Column(scale=1):
                    gr.Markdown("### Available Tools")
                    tools_btn = gr.Button("Tools info", variant="secondary")
                    self.tools_display = gr.Markdown(
                        value="Click 'Tools info' to see available MCP tools",
                        height=400
                    )
            
            # Event handlers
            self.btn.click(
                fn=self.run_chat,
                inputs=[self.txt, self.chat_history],
                outputs=[self.chat, self.txt],
            )
            
            self.txt.submit(
                fn=self.run_chat,
                inputs=[self.txt, self.chat_history],
                outputs=[self.chat, self.txt],
            )
            
            self.clear.click(
                lambda: ([], []),
                inputs=None,
                outputs=[self.chat, self.chat_history],
                queue=False
            )
            
            tools_btn.click(
                fn=self.list_available_tools,
                inputs=None,
                outputs=[self.tools_display]
            )
        
        return self.ui
    
    def launch(self):
        """Launch the chat interface."""
        if not self.ui:
            self.create_ui()
        
        launch_config = self.config.ui_config
        self.ui.launch(
            inbrowser=launch_config.get("launch_browser", True),
            share=launch_config.get("share", False),
            server_name=launch_config.get("server_name", "127.0.0.1"),
            server_port=launch_config.get("server_port", 8082)
        )


def main():
    """Main function to run the MCP chat interface."""
    try:
        interface = MCPChatInterface()
        print("Starting MCP Agent Chat Interface...")
        print(f"Model: {interface.config.model_name}")
        print(f"Provider: {interface.config.model_provider}")
        print(f"MCP Servers: {len(interface.config.mcp_servers)}")
        
        interface.launch()
        
    except Exception as e:
        print(f"Error starting interface: {e}")
        raise


if __name__ == "__main__":
    main()
