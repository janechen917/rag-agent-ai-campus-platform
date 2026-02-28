#!/usr/bin/env python
"""测试教师课程功能"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_platform.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, UserProfile

def test_teacher_courses():
    print("=" * 50)
    print("测试教师课程功能")
    print("=" * 50)
    
    # 获取教师用户
    teachers = User.objects.filter(profile__user_type='teacher')
    print(f"\n教师用户数: {teachers.count()}")
    
    for teacher in teachers:
        print(f"\n教师: {teacher.username}")
        courses = Course.objects.filter(instructor=teacher)
        print(f"  课程数: {courses.count()}")
        
        for course in courses:
            print(f"  - {course.title}")
            print(f"    已发布: {course.is_published}")
            print(f"    学生数: {course.students_count}")
            print(f"    大纲: {'有' if course.syllabus else '无'}")
            print(f"    资料: {'有' if course.materials else '无'}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == '__main__':
    test_teacher_courses()
