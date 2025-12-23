"""
测试数据工厂 - 使用工厂模式创建测试数据
"""
import factory
from datetime import datetime, timezone
from django.contrib.auth import get_user_model
from apps.datasets.models import Dataset, DatasetFollow
from apps.models.models import My_Model, ModelFollow
from apps.tasks.models import EvaluationTask, EvaluationItem
from apps.users.models import UserFollow
from apps.system.models import SystemEvent

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"testuser_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "test123456")
    is_active = True
    is_staff = False
    is_superuser = False
    bio = factory.Faker("paragraph", nb_sentences=3)
    phone = factory.Faker("phone_number")
    show_followed_models = True
    show_followed_datasets = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    @factory.post_generation
    def avatar(self, create, extracted, **kwargs):
        """生成头像"""
        if not create:
            return
        
        if extracted:
            # 使用提供的头像
            self.avatar = extracted
        elif kwargs.get('with_avatar', False):
            # 生成测试头像
            from django.core.files.uploadedfile import SimpleUploadedFile
            from io import BytesIO
            from PIL import Image
            
            # 创建测试图片
            image = Image.new('RGB', (100, 100), color='red')
            image_file = BytesIO()
            image.save(image_file, 'png')
            image_file.seek(0)
            
            avatar_file = SimpleUploadedFile(
                "avatar.png",
                image_file.read(),
                content_type="image/png"
            )
            self.avatar = avatar_file
            self.save()


class AdminUserFactory(UserFactory):
    """管理员用户工厂"""
    
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@admin.com")


