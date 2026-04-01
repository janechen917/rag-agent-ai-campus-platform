from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    """
    简单的健康检查端点
    验证数据库连接和基本应用状态
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'debug': False,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
        }, status=503)
