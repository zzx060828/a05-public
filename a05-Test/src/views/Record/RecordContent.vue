<template>
  <div class="interview-record-page">
    <main class="main-content">
      <h1 class="page-title">面试记录</h1>

      <div class="filter-container">
        <div class="filter-item">
          <label>岗位：</label>
          <select v-model="filters.position">
            <option value="">全部</option>
            <option value="Java后端开发工程师">Java后端开发工程师</option>
            <option value="Python后端开发工程师（AI方向）">Python后端开发工程师（AI方向）</option>
            <option value="Web前端工程师">Web前端工程师</option>
            <option value="AI专属模拟面试">AI专属模拟面试</option>
          </select>
        </div>
        <div class="filter-item">
          <label>状态：</label>
          <select v-model="filters.status">
            <option value="">全部</option>
            <option value="passed">优秀</option>
            <option value="failed">待提高</option>
            <option value="completed">已完成</option>
          </select>
        </div>
        <div class="filter-item">
          <label>难度：</label>
          <select v-model="filters.difficulty">
            <option value="">全部</option>
            <option value="简单">简单</option>
            <option value="中等">中等</option>
            <option value="困难">困难</option>
          </select>
        </div>
        <div class="search-box">
          <input 
            type="text" 
            placeholder="搜索关键词..." 
            v-model="searchKeyword"
            @input="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">
            <svg class="icon" viewBox="0 0 1024 1024"><path d="M212.194304 726.972416c33.760256 33.760256 73.08288 60.269568 116.876288 78.792704 45.357056 19.18464 93.518848 28.911616 143.147008 28.911616s97.788928-9.728 143.145984-28.911616c25.648128-10.848256 49.750016-24.457216 72.112128-40.63744l156.345344 156.484608c6.677504 6.683648 15.43168 10.025984 24.18688 10.025984 8.74496 0 17.490944-3.334144 24.1664-10.00448 13.35808-13.345792 13.36832-34.994176 0.021504-48.35328L739.03616 719.985664c30.533632-32.160768 54.736896-69.082112 71.99744-109.889536 19.183616-45.357056 28.911616-93.518848 28.911616-143.147008s-9.728-97.789952-28.911616-143.147008c-18.523136-43.792384-45.033472-83.115008-78.792704-116.876288-33.76128-33.760256-73.083904-60.270592-116.876288-78.793728-45.35808-19.18464-93.518848-28.911616-143.147008-28.911616s-97.789952 9.728-143.147008 28.911616c-43.793408 18.523136-83.116032 45.033472-116.876288 78.793728s-60.269568 73.083904-78.792704 116.876288c-19.183616 45.357056-28.911616 93.518848-28.911616 143.147008s9.728 97.789952 28.911616 143.147008C151.923712 653.888512 178.434048 693.21216 212.194304 726.972416zM260.547584 255.279104c56.539136-56.539136 131.710976-87.676928 211.670016-87.676928 79.958016 0 155.13088 31.137792 211.670016 87.676928s87.675904 131.710976 87.675904 211.670016S740.425728 622.08 683.887616 678.619136c-56.539136 56.539136-131.712 87.676928-211.670016 87.676928-79.95904 0-155.13088-31.136768-211.670016-87.675904s-87.675904-131.712-87.675904-211.670016S204.008448 311.81824 260.547584 255.279104z" fill="#272636"></path></svg>
          </button>
        </div>
      </div>

      <div v-if="isLoading" style="text-align: center; padding: 50px; color: #666;">
        <p>正在加载历史记录...</p>
      </div>
      <div v-else-if="recordList.length === 0" style="text-align: center; padding: 50px; color: #666;">
        <p>暂无面试记录，快去开启你的第一次面试吧！</p>
      </div>

      <div v-else class="table-card">
        <table class="record-table">
          <thead>
            <tr>
              <th>面试次数</th>
              <th>岗位</th>
              <th>时间</th>
              <th>难度</th>
              <th>面试时长</th>
              <th>综合得分</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedRecords" :key="item.id">
              <td>第 {{ item.round }} 次</td>
              <td>{{ item.job }}</td>
              <td>{{ item.time }}</td>
              <td>
                <span :class="['tag difficulty', `difficulty-${item.levelText}`]">
                  {{ item.levelText }}
                </span>
              </td>
              <td>{{ item.duration }} min</td>
              <td class="score">{{ item.score }}</td>
              <td>
                <span :class="['tag status', `status-${item.status}`]">
                  {{ statusMap[item.status] }}
                </span>
              </td>
              <td>
                <div class="action-cell">
                  <button class="btn-action" @click="viewReport(item.id)">查看报告</button>
                  <button 
                    v-if="item.score < 85" 
                    class="btn-recommend" 
                    @click="showResources(item)"
                    title="获取专属学习资料"
                  >
                    学习资源
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination">
          <div class="info">共 {{ filteredRecords.length }} 条记录</div>
          <div class="pager">
            <button :disabled="currentPage === 1" @click="currentPage--">上一页</button>
            <template v-for="(page, index) in visiblePages" :key="index">
              <span v-if="page === '...'" class="ellipsis">...</span>
              <span v-else
                    :class="['page-num', { active: currentPage === page }]"
                    @click="currentPage = page">
                {{ page }}
              </span>
            </template>
            <button :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
          </div>
        </div>
      </div>
    </main>

    <div v-if="isResourceModalVisible" class="modal-overlay" @click.self="isResourceModalVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📚 专属学习资源推送</h3>
          <button class="close-btn" @click="isResourceModalVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="isResourceLoading" class="loading-state">
            <div class="spinner"></div>
            <p>正在呼叫 AI 检索向量库，为您生成专属秘籍...</p>
          </div>
          <div v-else class="markdown-preview">
            {{ currentResourceMarkdown }}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="isResourceModalVisible = false">确认收到</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from "vue-router";
