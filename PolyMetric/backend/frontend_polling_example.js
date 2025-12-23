/**
 * 前端轮询示例代码
 * 用于查询数据集能力分析状态
 */

// 示例：轮询数据集能力分析状态
function pollDatasetCapabilityStatus(datasetId, callback, maxAttempts = 30) {
  let attempts = 0;
  
  const poll = async () => {
    attempts++;
    
    try {
      // 调用API查询状态
      const response = await fetch(`/api/datasets/${datasetId}/capability_status/`);
      const result = await response.json();
      
      if (result.code === 200) {
        const { capability_tag, capability_dimension, is_processing, is_verified } = result.data;
        
        // 检查审核状态
        if (!is_verified) {
          // 未审核，显示等待审核状态
          callback({
            success: true,
            data: result.data,
            isCompleted: false
          });
        } else {
          // 已审核，检查能力分析状态
          let status, message, type;
          
          switch (capability_tag) {
            case 'processing':
              status = 'processing';
              message = '数据集已审核通过，正在分析能力维度...';
              type = 'info';
              break;
              
            case 'no_file':
              status = 'error';
              message = '数据集文件缺失，无法进行能力分析';
              type = 'error';
              break;
              
            case 'no_samples':
              status = 'error';
              message = '数据集中没有有效的样本数据，无法进行能力分析';
              type = 'error';
              break;
              
            case 'analysis_failed':
              status = 'error';
              message = '能力分析失败，请检查数据集格式或稍后重试';
              type = 'error';
              break;
              
            default:
              status = 'completed';
              message = `数据集审核完成，能力分析结果: ${capability_tag}`;
              type = 'success';
              break;
          }
          
          // 调用回调函数，传递当前状态
          callback({
            success: true,
            data: result.data,
            isCompleted: !is_processing
          });
          
          // 如果处理完成，停止轮询
          if (!is_processing) {
            if (status === 'completed') {
              console.log(`数据集 ${datasetId} 完全就绪`);
            } else {
              console.warn(`数据集 ${datasetId} 处理失败: ${message}`);
            }
            return;
          }
        }
      } else {
        // 处理错误
        callback({
          success: false,
          error: result.msg
        });
        return;
      }
    } catch (error) {
      console.error('轮询请求失败:', error);
      callback({ 
        success: false, 
        error: error.message 
      });
    }
    
    // 如果未完成且未超过最大尝试次数，继续轮询
    if (attempts < maxAttempts) {
      setTimeout(poll, 2000); // 每2秒轮询一次
    } else {
      console.warn(`数据集 ${datasetId} 能力分析轮询超时`);
      callback({ 
        success: false, 
        error: '轮询超时，请稍后手动刷新页面查看结果' 
      });
    }
  };
  
  // 开始轮询
  poll();
}

// 使用示例：
// 1. 上传数据集后，获取数据集ID
// 2. 开始轮询状态
function onDatasetUploaded(datasetId) {
  // 显示审核中的UI状态
  updateUI({
    status: 'pending_verification',
    message: '数据集已上传，等待管理员审核...',
    type: 'info'
  });
  
  // 开始轮询
  pollDatasetCapabilityStatus(datasetId, (result) => {
    // 处理不同的状态
    let status, message, type;
    
    // 检查审核状态
    if (!result.data.is_verified) {
      status = 'pending_verification';
      message = '数据集正在审核中，请耐心等待...';
      type = 'info';
    } else {
      // 已审核，检查能力分析状态
      switch (result.data.capability_tag) {
        case 'processing':
          status = 'processing';
          message = '数据集已审核通过，正在分析能力维度...';
          type = 'info';
          break;
          
        case 'no_file':
          status = 'error';
          message = '数据集文件缺失，无法进行能力分析';
          type = 'error';
          break;
          
        case 'no_samples':
          status = 'error';
          message = '数据集中没有有效的样本数据，无法进行能力分析';
          type = 'error';
          break;
          
        case 'analysis_failed':
          status = 'error';
          message = '能力分析失败，请检查数据集格式或稍后重试';
          type = 'error';
          break;
          
        default:
          status = 'completed';
          message = `数据集审核完成，能力分析结果: ${result.data.capability_tag}`;
          type = 'success';
          break;
      }
    }
    
    // 更新UI
    updateUI({
      status: status,
      isVerified: result.data.is_verified,
      capabilityTag: result.data.capability_tag,
      capabilityDimension: result.data.capability_dimension,
      message: message,
      type: type
    });
    
    // 如果处理完成或有错误，停止轮询并显示通知
    if (!result.data.is_processing && result.data.is_verified) {
      if (status === 'completed') {
        showNotification('数据集已完全就绪', 'success');
      } else if (status === 'pending_verification') {
        // 继续轮询审核状态
        return;
      } else {
        showNotification(message, 'error');
      }
    }
  });
}

// UI更新函数（示例）
function updateUI(state) {
  console.log('UI状态更新:', state);
  
  // 这里可以根据实际的前端框架进行实现
  // 例如：
  // - 显示/隐藏加载动画
  // - 更新状态文本
  // - 更新能力标签显示
  // - 更新审核状态显示
  
  // 示例：更新状态显示元素
  const statusElement = document.getElementById('dataset-status');
  if (statusElement) {
    statusElement.textContent = state.message;
    statusElement.className = `status-${state.status}`;
  }
  
  // 示例：更新能力标签显示
  const capabilityElement = document.getElementById('capability-tag');
  if (capabilityElement && state.capabilityTag) {
    capabilityElement.textContent = state.capabilityTag;
  }
}

// 通知函数（示例）
function showNotification(message, type = 'info') {
  console.log(`[${type.toUpperCase()}] ${message}`);
  
  // 这里可以根据实际的前端框架实现通知
  // 例如：使用toast、alert、snackbar等
}

// 导出函数供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    pollDatasetCapabilityStatus,
    onDatasetUploaded
  };
}