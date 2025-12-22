from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q, F, Case, When, Value, IntegerField
from .services import update_model_rankings, get_top_models, get_model_ranking_history
from .models import ModelDimensionScore
from apps.models.models import My_Model
from apps.users.models import UserStar


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_rankings(request):
    """
    更新排名的API接口
    
    POST /api/rankings/update/
    Body: {
        "dataset_id": 1
    }
    """
    dataset_id = request.data.get('dataset_id')
    
    if not dataset_id:
        return Response(
            {"error": "dataset_id is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = update_model_rankings(dataset_id)
    
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def top_models(request):
    """
    获取顶级模型排名
    
    GET /api/rankings/top/?dataset_id=1&limit=10
    """
    dataset_id = request.query_params.get('dataset_id')
    limit = int(request.query_params.get('limit', 10))
    
    if not dataset_id:
        return Response(
            {"error": "dataset_id is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = get_top_models(dataset_id, limit)
    
    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "code": status.HTTP_200_OK,
        "data": result
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """
    获取完整排行榜 (Pivot 视图)
    
    GET /api/rankings/leaderboard/
    
    返回格式：
    {
        "code": 200,
        "msg": "success",
        "data": [
            {
                "rank": 1,
                "model_id": 101,
                "name": "GPT-4o",
                "company": "OpenAI",
                "category": "text",
                "star_count": 1205,
                "scores": {
                    "overall": 92.5,
                    "language": 94.0,
                    "math": 91.0,
                    "code": 93.5,
                    "multimodal": 88.0
                },
                "trends": {
                    "overall": "up",
                    "math": "stable"
                }
            }
        ]
    }
    """
    try:
        # 获取所有有overall分数的模型，按分数降序排列
        models_with_scores = My_Model.objects.filter(
            dimension_scores__dimension='overall'
        ).annotate(
            overall_score=F('dimension_scores__score')
        ).order_by('-overall_score')
        
        leaderboard_data = []
        
        for rank, model in enumerate(models_with_scores, 1):
            # 获取模型的所有维度分数
            dimension_scores = ModelDimensionScore.objects.filter(
                model=model
            ).values('dimension', 'score', 'previous_score')
            
            # 构建分数字典
            scores = {}
            trends = {}
            for score_data in dimension_scores:
                dimension = score_data['dimension']
                score = score_data['score']
                previous_score = score_data['previous_score']
                
                scores[dimension] = score
                
                # 计算趋势
                if score > previous_score:
                    trends[dimension] = 'up'
                elif score < previous_score:
                    trends[dimension] = 'down'
                else:
                    # 分数相等或者是初始状态(score=0, previous=0)
                    trends[dimension] = 'stable'
            
            # 获取模型的点赞数
            star_count = UserStar.objects.filter(
                content_type__model='my_model',
                object_id=model.id
            ).count()
            
            # 构建排行榜条目
            leaderboard_item = {
                "rank": rank,
                "model_id": model.id,
                "name": model.name,
                "company": model.company or "",
                "category": model.category,
                "star_count": star_count,
                "scores": scores,
                "trends": trends
            }
            
            leaderboard_data.append(leaderboard_item)
        
        return Response({
            "code": status.HTTP_200_OK,
            "msg": "success",
            "data": leaderboard_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "msg": f"获取排行榜失败: {str(e)}",
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def model_ranking_history(request, model_id):
    """
    获取模型排名历史
    
    GET /api/rankings/history/{model_id}/?dataset_id=1
    """
    dataset_id = request.query_params.get('dataset_id')
    
    result = get_model_ranking_history(model_id, dataset_id)
    
    return Response({
        "code": status.HTTP_200_OK,
        "data": result
    }, status=status.HTTP_200_OK)