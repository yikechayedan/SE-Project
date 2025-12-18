import request from './request'

// 获取评论列表
export function getComments(params) {
  return request({
    url: '/api/comments/',
    method: 'get',
    params
  })
}

// 发布评论
export function postComment(data) {
  return request({
    url: '/api/comments/',
    method: 'post',
    data
  })
}

// 删除评论
export function deleteComment(id) {
  return request({
    url: `/api/comments/${id}/`,
    method: 'delete'
  })
}

// 点赞/取消点赞评论
export function toggleCommentLike(id) {
  return request({
    url: `/api/comments/${id}/like/`,
    method: 'post'
  })
}
