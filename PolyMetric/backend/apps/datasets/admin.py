from django.contrib import admin
from .models import Dataset, DatasetFollow
from apps.datasets.services.ai_capability_judge import ai_judge_capability


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "creator", "category", "evaluation_type",
    "capability_tag","file_format", "is_public", "is_verified", "created_at")
    list_filter = ("category", "file_format", "is_public", "is_verified")
    search_fields = ("name", "creator__username")
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        """
        Admin 中：
        - 新建数据集（change=False） → 自动跑 AI
        - 修改数据集 + 重新上传文件 → 自动跑 AI
        """

        should_run_ai = False

        # 情况 1：新建
        if not change:
            should_run_ai = True

        # 情况 2：修改 & 文件被重新上传
        if change and "file_path" in form.changed_data:
            should_run_ai = True

        if should_run_ai and obj.file_path:
            samples = self._sample_dataset(obj.file_path, obj.file_format)
            if samples:
                try:
                    obj.capability_tag = ai_judge_capability(samples)
                except Exception as e:
                    # 防止 admin 保存失败
                    print("[AI capability judge failed]", e)

        super().save_model(request, obj, form, change)

    def _sample_dataset(self, file_obj, file_format, limit=5):
        """
        Admin 内部抽样（和 Serializer 解耦）
        """
        file_obj.seek(0)
        content = file_obj.read()

        if file_format == "json":
            try:
                data = json.loads(content.decode("utf-8"))
                if isinstance(data, list):
                    return data[:limit]
            except Exception:
                return []

        if file_format == "csv":
            try:
                text = content.decode("utf-8", errors="ignore")
                reader = csv.DictReader(io.StringIO(text))
                return list(reader)[:limit]
            except Exception:
                return []

        return []


@admin.register(DatasetFollow)
class DatasetFollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dataset", "created_at")
    search_fields = ("user__username", "dataset__name")
    ordering = ("-created_at",)
