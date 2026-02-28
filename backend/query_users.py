#!/usr/bin/env python
"""
用户数据库查询工具
用于查询和管理注册用户信息
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone


def show_all_users():
    """显示所有用户信息"""
    users = User.objects.all().order_by('-date_joined')
    
    print("\n" + "="*80)
    print(f"{'校园智慧学习平台 - 用户数据库':^80}")
    print("="*80)
    print(f"总用户数: {users.count()}\n")
    
    if not users:
        print("暂无用户注册\n")
        return
    
    for user in users:
        print(f"┌{'─'*78}┐")
        print(f"│ 用户ID: {user.id:<69} │")
        print(f"│ 用户名: {user.username:<69} │")
        print(f"│ 邮箱: {user.email:<71} │")
        print(f"│ 注册时间: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S'):<65} │")
        print(f"│ 最后登录: {(user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'):<65} │")
        print(f"│ 账户状态: {'✓ 已激活' if user.is_active else '✗ 未激活':<66} │")
        print(f"│ 权限: {('管理员' if user.is_superuser else ('员工' if user.is_staff else '普通用户')):<70} │")
        
        try:
            token = Token.objects.get(user=user)
            print(f"│ Token: {token.key:<70} │")
            print(f"│ Token创建时间: {token.created.strftime('%Y-%m-%d %H:%M:%S'):<61} │")
        except Token.DoesNotExist:
            print(f"│ Token: {'未创建':<70} │")
        
        print(f"└{'─'*78}┘\n")


def search_user(keyword):
    """搜索用户"""
    users = User.objects.filter(
        username__icontains=keyword
    ) | User.objects.filter(
        email__icontains=keyword
    )
    
    print(f"\n搜索关键词: '{keyword}' - 找到 {users.count()} 个结果\n")
    
    for user in users:
        print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")


def get_user_stats():
    """获取用户统计信息"""
    total = User.objects.count()
    active = User.objects.filter(is_active=True).count()
    staff = User.objects.filter(is_staff=True).count()
    superuser = User.objects.filter(is_superuser=True).count()
    
    # 最近7天注册用户
    from datetime import timedelta
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    print("\n" + "="*50)
    print("用户统计信息")
    print("="*50)
    print(f"总用户数: {total}")
    print(f"激活用户: {active}")
    print(f"员工账户: {staff}")
    print(f"管理员账户: {superuser}")
    print(f"最近7天注册: {recent}")
    print("="*50 + "\n")


def create_test_user():
    """创建测试用户"""
    username = input("输入用户名: ")
    email = input("输入邮箱: ")
    password = input("输入密码: ")
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        token = Token.objects.create(user=user)
        
        print(f"\n✓ 用户创建成功!")
        print(f"用户ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"Token: {token.key}\n")
        
    except Exception as e:
        print(f"\n✗ 创建失败: {e}\n")


def delete_user():
    """删除用户"""
    username = input("输入要删除的用户名: ")
    
    try:
        user = User.objects.get(username=username)
        confirm = input(f"确认删除用户 '{username}'? (yes/no): ")
        
        if confirm.lower() == 'yes':
            user.delete()
            print(f"\n✓ 用户 '{username}' 已删除\n")
        else:
            print("\n取消删除\n")
            
    except User.DoesNotExist:
        print(f"\n✗ 用户 '{username}' 不存在\n")


def main_menu():
    """主菜单"""
    while True:
        print("\n" + "="*50)
        print("数据库查询工具 - 主菜单")
        print("="*50)
        print("1. 查看所有用户")
        print("2. 搜索用户")
        print("3. 用户统计")
        print("4. 创建测试用户")
        print("5. 删除用户")
        print("0. 退出")
        print("="*50)
        
        choice = input("\n请选择操作 (0-5): ").strip()
        
        if choice == '1':
            show_all_users()
        elif choice == '2':
            keyword = input("输入搜索关键词: ")
            search_user(keyword)
        elif choice == '3':
            get_user_stats()
        elif choice == '4':
            create_test_user()
        elif choice == '5':
            delete_user()
        elif choice == '0':
            print("\n再见!\n")
            break
        else:
            print("\n无效选择，请重试\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            show_all_users()
        elif sys.argv[1] == '--stats':
            get_user_stats()
        else:
            print("用法: python query_users.py [--list|--stats]")
    else:
        main_menu()
