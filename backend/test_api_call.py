#!/usr/bin/env python
"""测试AI API调用"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/workspaces/project-test/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from ai_service.ai_engine import AIService

def test_ai_service():
    print("="*50)
    print("测试AI服务")
    print("="*50)
    
    # 初始化AI服务
    ai = AIService()
    
    # 检查LLM状态
    print(f"\nLLM初始化状态: {'✓ 成功' if ai.llm else '✗ 失败'}")
    
    if ai.llm:
        print(f"模型: {ai.model_name}")
        print(f"API Base: {ai.api_base}")
        print(f"使用GitHub Models: {ai.use_github_models}")
        
        # 测试调用
        print("\n开始测试AI调用...")
        try:
            response = ai.chat("测试消息：你好")
            print(f"\n✓ AI响应成功")
            print(f"响应内容: {response[:200]}...")
        except Exception as e:
            print(f"\n✗ AI调用失败")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {e}")
    else:
        print("\n✗ LLM未初始化，无法进行API调用测试")

if __name__ == '__main__':
    test_ai_service()
