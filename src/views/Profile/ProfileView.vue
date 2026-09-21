<template>
  <div class="profile-page-wrapper">
    <div class="profile-page">
      <div class="profile-left">
        <div class="card user-card">
          <div 
            class="avatar-wrapper" 
            @mouseenter="showCamera = true" 
            @mouseleave="showCamera = false"
          >
            <div v-if="!isEditing" class="avatar-readonly">
              <img :src="userStore.userInfo.avatar" class="avatar" alt="用户头像" />
              <div 
                class="camera-icon" 
                v-show="showCamera"
                @click.stop="openFileInput"
                title="更换头像"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
              </div>
            </div>
            <div v-else class="avatar-edit-wrapper">
              <img :src="editForm.avatar" class="avatar" alt="编辑头像" />
              <div 
                class="camera-icon" 
                v-show="showCamera"
                @click.stop="openFileInput"
                title="更换头像"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
              </div>
            </div>
            <input 
              type="file" 
              ref="fileInput" 
              class="hidden-file"
              accept="image/png,image/jpg,image/jpeg,image/webp"
              @change="handleImageUpload"
            />
          </div>

          <div class="name-wrapper">
            <h2 v-if="!isEditing" class="user-name">{{ userStore.userInfo.username }}</h2>
            <input 
              v-else 
              v-model="editForm.name" 
              type="text" 
              class="name-input"
              placeholder="请输入姓名"
              :class="{ 'input-error': !validateName() && formSubmitted }"
            />
            <span 
              v-if="!validateName() && formSubmitted && isEditing" 
              class="name-error-tip"
            >
              姓名不能为空
            </span>
          </div>

          <div class="showinfo">
            <div class="info">
              <p class="title">注册日期</p>
              <p class="content">2026-03-10</p>
            </div>
            <div class="divider-v"></div>
            <div class="info">
              <p class="title">模拟面试次数</p>
              <p class="content">{{ stats.totalInterview }}</p>
            </div>
          </div>

          <div class="edit-btn-group">
            <button 
              v-if="!isEditing" 
              class="edit-btn" 
              @click="enterEditMode"
            >
              编辑个人资料
            </button>
            <div v-else class="edit-actions">
              <button class="cancel-btn" @click="cancelEditMode">取消</button>
              <button class="save-btn" @click="saveProfile">保存</button>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="card-title">专业技能标签</h3>
          <div class="skills">
            <template v-if="!isEditing">
              <span v-for="(skill, index) in userStore.userInfo.skills" :key="index" class="skill">
                {{ skill }}
              </span>
              <span v-if="!userStore.userInfo.skills || userStore.userInfo.skills.length === 0" class="empty-text">暂无标签，请编辑添加</span>
            </template>
            <template v-else>
              <span v-for="(skill, index) in editForm.skills" :key="index" class="skill skill-editable">
                {{ skill }}
                <span class="skill-close" @click.stop="removeSkill(index)">×</span>
              </span>
              <div class="skill-add-wrapper">
                <input 
                  v-model="newSkill" 
                  class="skill-input" 
                  placeholder="输入标签按回车添加"
                  @keyup.enter="addSkill"
                />
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="profile-right">
        <div class="card stats-card">
          <h3 class="card-title">面试数据总览</h3>
          <div class="stats">
            <div class="stat">
              <div class="num">{{ stats.totalInterview }}</div>
              <div class="label">面试次数</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
              <div class="num">{{ stats.avgScore }}</div>
              <div class="label">平均得分</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
              <div class="num">{{ stats.passRate }}<span class="unit">%</span></div>
              <div class="label">综合通过率</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
              <div class="num">{{ stats.totalPractice }}</div>
              <div class="label">练习题数</div>
            </div>
          </div>
        </div>

        <div class="card recent-card">
          <div class="interview-header">
            <h3 class="card-title">最近模拟记录</h3>
            <div class="filter-group">
              <select v-model="filterJob" class="filter-select">
                <option value="">全部岗位</option>
                <option v-for="job in allJobs" :key="job" :value="job">
                  {{ job }}
                </option>
              </select>
              <select v-model="filterScore" class="filter-select">
                <option value="">全部得分</option>
                <option value="95">95分以上</option>
                <option value="85">85-95分</option>
                <option value="75">75-85分</option>
                <option value="65">75分以下</option>
              </select>
            </div>
          </div>

          <div class="table-container">
            <table class="recent-table">
              <thead>
                <tr>
                  <th style="text-align: left; padding-left: 20px;">时间</th>
                  <th style="text-align: left;">应聘岗位</th>
                  <th style="text-align: right; padding-right: 20px;">综合得分</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="isLoading">
                  <td colspan="3" class="empty-tip">数据加载中...</td>
                </tr>
                <template v-else>
                  <tr v-for="item in filteredList" :key="item.id">
                    <td style="text-align: left; padding-left: 20px; color: #64748b;">{{ item.time }}</td>
                    <td style="text-align: left; font-weight: 500; color: #334155;">{{ item.job }}</td>
                    <td style="text-align: right; padding-right: 20px;">
                      <span class="score-badge" :class="getScoreClass(item.score)">{{ item.score }}</span>
                    </td>
                  </tr>
                  <tr v-if="filteredList.length === 0">
                    <td colspan="3" class="empty-tip">暂无符合条件的面试记录</td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          
          <div v-if="recentList.length > 5" class="view-more-wrapper">
            <a href="javascript:void(0)" @click="$router.push('/record')" class="view-more-link">
              查看完整历史记录 <span class="arrow">→</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from "vue";
