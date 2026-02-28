#!/usr/bin/env python
"""测试CourseFile模型"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, CourseFile

def test_course_files():
    print("=" * 60)
    print("测试课程文件功能")
    print("=" * 60)
    
    # 获取教师和课程
    teachers = User.objects.filter(profile__user_type='teacher')
    print(f"\n教师数量: {teachers.count()}")
    
    for teacher in teachers:
        print(f"\n教师: {teacher.username}")
        courses = Course.objects.filter(instructor=teacher)
        print(f"  课程数: {courses.count()}")
        
        for course in courses:
            print(f"\n  课程: {course.title}")
            files = CourseFile.objects.filter(course=course)
            print(f"    文件数: {files.count()}")
            
            for file in files:
                print(f"      - {file.file_name}")
                print(f"        类型: {file.get_file_type_display()}")
                print(f"        大小: {file.file_size} bytes")
                print(f"        上传者: {file.uploaded_by.username if file.uploaded_by else '未知'}")
                print(f"        上传时间: {file.created_at}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_course_files()
