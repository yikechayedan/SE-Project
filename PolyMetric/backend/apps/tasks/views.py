# apps/tasks/views.py
import json
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .run_logic import run_evaluation, reuse_task_items_model_aware, load_image_from_dataset
from .tasks import init_evaluation_task
from .models import EvaluationTask, EvaluationItem
from .serializers import (
    EvaluationTaskSerializer,
    EvaluationTaskDetailSerializer,
)
from .benchmark import run_benchmark
from apps.system.services import log_task_create


User = get_user_model()


def _reuse_task_items(old_task, new_task):
    """
    Legacy wrapper for existing calls.
    """
    reuse_task_items_model_aware(old_task, new_task)


class EvaluationTaskViewSet(viewsets.ModelViewSet):
    queryset = EvaluationTask.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvaluationTaskDetailSerializer
        return EvaluationTaskSerializer

    # -----------------------------
    # 工具：检查是否任务创建者或管理员
    # -----------------------------
    def _check_owner_or_admin(self, request, task: EvaluationTask):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "仅任务创建者或管理员可操作此评测任务"}, status=403)
        if user.is_staff:
            return None
        # 允许创建者 或者 被授权的查看者 (用于查看报告)
        if task.creator_id == user.id:
            return None
        if task.authorized_viewers.filter(id=user.id).exists():
            return None
            
        return Response({"error": "仅任务创建者或管理员可操作此评测任务"}, status=403)

    # -----------------------------
    # 1 创建任务：POST /api/tasks/evaluation-tasks/
    # -----------------------------
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        
        my_model_id = data.get('myModel')
        dataset_id = data.get('dataset')
        method = data.get('method')
        judge_type = data.get('judge_type', 'human')
        judge_model_id = data.get('judge_model')
        my_model_2_id = data.get('myModel_2') # 对抗评测才会有

        # 基础参数校验
        if not (my_model_id and dataset_id and method):
             return Response({"error": "Missing required fields"}, status=400)

        one_hour_ago = timezone.now() - timedelta(hours=1)
        reuse_status_list = ['completed', 'awaiting_human_judge']

        # -----------------------------------------------------------
        # 【精准去重：四元组匹配 (A, B, D, J)】
        # 只要 模型、数据集、裁判方式 全都一致，直接跳转
        # 但如果是 人工评测 (human)，则不进行去重拦截，允许新建任务（复用回答）
        # -----------------------------------------------------------
        from django.db.models import Q
        
        identical_filters = {
            'method': method,
            'dataset_id': dataset_id,
            'judge_type': judge_type,
            'judge_model_id': judge_model_id,
            'created_at__gt': one_hour_ago,
            'status__in': reuse_status_list
        }

        existing_task = None
        
        # 仅当非人工评测时，才进行去重拦截
        if judge_type != 'human':
            if method == 'objective' or method == 'subjective':
                identical_filters['myModel_id'] = my_model_id
                existing_task = EvaluationTask.objects.filter(**identical_filters).first()
            
            elif method == 'adversarial':
                # 对抗评测支持镜像匹配 (A vs B == B vs A)
                existing_task = EvaluationTask.objects.filter(
                    **identical_filters
                ).filter(
                    (Q(myModel_id=my_model_id) & Q(myModel_2_id=my_model_2_id)) |
                    (Q(myModel_id=my_model_2_id) & Q(myModel_2_id=my_model_id))
                ).first()

        # 【优化】如果老任务虽然完成了，但里面有 Error，就不应该跳转，而应该允许用户新建任务去重试
        if existing_task:
            has_errors = existing_task.items.filter(
                Q(predicted_answer__startswith="[Error]") | 
                Q(predicted_answer_2__startswith="[Error]")
            ).exists()
            
            if not has_errors:
                existing_task.authorized_viewers.add(user)
                return Response({
                    "msg": "检测到完全一致的评测任务，已为您自动跳转。",
                    "code": 200,
                    "task_id": existing_task.id,
                    "is_duplicate": True
                }, status=status.HTTP_200_OK)

        # --- 默认流程：正常创建 ---
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)

        # creator 固定为当前登录用户
        serializer.save(creator=request.user)
        task = serializer.instance
        data = self.get_serializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    # -----------------------------
    # 2 列表：GET /api/tasks/evaluation-tasks/
    # -----------------------------
    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    # -----------------------------
    # 3 详情：GET /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
    
        # 权限检查
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task)
        data = serializer.data

        items_list = data.get('data', []) 

        for item in items_list:
            content_str = item.get('content', '')
            item['image_data'] = None  # 初始化字段
            
            if content_str and isinstance(content_str, str) and content_str.strip().startswith('{'):
                try:
                    content_json = json.loads(content_str)
                    # 检查是否包含 image 字段
                    display_text = content_json.get('text')
                    image_path = content_json.get('image')
                    if display_text:
                        item['content'] = display_text
                    if image_path:
                        b64_data = load_image_from_dataset(task.dataset, image_path)
                        item['image_data'] = b64_data
                    
                except Exception as e:
                    print(f"解析 Item ID {item.get('id')} 内容失败: {e}")

        return Response(data)

    # -----------------------------
    # 4 全量更新：PUT /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task, data=request.data)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)
        serializer.save()
        return Response(serializer.data)

    # -----------------------------
    # 5 部分更新：PATCH /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        serializer = self.get_serializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"error": str(serializer.errors)}, status=400)
        serializer.save()
        return Response(serializer.data)

    # -----------------------------
    # 6 删除任务：DELETE /api/tasks/evaluation-tasks/{id}/
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        perm = self._check_owner_or_admin(request, task)
        if perm is not None:
            return perm

        task.delete()
        return Response(status=204)

    # -----------------------------
    # 7 / 8 提交主观 / 对抗评分：
    #    POST /api/tasks/evaluation-tasks/{id}/
    #    body 里包含：
    #    {
    #      "myModel": 1,
    #      "dataset": 1,
    #      "reviewer": 1,
    #      "time_stamp": "...",   # 可选，目前未使用
    #      "itemID": 1,
    #      "score": 6,           # 主观
    #      "preference": "left"  # 对抗
    #    }
    # -----------------------------
    def submit_score(self, request, pk=None):
        try:
            task = EvaluationTask.objects.get(pk=pk)
        except EvaluationTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=400)

        # method 直接以任务本身为准，不强依赖前端传的 method
        method = task.method

        my_model_id = request.data.get("myModel")
        dataset_id = request.data.get("dataset")
        reviewer_id = request.data.get("reviewer")
        item_id = request.data.get("itemID")
        score = request.data.get("score")
        preference = request.data.get("preference")

        # 校验 reviewer 是否存在
        try:
            reviewer = User.objects.get(id=reviewer_id)
        except (User.DoesNotExist, TypeError, ValueError):
            return Response({"error": "Reviewer not found"}, status=400)

        # ⭐ 校验 myModel 和 dataset 是否与任务一致（使用 My_Model）
        try:
            if int(my_model_id) != task.myModel_id or int(dataset_id) != task.dataset_id:
                return Response({"error": "Model or dataset mismatch"}, status=400)
        except (TypeError, ValueError):
            return Response({"error": "Invalid myModel or dataset id"}, status=400)

        # 找到对应条目
        try:
            item = EvaluationItem.objects.get(task=task, id=item_id)
        except (EvaluationItem.DoesNotExist, TypeError, ValueError):
            return Response({"error": "Item not found"}, status=400)

        # 根据任务类型填充字段
        if method == "subjective":
            # 主观评分必须有 score
            try:
                item.score = int(score)
            except (TypeError, ValueError):
                return Response({"error": "Invalid score"}, status=400)

        elif method == "adversarial":
            # 对抗评测必须有 preference
            if preference not in ("left", "right", "tie"):
                return Response({"error": "Invalid preference"}, status=400)
            item.preference = preference
        else:
            # 目前文档只定义了主观 & 对抗两类提交
            return Response({"error": "Invalid method for submit_score"}, status=400)

        item.save()
        
        # -----------------------------
        # 新增：检查是否所有条目都已评测完成
        # -----------------------------
        is_completed = False
        if method == "subjective":
            # 检查是否还有未评分的条目
            if not task.items.filter(score__isnull=True).exists():
                is_completed = True
                # 计算平均分
                from django.db.models import Avg
                avg_score = task.items.aggregate(Avg("score"))["score__avg"]
                task.score = avg_score

        elif method == "adversarial":
            # 检查是否还有未选偏好的条目
            if not task.items.filter(preference__isnull=True).exists():
                is_completed = True
                # 对抗评测可能需要计算胜率等，暂只更新状态

        if is_completed:
            task.status = "completed"
            task.save()

            # --- 新增：自动生成汇总报告并更新排行榜 ---
            from .models import EvaluationSummary
            from apps.rankings.services import update_model_rankings

            # 1. 创建/更新 EvaluationSummary
            summary, created = EvaluationSummary.objects.get_or_create(task=task)
            summary.model_name = task.myModel.name
            
            if method == "subjective":
                summary.avg_score = task.score
            elif method == "adversarial":
                # 简单计算对抗评测的胜率（相对于 Model A），平局算 0.5 胜
                total_items = task.items.count()
                if total_items > 0:
                    win_count = task.items.filter(preference="left").count()
                    tie_count = task.items.filter(preference="tie").count()
                    
                    summary.correct = win_count  # 胜场仅记录完全胜利
                    summary.total = total_items
                    # 胜率 = (胜场 + 0.5 * 平局) / 总数
                    summary.accuracy = (win_count + 0.5 * tie_count) / total_items
            
            summary.save()

            # 2. 触发排行榜更新
            update_model_rankings(task.dataset_id)

        # 此处暂不记录 reviewer / time_stamp，可根据需要扩展模型
        return Response({}, status=200)


