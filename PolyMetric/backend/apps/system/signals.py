from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.datasets.models import Dataset
from apps.models.models import My_Model
from .models import SystemEvent


@receiver(post_save, sender=Dataset)
def log_dataset_upload(sender, instance, created, **kwargs):
    """
    当用户上传新数据集时，记录系统事件
    """
    if created and instance.is_public:  # 仅记录公开数据集
        SystemEvent.objects.create(
            event_type='dataset_upload',
            actor_id=instance.creator.id,
            actor_name=instance.creator.username,
            target_id=instance.id,
            target_name=instance.name,
            message=f"用户 {instance.creator.username} 上传了新数据集「{instance.name}」"
        )


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