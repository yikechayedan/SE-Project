import request from './request'

/**
 * 获取完整排行榜
 */
export function getLeaderboard() {
  return request({
    url: '/api/rankings/leaderboard/',
    method: 'get'
  })
}

/**
 * 获取指定数据集的模型排行榜
 */
export function getTopModels(datasetId, limit = 10) {
  return request({
    url: '/api/rankings/top/',
    method: 'get',
    params: { dataset_id: datasetId, limit }
  })
}

/**
 * 获取模型排名历史
 */
export function getModelRankingHistory(modelId, datasetId) {
  return request({
    url: `/api/rankings/history/${modelId}/`,
    method: 'get',
    params: { dataset_id: datasetId }
  })
}
