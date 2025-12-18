一、系统动态模型说明（背景）
SystemEvent（系统事件）

SystemEvent 用于记录已经发生的系统行为快照，
事件内容在写入时即固化，避免后续对象修改导致历史信息变化。

事件类型（event_type）
event_type	含义	前端展示风格
dataset_upload	数据集上传	success（绿色）
model_add	模型收录	primary（蓝色）
rank_up	排名上升	warning（金色/橙色）
task_complete	评测完成	info（灰色）
二、API 接口列表
API S1：获取系统动态新闻流

GET /api/system/news/
权限：无需登录（AllowAny）

📌 说明
返回最近的系统事件列表，用于首页 News Feed 展示，
当前最多返回 50 条最新事件，按时间倒序排列。

Response（200）
{
  "code": 200,
  "data": [
    {
      "id": 101,
      "content": "用户 shadow 上传了新数据集「MMLU」",
      "time": "2025-12-12T10:30:00Z",
      "type": "success",
      "icon": "Folder"
    },
    {
      "id": 100,
      "content": "平台新收录模型：DeepSeek-V3-250324 (DeepSeek)",
      "time": "2025-12-12T09:10:00Z",
      "type": "primary",
      "icon": "Box"
    }
  ]
}

返回字段说明
字段	说明
id	系统事件 ID
content	事件展示文案（已格式化）
time	事件发生时间（UTC，ISO 格式）
type	前端展示类型（success / primary / warning / info）
icon	前端展示图标名称

字段映射逻辑由序列化器统一完成，前端无需自行判断事件类型。