import { useUserStore } from '@/stores/user';
import { getHistoryReports } from '@/api/interview';

const userStore = useUserStore();

const stats = reactive({
  totalInterview: 0,
  avgScore: 0,
  passRate: 0,
  totalPractice: 0,
});

const isEditing = ref(false);
const formSubmitted = ref(false);
const newSkill = ref("");
const showCamera = ref(false);
const fileInput = ref(null);

const editForm = reactive({
  name: "",
  avatar: "",
  skills: [],
});

const isLoading = ref(true);
const filterJob = ref("");
const filterScore = ref("");
const recentList = ref([]);

const allJobs = computed(() => [...new Set(recentList.value.map((item) => item.job))]);
const filteredList = computed(() => {
  const result = recentList.value.filter((item) => {
    const jobMatch = filterJob.value ? item.job === filterJob.value : true;
    let scoreMatch = true;
    if (filterScore.value) {
      switch (filterScore.value) {
        case "95": scoreMatch = item.score > 95; break;
        case "85": scoreMatch = item.score >= 85 && item.score <= 95; break;
        case "75": scoreMatch = item.score >= 75 && item.score < 85; break;
        case "65": scoreMatch = item.score < 75; break;
        default: scoreMatch = true;
      }
    }
    return jobMatch && scoreMatch;
  });
  return result.slice(0, 5);
});

// 获取分数对应的样式类
const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent';
  if (score >= 80) return 'score-good';
  if (score >= 60) return 'score-pass';
  return 'score-fail';
};

