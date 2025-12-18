from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SystemEvent
from .serializers import SystemEventSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def news_feed(request):
    """
    获取系统动态新闻流
    返回格式化的系统事件列表，用于首页展示
    """
    # 获取最近的系统事件，限制数量为50条
    events = SystemEvent.objects.all()[:50]
    serializer = SystemEventSerializer(events, many=True)
    
    return Response({
        "code": status.HTTP_200_OK,
        "data": serializer.data
    }, status=status.HTTP_200_OK)