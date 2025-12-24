from .models import SystemEvent


def log_rank_change(model_obj, old_rank, new_rank):
    """
    记录模型排名变化的系统事件
    
    Args:
        model_obj: 模型对象
        old_rank: 旧排名
        new_rank: 新排名
    """
    if old_rank is None or new_rank is None:
        return
        
    rank_change = old_rank - new_rank  # 排名数字越小，排名越高
    
    company_name = getattr(model_obj, 'company', '') or '未知公司'
        
    # --- 添加调试代码 ---
    print(f"DEBUG: model_id={model_obj.id}, model_name={model_obj.name}")
    print(f"DEBUG: company_name value is: '{company_name}' (type: {type(company_name)})")
    if rank_change > 0:  # 排名上升
        SystemEvent.objects.create(
            event_type='rank_up',
            actor_name="榜单更新",
            target_id=model_obj.id,
            target_name=model_obj.name,
            target_extra=company_name,
            message=f"{company_name} 的模型 {model_obj.name} 排名飙升，上升了 {rank_change} 位！"
        )


def log_task_complete(task_obj, user_obj=None):
    """
    记录评测任务完成的系统事件
    
    Args:
        task_obj: 任务对象
        user_obj: 用户对象（可选）
    """
    actor_name = "系统"
    actor_id = None
    
    if user_obj:
        actor_name = user_obj.username
        actor_id = user_obj.id
    
    SystemEvent.objects.create(
        event_type='task_complete',
        actor_id=actor_id,
        actor_name=actor_name,
        target_id=task_obj.id,
        target_name=task_obj.name,
        message=f"评测任务「{task_obj.name}」已完成"
    )


def log_task_create(task_obj, user_obj=None):
    """
    记录评测任务创建/启动的系统事件
    """
    actor_name = "系统"
    actor_id = None
    
    if user_obj:
        actor_name = user_obj.username
        actor_id = user_obj.id

    SystemEvent.objects.create(
        event_type='task_create',
        actor_id=actor_id,
        actor_name=actor_name,
        target_id=task_obj.id,
        target_name=task_obj.name,
        message=f"发起了新的评测任务「{task_obj.name}」"
    )