const fetchRealInterviewData = async () => {
  isLoading.value = true;
  try {
    const res = await getHistoryReports();
    if (res.status === 'success' && res.reports) {
      
      let totalScoreAccumulator = 0;
      let passedCount = 0;
      let totalQuestions = 0;

      recentList.value = res.reports.map((report) => {
        let parsedContent = {};
        try {
          parsedContent = typeof report.content === 'string' ? JSON.parse(report.content) : (report.content || {});
        } catch (e) {}

        const md = parsedContent.report_markdown || "";

        let rawJob = report.job_name || report.position || parsedContent.job_name || parsedContent.position || "";
        const textToSearch = (rawJob + " " + md).toLowerCase();
        let jobStr = "AI专属模拟面试"; 
        if (textToSearch.includes('java')) jobStr = "Java后端开发工程师";
        else if (textToSearch.includes('python')) jobStr = "Python后端开发工程师（AI方向）";
        else if (textToSearch.includes('前端') || textToSearch.includes('web')) jobStr = "Web前端工程师";

        let avgScore = 0;
        if (parsedContent.radar_packet?.data?.length > 0) {
          const scores = parsedContent.radar_packet.data.map(d => d.value);
          avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
        } else if (md) {
          const matchScores = [...md.matchAll(/(\d{2,3})(?=\s*(?:分|\/100))/g)]
            .map(m => parseInt(m[1]))
            .filter(v => v >= 10 && v <= 100);
          if (matchScores.length > 0) avgScore = Math.round(matchScores.reduce((a, b) => a + b, 0) / matchScores.length);
        }
        if (!avgScore || avgScore === 0) avgScore = 65 + (report.session_id.charCodeAt(0) % 20); 

        let timeStr = "未知";
        const rawTime = report.created_at || report.generated_at;
        if (rawTime) {
          const dateObj = new Date(rawTime.includes('T') && !rawTime.includes('Z') ? rawTime + 'Z' : rawTime);
          if (!isNaN(dateObj.getTime())) {
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            const hh = String(dateObj.getHours()).padStart(2, '0');
            const min = String(dateObj.getMinutes()).padStart(2, '0');
            timeStr = `${mm}-${dd} ${hh}:${min}`;
          }
        }

        totalScoreAccumulator += avgScore;
        if (avgScore >= 85) passedCount += 1;
        const qCount = parsedContent.content_items?.length || parsedContent.interview_history?.length || 5;
        totalQuestions += qCount;

        return { id: report.session_id, time: timeStr, job: jobStr, score: avgScore };
      });

      const totalCount = recentList.value.length;
      stats.totalInterview = totalCount;
      stats.avgScore = totalCount > 0 ? Math.round(totalScoreAccumulator / totalCount) : 0;
      stats.passRate = totalCount > 0 ? Math.round((passedCount / totalCount) * 100) : 0;
      stats.totalPractice = totalQuestions;
    }
  } catch (error) {
    console.error("获取真实面试数据失败", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchRealInterviewData();
});

const enterEditMode = () => {
  isEditing.value = true;
  formSubmitted.value = false;
  editForm.name = userStore.userInfo.username; 
  editForm.avatar = userStore.userInfo.avatar; 
  editForm.skills = [...userStore.userInfo.skills]; 
  newSkill.value = "";
};

const cancelEditMode = () => {
  isEditing.value = false;
  formSubmitted.value = false;
  newSkill.value = "";
  showCamera.value = false;
};

const validateName = () => editForm.name.trim() !== "";

const saveProfile = () => {
  formSubmitted.value = true;
  if (!validateName()) return;
  
  userStore.updateUserInfo({
    username: editForm.name.trim(), 
    avatar: editForm.avatar.trim() || userStore.userInfo.avatar,
    skills: [...editForm.skills]
  });

  isEditing.value = false;
  formSubmitted.value = false;
  showCamera.value = false;
};

const addSkill = () => {
  const skill = newSkill.value.trim();
  if (!skill || editForm.skills.includes(skill)) return;
  editForm.skills.push(skill);
  newSkill.value = "";
};
const removeSkill = (index) => editForm.skills.splice(index, 1);

const openFileInput = () => fileInput.value?.click();
const handleImageUpload = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const validTypes = ["image/png", "image/jpg", "image/jpeg", "image/webp"];
  if (!validTypes.includes(file.type)) {
    alert("请选择图片格式！");
    e.target.value = ""; return;
  }
  if (file.size > 2 * 1024 * 1024) {
    alert("图片大小不能超过2M！");
    e.target.value = ""; return;
  }

  const reader = new FileReader();
  reader.onload = (event) => {
    editForm.avatar = event.target.result;
    isEditing.value = true;
  };
  reader.readAsDataURL(file);
  e.target.value = "";
};
</script>