import { getHistoryReports } from '@/api/interview';

const router = useRouter();

const recordList = ref([]);
const isLoading = ref(true);

const statusMap = { passed: "优秀", failed: "待提高", completed: "已完成" };
const searchKeyword = ref('');
const filters = ref({ position: '', status: '', difficulty: '' });

// 🌟 修改点 3：弹窗的状态控制变量
const isResourceModalVisible = ref(false);
const isResourceLoading = ref(false);
const currentResourceMarkdown = ref('');

const fetchHistoryRecords = async () => {
  try {
    isLoading.value = true;
    const res = await getHistoryReports();
    
    if (res.status === 'success' && res.reports) {
      recordList.value = res.reports.map((report, index) => {
        let parsedContent = {};
        try {
          parsedContent = typeof report.content === 'string' ? JSON.parse(report.content) : (report.content || {});
        } catch (e) {
          console.warn("报告内容解析失败", e);
        }

        const md = parsedContent.report_markdown || "";

        let rawJob = report.job_name || report.position || parsedContent.job_name || parsedContent.position || "";
        const textToSearch = (rawJob + " " + md).toLowerCase();
        let jobStr = "AI专属模拟面试"; 
        if (textToSearch.includes('java')) {
          jobStr = "Java后端开发工程师";
        } else if (textToSearch.includes('python')) {
          jobStr = "Python后端开发工程师（AI方向）";
        } else if (textToSearch.includes('前端') || textToSearch.includes('frontend') || textToSearch.includes('web')) {
          jobStr = "Web前端工程师";
        } else if (textToSearch.includes('后端')) {
          jobStr = "后端开发工程师";
        }

        let avgScore = report.score
          || parsedContent.average_score
          || parsedContent.summary_packet?.averageScore
          || 0;
        if (!avgScore && parsedContent.radar_packet && parsedContent.radar_packet.data && parsedContent.radar_packet.data.length > 0) {
          const scores = parsedContent.radar_packet.data.map(d => d.value).filter(v => v > 0);
          avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
        }
        if (!avgScore) {
          avgScore = parsedContent.match_score || 0;
        }

        let timeStr = "未知时间";
        const rawTime = report.created_at || report.generated_at;
        if (rawTime) {
          const dateObj = new Date(rawTime.includes('T') && !rawTime.includes('Z') ? rawTime + 'Z' : rawTime);
          if (!isNaN(dateObj.getTime())) {
            const yyyy = dateObj.getFullYear();
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            const hh = String(dateObj.getHours()).padStart(2, '0');
            const min = String(dateObj.getMinutes()).padStart(2, '0');
            timeStr = `${yyyy}-${mm}-${dd} ${hh}:${min}`;
          }
        }

        // 使用后端报告中的真实难度
        const rawDifficulty = parsedContent.difficulty || "";
        let levelText = "中等";
        if (rawDifficulty.toLowerCase().includes('easy') || rawDifficulty.includes('简')) { levelText = "简单"; }
        else if (rawDifficulty.toLowerCase().includes('hard') || rawDifficulty.includes('难')) { levelText = "困难"; }

        // 使用后端计算的真实时长
        let duration = parsedContent.duration || report.duration || 0;
        if (!duration) {
          const qCount = parsedContent.content_items?.length || 0;
          duration = qCount > 0 ? Math.max(10, qCount * 4) : 15;
        }

        let finalStatus = "completed";
        if (avgScore >= 85) {
          finalStatus = "passed"; 
        } else {
          finalStatus = "failed"; 
        }

        return {
          id: report.session_id, 
          round: res.reports.length - index, 
          job: jobStr, 
          time: timeStr,
          levelText: levelText,
          duration: duration, 
          score: avgScore, 
          status: finalStatus
        };
      });
    }
  } catch (error) {
    console.error("❌ 获取历史记录失败", error);
  } finally {
    isLoading.value = false;
  }
};

