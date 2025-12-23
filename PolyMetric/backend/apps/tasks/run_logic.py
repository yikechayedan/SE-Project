# apps/tasks/run_logic.py

import json
import re
from django.utils import timezone
from django.db import transaction

from .services import call_llm_api
from .models import EvaluationTask, EvaluationItem
from apps.datasets.models import Dataset
from .models import EvaluationSummary
from apps.system.services import log_task_complete

# =========================================================
# Step 3 核心：Prompt 工业级约束 + 输出清洗
# =========================================================

def get_item_text(item_content: str) -> str:
    """从可能为 JSON 的 content 中提取纯文本"""
    try:
        if item_content.strip().startswith("{") and '"image":' in item_content:
            data = json.loads(item_content)
            return data.get("text", item_content)
    except:
        pass
    return item_content

def extract_multimodal_data(item):
    """提取文本和图片（用于 API 调用）"""
    text = get_item_text(item.content)
    images = []
    
    try:
        if item.content.strip().startswith("{") and '"image":' in item.content:
            data = json.loads(item.content)
            img_path = data.get("image")
            if img_path:
                b64 = load_image_from_dataset(item.task.dataset, img_path)
                if b64: images.append(b64)
    except Exception as e:
        print(f"Error extracting multimodal data: {e}")
        
    return text, images

def build_objective_prompt(item: EvaluationItem) -> str:
    """
    构造【工业级客观题 Prompt】
    """
    text = get_item_text(item.content)
    return f"""
你是一个自动判题系统。

下面是一道客观题，请你认真作答。
你的任务是：给出唯一正确的选项。

【非常重要的输出要求】
1. 只输出最终答案本身
2. 如果是选择题，只输出 A / B / C / D（大写）
3. 如果是数字题，只输出数字本身
4. 不要解释，不要多说一句话，不要输出多余字符

题目如下：
{text}

请直接输出答案：
""".strip()

def build_subjective_prompt(question, model_answer, reference=None):
    # 此函数通常用于 Judge，question 已经是文本
    return f"""
你是一个严格的评分员，请根据问题和模型回答进行评分。

【评分规则】
- 评分范围：1 到 10 分
- 10 分：回答准确、完整、清晰
- 5 分：回答部分正确但不完整
- 1 分：回答错误或无关

【输出要求】
- 只输出一个整数（1-10）
- 不要解释，不要多余文字

【问题】
{question}

【模型回答】
{model_answer}

【参考答案】
{reference or "无"}

请给出评分：
""".strip()


def build_subjective_answer_prompt(item: EvaluationItem) -> str:
    text = get_item_text(item.content)
    return f"""
请认真回答下面的主观问题。

问题：
{text}

请直接给出你的回答，不要自我评价，不要打分，字数限制在300以内。
""".strip()



def build_subjective_judge_prompt(item: EvaluationItem) -> str:
    text = get_item_text(item.content)
    return f"""
你是一个严格、公正的评测专家。

【问题】
{text}

【参考答案 / 评分要点】
{item.correct_answer}

【模型回答】
{item.predicted_answer}

请你根据参考答案，对模型回答进行评分。

评分要求：
1. 评分范围：1–10 的整数
2. 只输出一个数字
3. 不要解释，不要输出多余内容

请直接输出分数：
""".strip()

# =========================================================
# 对抗评测：模型裁判 Prompt
# =========================================================

def build_adversarial_judge_prompt(item):
    """
    构造对抗评测的裁判 Prompt
    """
    text = get_item_text(item.content)
    return f"""
你是一个严格、公正的评测裁判。

下面给出同一个问题的两个模型回答，请你判断哪一个更好。

【评判标准】
- 准确性
- 完整性
- 逻辑清晰度
- 与问题的相关性

【问题】
{text}

【模型 A 回答】
{item.predicted_answer}

【模型 B 回答】
{item.predicted_answer_2}

【输出要求（非常重要）】
- 如果模型 A 更好，只输出：left
- 如果模型 B 更好，只输出：right
- 如果两者水平相当，只输出：tie
- 不要解释
- 不要输出任何多余字符

请直接输出裁判结果：
""".strip()




def clean_choice_answer(raw_text: str) -> str:
    """
    从模型输出中提取最终答案（兜底防御）
    """
    if not raw_text:
        return ""

    text = raw_text.strip().upper()

    # 优先提取字母选项
    for ch in ["A", "B", "C", "D", "E", "F"]:
        if ch in text:
            return ch

    # 再提取数字
    match = re.search(r"-?\d+(\.\d+)?", text)
    if match:
        return match.group(0)

    return text


