# app/services/llm_factory.py
from typing import Literal, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from app.core.config import settings
from app.core.logger import logger


class LLMFactory:
    """LLM 工厂类 - 管理模型"""

    # 支持的提供商和模型
    PROVIDERS = {
        "qwen": {
            "default": "qwen-plus",
            "premium": "qwen-max",
            "fast": "qwen-plus"
        },
        "deepseek": {
            "default": "deepseek-chat",
            "premium": "deepseek-chat",
            "fast": "deepseek-chat"
        },
        "siliconflow": {
            "default": "Qwen/Qwen2-7B-Instruct",
            "premium": "meta-llama/Llama-2-70b-chat-hf",
            "fast": "Qwen/Qwen2-7B-Instruct"
        }
    }

    @staticmethod
    def create_chat_model(
        provider: Literal["qwen", "deepseek", "siliconflow"] = "qwen",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        创建 ChatModel 实例
        
        Args:
            provider: LLM 提供商 (qwen, deepseek, siliconflow)
            model_name: 模型名称 (为 None 则使用默认推荐模型)
            temperature: 采样温度 (0.0-1.0)
            max_tokens: 最大输出 token 数
            **kwargs: 其他模型特定参数
            
        Returns:
            BaseChatModel 实例
            
        Examples:
            >>> llm = LLMFactory.create_chat_model(provider="qwen")
            >>> llm = LLMFactory.create_chat_model(provider="deepseek", model_name="deepseek-chat")
        """
        
        # 使用默认模型
        if model_name is None:
            model_name = LLMFactory.PROVIDERS[provider]["default"]

        # 基础配置
        base_config = {
            "temperature": temperature,
            "model": model_name,
        }
        
        if max_tokens:
            base_config["max_tokens"] = max_tokens

        # 合并自定义参数
        config = {**base_config, **kwargs}

        try:
            if provider == "qwen":
                # 阿里云 Qwen - 使用 OpenAI 兼容 API
                llm = ChatOpenAI(
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    api_key=settings.QWEN_API_KEY,
                    **config
                )
                logger.success(f"✅ 阿里云 Qwen 模型已加载: {model_name}")
                return llm
            
            elif provider == "deepseek":
                # Deepseek - 使用 OpenAI 兼容 API
                llm = ChatOpenAI(
                    base_url="https://api.deepseek.com",
                    api_key=settings.DEEPSEEK_API_KEY,
                    **config
                )
                logger.success(f"✅ Deepseek 模型已加载: {model_name}")
                return llm
            
            elif provider == "siliconflow":
                # Siliconflow - 使用 OpenAI 兼容 API
                llm = ChatOpenAI(
                    base_url="https://api.siliconflow.cn/v1",
                    api_key=settings.SILICONFLOW_API_KEY,
                    **config
                )
                logger.success(f"✅ Siliconflow 模型已加载: {model_name}")
                return llm
            
            else:
                logger.error(f"❌ 不支持的提供商: {provider}")
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"❌ LLM 模型创建失败 ({provider}/{model_name}): {e}")
            raise

    @staticmethod
    def create_with_tools(
        tools: List,
        provider: str = "qwen",
        model_name: Optional[str] = None,
        system_prompt: str = "",
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """
        创建带有工具绑定的 ChatModel
        
        Args:
            tools: LangChain Tool 列表
            provider: LLM 提供商
            model_name: 模型名称
            system_prompt: 系统提示词（可选）
            temperature: 采样温度
            **kwargs: 其他配置参数
            
        Returns:
            带有工具绑定的 ChatModel
            
        Examples:
            >>> from langchain.tools import tool
            >>> @tool
            >>> def search(query: str) -> str:
            >>>     return f"Results for {query}"
            >>> llm = LLMFactory.create_with_tools([search], provider="qwen")
        """
        
        try:
            # 创建基础 LLM
            llm = LLMFactory.create_chat_model(
                provider=provider,
                model_name=model_name,
                temperature=temperature,
                **kwargs
            )
            
            # 绑定工具到模型
            llm_with_tools = llm.bind_tools(tools)
            logger.info(f"✅ 已绑定 {len(tools)} 个工具到模型")
            
            return llm_with_tools
            
        except Exception as e:
            logger.error(f"❌ 工具绑定失败: {e}")
            raise

    @staticmethod
    def get_preset_config(preset: Literal["fast", "balanced", "quality"]) -> dict:
        """
        获取预设配置
        
        Args:
            preset: 预设类型
                - fast: 快速响应 (Deepseek-Chat, 温度 0.5)
                - balanced: 平衡 (Qwen-Plus, 温度 0.7) 
                - quality: 高质量 (Qwen-Max, 温度 0.7)
                
        Returns:
            包含 provider 和 config 的字典
        """
        
        presets = {
            "fast": {
                "provider": "deepseek",
                "config": {
                    "model_name": "deepseek-chat",
                    "temperature": 0.5,
                    "max_tokens": 1000
                }
            },
            "balanced": {
                "provider": "qwen",
                "config": {
                    "model_name": "qwen-plus",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            },
            "quality": {
                "provider": "qwen",
                "config": {
                    "model_name": "qwen-max",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
        }
        
        if preset not in presets:
            logger.warning(f"⚠️ 未知的预设 {preset}，使用默认配置")
            preset = "balanced"
        
        return presets[preset]


# 单例模式 - 全局 LLM 实例
class LLMManager:
    """LLM 管理器 - 维护全局模型实例"""
    
    _instances = {}

    def __init__(self, name: str = "default"):
        """
        初始化 LLM 管理器
        
        Args:
            name: 模型实例名称
        """
        self.name = name
        self._model: Optional[BaseChatModel] = None
        self._initialize()

    def _initialize(self):
        """内部初始化方法"""
        try:
            # 创建默认 LLM 实例
            self._model = LLMFactory.create_chat_model(
                provider=settings.LLM_PROVIDER,
                model_name=settings.LLM_MODEL_NAME,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            logger.success(f"✅ LLM 管理器 '{self.name}' 已初始化")
        except Exception as e:
            logger.error(f"❌ LLM 管理器初始化失败: {e}")
            raise

    def get_model(self) -> BaseChatModel:
        """获取 LLM 模型实例"""
        if self._model is None:
            logger.warning(f"⚠️ 模型未初始化，尝试重新初始化...")
            self._initialize()
        return self._model

    def invoke(self, messages, **kwargs):
        """调用模型"""
        try:
            return self._model.invoke(messages, **kwargs)
        except Exception as e:
            logger.error(f"❌ 模型调用失败: {e}")
            raise

    @classmethod
    def get_instance(cls, name: str = "default") -> 'LLMManager':
        """
        获取单例实例
        
        Args:
            name: 实例名称
            
        Returns:
            LLMManager 单例实例
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]


# 全局单例实例
try:
    llm_manager = LLMManager.get_instance()
    logger.success("✅ LLM 工厂已就绪")
except Exception:
    llm_manager = None
    logger.error("❌ LLM 工厂初始化失败")


if __name__ == "__main__":
    # 测试基础创建
    logger.info("=== 测试 LLM Factory ===")
    
    # 1. 创建 Qwen 模型
    logger.info("\n1️⃣ 创建阿里云 Qwen 模型...")
    llm_qwen = LLMFactory.create_chat_model(provider="qwen")
    
    # 2. 创建 Deepseek 模型
    logger.info("\n2️⃣ 创建 Deepseek 模型...")
    llm_deepseek = LLMFactory.create_chat_model(provider="deepseek")
    
    # 3. 创建 Siliconflow 模型
    logger.info("\n3️⃣ 创建 Siliconflow 模型...")
    llm_siliconflow = LLMFactory.create_chat_model(provider="siliconflow")
    
    # 4. 使用预设配置
    logger.info("\n4️⃣ 使用快速预设...")
    config = LLMFactory.get_preset_config("fast")
    logger.info(f"预设配置: {config}")
    
    logger.success("✅ 所有测试通过！")