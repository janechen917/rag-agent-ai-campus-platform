"""
Management command：为课程建立 RAG 向量索引

用法：
  python manage.py index_course --course_id 5      # 单门课
  python manage.py index_course --all              # 所有课
  python manage.py index_course --list             # 列出已建索引的课程
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from courses.models import Course


class Command(BaseCommand):
    help = '为课程建立 RAG 向量索引（解析 CourseFile → 向量化 → FAISS）'

    def add_arguments(self, parser):
        parser.add_argument('--course_id', type=int, help='指定课程 ID')
        parser.add_argument('--all', action='store_true', help='为所有有文件的课程建索引')
        parser.add_argument('--list', action='store_true', help='列出已建索引的课程')

    def handle(self, *args, **opts):
        if opts['list']:
            self._list_indexed()
            return

        if opts['all']:
            self._build_all()
            return

        course_id = opts.get('course_id')
        if not course_id:
            raise CommandError('请指定 --course_id <ID> 或 --all 或 --list')
        self._build_one(course_id)

    # ------------ 内部方法 ------------

    def _list_indexed(self):
        root = Path(settings.RAG_VECTOR_DB_ROOT)
        if not root.exists():
            self.stdout.write('暂无任何索引')
            return
        items = sorted(root.glob('course_*'))
        if not items:
            self.stdout.write('暂无任何索引')
            return
        self.stdout.write(self.style.SUCCESS(f'已建索引的课程（共 {len(items)} 门）：'))
        for d in items:
            try:
                cid = int(d.name.replace('course_', ''))
                course = Course.objects.filter(id=cid).first()
                title = course.title if course else '<已删除>'
            except ValueError:
                cid, title = '?', d.name
            faiss_file = d / 'index.faiss'
            size = faiss_file.stat().st_size if faiss_file.exists() else 0
            self.stdout.write(f'  course_{cid:>3}  {title:<30}  {size/1024:>8.1f} KB')

    def _build_all(self):
        # 找有文件的课程
        course_ids = (
            Course.objects.filter(files__file__isnull=False)
            .values_list('id', flat=True)
            .distinct()
        )
        if not course_ids:
            self.stdout.write(self.style.WARNING('没有任何课程包含文件'))
            return
        self.stdout.write(f'将为 {len(course_ids)} 门课建索引...\n')
        for cid in course_ids:
            self._build_one(cid)

    def _build_one(self, course_id: int):
        course = Course.objects.filter(id=course_id).first()
        if not course:
            self.stderr.write(self.style.ERROR(f'课程 {course_id} 不存在'))
            return

        self.stdout.write(f'\n📚 课程 {course_id}《{course.title}》建索引中...')

        # 延迟导入：确保 Django 已就绪、避免启动时加载 transformers
        from ai_service.rag import build_course_index

        try:
            result = build_course_index(course_id)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'  ✗ 失败: {e}'))
            return

        files = result.get('files', 0)
        chunks = result.get('chunks', 0)
        skipped = result.get('skipped', [])
        msg = result.get('message')

        if msg:
            self.stdout.write(self.style.WARNING(f'  ⚠ {msg}'))
        self.stdout.write(f'  ✓ 处理文件: {files}')
        self.stdout.write(f'  ✓ 片段总数: {chunks}')
        if skipped:
            self.stdout.write(f'  ⚠ 跳过 {len(skipped)} 个:')
            for s in skipped:
                self.stdout.write(f'     - {s}')
        if 'index_dir' in result:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 索引位置: {result["index_dir"]}'))