# --------------------------------------------------
# 9. 请求待测条目列表：
#    GET /api/tasks/get-pending-items?taskid=1&reviewerid=1
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_items(request):
    task_param = (
        request.query_params.get("task")
        or request.query_params.get("taskid")
        or request.query_params.get("task_id")
    )
    reviewer_param = (
        request.query_params.get("reviewer")
        or request.query_params.get("reviewerid")
        or request.query_params.get("reviewer_id")
    )

    try:
        task_id = int(task_param)
        reviewer_id = int(reviewer_param)
    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
    except EvaluationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=400)

    try:
        User.objects.get(id=reviewer_id)
    except User.DoesNotExist:
        return Response({"error": "Reviewer not found"}, status=400)

    # 1. 获取全部条目的 QuerySet
    all_items_qs = task.items.all()
    all_ids = [str(item.id) for item in all_items_qs]

    # 2. 获取“待评测”条目 (score 和 preference 都为空)
    pending_items_qs = all_items_qs.filter(score__isnull=True, preference__isnull=True)
    pending_ids = [str(item.id) for item in pending_items_qs]

    # 3. 获取“已评测”条目 (score 不为空 OR preference 不为空)
    completed_items_qs = all_items_qs.exclude(score__isnull=True, preference__isnull=True)
    
    # 构造已评测数据的列表，包含 id 及其评分/偏好
    completed_data = []
    for item in completed_items_qs:
        completed_data.append({
            "id": str(item.id),
            "score": item.score,
            "preference": item.preference
        })

    return Response(
        {
            "task": task.id,
            "reviewer": reviewer_id,
            "total_count": len(all_ids),
            "all_item_ids": all_ids,
            "pending_count": len(pending_ids),
            "pending_item_ids": pending_ids,
            "completed_count": len(completed_data),
            "completed_items": completed_data  # 返回详细的已评测信息
        }
    )

