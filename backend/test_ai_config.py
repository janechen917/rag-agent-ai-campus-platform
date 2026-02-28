#!/usr/bin/env python
"""
快速AI配置测试脚本（不需要torch）
"""
import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('/workspaces/project-test/.env')

print("\n" + "=" * 60)
print("  AI服务快速配置测试")
print("=" * 60 + "\n")

# 1. 检查环境变量
print("【环境变量检查】")
print("=" * 60)
api_key = os.getenv('OPENAI_API_KEY', '')
use_github = os.getenv('USE_GITHUB_MODELS', 'False')
api_base = os.getenv('OPENAI_API_BASE', '')
model_name = os.getenv('AI_MODEL_NAME', '')

if api_key and len(api_key) > 8:
    masked_key = api_key[:8] + '*' * 20 + api_key[-4:]
    print(f"✓ OPENAI_API_KEY:        {masked_key}")
else:
    print(f"✗ OPENAI_API_KEY:        未配置")

print(f"  USE_GITHUB_MODELS:     {use_github}")
print(f"  OPENAI_API_BASE:       {api_base}")
print(f"  AI_MODEL_NAME:         {model_name}")
print()

# 2. 检查LangChain依赖
print("【核心依赖检查】")
print("=" * 60)
deps = {
    'langchain': 'LangChain',
    'langchain_openai': 'LangChain OpenAI',
    'openai': 'OpenAI SDK',
}

all_installed = True
for module, name in deps.items():
    try:
        __import__(module)
        print(f"✓ {name:25} 已安装")
    except ImportError:
        print(f"✗ {name:25} 未安装")
        all_installed = False
print()

# 3. 测试AI服务初始化
if all_installed:
    print("【AI服务测试】")
    print("=" * 60)
    try:
        from langchain_openai import ChatOpenAI
        
        llm_config = {
            'model': model_name or 'gpt-4o-mini',
            'temperature': 0.7,
            'api_key': api_key,
        }
        
        if use_github == 'True' and api_base:
            llm_config['base_url'] = api_base
        
        llm = ChatOpenAI(**llm_config)
        print("✓ ChatOpenAI 实例创建成功")
        
        # 尝试简单调用
        print("\n测试消息发送...")
        from langchain_core.messages import HumanMessage
        
        response = llm([HumanMessage(content="你好，请用一句话介绍你自己")])
        print(f"\nAI回复: {response.content}")
        print("\n✓ AI服务运行正常！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print("\n可能的原因：")
        print("1. API密钥无效或已过期")
        print("2. 网络连接问题")
        print("3. API配额已用完")
        print("\n即使测试失败，系统仍会使用备用响应模式。")
else:
    print("【提示】")
    print("=" * 60)
    print("请先安装依赖：")
    print("  pip install langchain langchain-openai openai")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60 + "\n")