const filteredRecords = computed(() => {
  const keyword = searchKeyword.value.toLowerCase();
  return recordList.value.filter(item => {
    const matchKey = !keyword || item.job.toLowerCase().includes(keyword);
    const matchPos = !filters.value.position || item.job === filters.value.position;
    const matchStatus = !filters.value.status || item.status === filters.value.status;
    const matchDiff = !filters.value.difficulty || item.levelText === filters.value.difficulty;
    return matchKey && matchPos && matchStatus && matchDiff;
  });
});

const currentPage = ref(1);
const pageSize = ref(6);

const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  if (current <= 4) {
    return [1, 2, 3, 4, 5, '...', total];
  }
  if (current >= total - 3) {
    return [1, '...', total - 4, total - 3, total - 2, total - 1, total];
  }
  return [1, '...', current - 1, current, current + 1, '...', total];
});

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredRecords.value.slice(start, start + pageSize.value);
});

const totalPages = computed(() => Math.ceil(filteredRecords.value.length / pageSize.value) || 1);
const handleSearch = () => currentPage.value = 1;

// 💡 核心修改在这里：改为对象形式跳转，并附带 query 参数
function viewReport(sessionId) {
  router.push({
    path: `/report/${sessionId}`,
    query: { from: 'history' }
  });
}

// 🌟 修改点 4：获取 RAG 学习资料并弹窗展示的逻辑
const showResources = (item) => {
  // 直接跳转到新路由，把参数带过去
  router.push({
    name: 'LearningPath',
    params: {
      sessionId: item.id,
      role: item.job
    }
  });
};

onMounted(() => {
  fetchHistoryRecords();
});
</script>

<style scoped>
/* 你的所有原始 CSS 完全保留，未做任何删改 */
.interview-record-page {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background-color: #ffffff;
  min-height: calc(100vh - 120px);
  margin-top: 120px;
}

.main-content {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 24px;
}
.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
  text-align: center;
}

