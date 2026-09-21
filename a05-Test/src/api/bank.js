// src/api/bank.js
import apiClient from './client';

// ==========================================
// 2. 题库专属接口
// ==========================================

/**
 * 获取题库列表
 * @param {Object} params - 请求参数
 * @param {string} params.category - [必填] 分类标签 (如 'python_knowledge', 'common_behavior')
 * @param {number} [params.page=1] - 当前页码
 * @param {number} [params.limit=10] - 每页条数
 * @param {string} [params.difficulty='all'] - 难度筛选 ('all', 'Easy', 'Medium', 'Hard')
 * @returns {Promise<Object>} 后端返回的 JSON 数据
 */
export const getQuestionBank = async (params) => {
  try {
    

    const response = await apiClient.get('/api/question_bank', {
      params: params
    });
    
    // 返回真实的 data 层
    return response.data;
  } catch (error) {
    console.error('【API 错误】获取题库列表失败:', error);
    throw error;
  }
};

/**
 * 获取单道题目的详细内容/参考答案 (预留接口，用于之后点击“查看详情”)
 * @param {string|number} questionId - 题目ID
 * @returns {Promise<Object>} 题目详情
 */
export const getQuestionDetail = async (questionId) => {
  try {
    if (!questionId) throw new Error('缺少题目 ID');
    
    // 这里假设后端的详情路径是 /api/question_bank/{id}，如果不同请自行修改
    const response = await apiClient.get(`/api/question_bank/${questionId}`);
    return response.data;
  } catch (error) {
    console.error(`【API 错误】获取题目 ${questionId} 详情失败:`, error);
    throw error;
  }
};
