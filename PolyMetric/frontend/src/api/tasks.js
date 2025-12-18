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

//删除评测任务
export function deleteEvaluationTask(id) {
    return request.delete(`/api/tasks/evaluation-tasks/${id}/`)
}

//更新评测任务
export function updateEvaluationTask(id, data) {
    return request.put(`/api/tasks/evaluation-tasks/${id}/`, data)
}

//发起评测
export function runEvaluationTask(taskId) {
  return request({
    url: '/api/tasks/run-task/',
    method: 'post',
    data: { task_id: taskId } // 请求体格式
  });
}

//获取待测条目
export function getPendingItems() {
  
}