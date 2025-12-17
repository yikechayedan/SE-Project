from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .services import update_model_rankings, get_top_models, get_model_ranking_history


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