from django.db import transaction
from .models import ModelRanking, RankingHistory
from apps.system.services import log_rank_change


def update_model_rankings(dataset_id):
    """
    更新指定数据集上的所有模型排名
    
    Args:
        dataset_id: 数据集ID
    """
    from apps.datasets.models import Dataset
    from apps.tasks.models import EvaluationSummary
    
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return {"error": f"Dataset with id {dataset_id} not found"}
    
    # 获取该数据集上的所有评测结果
    summaries = EvaluationSummary.objects.filter(
        task__dataset=dataset
    ).select_related('task__myModel').order_by('-accuracy', '-avg_score')
    
    if not summaries.exists():
        return {"error": f"No evaluation results found for dataset {dataset.name}"}
    
    with transaction.atomic():
        # 获取当前所有排名记录
        existing_rankings = {
            ranking.model_id: ranking for ranking in 
            ModelRanking.objects.filter(dataset=dataset)
        }
        
        # 更新排名
        for index, summary in enumerate(summaries, 1):
            model = summary.task.myModel
            old_rank = None
            
            # 获取旧排名
            if model.id in existing_rankings:
                old_rank = existing_rankings[model.id].rank
                # 更新现有排名记录
                ranking = existing_rankings[model.id]
                ranking.previous_rank = ranking.rank
                ranking.rank = index
                ranking.score = summary.accuracy or summary.avg_score or 0
                ranking.save()
            else:
                # 创建新排名记录
                ranking = ModelRanking.objects.create(
                    model=model,
                    dataset=dataset,
                    rank=index,
                    score=summary.accuracy or summary.avg_score or 0,
                    previous_rank=None
                )
            
            # 记录排名历史
            RankingHistory.objects.create(
                model=model,
                dataset=dataset,
                rank=index,
                score=summary.accuracy or summary.avg_score or 0
            )
            
            # 如果排名上升，记录系统事件
            if old_rank is not None and old_rank > index:
                rank_change = old_rank - index
                log_rank_change(model, old_rank, index)
    
    return {
        "success": True,
        "message": f"Updated rankings for dataset {dataset.name}",
        "dataset": dataset.name,
        "total_models": summaries.count()
    }


def get_top_models(dataset_id, limit=10):
    """
    获取指定数据集上的顶级模型
    
    Args:
        dataset_id: 数据集ID
        limit: 返回数量限制
        
    Returns:
        模型排名列表
    """
    try:
        rankings = ModelRanking.objects.filter(
            dataset_id=dataset_id
        ).select_related('model', 'dataset').order_by('rank')[:limit]
        
        return [
            {
                "rank": ranking.rank,
                "model_id": ranking.model.id,
                "model_name": ranking.model.name,
                "company": ranking.model.company,
                "score": ranking.score,
                "previous_rank": ranking.previous_rank,
                "rank_change": ranking.previous_rank - ranking.rank if ranking.previous_rank else None
            }
            for ranking in rankings
        ]
    except Exception as e:
        return {"error": str(e)}


def get_model_ranking_history(model_id, dataset_id=None):
    """
    获取模型的排名历史
    
    Args:
        model_id: 模型ID
        dataset_id: 可选的数据集ID，如果提供则只返回该数据集的历史
        
    Returns:
        排名历史列表
    """
    query = RankingHistory.objects.filter(model_id=model_id)
    
    if dataset_id:
        query = query.filter(dataset_id=dataset_id)
    
    history = query.select_related('model', 'dataset').order_by('-recorded_at')
    
    return [
        {
            "rank": h.rank,
            "score": h.score,
            "dataset_name": h.dataset.name,
            "recorded_at": h.recorded_at
        }
        for h in history
    ]