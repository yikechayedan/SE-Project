# datasets/management/commands/import_examples.py
import os
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset

User = get_user_model()

class Command(BaseCommand):
    help = "导入 examples 目录下的样例数据集"

    def handle(self, *args, **options):
        # 示例：使用第一个个测试用户（需提前存在）
        user = User.objects.filter(username="testuser").first()
        if not user:
            self.stdout.write(self.style.ERROR("请先创建测试用户 'testuser'"))
            return

        # 样例文件路径
        examples_dir = os.path.join(os.path.dirname(__file__), "../../examples")
        files = ["user_profile_dataset.json", "logistics_delivery_dataset.json"]

        for filename in files:
            file_path = os.path.join(examples_dir, filename)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"文件不存在: {file_path}"))
                continue

            # 读取 JSON 内容
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 映射字段并创建数据集
            dataset = Dataset(
                name=data["dataset_name"],
                description=data["description"],
                category="text",  # 样例均为文本类型
                file_format="json",
                file_size=round(os.path.getsize(file_path) / (1024 * 1024), 2),  # 转换为 MB
                sample_count=len(data["data"]),  # 样本数量
                creator=user,
                is_public=True,
                is_verified=True
            )
            dataset.save()
            self.stdout.write(self.style.SUCCESS(f"导入成功: {dataset.name}"))