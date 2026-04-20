"""
配置加载模块
"""
import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                f"Please copy config/config.example.yaml to config/config.yaml and fill in API key"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证必需配置
        self._validate_config(config)
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]):
        """验证配置"""
        required_keys = ['llm', 'concurrency', 'tools', 'logging']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Config missing required key: {key}")
        
        # 验证LLM配置
        llm_config = config['llm']
        required_llm_keys = ['api_key', 'base_url', 'model']
        for key in required_llm_keys:
            if key not in llm_config:
                raise ValueError(f"LLM config missing required key: {key}")
            
            if key == 'api_key' and llm_config[key] == 'your-deepseek-api-key-here':
                raise ValueError("Please fill in a valid API key in config file")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        return self.config['llm']
    
    def get_concurrency_config(self) -> Dict[str, Any]:
        """获取并发配置"""
        return self.config['concurrency']
    
    def get_tools_config(self) -> Dict[str, Any]:
        """获取工具配置"""
        return self.config['tools']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config['logging']
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
