# PolyMetric/celery.py
import os

try:
    from celery import Celery
    
    # 设置 Django settings 模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
    
    app = Celery('PolyMetric')
    
    # 从 Django settings 加载配置
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # 自动发现所有已注册 app 下的 tasks.py 模块
    app.autodiscover_tasks()
    
    
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
    
    @app.task
    def update_all_rankings():
        """
        定期更新所有数据集的排名
        """
        from apps.datasets.models import Dataset
        from apps.rankings.services import update_model_rankings
        
        datasets = Dataset.objects.all()
        results = []
        
        for dataset in datasets:
            result = update_model_rankings(dataset.id)
            results.append({
                "dataset_id": dataset.id,
                "dataset_name": dataset.name,
                "result": result
            })
        
        return {
            "message": "Rankings update completed",
            "results": results
        }
        
except ImportError:
    # 如果没有安装celery，创建一个占位符
    class MockCelery:
        def __init__(self, *args, **kwargs):
            pass
        
        def config_from_object(self, *args, **kwargs):
            pass
            
        def autodiscover_tasks(self):
            pass
            
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    app = MockCelery()
