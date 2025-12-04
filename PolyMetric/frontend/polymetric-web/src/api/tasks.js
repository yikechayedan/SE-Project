import request from './request'

//获取评测任务列表
export function getEvaluationTasks() {
  return request.get('/api/tasks/evaluation-tasks/')
}

//创建评测任务
export function createEvaluationTask(data) {
  return request.post('/api/tasks/evaluation-tasks/', data)
}

//获取评测任务详情
export function getEvaluationTaskDetail(id) {
    return request.get(`/api/tasks/evaluation-tasks/${id}/`)
}