def parse_adversarial_judge(raw_text: str) -> str:
    """
    解析对抗评测裁判模型的输出。
    目标：从一段话中提取出 'left', 'right' 或 'tie'。
    """
    if not raw_text:
        return "tie"

    # 特殊情况：如果是 API 报错，直接返回 error (之前逻辑已有处理，这里做兜底)
    if raw_text.startswith("[Error]"):
        return "error"

    text = raw_text.lower().strip()

    # 优先级匹配：
    # 1. 明确的关键词匹配
    if "left" in text:
        return "left"
    if "right" in text:
        return "right"
    if "tie" in text or "equal" in text or "draw" in text or "平局" in text:
        return "tie"

    # 2. 如果都没有找到，尝试正则匹配单词
    if re.search(r"\bleft\b", text): return "left"
    if re.search(r"\bright\b", text): return "right"
    
    # 3. 实在找不到，默认平局
    return "tie"


def normalize_answer(text: str) -> str:
    """
    标准化答案（防止空格、大小写差异）
    """
    if not text:
        return ""
    return re.sub(r"\s+", "", str(text)).lower()


def generate_adversarial_summary(task):
    """
    根据人类裁判 preference，生成对抗评测汇总结果
    preference:
        - left  : Model A 胜
        - right : Model B 胜
        - tie   : 平局
    """

    items = EvaluationItem.objects.filter(task=task)

    total = items.count()
    if total == 0:
        # 避免报错，如果还没生成 items，直接返回 None
        return None

    win_a = items.filter(preference="left").count()
    win_b = items.filter(preference="right").count()
    tie = items.filter(preference="tie").count()

    # 防止除 0
    # 胜率计算：(胜场 + 0.5 * 平局) / 总场次
    win_rate_a = round((win_a + 0.5 * tie) / total, 4) if total > 0 else 0.0

    model_a_name = task.myModel.name
    model_b_name = task.myModel_2.name if task.myModel_2 else "Unknown"

    summary_text = (
        f"对抗评测结果：\n"
        f"模型 A（{model_a_name}） vs 模型 B（{model_b_name}）\n"
        f"总题数：{total}\n"
        f"模型 A 胜：{win_a}\n"
        f"模型 B 胜：{win_b}\n"
        f"平局：{tie}\n"
        f"模型 A 胜率：{win_rate_a * 100:.2f}%\n"
    )

    summary, _ = EvaluationSummary.objects.update_or_create(
        task=task,
        defaults={
            "model_name": f"{model_a_name} vs {model_b_name}",
            "total": total,
            "correct": win_a,        # A 胜场
            "accuracy": win_rate_a,  # A 胜率
            "summary": summary_text,
        },
    )

    return summary


# =========================================================
# Dataset → EvaluationItem
# =========================================================

import base64
import zipfile
import io

