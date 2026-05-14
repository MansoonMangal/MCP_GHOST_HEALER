import os
import yaml
from pydantic import BaseModel, Field
from typing import Optional

class MCPServerConfig(BaseModel):
    url: str = "http://localhost:8000"
    timeout: int = 30
    confidence_threshold: float = 0.5

class HealingConfig(BaseModel):
    mode: str = "runtime"  # runtime, suggestion, strict
    auto_patch: bool = True
    cache_enabled: bool = True

class ReportingConfig(BaseModel):
    output_dir: str = "reports/ghost"
    format: str = "json"
    save_traces: bool = True

class GhostConfig(BaseModel):
    mcp_server: MCPServerConfig = Field(default_factory=MCPServerConfig)
    healing: HealingConfig = Field(default_factory=HealingConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)

def load_config() -> GhostConfig:
    config_path = "ghost.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            return GhostConfig(**data)
    return GhostConfig()

# Global config instance
settings = load_config()
