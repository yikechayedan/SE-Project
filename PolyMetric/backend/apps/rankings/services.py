from django.db import transaction
from .models import ModelRanking, RankingHistory
from apps.system.services import log_rank_change


def _get_dataset_dimension(dataset):
    """根据数据集自动推断评测维度"""
    cat = dataset.category
    name = dataset.name.lower()
    
    if cat in ['multimodal', 'image']:
        return 'multimodal'
    
    if 'math' in name:
        return 'math'
    if 'code' in name:
        return 'code'
        
    return 'language'


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
            
            # --- 标准化分数计算 (Unified 0-100 Scale) ---
            normalized_score = 0.0
            if summary.task.method == 'subjective':
                # 主观评分 (1-10) -> 放大 10 倍
                val = summary.avg_score or 0
                normalized_score = val * 10
            else:
                # 客观/对抗 (0-1) -> 放大 100 倍
                val = summary.accuracy or 0
                normalized_score = val * 100
            
            normalized_score = round(normalized_score, 2)
            # ------------------------------------------

            # 获取旧排名
            if model.id in existing_rankings:
                old_rank = existing_rankings[model.id].rank
                # 更新现有排名记录
                ranking = existing_rankings[model.id]
                ranking.previous_rank = ranking.rank
                ranking.rank = index
                ranking.score = normalized_score
                ranking.save()
            else:
                # 创建新排名记录
                ranking = ModelRanking.objects.create(
                    model=model,
                    dataset=dataset,
                    rank=index,
                    score=normalized_score,
                    previous_rank=None
                )
            
            # 记录排名历史
            RankingHistory.objects.create(
                model=model,
                dataset=dataset,
                rank=index,
                score=normalized_score
            )
            
            # 如果排名上升，记录系统事件
            if old_rank is not None and old_rank > index:
                rank_change = old_rank - index
                log_rank_change(model, old_rank, index)

        # ==========================================
        # 新增：更新 ModelDimensionScore (首页大榜单)
        # ==========================================
        from .models import ModelDimensionScore
        from django.db.models import Avg

        target_dim = _get_dataset_dimension(dataset)
        
        # 获取本次更新涉及的所有模型
        involved_models = set(summary.task.myModel for summary in summaries)
        
        for model in involved_models:
            # 1. 更新特定维度的分数
            all_rankings = ModelRanking.objects.filter(model=model).select_related('dataset')
            
            dim_scores = []
            for r in all_rankings:
                if _get_dataset_dimension(r.dataset) == target_dim:
                    dim_scores.append(r.score)
            
            if dim_scores:
                avg_val = sum(dim_scores) / len(dim_scores)
                
                mds, _ = ModelDimensionScore.objects.get_or_create(model=model, dimension=target_dim)
                mds.previous_score = mds.score
                mds.score = avg_val
                mds.save()
                
            # 2. 更新 Overall 综合分数
            existing_dims = ModelDimensionScore.objects.filter(model=model).exclude(dimension='overall')
            if existing_dims.exists():
                overall_avg = existing_dims.aggregate(Avg('score'))['score__avg']
                
                mds_all, _ = ModelDimensionScore.objects.get_or_create(model=model, dimension='overall')
                mds_all.previous_score = mds_all.score
                mds_all.score = overall_avg
                mds_all.save()
    
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