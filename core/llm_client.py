"""
TaskWeaver AI 统一LLM客户端

支持多种LLM提供商，包括硅基流动、OpenAI等
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum

# 自动加载.env文件
def load_env():
    """加载.env文件中的环境变量"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if not os.getenv(key):  # 只设置未设置的变量
                            os.environ[key] = value
        except Exception:
            pass  # 静默失败

# 加载环境变量
load_env()


class LLMProvider(Enum):
    """LLM提供商枚举"""
    SILICONFLOW = "siliconflow"
    OPENAI = "openai"


class LLMClient:
    """
    统一LLM客户端
    
    自动根据配置选择最佳可用的LLM提供商
    """
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """
        初始化LLM客户端
        
        Args:
            provider: LLM提供商 ('siliconflow' 或 'openai')，默认从环境变量读取
            api_key: API密钥，默认从环境变量读取
            model: 模型名称，默认从环境变量读取
        """
        self.provider = provider or os.getenv('DEFAULT_LLM_PROVIDER', 'siliconflow')
        self.client = None
        self.model = model
        
        # 初始化客户端
        self._init_client(api_key)
    
    def _init_client(self, api_key: str = None):
        """初始化具体的客户端"""
        if self.provider == LLMProvider.SILICONFLOW.value:
            self._init_siliconflow_client(api_key)
        elif self.provider == LLMProvider.OPENAI.value:
            self._init_openai_client(api_key)
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    def _init_siliconflow_client(self, api_key: str = None):
        """初始化硅基流动客户端"""
        try:
            import openai
            
            # 使用API密钥
            api_key = api_key or os.getenv('SILICONFLOW_API_KEY')
            if not api_key:
                raise ValueError("缺少硅基流动API密钥")
            
            # 设置默认模型
            if not self.model:
                self.model = os.getenv('SILICONFLOW_MODEL', 'Qwen/Qwen2.5-72B-Instruct')
            
            # 创建客户端，使用硅基流动的API端点
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
            )
            
            print(f"✅ 硅基流动客户端初始化成功，模型: {self.model}")
            
        except ImportError:
            print("❌ 未安装openai库，无法使用硅基流动API")
            self.client = None
        except Exception as e:
            print(f"❌ 硅基流动客户端初始化失败: {e}")
            self.client = None
    
    def _init_openai_client(self, api_key: str = None):
        """初始化OpenAI客户端"""
        try:
            import openai
            
            # 使用API密钥
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("缺少OpenAI API密钥")
            
            # 设置默认模型
            if not self.model:
                self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
            
            # 创建客户端
            self.client = openai.OpenAI(api_key=api_key)
            
            print(f"✅ OpenAI客户端初始化成功，模型: {self.model}")
            
        except ImportError:
            print("❌ 未安装openai库，无法使用OpenAI API")
            self.client = None
        except Exception as e:
            print(f"❌ OpenAI客户端初始化失败: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        return self.client is not None
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.1, 
                       max_tokens: int = 2000) -> Optional[str]:
        """
        聊天完成API调用
        
        Args:
            messages: 消息列表，格式为 [{"role": "system/user/assistant", "content": "内容"}]
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AI回复内容，失败时返回None
        """
        if not self.client:
            print("❌ LLM客户端未初始化")
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ LLM API调用失败: {e}")
            return None
    
    def simple_completion(self, prompt: str, 
                         system_prompt: str = None,
                         temperature: float = 0.1, 
                         max_tokens: int = 2000) -> Optional[str]:
        """
        简单完成API调用
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            AI回复内容，失败时返回None
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages, temperature, max_tokens)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取提供商信息"""
        return {
            "provider": self.provider,
            "model": self.model,
            "available": self.is_available(),
            "api_base": getattr(self.client, 'base_url', None) if self.client else None
        }


# 便捷函数
def create_llm_client(provider: str = None, api_key: str = None, model: str = None) -> LLMClient:
    """创建LLM客户端的便捷函数"""
    return LLMClient(provider, api_key, model)


def get_available_providers() -> List[str]:
    """获取所有可用的LLM提供商"""
    providers = []
    
    # 检查硅基流动
    if os.getenv('SILICONFLOW_API_KEY'):
        providers.append(LLMProvider.SILICONFLOW.value)
    
    # 检查OpenAI
    if os.getenv('OPENAI_API_KEY'):
        providers.append(LLMProvider.OPENAI.value)
    
    return providers


def auto_select_provider() -> str:
    """自动选择最佳可用的LLM提供商"""
    available = get_available_providers()
    
    if not available:
        raise ValueError("没有可用的LLM提供商，请配置API密钥")
    
    # 优先选择硅基流动
    if LLMProvider.SILICONFLOW.value in available:
        return LLMProvider.SILICONFLOW.value
    
    # 备选OpenAI
    if LLMProvider.OPENAI.value in available:
        return LLMProvider.OPENAI.value
    
    return available[0]


if __name__ == "__main__":
    """测试LLM客户端"""
    print("🤖 测试LLM客户端...")
    
    try:
        # 自动选择提供商
        provider = auto_select_provider()
        print(f"自动选择提供商: {provider}")
        
        # 创建客户端
        client = create_llm_client(provider)
        
        if client.is_available():
            print("客户端可用，进行测试...")
            
            response = client.simple_completion(
                "你好，请简单介绍一下自己。",
                "你是TaskWeaver AI项目规划助手。"
            )
            
            if response:
                print(f"✅ 测试成功: {response[:100]}...")
            else:
                print("❌ 测试失败")
        else:
            print("❌ 客户端不可用")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
