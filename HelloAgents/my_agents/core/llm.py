"""
hello_agents.core.llm
=====================

HelloAgentsLLM —— 统一 LLM 调用接口。

本模块对底层大语言模型（LLM）的调用细节进行封装，向上层 Agent 提供
一致的 ``chat`` / ``complete`` 接口，屏蔽不同 SDK 的差异。

支持的后端（通过 Config 中的 ``provider`` 字段切换）:
    - ``anthropic``  : Anthropic Claude 系列
    - ``openai``     : OpenAI GPT 系列（预留）
    - ``ollama``     : 本地 Ollama 服务（预留）

典型用法::

    from hello_agents.core.llm import HelloAgentsLLM
    from hello_agents.core.config import Config

    cfg = Config(provider="anthropic", model="claude-sonnet-4-6", api_key="sk-...")
    llm = HelloAgentsLLM(config=cfg)
    reply = llm.chat([{"role": "user", "content": "你好"}])
"""

from __future__ import annotations

import os 

from typing import Dict, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

from  import SimpleAgent, HelloAgentsLLM

load_dotenv()

class baseLLM(HelloAgentsLLM):
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = "auto",
        **kwargs
    ):
        # 检查provider是否为我们想处理的'dashscope'
        if provider == "dashscope":
            print("正在使用自定义的 DashScope Provider")
            self.provider = "dashscope"

            # 解析 DashScope 的凭证
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

            # 验证凭证是否存在
            if not self.api_key:
                raise ValueError("DashScope API key not found. Please set DASHSCOPE_API_KEY environment variable.")

            # 设置默认模型和其他参数
            self.model = model or os.getenv("LLM_MODEL_ID") or "qwen3.5-flash"
            self.temperature = kwargs.get('temperature', 0.7)
            self.max_tokens = kwargs.get('max_tokens')
            self.timeout = kwargs.get('timeout', 60)
            
            # 使用获取的参数创建OpenAI客户端实例
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

        else:
            # 如果不是 dashscope, 则完全使用父类的原始逻辑来处理
            super().__init__(model=model, api_key=api_key, base_url=base_url, provider=provider, **kwargs)


if __name__ == '__main__':
    
    # 实例化我们重写的客户端，并指定provider
    llm = baseLLM(provider="dashscope")

    # 准备消息
    messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]

    # 发起调用，think等方法都已从父类继承，无需重写
    response_stream = llm.think(messages)

    # 打印响应
    print("ModelScope Response:")
    for chunk in response_stream:
        # chunk在my_llm库中已经打印过一遍，这里只需要pass即可
        # print(chunk, end="", flush=True)
        pass