.filter-container {
  background-color: #ffffff;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: nowrap; 
  gap: 12px; 
  align-items: center;
  border: 1px solid #f0f0f0;
}

.filter-item { 
  display: flex; 
  align-items: center; 
  gap: 6px;
  flex-shrink: 0; 
}

.filter-item label { 
  font-size: 14px; 
  color: #374151; 
  white-space: nowrap;
}

.filter-item select {
  appearance: none;
  -webkit-appearance: none;
  padding: 6px 28px 6px 10px; 
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: #fff;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 14px;
  min-width: 120px; 
}

.search-box {
  margin-left: auto; 
  display: flex;
  align-items: center;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
  height: 32px;
  flex-shrink: 1; 
  min-width: 180px;
}

.search-box input {
  border: none;
  outline: none;
  padding: 0 10px;
  height: 100%;
  flex: 1;
  width: 100%;
  font-size: 13px;
}

.search-btn {
  border: none;
  background: #f8f8f8;
  height: 100%;
  width: 30px;
  padding: 0 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.status-passed { background: #d1fae5; color: #065f46; }
.status-failed { background: #fff7ed; color: #9a3412; } 
.status-completed { background: #f3f4f6; color: #4b5563; }

.table-card { background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
.record-table { width: 100%; border-collapse: collapse; }
.record-table th { background-color: #f9fafb; font-weight: 600; text-align: left; padding: 12px 16px; color: #374151; border-bottom: 1px solid #e5e7eb; font-size: 14px; }
.record-table td { padding: 14px 16px; border-bottom: 1px solid #e5e7eb; font-size: 14px; }

/* 之前加的：状态标签强制不换行 */
.tag { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; white-space: nowrap; display: inline-block; }

.difficulty-简单 { background: #dbeafe; color: #1e40af; }
.difficulty-中等 { background: #fef3c7; color: #92400e; }
.difficulty-困难 { background: #fecaca; color: #991b1b; }
.score { color: #3b8dcb; font-weight: 600; font-size: 15px; }

/* 🌟 唯一修改点：给查看报告按钮也加上 white-space: nowrap; */
.btn-action { background: #6b8fc9; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: 0.3s; white-space: nowrap; }
.btn-action:hover { background: #6fb2ec; }

.pagination { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f5f5f5; }
.info { color: #6b7280; font-size: 13px; }
.pager { display: flex; gap: 8px; align-items: center; }
.pager button { padding: 5px 10px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 13px; }
.page-num { padding: 5px 10px; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 13px; }
.page-num.active { background: #5c9cdc; color: white; border-color: #5c9cdc; }
.ellipsis { padding: 0 4px; color: #9ca3af; letter-spacing: 2px; }

/* ======================================================== */
/* 以下为新增样式，用于表格按钮排版和弹窗，绝对不干扰上方样式 */
/* ======================================================== */

/* 操作列并排显示 */
.action-cell {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 提分秘籍按钮，用橙色区分 */
.btn-recommend {
  background: #fff7ed;
  color: #b46236;
  border: 1px solid #fed7aa;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: 0.3s;
  white-space: nowrap; 
}
.btn-recommend:hover {
  background: #ffedd5;
  border-color: #fdba74;
}

/* 弹窗遮罩层 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* 弹窗主体 */
.modal-content {
  background: #ffffff;
  border-radius: 12px;
  width: 560px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modal-fade-in 0.2s ease-out forwards;
}

/* 弹窗头部 */
.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}
.close-btn:hover { color: #4b5563; }

/* 弹窗身体区域 */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
  background-color: #f9fafb;
}

/* Markdown文本预览区 */
.markdown-preview {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  white-space: pre-wrap; 
}

/* 加载动画 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
  font-size: 14px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

/* 弹窗底部 */
.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
}
.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}
.btn-primary:hover { background: #2563eb; }

@keyframes modal-fade-in {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

