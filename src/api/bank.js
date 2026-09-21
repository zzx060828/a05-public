// src/api/bank.js
import axios from 'axios';

// ==========================================
// 1. Axios 实例与拦截器配置 (与 interview.js 保持一致)
// ==========================================
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
  timeout: 30000, // 题库拉取一般不需要像报告那么久，30秒足够了
});

apiClient.interceptors.request.use(
  (config) => {
    // 携带 Token 认证
    const token = localStorage.getItem('token'); 
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 处理 Content-Type
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    } else if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => {
    return Promise.reject({
      message: '请求拦截器错误',
      originalError: error
    });
  }
);

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