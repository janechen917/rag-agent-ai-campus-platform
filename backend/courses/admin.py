from django.contrib import admin
from .models import Course, Chapter, Lesson, Enrollment, LessonProgress, Review, CourseFile


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'price', 'students_count', 'rating', 'is_published']
    list_filter = ['category', 'level', 'is_published']
    search_fields = ['title', 'description']
    list_editable = ['is_published']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'duration_minutes', 'order', 'is_free']
    list_filter = ['chapter__course', 'is_free']
    search_fields = ['title']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress', 'completed', 'enrolled_at']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['user__username', 'course__title']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'last_position']
    list_filter = ['completed']
    search_fields = ['user__username', 'lesson__title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'course__title', 'content']


@admin.register(CourseFile)
class CourseFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'course', 'file_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'course__title', 'description']
    readonly_fields = ['file_size', 'created_at']