# --------------------------------------------------
# 10. 请求单条条目详情：
#     GET /api/tasks/get-item-detail?task=1&itemID=1
# --------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_item_detail(request):
    task_param = request.query_params.get("task") or request.data.get("task")
    item_param = request.query_params.get("itemID") or request.data.get("itemID")

    try:
        task_id = int(task_param)
        item_id = int(item_param)
    except (TypeError, ValueError):
        return Response({"error": "Invalid parameters"}, status=400)

    try:
        task = EvaluationTask.objects.get(id=task_id)
        item = EvaluationItem.objects.get(task=task, id=item_id)
    except (EvaluationTask.DoesNotExist, EvaluationItem.DoesNotExist):
        return Response({"error": "Task or item not found"}, status=400)

    raw_content = item.content
    display_text = raw_content
    image_base64 = None

    try:
        if raw_content.strip().startswith("{"):
            data = json.loads(raw_content)
            display_text = data.get("text", raw_content)
            rel_path = data.get("image")

            if rel_path:
                # 调用你那个现成的函数，从 ZIP 中提取 Base64
                # 注意：确保你传入了正确的 dataset 对象
                image_base64 = load_image_from_dataset(task.dataset, rel_path)
    except Exception as e:
        print(f"Error: {e}")

    # 获取图片 Base64 (通过序列化器复用逻辑)
    from .serializers import EvaluationItemSerializer
    item_serializer = EvaluationItemSerializer(item)
    
    return Response({
        "method": task.method,
        "itemID": item.id,
        "item_content": {
            "input_query": display_text,
            "image_data": image_base64,  # 返回 Base64 而不是 URL
            "myModel1_response": item.predicted_answer,
            "myModel2_response": item.predicted_answer_2,
            "predicted_image_data": item_serializer.data.get("predicted_image_data"),
            "predicted_image_2_data": item_serializer.data.get("predicted_image_2_data")
        },
        "completed": item.score is not None
    })


