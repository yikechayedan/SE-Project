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
        const { capability_tag, capability_dimension, is_processing } = result.data;
        
        // 调用回调函数，传递当前状态
        callback({
          success: true,
          data: result.data,
          isCompleted: !is_processing
        });
        
        // 如果处理完成，停止轮询
        if (!is_processing) {
          console.log(`数据集 ${datasetId} 能力分析完成: ${capability_tag}`);
          return;
        }
      } else {
        console.error(`查询失败: ${result.msg}`);
        callback({ success: false, error: result.msg });
      }
    } catch (error) {
      console.error('轮询请求失败:', error);
      callback({ success: false, error: error.message });
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
  // 显示处理中的UI状态
  updateUI({
    status: 'processing',
    message: '正在分析数据集能力维度，请稍候...'
  });
  
  // 开始轮询
  pollDatasetCapabilityStatus(datasetId, (result) => {
    if (result.success) {
      // 更新UI
      updateUI({
        status: result.data.is_processing ? 'processing' : 'completed',
        capabilityTag: result.data.capability_tag,
        capabilityDimension: result.data.capability_dimension,
        message: result.data.is_processing 
          ? '正在分析数据集能力维度...' 
          : `能力分析完成: ${result.data.capability_tag}`
      });
      
      // 如果处理完成，可以执行其他操作
      if (result.isCompleted) {
        // 例如：显示成功通知，刷新页面等
        showNotification('数据集能力分析完成', 'success');
      }
    } else {
      // 处理错误
      updateUI({
        status: 'error',
        message: `查询失败: ${result.error}`
      });
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
  // - 显示错误信息等
  
  // 示例：更新状态显示元素
  const statusElement = document.getElementById('capability-status');
  if (statusElement) {
    statusElement.textContent = state.message;
    statusElement.className = `status-${state.status}`;
  }
  
  // 示例：更新能力标签显示
  if (state.capabilityTag) {
    const tagElement = document.getElementById('capability-tag');
    if (tagElement) {
      tagElement.textContent = state.capabilityTag;
    }
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