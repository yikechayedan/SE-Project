# apps/tasks/benchmark.py

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction
from django.utils import timezone

from django.contrib.auth import get_user_model
from apps.models.models import My_Model
from apps.datasets.models import Dataset
from .models import EvaluationTask, EvaluationSummary
from .run_logic import run_evaluation

User = get_user_model()


# ---------------------------------------------------------
# 工具：单模型评测（带重试 + 超时）
# ---------------------------------------------------------
def evaluate_single_model(creator, dataset, model, max_retry=2):
    """
    针对单个模型执行评测，带：失败自动重试
    """
    retries = 0

    while retries <= max_retry:
        try:
            # 1️⃣ 创建 Task
            task = EvaluationTask.objects.create(
                name=f"Benchmark - {dataset.name} - {model.name}",
                creator=creator,
                dataset=dataset,
                method="objective",
                myModel=model,
                status="pending",
            )

            # 2️⃣ 调用统一评测逻辑
            result = run_evaluation(task.id)

            # 3️⃣ 转为结构化 summary（失败会抛异常）
            summary = EvaluationSummary.objects.get(task=task)

            return {
                "task_id": task.id,
                "model": summary.model_name,
                "total": summary.total,
                "correct": summary.correct,
                "accuracy": summary.accuracy,
            }

        except Exception as e:
            retries += 1
            if retries > max_retry:
                return {
                    "task_id": None,
                    "model": model.name,
                    "error": f"FAILED after {max_retry} retries: {str(e)}"
                }
            time.sleep(1)  # 等待 1 秒重试


# ---------------------------------------------------------
# Step 3-A + 3-B + 3-C：Benchmark 主逻辑（支持并发）
# ---------------------------------------------------------
def run_benchmark(creator, dataset_id, model_ids, max_workers=3):
    """
    用多个模型对同一 dataset 进行评测
    支持：
      ✔ 并发（ThreadPoolExecutor）
      ✔ 自动重试
      ✔ 自动生成 Summary
      ✔ 排序返回排行榜
    """
    dataset = Dataset.objects.get(id=dataset_id)

    models = My_Model.objects.filter(id__in=model_ids)
    if not models.exists():
        return {"error": "no models found"}

    results = []

    # -------- 并发执行 --------
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {
            executor.submit(evaluate_single_model, creator, dataset, m): m
            for m in models
        }

        for future in as_completed(future_to_model):
            try:
                res = future.result(timeout=120)
            except Exception as e:
                model = future_to_model[future]
                results.append({
                    "task_id": None,
                    "model": model.name,
                    "error": f"Timeout or executor error: {str(e)}"
                })
                continue

            results.append(res)

    # -------- 排序 + 返回结果 --------
    results.sort(key=lambda x: x.get("accuracy", 0) or 0, reverse=True)

    return results