# --------------------------------------------------
# 11. 手动运行任务：POST /api/tasks/run-task
# --------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_task(request):
    task_id = request.data.get("task_id")
    from .tasks import init_evaluation_task

    try:
        from django.db import transaction
        with transaction.atomic():
            task = EvaluationTask.objects.select_for_update().get(id=task_id)
            
            if task.status != 'pending':
                return Response({"msg": "Task is already running or completed", "status": task.status})

            # -----------------------------------------------------------
            # 【高级优化：寻找生产者任务 (Producers)】
            # 只有正在运行或已完成的任务才能作为“生产者”供别人挂载
            # -----------------------------------------------------------
            one_hour_ago = timezone.now() - timedelta(hours=1)
            # 排除 'pending'，因为未启动的任务无法提供回答
            active_statuses = ['running', 'completed', 'awaiting_human_judge']
            
            from django.db.models import Q
            
            # 搜索策略：
            # 1. 必须是同一个数据集
            # 2. 模型重合
            # 3. 必须是比自己早创建的任务 (ID 更小)，确保单向依赖
            upstream_search = EvaluationTask.objects.filter(
                dataset_id=task.dataset_id,
                created_at__gt=one_hour_ago,
                status__in=active_statuses,
                id__lt=task.id
            )

            model_q = Q(myModel_id=task.myModel_id) | Q(myModel_2_id=task.myModel_id)
            if task.method == 'adversarial':
                model_q |= Q(myModel_id=task.myModel_2_id) | Q(myModel_2_id=task.myModel_2_id)
            
            # 优先找完成的，次之找正在跑的
            existing_runner = upstream_search.filter(model_q).order_by('status').first()
            
            if existing_runner:
                # 1. 发现上游任务已完成：立即复用并分流
                if existing_runner.status in ['completed', 'awaiting_human_judge']:
                    reuse_task_items_model_aware(existing_runner, task)
                    
                    if task.judge_type == 'human':
                        # 检查是否复用后还有缺口
                        if task.items.filter(Q(predicted_answer__isnull=True) | Q(predicted_answer_2__isnull=True)).exists():
                            task.status = 'running'
                            task.save(update_fields=['status'])
                            
                            # 记录任务启动 (部分复用，仍需运行)
                            log_task_create(task, request.user)
                            
                            init_evaluation_task.delay(task.id)
                            return Response({"msg": "已复用部分回答，正在补全其余模型回答...", "status": "running"})
                        else:
                            task.status = 'awaiting_human_judge'
                            task.save(update_fields=['status'])
                            
                            # 记录任务启动 (完全复用，进入人工评分)
                            log_task_create(task, request.user)
                            
                            return Response({"msg": "所有回答已复用，请开始人工评分。", "status": "awaiting_human_judge"})
                    else:
                        task.status = 'running'
                        task.save(update_fields=['status'])
                        init_evaluation_task.delay(task.id)
                        return Response({"msg": "已复用相关回答，正在进行补全与评分...", "status": "running"})

                # 2. 发现上游任务正在运行：建立“任务级等待”
                else:
                    task.shared_from = existing_runner
                    task.status = 'running' 
                    task.save(update_fields=['shared_from', 'status'])
                    
                    # 记录任务启动 (等待上游)
                    log_task_create(task, request.user)
                    
                    return Response({
                        "msg": f"检测到重合任务(ID:{existing_runner.id})正在生成回答，本任务将排队等待其结果以节省开销。",
                        "status": "running"
                    })

            # 3. 彻底无重合：正常启动
            task.status = "running"
            task.save()
            
            # 记录任务启动 (正常流程)
            log_task_create(task, request.user)
            
            init_evaluation_task.delay(task_id)
            
            return Response({
                "msg": "Task submitted to background queue", 
                "status": "running",
                "task_id": task_id
            })

    except EvaluationTask.DoesNotExist:
        return Response({"error": "task not found"}, status=404)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in run_task: {error_details}")
        return Response({
            "error": "Internal Server Error",
            "details": str(e),
            "traceback": error_details
        }, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_benchmark_view(request):
    """
    POST /api/tasks/run-benchmark/
    {
        "dataset": 1,
        "models": [1,2,3],
        "max_workers": 3   # 可选
    }
    """
    dataset_id = request.data.get("dataset")
    model_ids = request.data.get("models")
    max_workers = request.data.get("max_workers", 3)
    method = request.data.get("method", "objective")
    if not dataset_id or not model_ids:
        return Response({"error": "dataset and models are required"}, status=400)

    results = run_benchmark(
        creator=request.user,
        dataset_id=dataset_id,
        model_ids=model_ids,
        method=method,
        max_workers=max_workers,
    )

    return Response(results, status=200)