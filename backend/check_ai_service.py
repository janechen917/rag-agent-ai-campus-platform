#!/usr/bin/env python
"""
AI服务诊断脚本
检查AI服务配置和连接状态
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from django.conf import settings
from ai_service.ai_engine import ai_service

def check_dependencies():
    """检查依赖安装情况"""
    print("=" * 60)
    print("【依赖检查】")
    print("=" * 60)
    
    deps = {
        'Django': 'django',
        'LangChain': 'langchain',
        'LangChain Community': 'langchain_community',
        'LangChain OpenAI': 'langchain_openai',
        'OpenAI': 'openai',
        'Transformers': 'transformers',
        'Sentence Transformers': 'sentence_transformers',
    }
    
    for name, module in deps.items():
        try:
            __import__(module)
            print(f"✓ {name:25} 已安装")
        except ImportError:
            print(f"✗ {name:25} 未安装")
    print()

def check_config():
    """检查配置"""
    print("=" * 60)
    print("【配置检查】")
    print("=" * 60)
    
    api_key = settings.OPENAI_API_KEY
    if api_key and api_key != 'your-openai-api-key-here':
        masked_key = api_key[:8] + '*' * 20 + api_key[-4:]
        print(f"✓ OPENAI_API_KEY:        {masked_key}")
    else:
        print(f"✗ OPENAI_API_KEY:        未配置")
        print(f"  兼容变量: OPENAI_API_KEY / GITHUB_MODEL_API_KEY / GITHUB_TOKEN")
    
    print(f"  AI_MODEL_NAME:         {settings.AI_MODEL_NAME}")
    print(f"  USE_GITHUB_MODELS:     {settings.USE_GITHUB_MODELS}")
    print(f"  OPENAI_API_BASE:       {settings.OPENAI_API_BASE}")
    print()

def check_service():
    """检查服务状态"""
    print("=" * 60)
    print("【服务状态】")
    print("=" * 60)
    
    print(f"  LLM初始化状态:         {'✓ 已初始化' if ai_service.llm else '✗ 未初始化'}")
    print(f"  Embeddings状态:        {'✓ 已初始化' if ai_service.embeddings else '✗ 未初始化'}")
    print(f"  本地Embeddings:        {'✓ 可用' if ai_service.local_embeddings else '✗ 不可用'}")
    print()

def test_chat():
    """测试聊天功能"""
    print("=" * 60)
    print("【功能测试】")
    print("=" * 60)
    
    test_messages = [
        "你好",
        "Python怎么学？",
        "什么是Django？"
    ]
    
    for msg in test_messages:
        print(f"\n用户: {msg}")
        try:
            response = ai_service.chat(msg)
            print(f"AI: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    print()

def provide_solutions():
    """提供解决方案"""
    print("=" * 60)
    print("【解决方案】")
    print("=" * 60)
    
    if not ai_service.llm:
        print("""
⚠️  AI服务未正常初始化，可能的原因：

1. API密钥未配置
   解决方法：
   - 设置环境变量：export OPENAI_API_KEY="your-api-key"
   - 或在 .env 文件中添加：OPENAI_API_KEY=your-api-key

2. 使用GitHub Models
   解决方法：
   - 设置 USE_GITHUB_MODELS=True
   - 设置 GITHUB_TOKEN=your-github-token
   - 模型会自动使用GitHub Models API

3. 依赖未安装
   解决方法：
   - 安装LangChain: pip install langchain langchain-community langchain-openai
   - 安装OpenAI SDK: pip install openai

📝 当前状态：
   系统将使用备用响应模式，提供基础的学习建议和资源推荐。
   虽然不能使用完整的AI智能功能，但仍可为用户提供有用的帮助。
        """)
    else:
        print("""
✓ AI服务运行正常！

如果在使用中遇到问题，可能是：
1. 网络连接问题 - 检查网络和代理设置
2. API配额限制 - 检查OpenAI账户余额
3. API调用超时 - 可以尝试重新发送

系统已配置备用响应机制，即使AI服务暂时不可用，
也会为用户提供有用的学习建议。
        """)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  AI学习导师 - 服务诊断工具")
    print("=" * 60 + "\n")
    
    check_dependencies()
    check_config()
    check_service()
    test_chat()
    provide_solutions()
    
    print("=" * 60)
    print("诊断完成！")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
