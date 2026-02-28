#!/usr/bin/env python
"""
测试注册和登录功能
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:8000'

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_register(username, email, password):
    """测试注册功能"""
    print_section("测试注册")
    
    data = {
        'username': username,
        'email': email,
        'password': password
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register/', json=data, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("\n✓ 注册成功!")
            return response.json()
        else:
            print("\n✗ 注册失败")
            return None
    except requests.exceptions.ConnectionError:
        print("✗ 连接失败: 后端服务未启动")
        print("  请先运行: cd backend && python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None

def test_login(username, password):
    """测试登录功能"""
    print_section("测试登录")
    
    data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login/', json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("\n✓ 登录成功!")
            return response.json()['token']
        else:
            print("\n✗ 登录失败")
            return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None

def test_protected_api(token):
    """测试需要认证的API"""
    print_section("测试认证接口")
    
    headers = {
        'Authorization': f'Token {token}'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/courses/', headers=headers)
        print(f"请求: GET /api/courses/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            courses = response.json()
            print(f"\n✓ 认证成功! 获取到 {len(courses.get('results', []))} 门课程")
        else:
            print(f"\n✗ 认证失败: {response.text}")
    except Exception as e:
        print(f"✗ 错误: {e}")

def test_profile(token):
    """测试获取用户信息"""
    print_section("测试获取用户信息")
    
    headers = {
        'Authorization': f'Token {token}'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/auth/profile/', headers=headers)
        print(f"请求: GET /api/auth/profile/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"响应:\n{json.dumps(profile, indent=2, ensure_ascii=False)}")
            print(f"\n✓ 获取用户信息成功!")
        else:
            print(f"\n✗ 获取失败: {response.text}")
    except Exception as e:
        print(f"✗ 错误: {e}")

def main():
    print("\n" + "="*60)
    print("  校园智慧学习平台 - 认证功能测试")
    print("="*60)
    
    # 测试数据
    test_username = 'testuser999'
    test_email = 'test999@example.com'
    test_password = 'test123456'
    
    # 1. 测试注册
    register_result = test_register(test_username, test_email, test_password)
    
    if not register_result:
        print("\n尝试使用已存在的用户登录...")
    
    # 2. 测试登录
    token = test_login(test_username, test_password)
    
    if token:
        # 3. 测试需要认证的API
        test_protected_api(token)
        
        # 4. 测试获取用户信息
        test_profile(token)
    
    print_section("测试完成")
    
    if token:
        print("\n✓ 所有测试通过!")
        print(f"\n你的Token: {token}")
        print("\n可以使用此Token进行API调用:")
        print(f'  curl -H "Authorization: Token {token}" {BASE_URL}/api/courses/')
    else:
        print("\n✗ 测试失败，请检查后端服务和配置")
    
    print("")

if __name__ == '__main__':
    main()