def load_dataset_entries(dataset: Dataset):
    """
    从 Dataset.file_path 读取数据
    支持 JSON 和 ZIP (读取内部 data.json)
    """
    if not dataset.file_path:
        raise ValueError("Dataset has no file")

    file_format = dataset.file_format.lower()
    
    if file_format == "json":
        with open(dataset.file_path.path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Dataset JSON must be a list")
            return data

    elif file_format == "zip":
        try:
            with zipfile.ZipFile(dataset.file_path.path, 'r') as zf:
                # 查找 data.json
                target = "data.json"
                if target not in zf.namelist():
                    # 尝试找任何 json
                    json_files = [f for f in zf.namelist() if f.endswith('.json')]
                    if not json_files:
                        raise ValueError("ZIP file must contain data.json")
                    target = json_files[0]
                
                with zf.open(target) as f:
                    data = json.loads(f.read().decode('utf-8'))
                    if not isinstance(data, list):
                        raise ValueError("Dataset JSON inside ZIP must be a list")
                    return data
        except Exception as e:
            raise ValueError(f"Failed to read ZIP dataset: {e}")

    else:
        # 暂时不支持 CSV 用于评测 (因为需要复杂结构)
        raise ValueError(f"Unsupported format for evaluation: {file_format}")


def load_image_from_dataset(dataset: Dataset, image_path: str) -> str:
    """
    从数据集 ZIP 文件中读取图片并转为 Base64
    """
    if not dataset.file_path or dataset.file_format.lower() != "zip":
        return None
        
    try:
        with zipfile.ZipFile(dataset.file_path.path, 'r') as zf:
            if image_path not in zf.namelist():
                # 尝试模糊匹配 (有的路径带 ./ 或 /)
                for name in zf.namelist():
                    if name.endswith(image_path) or image_path.endswith(name):
                        image_path = name
                        break
                else:
                    return None # 没找到

            with zf.open(image_path) as f:
                content = f.read()
                return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None



def normalize_content(text: str) -> str:
    """
    归一化内容：去除所有空白字符，用于比对
    """
    if not text:
        return ""
    return "".join(text.split())

def find_existing_answer(model_id, dataset_id, content):
    """
    精准复用：在同一个数据集 ID 下寻找该模型对该特定内容的回答
    【增强】支持 JSON 格式内容与纯文本内容的交叉比对
    """
    if not content:
        return None
        
    # 1. 获取纯文本内容用于比对
    text_to_match = get_item_text(content)
    norm_text_to_match = normalize_content(text_to_match)
    
    if not norm_text_to_match:
        return None

    from django.db.models import Q
    
    # 2. 模糊匹配前缀以缩小范围 (取前20位，考虑 JSON 头部)
    clean_prefix = text_to_match.strip()[:10] 

    match = EvaluationItem.objects.filter(
        task__dataset_id=dataset_id,
        content__contains=clean_prefix 
    ).filter(
        (Q(task__myModel_id=model_id) & Q(predicted_answer__isnull=False) & ~Q(predicted_answer__startswith="[Error]")) |
        (Q(task__myModel_2_id=model_id) & Q(predicted_answer_2__isnull=False) & ~Q(predicted_answer_2__startswith="[Error]"))
    )
    
    # 3. 在内存中做精确匹配
    for it in match:
        it_text = get_item_text(it.content)
        if normalize_content(it_text) == norm_text_to_match:
            # 如果是多模态，还需要校验图片路径是否一致
            if "image" in content and "image" in it.content:
                try:
                    img1 = json.loads(content).get("image")
                    img2 = json.loads(it.content).get("image")
                    if img1 != img2: continue # 图片不同，不能复用
                except: pass

            if it.task.myModel_id == model_id:
                ans = it.predicted_answer
            else:
                ans = it.predicted_answer_2
            
            if ans and not ans.startswith("[Error]"):
                return ans
            
    return None


def get_entry_data(entry):
    """统一解析 entry 逻辑：处理 text, image, gold_answer"""
    text = (
        entry.get("input")
        or entry.get("question")
        or entry.get("prompt")
        or entry.get("text")
    )
    gold_answer = (
        entry.get("answer")
        or entry.get("label")
        or entry.get("target")
    )
    
    image_path = entry.get("image") or entry.get("image_path")
    if image_path:
        content = json.dumps({"text": text, "image": image_path}, ensure_ascii=False)
    else:
        content = text
        
    return content, gold_answer

def reuse_task_items_model_aware(old_task, new_task):
    """
    模型感知型复用：从旧任务中精准提取新任务需要的模型回复。
    """
    from .models import EvaluationItem
    
    # 建立旧任务内容的索引
    old_items = {it.content: it for it in EvaluationItem.objects.filter(task=old_task)}
    
    # --- 场景 A: 任务已初始化，执行 Update 逻辑 ---
    if new_task.items.exists():
        # ... (内部逻辑保持不变，因为匹配的是 existing items)
        pass # 这里省略部分代码，replace 整体替换下面函数

    # --- 场景 B: 任务未初始化，执行 Create 逻辑 ---
    new_items_to_create = []
    
    entries = load_dataset_entries(new_task.dataset)
    for entry in entries:
        content, gold_answer = get_entry_data(entry)
        old_item = old_items.get(content)
        
        pred_1 = None
        pred_2 = None
        is_correct = None
        
        if old_item:
            # 1. 为新任务的第一个模型寻找回复
            if old_task.myModel_id == new_task.myModel_id:
                val = old_item.predicted_answer
                if val and not val.startswith("[Error]"):
                    pred_1 = val
            elif old_task.myModel_2_id == new_task.myModel_id:
                val = old_item.predicted_answer_2
                if val and not val.startswith("[Error]"):
                    pred_1 = val
            
            # 客观题立即判分
            if new_task.method == 'objective' and pred_1:
                pred = normalize_answer(clean_choice_answer(pred_1))
                gold = normalize_answer(gold_answer)
                is_correct = 1 if pred == gold else 0

            # 2. 如果是新任务是对抗任务，为第二个模型寻找回复
            if new_task.method == 'adversarial':
                if old_task.myModel_id == new_task.myModel_2_id:
                    val = old_item.predicted_answer
                    if val and not val.startswith("[Error]"):
                        pred_2 = val
                elif old_task.myModel_2_id == new_task.myModel_2_id:
                    val = old_item.predicted_answer_2
                    if val and not val.startswith("[Error]"):
                        pred_2 = val
        
        new_items_to_create.append(EvaluationItem(
            task=new_task,
            content=content,
            correct_answer=gold_answer,
            predicted_answer=pred_1,
            predicted_answer_2=pred_2,
            is_correct=is_correct  # 写入判分结果
        ))
    
    EvaluationItem.objects.bulk_create(new_items_to_create)


@transaction.atomic
def prepare_evaluation_items(task: EvaluationTask):
    """
    增强版：创建条目时自动跨任务复用模型回答
    """
    from .models import EvaluationItem

    if task.items.exists():
        # ... (保留存量条目补全逻辑)
        all_items = list(task.items.all())
        updated_items = []
        for item in all_items:
            changed = False
            if not item.predicted_answer:
                ans = find_existing_answer(task.myModel_id, task.dataset_id, item.content)
                if ans:
                    item.predicted_answer = ans
                    changed = True
            
            if task.method == 'adversarial' and task.myModel_2_id and not item.predicted_answer_2:
                ans = find_existing_answer(task.myModel_2_id, task.dataset_id, item.content)
                if ans:
                    item.predicted_answer_2 = ans
                    changed = True
            
            if changed:
                updated_items.append(item)
        
        if updated_items:
            EvaluationItem.objects.bulk_update(updated_items, ['predicted_answer', 'predicted_answer_2'])
            
        return [it.id for it in all_items]

    entries = load_dataset_entries(task.dataset)
    items_to_create = []

    for entry in entries:
        content, gold_answer = get_entry_data(entry)
        
        if not content:
            continue

        # 核心：尝试搜刮已有的回答
        pred_1 = find_existing_answer(task.myModel_id, task.dataset_id, content)
        pred_2 = None
        if task.method == 'adversarial' and task.myModel_2_id:
            pred_2 = find_existing_answer(task.myModel_2_id, task.dataset_id, content)

        items_to_create.append(
            EvaluationItem(
                task=task,
                content=content,
                correct_answer=gold_answer,
                predicted_answer=pred_1,
                predicted_answer_2=pred_2
            )
        )

    created_items = EvaluationItem.objects.bulk_create(items_to_create)
    return list(task.items.values_list("id", flat=True))


def get_pending_item_ids(task: EvaluationTask, limit: int = 100):
    """
    高效获取待处理条目的 ID 列表（用于分批调度）
    不仅检查预测结果，还要检查模型评分状态
    """
    from django.db.models import Q
    qs = task.items.all().order_by("id")
    
    if task.method == "adversarial":
        if task.judge_type == "model":
            # 只要缺一个回答，或者 (两个回答都有但缺偏好 且 无 Error)
            qs = qs.filter(
                Q(predicted_answer__isnull=True) | 
                Q(predicted_answer_2__isnull=True) |
                (Q(preference__isnull=True) & 
                 ~Q(predicted_answer__startswith="[Error]") & 
                 ~Q(predicted_answer_2__startswith="[Error]"))
            )
        else:
            # 人工判定，只需生成回答
            qs = qs.filter(Q(predicted_answer__isnull=True) | Q(predicted_answer_2__isnull=True))
            
    elif task.method == "objective":
        # 客观评测，只需生成回答
        qs = qs.filter(predicted_answer__isnull=True)
        
    elif task.method == "subjective":
        if task.judge_type == "model":
            # 只要缺回答，或者 (有回答但缺分数 且 无 Error)
            qs = qs.filter(
                Q(predicted_answer__isnull=True) | 
                (Q(score__isnull=True) & ~Q(predicted_answer__startswith="[Error]"))
            )
        else:
            # 人工判定，只需生成回答
            qs = qs.filter(predicted_answer__isnull=True)
        
    return list(qs.values_list("id", flat=True)[:limit])


# ... (imports remain similar, assume existing context)

# =========================================================
# Single Item Logic (Granular Execution)
# =========================================================

def run_single_item_logic(item_id: int, phase='both'):
    """
    执行单个 Item 的评测逻辑 (Worker 核心逻辑)
    phase: 'generation', 'judging', 'both'
    """
    try:
        # 必须 select_related task，以便访问 task.method 等配置
        try:
            item = EvaluationItem.objects.select_related(
                "task", 
                "task__myModel", 
                "task__myModel_2", 
                "task__judge_model",
                "task__dataset"  # [Fix] 需要 dataset 才能加载图片
            ).get(id=item_id)
        except EvaluationItem.DoesNotExist:
            return

        task = item.task
        method = task.method
        
        # [New] 提取多模态数据
        _, images = extract_multimodal_data(item)
        
        # 定义一个辅助闭包，判断指定模型是否能看图
        def can_see(model_obj):
            return model_obj and model_obj.category == "multimodal"

        # 1. 客观评测
        if method == "objective" and phase in ['generation', 'both']:
            if item.predicted_answer: return
            prompt = build_objective_prompt(item)
            # 按需发图
            raw_prediction = call_llm_api(
                prompt, 
                task.myModel.name, 
                images=images if can_see(task.myModel) else None
            )
            item.predicted_answer = raw_prediction
            if raw_prediction.startswith("[Error]"):
                item.is_correct = 0
            else:
                pred = normalize_answer(clean_choice_answer(raw_prediction))
                gold = normalize_answer(item.correct_answer)
                item.is_correct = 1 if pred == gold else 0
            item.save(update_fields=["predicted_answer", "is_correct"])

        # 2. 主观评测
        elif method == "subjective":
            if phase in ['generation', 'both'] and not item.predicted_answer:
                item.predicted_answer = call_llm_api(
                    build_subjective_answer_prompt(item), 
                    task.myModel.name,
                    images=images if can_see(task.myModel) else None
                )
                item.save(update_fields=["predicted_answer"])

            if phase in ['judging', 'both'] and task.judge_type == "model":
                if item.predicted_answer and not item.predicted_answer.startswith("[Error]") and item.score is None:
                    judge_m = task.judge_model or task.myModel
                    raw_score = call_llm_api(
                        build_subjective_judge_prompt(item), 
                        judge_m.name,
                        images=images if can_see(judge_m) else None
                    )
                    if raw_score.startswith("[Error]"): item.score = -1
                    else:
                        try:
                            score = int(raw_score.strip())
                            item.score = max(1, min(10, score))
                        except: item.score = 1
                    item.save(update_fields=["score"])

        # 3. 对抗评测
        elif method == "adversarial":
            if phase in ['generation', 'both']:
                updated = False
                if not item.predicted_answer:
                    item.predicted_answer = call_llm_api(
                        get_item_text(item.content),
                        task.myModel.name,
                        images=images if can_see(task.myModel) else None
                    )
                    updated = True
                if not item.predicted_answer_2 and task.myModel_2:
                    item.predicted_answer_2 = call_llm_api(
                        get_item_text(item.content),
                        task.myModel_2.name,
                        images=images if can_see(task.myModel_2) else None
                    )
                    updated = True
                if updated:
                    item.save(update_fields=["predicted_answer", "predicted_answer_2"])

            if phase in ['judging', 'both'] and task.judge_type == "model" and item.preference is None:
                ans1, ans2 = item.predicted_answer, item.predicted_answer_2
                if ans1 and ans2 and not (ans1.startswith("[Error]") or ans2.startswith("[Error]")):
                    judge_m = task.judge_model or task.myModel
                    raw_judge = call_llm_api(
                        build_adversarial_judge_prompt(item),
                        judge_m.name,
                        images=images if can_see(judge_m) else None
                    )
                    item.preference = "error" if raw_judge.startswith("[Error]") else parse_adversarial_judge(raw_judge)
                    item.save(update_fields=["preference"])
                elif (ans1 and ans1.startswith("[Error]")) or (ans2 and ans2.startswith("[Error]")):
                    item.preference = "error"
                    item.save(update_fields=["preference"])

    except Exception as outer_e:
        # [Ultimate Fail-Safe] 兜底异常捕获
        # 如果发生任何未捕获异常，强制将 predicted_answer 标记为 Error，
        # 防止该条目无限期卡在 pending 状态导致死循环。
        try:
            if 'item' in locals() and item:
                error_msg = f"[Error] System Failure: {str(outer_e)}"
                # 只有当字段为空时才覆盖，保留部分结果
                if not item.predicted_answer:
                    item.predicted_answer = error_msg
                if item.task.method == "adversarial" and not item.predicted_answer_2:
                    item.predicted_answer_2 = error_msg
                
                # 针对打分字段也要兜底
                if item.task.method == "subjective" and item.score is None:
                    item.score = -1
                if item.task.method == "adversarial" and item.preference is None:
                    item.preference = "error"
                    
                item.save()
        except:
            # 如果连 save 都失败（例如 DB 挂了），那确实没办法了，
            # 但至少 Worker 不会崩溃，Log 会记录下来。
            pass
        print(f"Critical error in run_single_item_logic: {outer_e}")


# =========================================================
# Task Finalizer (Thread-Safe & Optimized)
# =========================================================

def sync_downstream_tasks(upstream_task):
    """
    当上游任务生成完毕后，同步数据到下游挂起的任务
    """
    # 查找所有挂起的下游任务
    downstream_tasks = upstream_task.downstream_tasks.filter(status__in=['pending', 'running'])
    
    if not downstream_tasks.exists():
        return

    for dt in downstream_tasks:
        # 防御性检查：如果下游任务已经有 items 了（异常情况），跳过复制
        if dt.items.exists():
            continue

        # 1. 使用模型感知型复制 (可能只复制了部分模型回答)
        reuse_task_items_model_aware(upstream_task, dt)
        
        # 2. 检查同步后的状态，决定下一步
        from django.db.models import Q
        has_missing_answers = dt.items.filter(Q(predicted_answer__isnull=True) | Q(predicted_answer_2__isnull=True)).exists()

        if dt.method == 'objective' and not has_missing_answers:
             # 客观评测且回答全了：直接结算
             try_finalize_task(dt.id, from_dispatcher=True)

        elif dt.judge_type == 'human' and not has_missing_answers:
            dt.status = 'awaiting_human_judge'
            dt.save(update_fields=['status'])

        else:
            # 需要补全回答或进行模型打分
            from .tasks import init_evaluation_task
            init_evaluation_task.delay(dt.id)


def try_finalize_task(task_id: int, from_dispatcher: bool = False):
    """
    检查任务是否全部完成，如果是，执行汇总逻辑。
    
    优化逻辑：
    - 如果 from_dispatcher=True，说明调度器已经发完了所有任务。
      此时如果发现还有 pending items，不再只是 return，而是安排一个延时检查 (reschedule)。
      这避免了 Worker 每次都 select_for_update 的开销。
    """
    from apps.tasks.tasks import try_finalize_task_delayed # 避免循环引用，lazy import
    
    with transaction.atomic():
        try:
            task = EvaluationTask.objects.select_related("dataset", "myModel").select_for_update().get(id=task_id)
        except EvaluationTask.DoesNotExist:
            return

        if task.status != "running":
            return

        method = task.method
        has_pending = False
        
        # 判定 pending 逻辑 (包含 [Error] 视为已处理)
        # 注意：这里我们只看“是否还有没填值的”。[Error] 也是值，所以不算 pending。
        
        if method == "objective":
            # 只要有 predicted_answer 为空的，就算没完
            has_pending = task.items.filter(predicted_answer__isnull=True).exists()
            
        elif method == "subjective":
            # 1. 必须都有 predicted_answer
            # 2. 如果是 model judge，还必须都有 score (前提是 predicted_answer 正常)
            if task.items.filter(predicted_answer__isnull=True).exists():
                has_pending = True
            elif task.judge_type == "model":
                # 复杂的 pending 检查：
                # 还有“预测成功(非Error) 但 分数为空”的吗？
                # 如果预测失败([Error])，score 可以为空，不算 pending
                has_pending = task.items.exclude(predicted_answer__startswith="[Error]").filter(score__isnull=True).exists()
                
        elif method == "adversarial":
            if task.items.filter(predicted_answer__isnull=True).exists() or \
               task.items.filter(predicted_answer_2__isnull=True).exists():
                has_pending = True
            elif task.judge_type == "model":
                has_pending = task.items.exclude(predicted_answer__startswith="[Error]") \
                                        .exclude(predicted_answer_2__startswith="[Error]") \
                                        .filter(preference__isnull=True).exists()

        if has_pending:
            if from_dispatcher:
                # 调度器说发完了，但数据库说没做完 -> 可能是 Worker 还在跑
                # 触发“延时最终检查”，过 5 秒再来看看
                try_finalize_task_delayed.apply_async(args=[task_id], countdown=5)
            return

        # === 到这里说明所有条目都已处理完毕 ===
        
        # 1. 特殊情况：如果是 人类裁判，状态转为 awaiting
        if method in ["subjective", "adversarial"] and task.judge_type == "human":
            task.status = "awaiting_human_judge"
            task.save(update_fields=["status"])
            
            # --- Sync Downstream Tasks (For Human Judge path) ---
            sync_downstream_tasks(task)
            
            return

        # 2. 正常情况：计算统计数据 & 标记 Completed
        if method == "objective":
            # 聚合计算
            total = task.items.count()
            # 排除 [Error]
            valid_items = task.items.exclude(predicted_answer__startswith="[Error]")
            correct = valid_items.filter(is_correct=1).count()
            
            # 分母用 total 还是 valid_total？通常用 total 统计完成率，但准确率可能仅针对 valid
            # 这里简单起见，[Error] 算错
            acc = round(correct / total, 4) if total > 0 else 0
            
            task.accuracy = acc
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["accuracy", "status", "time_used"])
            
            EvaluationSummary.objects.update_or_create(
                task=task,
                defaults={
                    "model_name": task.myModel.name,
                    "total": total,
                    "correct": correct,
                    "accuracy": acc,
                }
            )

        elif method == "subjective":
            from django.db.models import Avg
            valid_items = task.items.exclude(predicted_answer__startswith="[Error]")
            avg = valid_items.aggregate(Avg("score"))["score__avg"] or 0
            avg = round(avg, 4)
            
            task.score = avg
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["score", "status", "time_used"])
            
            EvaluationSummary.objects.update_or_create(
                task=task,
                defaults={
                    "model_name": f"{task.myModel.name} (judge=Model)",
                    "total": task.items.count(),
                    "avg_score": avg,
                }
            )

        elif method == "adversarial":
            summary_obj = generate_adversarial_summary(task)
            task.status = "completed"
            task.time_used = timezone.now() - task.created_at
            task.save(update_fields=["status", "time_used"])

        # --- Sync Downstream Tasks (For Model Judge / Objective path) ---
        sync_downstream_tasks(task)

        # 3. 通用收尾
        log_task_complete(task, task.creator)
        
        from apps.rankings.services import update_model_rankings
        
        # 【新增】防刷分机制：如果是纯复用任务（耗时极短），不更新排行榜
        should_update_rankings = True
        
        # 对所有类型的评测都生效
        if task.time_used:
            total_cnt = task.items.count()
            if total_cnt > 0:
                avg_time = task.time_used.total_seconds() / total_cnt
                # 如果每题平均耗时 < 0.5秒，认为是全复用（正常 API 至少 1-2秒/题）
                if avg_time < 0.5:
                    should_update_rankings = False
                    print(f"Task {task_id} ({method}) completed via full reuse (avg {avg_time:.2f}s/item), skipping ranking update.")

        if should_update_rankings:
            update_model_rankings(task.dataset_id)


# =========================================================
# 对外统一入口
# =========================================================

def run_evaluation(task_id: int):
    """
    执行评测全流程 (双阶段执行以优化复用)
    1. 生成阶段: 获取所有模型回答
    2. 同步点: 通知下游任务
    3. 判定阶段: 进行模型打分
    """
    task = EvaluationTask.objects.get(id=task_id)
    item_ids = prepare_evaluation_items(task)
    task.status = "running"
    task.save()
    
    # --- 阶段 1: 仅生成回答 ---
    # 我们通过向 run_single_item_logic 传递 flag 来只跑生成
    for iid in item_ids:
        run_single_item_logic(iid, phase='generation')
        
    # --- 阶段 2: 同步下游 (关键优化点) ---
    sync_downstream_tasks(task)
    
    # --- 阶段 3: 进行打分 (如果是模型评测) ---
    if task.judge_type == 'model':
        from .tasks import init_evaluation_task
        for iid in item_ids:
            run_single_item_logic(iid, phase='judging')
        
    try_finalize_task(task_id, from_dispatcher=True)
    return {"status": "completed"}