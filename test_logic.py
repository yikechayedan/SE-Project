import os
import django
import sys

# 设置 Django 环境
sys.path.append('/mnt/d/3_autumn/software_project/teamwork/SE-Project/PolyMetric/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PolyMetric.settings')
django.setup()

from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.models.models import My_Model
from apps.datasets.models import Dataset
from apps.tasks.views import run_task
from apps.tasks.run_logic import sync_downstream_tasks, prepare_evaluation_items
from django.contrib.auth import get_user_model
from rest_framework.response import Response

User = get_user_model()

def run_test():
    print("=== 开始逻辑验证测试 ===")
    
    # 1. 准备基础数据
    m1 = My_Model.objects.first()
    m2 = My_Model.objects.all()[1]
    m3 = My_Model.objects.all()[2]
    ds = Dataset.objects.filter(file_format='json').first()
    user = User.objects.first()
    
    if not all([m1, m2, m3, ds, user]):
        print("错误：测试数据不足（需要至少3个模型和1个数据集）")
        return

    # 清理旧测试任务
    EvaluationTask.objects.filter(name__startswith="TEST_").delete()

    # ---------------------------------------------------------
    # 场景 1: 镜像任务挂载测试 (A vs B 正在跑，B vs A 传入)
    # ---------------------------------------------------------
    print("\n[测试 1] 镜像任务挂载与等待...")
    t1 = EvaluationTask.objects.create(
        name="TEST_A_vs_B", myModel=m1, myModel_2=m2, 
        dataset=ds, method='adversarial', creator=user, status='running'
    )
    
    t2 = EvaluationTask.objects.create(
        name="TEST_B_vs_A", myModel=m2, myModel_2=m1, 
        dataset=ds, method='adversarial', creator=user, status='pending'
    )

    # 模拟 API 调用启动 t2
    class FakeRequest:
        def __init__(self, data): self.data = data; self.user = user
    
    res = run_task(FakeRequest({"task_id": t2.id}))
    t2.refresh_from_db()
    
    print(f"t2 启动响应: {res.data.get('msg')}")
    if t2.shared_from_id == t1.id and t2.status == 'running':
        print("√ 成功：t2 已正确挂载到正在运行的 t1 上并进入等待。")
    else:
        print(f"X 失败：t2 状态异常 (Status: {t2.status}, SharedFrom: {t2.shared_from_id})")

    # ---------------------------------------------------------
    # 场景 2: 镜像同步与回复对调测试
    # ---------------------------------------------------------
    print("\n[测试 2] 镜像回复自动对调验证...")
    # 模拟 t1 生成了条目和回答
    it1 = EvaluationItem.objects.create(
        task=t1, content="Test Content", 
        predicted_answer="ANS_A", predicted_answer_2="ANS_B"
    )
    
    # 触发同步
    sync_downstream_tasks(t1)
    
    # 检查 t2 是否创建了条目且回答已对调
    it2 = EvaluationItem.objects.filter(task=t2).first()
    if it2:
        print(f"t2 获得回答 - Pred1: {it2.predicted_answer}, Pred2: {it2.predicted_answer_2}")
        if it2.predicted_answer == "ANS_B" and it2.predicted_answer_2 == "ANS_A":
            print("√ 成功：镜像复用时回答位置已自动交换。")
        else:
            print("X 失败：回答位置未正确对调。")
    else:
        print("X 失败：t2 未能同步生成条目。")

    # ---------------------------------------------------------
    # 场景 3: 部分复用补全测试 (A vs B 存在 -> A vs C 复用 A)
    # ---------------------------------------------------------
    print("\n[测试 3] 部分重叠模型搜刮测试 (A+B -> A+C)...")
    t3 = EvaluationTask.objects.create(
        name="TEST_A_vs_C", myModel=m1, myModel_2=m3, 
        dataset=ds, method='adversarial', creator=user, status='pending'
    )
    
    # 初始化条目，应自动搜刮模型 A 的回答
    prepare_evaluation_items(t3)
    it3 = EvaluationItem.objects.filter(task=t3).first()
    
    if it3:
        print(f"t3 获得回答 - Pred1(A): {it3.predicted_answer}, Pred2(C): {it3.predicted_answer_2}")
        if it3.predicted_answer == "ANS_A" and it3.predicted_answer_2 is None:
            print("√ 成功：已从全库精准搜刮到 A 的回答，C 留空等待生成。")
        else:
            print("X 失败：搜刮逻辑不符合预期。")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    run_test()
