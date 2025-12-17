from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Dataset
from apps.system.models import SystemEvent


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