from django.db import models


class SystemEvent(models.Model):
    """
    记录系统全局动态，用于首页 News Feed 展示
    """
    EVENT_TYPES = [
        ('dataset_upload', '数据集上传'),  # 绿色
        ('model_add', '模型收录'),      # 蓝色
        ('rank_up', '排名上升'),        # 金色/橙色
        ('task_complete', '评测完成'),  # 灰色
        ('task_create', '发起评测'),    # 新增：青色/紫色
    ]

    # 1. 事件元数据
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True, verbose_name="事件类型")
    
    # 2. 触发者 (Actor) - 记录当时的快照，防止用户注销后数据丢失
    actor_id = models.IntegerField(null=True, blank=True, help_text="触发事件的用户ID，系统事件可为空")
    actor_name = models.CharField(max_length=150, default="PolyMetric系统", verbose_name="触发者名称")
    
    # 3. 目标对象 (Target) - 记录当时的对象信息
    target_id = models.IntegerField(null=True, blank=True)
    target_name = models.CharField(max_length=255, verbose_name="目标名称", help_text="如模型名、数据集名")
    target_extra = models.CharField(max_length=255, blank=True, verbose_name="额外信息", help_text="如模型公司、排名变化幅度")

    # 4. 展示文案
    # 建议在写入时生成好，避免读取时反复拼接，也支持历史文案不随对象改名而改变
    message = models.TextField(verbose_name="动态消息内容") 

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "系统动态"
        verbose_name_plural = "系统动态"

    def __str__(self):
        return f"{self.get_event_type_display()}: {self.message[:50]}..."