class ModelFactory(factory.django.DjangoModelFactory):
    """模型工厂"""
    
    class Meta:
        model = My_Model
    
    name = factory.Faker("company")
    company = factory.Faker("company")
    category = factory.Iterator(["text", "image", "multimodal", "audio", "video"])
    parameter_size = factory.Iterator(["1B", "7B", "13B", "70B", "100B+", "unknown"])
    description = factory.Faker("paragraph", nb_sentences=5)
    version = factory.Faker("semver")
    official_url = factory.Faker("url")
    paper_url = factory.Faker("url")
    github_url = factory.Faker("url")
    license = factory.Iterator(["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "Proprietary"])
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class DatasetFactory(factory.django.DjangoModelFactory):
    """数据集工厂"""
    
    class Meta:
        model = Dataset
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=5)
    category = factory.Iterator(["text", "image", "multimodal"])
    file_format = factory.Iterator(["json", "csv", "zip"])
    is_public = factory.Faker("boolean", chance_of_getting_true=70)
    is_verified = factory.Faker("boolean", chance_of_getting_true=50)
    file_size = factory.Faker("random_int", min=1024, max=1073741824)  # 1KB到1GB
    sample_count = factory.Faker("random_int", min=100, max=1000000)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    # 新增字段
    evaluation_type = factory.Iterator(["subjective", "objective", "adversarial"])
    capability_dimension = factory.Iterator(["language", "math", "code", "multimodal", "other"])
    capability_tag = factory.Iterator(["language", "reasoning", "coding", None])
    has_images = factory.Faker("boolean", chance_of_getting_true=30)
    image_count = factory.Faker("random_int", min=0, max=1000)
    
    creator = factory.SubFactory(UserFactory)
    
    @factory.post_generation
    def file_path(self, create, extracted, **kwargs):
        """生成测试文件"""
        if not create:
            return
        
        if extracted:
            # 使用提供的文件
            self.file_path = extracted
        elif kwargs.get('with_file', False):
            # 生成测试文件
            from django.core.files.uploadedfile import SimpleUploadedFile
            import json
            
            test_data = [
                {"id": i, "question": f"测试问题{i}", "answer": f"测试答案{i}"}
                for i in range(1, 11)
            ]
            
            file_content = json.dumps(test_data, ensure_ascii=False)
            
            test_file = SimpleUploadedFile(
                "test_data.json",
                file_content.encode('utf-8'),
                content_type="application/json"
            )
            self.file_path = test_file
            self.save()


class EvaluationTaskFactory(factory.django.DjangoModelFactory):
    """评测任务工厂"""
    
    class Meta:
        model = EvaluationTask
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph", nb_sentences=3)
    method = factory.Iterator(["objective", "subjective", "adversarial"])
    status = factory.Iterator(["pending", "running", "completed", "failed"])
    progress = factory.Faker("random_int", min=0, max=100)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    # 新增字段
    judge_type = factory.Iterator(["human", "model"])
    judge_model = factory.Maybe(
        "judge_type",
        yes_factory=factory.SubFactory(ModelFactory),
        no_factory=None,
        decider=lambda judge_type: judge_type == "model"
    )
    myModel_2 = factory.Maybe(
        "method",
        yes_factory=factory.SubFactory(ModelFactory),
        no_factory=None,
        decider=lambda method: method == "adversarial"
    )
    
    creator = factory.SubFactory(UserFactory)
    dataset = factory.SubFactory(DatasetFactory)
    myModel = factory.SubFactory(ModelFactory)


class EvaluationItemFactory(factory.django.DjangoModelFactory):
    """评测项工厂"""
    
    class Meta:
        model = EvaluationItem
    
    content = factory.Faker("paragraph", nb_sentences=2)
    correct_answer = factory.Faker("sentence")
    predicted_answer = factory.Faker("sentence")
    predicted_answer_2 = factory.Maybe(
        "task__method",
        yes_factory=factory.Faker("sentence"),
        no_factory=None,
        decider=lambda method: method == "adversarial"
    )
    score = factory.Faker("random_int", min=1, max=10)
    preference = factory.Maybe(
        "task__method",
        yes_factory=factory.Iterator(["left", "right", "tie"]),
        no_factory=None,
        decider=lambda method: method == "adversarial"
    )
    is_correct = factory.Faker("boolean")
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    
    task = factory.SubFactory(EvaluationTaskFactory)


class UserFollowFactory(factory.django.DjangoModelFactory):
    """用户关注工厂"""
    
    class Meta:
        model = UserFollow
    
    follower = factory.SubFactory(UserFactory)
    followed = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ModelFollowFactory(factory.django.DjangoModelFactory):
    """模型关注工厂"""
    
    class Meta:
        model = ModelFollow
    
    user = factory.SubFactory(UserFactory)
    model = factory.SubFactory(ModelFactory)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class DatasetFollowFactory(factory.django.DjangoModelFactory):
    """数据集关注工厂"""
    
    class Meta:
        model = DatasetFollow
    
    user = factory.SubFactory(UserFactory)
    dataset = factory.SubFactory(DatasetFactory)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class SystemEventFactory(factory.django.DjangoModelFactory):
    """系统事件工厂"""
    
    class Meta:
        model = SystemEvent
    
    event_type = factory.Iterator([
        "user_register", "user_login", "dataset_upload", "dataset_verify",
        "model_add", "task_create", "task_complete", "follow", "unfollow"
    ])
    content = factory.Faker("paragraph", nb_sentences=2)
    metadata = factory.LazyFunction(lambda: {})
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class BulkDataFactory:
    """批量数据工厂 - 用于创建大量测试数据"""
    
    @staticmethod
    def create_users(count: int, **kwargs):
        """批量创建用户"""
        return UserFactory.create_batch(count, **kwargs)
    
    @staticmethod
    def create_models(count: int, **kwargs):
        """批量创建模型"""
        return ModelFactory.create_batch(count, **kwargs)
    
    @staticmethod
    def create_datasets(count: int, **kwargs):
        """批量创建数据集"""
        return DatasetFactory.create_batch(count, **kwargs)
    
    @staticmethod
    def create_evaluation_tasks(count: int, **kwargs):
        """批量创建评测任务"""
        return EvaluationTaskFactory.create_batch(count, **kwargs)
    
    @staticmethod
    def create_complete_scenario():
        """创建完整的测试场景"""
        # 创建用户
        users = UserFactory.create_batch(5)
        admin = AdminUserFactory()
        
        # 创建模型
        models = ModelFactory.create_batch(10)
        
        # 创建数据集
        datasets = DatasetFactory.create_batch(10, with_file=True)
        
        # 创建评测任务
        tasks = []
        for i in range(5):
            task = EvaluationTaskFactory(
                creator=users[i % len(users)],
                dataset=datasets[i % len(datasets)],
                myModel=models[i % len(models)]
            )
            # 为每个任务创建评测项
            EvaluationItemFactory.create_batch(
                10,
                task=task
            )
            tasks.append(task)
        
        # 创建关注关系
        for user in users:
            # 用户关注模型
            for model in models[:3]:
                ModelFollowFactory(user=user, model=model)
            
            # 用户关注数据集
            for dataset in datasets[:3]:
                DatasetFollowFactory(user=user, dataset=dataset)
        
        # 用户之间关注
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                UserFollowFactory(follower=users[i], followed=users[j])
        
        # 创建系统事件
        for _ in range(20):
            SystemEventFactory()
        
        return {
            'users': users,
            'admin': admin,
            'models': models,
            'datasets': datasets,
            'tasks': tasks,
            'events': SystemEvent.objects.all()
        }


class ScenarioFactory:
    """场景工厂 - 创建特定测试场景"""
    
    @staticmethod
    def create_user_registration_scenario():
        """创建用户注册测试场景"""
        return {
            'valid_user': UserFactory.build(),
            'duplicate_username': UserFactory(),
            'invalid_email_user': UserFactory.build(email="invalid-email"),
            'weak_password_user': UserFactory.build(password="123")
        }
    
    @staticmethod
    def create_dataset_upload_scenario():
        """创建数据集上传测试场景"""
        creator = UserFactory()
        return {
            'creator': creator,
            'public_dataset': DatasetFactory.build(
                creator=creator,
                is_public=True,
                is_verified=True
            ),
            'private_dataset': DatasetFactory.build(
                creator=creator,
                is_public=False,
                is_verified=False
            ),
            'large_dataset': DatasetFactory.build(
                creator=creator,
                file_size=1073741824,  # 1GB
                sample_count=1000000
            )
        }
    
    @staticmethod
    def create_evaluation_scenario():
        """创建评测测试场景"""
        creator = UserFactory()
        reviewer = UserFactory()
        model = ModelFactory()
        dataset = DatasetFactory(with_file=True)
        
        # 创建不同类型的评测任务
        objective_task = EvaluationTaskFactory(
            creator=creator,
            model=model,
            dataset=dataset,
            method="objective"
        )
        
        subjective_task = EvaluationTaskFactory(
            creator=creator,
            model=model,
            dataset=dataset,
            method="subjective"
        )
        
        adversarial_task = EvaluationTaskFactory(
            creator=creator,
            model=model,
            dataset=dataset,
            method="adversarial"
        )
        
        # 为每个任务创建评测项
        for task in [objective_task, subjective_task, adversarial_task]:
            EvaluationItemFactory.create_batch(10, task=task)
        
        return {
            'creator': creator,
            'reviewer': reviewer,
            'model': model,
            'dataset': dataset,
            'objective_task': objective_task,
            'subjective_task': subjective_task,
            'adversarial_task': adversarial_task
        }
    
    @staticmethod
    def create_performance_test_scenario():
        """创建性能测试场景"""
        # 创建大量数据
        users = UserFactory.create_batch(100)
        models = ModelFactory.create_batch(50)
        datasets = DatasetFactory.create_batch(50, with_file=True)
        
        # 创建大量关注关系
        follows = []
        for user in users:
            for model in models[:10]:
                follows.append(ModelFollowFactory(user=user, model=model))
            for dataset in datasets[:10]:
                follows.append(DatasetFollowFactory(user=user, dataset=dataset))
        
        return {
            'users': users,
            'models': models,
            'datasets': datasets,
            'follows': follows
        }