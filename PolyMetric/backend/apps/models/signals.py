from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import My_Model
from apps.system.models import SystemEvent


@receiver(post_save, sender=My_Model)
def log_model_add(sender, instance, created, **kwargs):
    """
    当平台新增模型时，记录系统事件
    """
    if created:
        SystemEvent.objects.create(
            event_type='model_add',
            actor_name="系统管理员",
            target_id=instance.id,
            target_name=instance.name,
            target_extra=instance.company or "",
            message=f"平台新收录模型：{instance.name} ({instance.company or '未知公司'})"
        )