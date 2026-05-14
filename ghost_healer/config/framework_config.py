import os

class FrameworkConfig:
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")
        self.enable_visual_highlight = True
        self.enable_smart_memory = True
        self.memory_dir = os.path.join(os.getcwd(), "reports", "memory")
        
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir, exist_ok=True)

config = FrameworkConfig()
