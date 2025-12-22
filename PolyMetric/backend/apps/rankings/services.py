from django.db import transaction
from .models import ModelRanking, RankingHistory
from apps.system.services import log_rank_change


def _get_dataset_dimension(dataset):
    """根据数据集配置获取评测维度"""
    # 优先使用数据库中明确配置的维度
    if hasattr(dataset, 'capability_dimension') and dataset.capability_dimension:
        # 如果是 'other'，尝试回退到旧的推断逻辑（兼容旧数据）
        if dataset.capability_dimension != 'other':
            return dataset.capability_dimension
            
    # --- 旧的兼容逻辑 (Fallback) ---
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
    
    # 1. 获取所有评测结果（按时间排）
    all_summaries = EvaluationSummary.objects.filter(
        task__dataset=dataset
    ).select_related('task__myModel').order_by('-task__created_at')

    # 2. 逻辑聚合：每个模型取最近 N 次评测的平均值（防恶意打分/刷分）
    # 策略：不再只取最新的一条，而是取最近 5 条的平均分
    WINDOW_SIZE = 5
    model_groups = {}
    for s in all_summaries:
        model_id = s.task.myModel_id
        if model_id not in model_groups:
            model_groups[model_id] = []
        if len(model_groups[model_id]) < WINDOW_SIZE:
            model_groups[model_id].append(s)

    # 3. 计算聚合表现
    final_sorted_summaries = []
    for model_id, summaries in model_groups.items():
        # 计算该模型在该数据集上的平均表现
        count = len(summaries)
        avg_acc = sum((s.accuracy or 0) for s in summaries) / count
        avg_score_val = sum((s.avg_score or 0) for s in summaries) / count
        
        # 构造一个虚拟的聚合对象用于排序（借用第一个 summary 的信息）
        rep = summaries[0]
        rep.accuracy = avg_acc
        rep.avg_score = avg_score_val
        final_sorted_summaries.append(rep)

    # 4. 第二次排序：按聚合后的分数进行排名
    final_sorted_summaries.sort(
        key=lambda x: (x.accuracy or 0, x.avg_score or 0),
        reverse=True
    )

    with transaction.atomic():
        
        # 获取当前所有排名记录
        existing_rankings = {
            ranking.model_id: ranking for ranking in 
            ModelRanking.objects.filter(dataset=dataset)
        }
        
        # 5. 此时的 index 才是真正的“战力排名”
        for index, summary in enumerate(final_sorted_summaries, 1):
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

            # 先获取旧排名（如果有的话）
            old_ranking_obj = existing_rankings.get(model.id)
            old_rank = old_ranking_obj.rank if old_ranking_obj else None

            # 使用 update_or_create
            ranking, created = ModelRanking.objects.update_or_create(
                model=model,
                dataset=dataset,
                defaults={
                    'score': normalized_score,
                    'rank': index,
                    'previous_rank': old_rank  # 将刚才取到的旧排名存入
                }
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
        involved_models = set(summary.task.myModel for summary in final_sorted_summaries)
        
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
                
                # Sticky Trend Logic: 只有当分数发生实质性变化时，才更新 previous_score
                # 这样可以保持趋势箭头的状态，直到下一次变化
                if abs(mds.score - avg_val) > 0.001:
                    mds.previous_score = mds.score
                    mds.score = avg_val
                    mds.save()
                
            # 2. 更新 Overall 综合分数
            existing_dims = ModelDimensionScore.objects.filter(model=model).exclude(dimension='overall')
            if existing_dims.exists():
                overall_avg = existing_dims.aggregate(Avg('score'))['score__avg']
                
                mds_all, _ = ModelDimensionScore.objects.get_or_create(model=model, dimension='overall')
                
                # Sticky Trend Logic for Overall
                if abs(mds_all.score - overall_avg) > 0.001:
                    mds_all.previous_score = mds_all.score
                    mds_all.score = overall_avg
                    mds_all.save()
    
    return {
        "success": True,
        "message": f"Updated rankings for dataset {dataset.name}",
        "dataset": dataset.name,
        "total_models": len(final_sorted_summaries)
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