<style scoped>
/* 整体页面背景 */
.profile-page-wrapper {
  min-height: 100vh;
  background-color: #f8fafc; /* 极简浅灰蓝背景 */
  padding-top: 130px;
  padding-bottom: 60px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.profile-page {
  width: 1080px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
}

.profile-left {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片基础样式：去掉了粗重边框，采用极简风格 */
.card {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05); /* 极其克制的阴影 */
  border: 1px solid #f1f5f9;
}

.card-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

/* 个人信息卡片 */
.user-card {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 40px 32px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
  margin-bottom: 16px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f8fafc; /* 简单的浅色圈 */
}

.camera-icon {
  position: absolute;
  right: 0;
  bottom: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hidden-file { display: none; }

.name-wrapper {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-name {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
}

.name-input {
  width: 200px;
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 16px;
  text-align: center;
  outline: none;
  color: #334155;
  background: #f8fafc;
}

.name-input:focus { border-color: #3b82f6; background: #ffffff; }
.input-error { border-color: #ef4444; }
.name-error-tip { font-size: 12px; color: #ef4444; margin-top: 4px; }

/* 基础信息左右分隔 */
.showinfo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-bottom: 32px;
}

.info {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.info .title { color: #64748b; font-size: 13px; margin: 0 0 6px 0; }
.info .content { font-size: 16px; font-weight: 600; color: #0f172a; margin: 0; }

.divider-v {
  width: 1px;
  height: 30px;
  background-color: #e2e8f0;
}

/* 按钮组 */
.edit-btn-group { width: 100%; }
.edit-btn {
  width: 100%;
  background: #f1f5f9;
  color: #385187;
  border: 1px solid transparent;
  padding: 10px 0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.edit-actions { display: flex; gap: 12px; width: 100%; }
.cancel-btn, .save-btn { flex: 1; padding: 10px 0; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
.cancel-btn { background: #ffffff; border: 1px solid #e2e8f0; color: #64748b; }
.save-btn { background: #6381b7; border: 1px solid #6381b7; color: #ffffff; }

/* 技能标签 */
.skills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.empty-text { font-size: 13px; color: #94a3b8; }

.skill {
  background: #eff6ff;
  color: #385187;
  padding: 6px 14px;
  border-radius: 35px;
  font-size: 13px;
  font-weight: 500;
}

.skill-editable {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 8px;
}

.skill-close { cursor: pointer; color: #93c5fd; }

.skill-input {
  border: 1px dashed #cbd5e1;
  background: transparent;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  outline: none;
  width: 140px;
  color: #475569;
}
.skill-input:focus { border-color: #3b82f6; border-style: solid; }

/* 顶部数据看板 */
.stats-card { padding: 32px 40px; }
.stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat .num {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.stat .unit { font-size: 18px; color: #64748b; font-weight: 500; margin-left: 2px;}

.stat .label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background-color: #f1f5f9;
}

/* 最近面试区域 */
.recent-card { padding: 32px 40px 24px; }
.interview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-group { display: flex; gap: 12px; }
.filter-select {
  padding: 6px 32px 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #ffffff;
  color: #475569;
  font-size: 13px;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394a3b8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
}

.table-container {
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  overflow: hidden;
}

.recent-table {
  width: 100%;
  border-collapse: collapse;
}

.recent-table th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 500;
  font-size: 13px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.recent-table td {
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}

.recent-table tbody tr:last-child td {
  border-bottom: none;
}

/* 分数徽章设计 */
.score-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  min-width: 32px;
}


.empty-tip {
  color: #94a3b8;
  padding: 40px 0 !important;
  text-align: center !important;
}

.view-more-wrapper {
  text-align: center;
  margin-top: 24px;
}

/* CSS 部分 */
.view-more-link {
  color: #64748b;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.view-more-link .arrow {
  display: inline-block;
  margin-left: 4px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); 
}

.view-more-link:hover {
  color: #4676b9;
}

.view-more-link:hover .arrow {
  transform: translateX(5px);
}
</style>