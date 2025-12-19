import request from './request'

/**
 * 获取系统动态/新闻流
 * @returns {Promise} 
 */
export function getNewsFeed() {
  return request({
    url: '/api/system/news/',
    method: 'get'
  })
}
