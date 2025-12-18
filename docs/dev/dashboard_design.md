# Dashboard & Leaderboard System Design

## 1. Overview
This document outlines the backend requirements and data structures needed to support the real-time Dashboard statistics and the dynamic Leaderboard on the Home page (`LoggedHome.vue`).

## 2. Backend Implementation Requirements

### 2.1. Statistics API
**Goal**: Provide system-wide counts and online status.

*   **Endpoint**: `GET /api/system/stats/`
*   **Permission**: AllowAny (or Authenticated)

**Response Structure (JSON)**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "models_count": 42,
    "datasets_count": 15,
    "tasks_count": 128,
    "users_count": 305,
    "online_users_count": 12, // Requires Redis/Cache tracking
    "active_users_last_24h": 45
  }
}
```

**Implementation Logic**:
*   `models_count`: `My_Model.objects.count()`
*   `datasets_count`: `Dataset.objects.count()`
*   `tasks_count`: `EvaluationTask.objects.count()`
*   `users_count`: `User.objects.count()`
*   `online_users`: Check Django sessions or cache keys (optional, can be 0 if not implemented).

### 2.2. Leaderboard API
**Goal**: Provide ranked model performance across different dimensions.

*   **Endpoint**: `GET /api/rankings/leaderboard/`
*   **Parameters**:
    *   `dimension`: string (optional, default='overall'). Values: `overall`, `language`, `reasoning`, `code`, `knowledge`.
    *   `limit`: int (optional, default=10).

**Response Structure (JSON)**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "dimension": "overall",
    "last_updated": "2023-10-27T10:00:00Z",
    "rankings": [
      {
        "rank": 1,
        "model_id": 101,
        "model_name": "GPT-4o",
        "company": "OpenAI",
        "scores": {
          "overall": 92.5,
          "language": 94.2,
          "reasoning": 91.8,
          "code": 93.1,
          "knowledge": 90.5
        },
        "trend": 1, // 1: Up, 0: Stable, -1: Down (Compared to last week/snapshot)
        "tags": ["text", "code"]
      },
      // ... more models
    ]
  }
}
```

### 2.3. Data Modeling Changes

To support the dimensions above, we need to map Datasets to Dimensions or store aggregate scores.

**Option A: Tagging Datasets (Recommended)**
Update `Dataset` model in `apps/datasets/models.py`:
```python
class Dataset(models.Model):
    # ... existing fields
    dimension = models.CharField(
        max_length=50, 
        choices=[
            ('language', 'Language Understanding'), 
            ('reasoning', 'Reasoning'), 
            ('code', 'Code Generation'), 
            ('knowledge', 'Knowledge Q&A')
        ],
        default='language'
    )
```

**Option B: Model Score Table (for fast reads)**
Create `ModelDimensionScore` in `apps/rankings/models.py`:
```python
class ModelDimensionScore(models.Model):
    model = models.ForeignKey(My_Model, ...)
    dimension = models.CharField(max_length=50) # 'overall', 'language', ...
    score = models.FloatField()
    trend = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
```

## 3. Frontend Integration Guide

1.  **Stats**: Call `/api/system/stats/` on mount.
2.  **Leaderboard**:
    *   On mount or dropdown change, call `/api/rankings/leaderboard/?dimension={selected}`.
    *   **Highlighting**:
        *   If `dimension == 'overall'`, highlight the "Overall" column.
        *   If `dimension == 'code'`, highlight the "Code" column.
    *   **Trend Animation**: Use CSS transitions when the `rank` order changes.

## 4. Mocking Strategy (Current Frontend Implementation)
Since the backend APIs are not yet ready:
1.  **Stats**: Derived from `getAllModels()`, `getAllDatasets()`, `getEvaluationTasks()`.
2.  **Leaderboard**: 
    *   Fetch `getAllModels()`.
    *   Generate deterministic mock scores based on Model ID to ensure consistency during the demo.
    *   Calculate "Trend" randomly or store in local storage to simulate changes.

