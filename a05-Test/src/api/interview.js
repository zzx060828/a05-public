import apiClient from './client';

export const getAvatarConnection = async () => {
  const response = await apiClient.get('/api/avatar/signed-url');
  return response.data;
};

// ==========================================
// 2. 面试流程核心接口
// ==========================================

// 创建面试
export const createInterview = async (config) => {
  try {
    const tempId = `session_${Date.now()}`;
    const requestData = {
      session_id: tempId,
      token: config.token || "",
      target_role: config.position || "Java后端开发工程师",
      experience: config.experience || "middle",
      type: config.type || "technical",
      difficulty: config.difficulty || 3,
      resume_text: config.resumeText || "",
      job_description: config.jobRequirements || ""
    };
    
    const response = await apiClient.post('/api/start', requestData);
    const resData = response.data || response;
    
    const finalId = resData.sessionId || 
                    resData.session_id || 
                    resData.sessionid || 
                    resData.data?.session_id || 
                    resData.data?.sessionId;

    if (!finalId) console.error("无法从后端返回中提取到任何 ID 字段！");
    
    return {
      ...resData,
      sessionId: finalId 
    };
  } catch (error) {
    console.error('【API 错误】创建面试失败:', error);
    throw error;
  }
};

// 提交录音答案
export const submitAnswer = async (formData, config = {}) => {
  try {
    const response = await apiClient.post('/api/chat_with_audio', formData, config);
    return response.data;
  } catch (error) {
    console.error('【API 错误】提交回答失败:', error);
    throw error;
  }
};

// 提交纯文字答案
export const submitTextAnswer = async (data, config = {}) => {
  try {
    const response = await apiClient.post('/api/chat', data, config);
    return response.data;
  } catch (error) {
    console.error('【API 错误】提交文字回答失败:', error);
    throw error;
  }
};


// ==========================================
// 3. 报告与历史记录接口
// ==========================================

// 获取全量专属报告 (支持雷达图、音视频进度条等所有模块)
export const getStreamingReport = async (sessionId, onChunk, onDone) => {
  try {
    const token = sessionStorage.getItem('candidate_token') || '';
    console.log("🚀 开始获取报告数据，ID:", sessionId);
    const response = await apiClient.post('/api/report', { session_id: sessionId, token });
    const data = response.data;

    console.log("📦 成功获取全量数据:", data);

    // 🔴 关键修复：把完整的大包先传给外面的收集器！你的报告页就靠这行代码活命了！
    const emitChunk = typeof onChunk === 'function' ? onChunk : () => {};
    emitChunk(data); 

    if (data.status === 'success') {
        // 依次将所有数据包派发给前端 Vue 组件渲染
        if (data.radar_packet) emitChunk(data.radar_packet);
        if (data.summary_packet) emitChunk(data.summary_packet);
        if (data.content_items && data.content_items.length > 0) {
            data.content_items.forEach(item => emitChunk(item));
        }
        if (data.voice_data) emitChunk({ type: 'voice', data: data.voice_data });
        if (data.video_data) emitChunk({ type: 'video', data: data.video_data });
        if (data.tips_data) emitChunk({ type: 'encourage', data: data.tips_data });
        if (data.history_trend) emitChunk({ type: 'history_trend', data: data.history_trend });
    } else {
        console.error("❌ 后端返回业务错误:", data.message);
    }
    
    if (onDone) onDone();

    // 🔴 放在最后：把数据 return 给 await 的调用者
    return data;

  } catch (err) {
    console.error("❌ 网络或接口请求失败", err);
    if (onDone) onDone();
    return { status: 'error', detail: err.message || '网络异常' }; // 给个安全的保底返回值
  }
};

// 获取我的面试历史报告列表
export const getHistoryReports = async () => {
  try {
    const response = await apiClient.get('/api/history_reports');
    return response.data;
  } catch (error) {
    console.error('获取历史报告失败:', error);
    throw error;
  }
};

// 专门用于安全获取后端音频 Blob 的方法
export const fetchAudioBlob = async (audioUrl) => {
  try {
    // 使用配置好的 apiClient，自动处理相对路径和跨域
    const response = await apiClient.get(audioUrl, {
      responseType: 'blob' // 🔴 必须指定接收类型为 blob！否则音频会变成乱码
    });
    return response.data;
  } catch (error) {
    console.error('【API 错误】获取音频文件失败:', error);
    throw error;
  }
};

// 提交实时截图 (每5秒发一次)
export const uploadScreenshot = async (formData) => {
  try {
    if (!(formData instanceof FormData)) {
      throw new Error('提交的数据必须是 FormData 类型');
    }
    return await apiClient.post('/api/upload_frame', formData);
  } catch (error) {
    console.error('【API 错误】实时截图上传失败:', error);
    throw error;
  }
};

// ==========================================
// 4. 新增：AI 定制练习计划接口
// ==========================================

// 获取根据短板动态生成的 AI 练习计划
export const getAiPracticePlan = async (params) => {
  try {
    // 这里的 params 应该是一个对象：{ weak_dimension: "xxx", report_markdown: "###..." }
    console.log(`🧠 正在请求后端提取计划，针对短板: [${params.weak_dimension}]`);
    
    const response = await apiClient.post('/api/generate-plan', { 
      weak_dimension: params.weak_dimension,
      report_markdown: params.report_markdown  // 👈 关键：把报告文本传给后端
    });
    
    return response.data;
  } catch (error) {
    console.error('【API 错误】练习计划获取失败:', error);
    throw error;
  }
};
