<template>
  <div class="collect-page">
    
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack" title="返回题库">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 19l-7-7 7-7"/></svg>
        </button>
        <div class="icon-wrapper">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
        </div>
        <div>
          <h1 class="page-title">我的收藏</h1>
          <p class="page-subtitle">好记性不如烂笔头，共收藏了 {{ collections.length }} 道精选题</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">拼命加载中...</div>

    <div v-else-if="collections.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg t="1775120948615" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6254" width="200" height="200"><path d="M512 39.384615l169.353846 295.384615 342.646154 63.015385-240.246154 248.123077L827.076923 984.615385l-315.076923-145.723077L196.923077 984.615385l43.323077-334.769231L0 401.723077l342.646154-63.015385L512 39.384615" fill="#F3D958" p-id="6255"></path></svg>
      </div>
      <h3>暂无收藏内容</h3>
      <p>在题库中遇到重点难题，点击卡片右上角的星星即可收藏到这里</p>
      <button @click="goBack" class="go-bank-btn">去题库看看</button> 
    </div>

    <div v-else>
      <transition-group name="list" tag="div" class="articles-grid">
        <div class="pro-card" v-for="item in currentHistoryPageData" :key="item.id || item.question" @click="openDrawer(item)">
          <div class="pro-card-header">
            <h3 class="pro-title">{{ item.core_entity ? item.core_entity : (item.question ? item.question.substring(0, 20) : '无标题') }}</h3>
            <div class="favorite-action" @click.stop="askUnfavorite(item)" title="取消收藏">
              <svg class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
            </div>
          </div>
          
          <div class="pro-desc">{{ (item.question || '').substring(0, 60) }}...</div>
          
          <div class="pro-card-footer">
            <div class="pro-tags">
              <span class="pro-tag difficulty" :class="(item.difficulty || 'Medium').toLowerCase()">
                {{ item.difficulty === 'Easy' ? '简单' : item.difficulty === 'Hard' ? '困难' : '中等' }}
              </span>
            </div>
            <button class="pro-read-btn">深度复习 <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></button>
          </div>
        </div>
      </transition-group>

      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">‹ 上一页</button>
        <button 
          v-for="(p, index) in visiblePages" 
          :key="index"
          class="page-num" 
          :class="{ active: currentPage === p, dots: p === '...' }"
          :disabled="p === '...'"
          @click="p !== '...' && changePage(p)"
        >{{ p }}</button>
        <button class="page-btn" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">下一页 ›</button>
      </div>
    </div>

    <Teleport to="body">
      <transition name="fade">
        <div class="drawer-overlay" v-if="isDrawerVisible" @click="closeDrawer"></div>
      </transition>
      
      <transition name="slide-right">
        <div class="drawer-wrapper" v-if="isDrawerVisible">
          <div class="drawer-header">
            <h2 class="drawer-title">题目解析</h2>
            <div class="drawer-actions">
              <button class="action-btn icon-btn" @click="currentDetail && askUnfavorite(currentDetail)" title="取消收藏">
                <svg class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              </button>
              <button class="action-btn icon-btn" @click="closeDrawer" title="关闭">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
              </button>
            </div>
          </div>

          <div class="drawer-content">
            <div v-if="isDetailLoading" class="loading-state">拼命加载解析中...</div>
            <div v-else-if="currentDetail" class="detail-body">
              <div class="detail-meta">
                <span class="pro-tag difficulty" :class="(currentDetail.difficulty || 'Medium').toLowerCase()">
                  {{ currentDetail.difficulty === 'Easy' ? '简单' : currentDetail.difficulty === 'Hard' ? '困难' : '中等' }}
                </span>
                <h1 class="detail-core">{{ currentDetail.core_entity || '未命名考点' }}</h1>
              </div>

              <div class="question-box">
                <div class="box-label">问题描述</div>
                <div class="box-text">{{ currentDetail.question || '暂无详细描述' }}</div>
              </div>

              <div class="answer-section">
                <div class="divider">
                  <span>参考解析</span>
                </div>
                <div class="answer-content">
                  {{ currentDetail.answer || '暂无解析内容...' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <Teleport to="body">
      <transition name="modal-fade">
        <div class="confirm-modal-overlay" v-if="confirmDialog.visible" @click.self="cancelUnfavorite">
          <div class="confirm-modal-box">
            <div class="modal-icon warning">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            </div>
            <h3 class="modal-title">取消收藏</h3>
            <p class="modal-desc">确定要将这道题从收藏中移除吗？移除后可在题库重新收藏。</p>
            <div class="modal-actions">
              <button class="btn-cancel" @click="cancelUnfavorite">取消</button>
              <button class="btn-confirm" @click="executeUnfavorite">确定移除</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 1. 状态管理
const collections = ref([])
const currentPage = ref(1)
const pageSize = ref(12) 
const isLoading = ref(false)

// 2. 抽屉专属状态
const isDrawerVisible = ref(false)
const currentDetail = ref(null)
const isDetailLoading = ref(false)

// 3. 自定义确认弹窗状态 (新增)
const confirmDialog = ref({
  visible: false,
  targetItem: null
})

// 返回上一页
const goBack = () => {
  router.push('/bank')
}

// 读取收藏记录
const loadCollections = () => {
  isLoading.value = true
  try {
    const collectStr = localStorage.getItem('bank_collections')
    let parsed = collectStr ? JSON.parse(collectStr) : []
    if (!Array.isArray(parsed)) parsed = []
    
    parsed.forEach(item => item.isFavorited = true)
    collections.value = parsed
  } catch (e) {
    console.error('读取收藏失败', e)
    collections.value = []
  } finally {
    isLoading.value = false
  }
}

// ================== 新增：弹窗交互逻辑 ==================
// 唤起确认弹窗
const askUnfavorite = (item) => {
  if (!item) return
  confirmDialog.value = {
    visible: true,
    targetItem: item
  }
}

// 取消移除
const cancelUnfavorite = () => {
  confirmDialog.value.visible = false
  setTimeout(() => {
    confirmDialog.value.targetItem = null
  }, 300) // 等待动画结束
}

// 确认执行移除 (原 toggleFavorite 的核心逻辑)
const executeUnfavorite = () => {
  const item = confirmDialog.value.targetItem
  if (!item) return

  // 从列表中过滤掉
  collections.value = collections.value.filter(c => {
    if (c.id && item.id) return c.id !== item.id
    return c.question !== item.question
  })
  
  // 同步到本地存储
  localStorage.setItem('bank_collections', JSON.stringify(collections.value))
  
  // 如果当前页被删空了，并且不是第一页，就往前翻一页
  if (currentHistoryPageData.value.length === 0 && currentPage.value > 1) {
    currentPage.value--
  }
  
  // 如果是在抽屉里取消收藏的，顺便把抽屉关了
  if (isDrawerVisible.value && currentDetail.value === item) {
    closeDrawer()
  }

  // 关闭弹窗
  cancelUnfavorite()
}
// =======================================================

// 分页逻辑计算
const totalPages = computed(() => Math.ceil(collections.value.length / pageSize.value) || 1)

const currentHistoryPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const safeList = Array.isArray(collections.value) ? collections.value : []
  return safeList.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', total]
  if (current >= total - 3) return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  return [1, '...', current - 1, current, current + 1, '...', total]
})

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const openDrawer = async (item) => {
  if (!item) return
  isDrawerVisible.value = true
  isDetailLoading.value = true
  currentDetail.value = item 
  
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
  } finally {
    isDetailLoading.value = false
  }
}

const closeDrawer = () => {
  isDrawerVisible.value = false
  setTimeout(() => {
    currentDetail.value = null
  }, 300) 
}

onMounted(() => {
  loadCollections()
})
</script>

<style scoped>
/* 原有样式保持不变 */
.collect-page { padding: 32px 40px; background-color: #f5f7fa; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

.page-header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 24px 32px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02); margin-bottom: 32px; }
.header-left { display: flex; align-items: center; gap: 20px; }

.back-btn { background: #f1f5f9; border: none; width: 40px; height: 40px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; color: #475569; transition: all 0.2s; margin-right: 8px; }
.back-btn:hover { background: #e2e8f0; color: #0f172a; }
.back-btn svg { width: 20px; height: 20px; }

.icon-wrapper { width: 56px; height: 56px; background: #fef3c7; color: #f59e0b; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.icon-wrapper svg { width: 28px; height: 28px; }
.page-title { margin: 0 0 4px 0; font-size: 24px; font-weight: 700; color: #1e293b; }
.page-subtitle { margin: 0; font-size: 14px; color: #64748b; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; background: white; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.empty-icon { font-size: 64px; margin-bottom: 16px; }
.empty-state h3 { font-size: 20px; color: #1e293b; margin: 0 0 8px 0; }
.empty-state p { color: #64748b; margin: 0 0 24px 0; font-size: 15px; }
.go-bank-btn { background: #f59e0b; border: none; color: white; cursor: pointer; padding: 10px 24px; border-radius: 8px; font-weight: 500; transition: background 0.2s; font-size: 15px; }
.go-bank-btn:hover { background: #d97706; }

.list-enter-active, .list-leave-active { transition: all 0.4s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: scale(0.9); }

.articles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px; }
.pro-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; transition: all 0.3s ease; position: relative; cursor: pointer; }
.pro-card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06); border-color: #fde68a; } 
.pro-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; }
.pro-title { font-size: 16px; font-weight: 600; color: #1e293b; margin: 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.pro-desc { font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 20px; flex-grow: 1; }
.pro-card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 16px; }
.pro-tags { display: flex; gap: 8px; }
.pro-tag { font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 500; background: #f1f5f9; color: #64748b; }
.pro-tag.easy { color: #10b981; background: #d1fae5; }
.pro-tag.medium { color: #f59e0b; background: #fef3c7; }
.pro-tag.hard { color: #ef4444; background: #fee2e2; }
.pro-read-btn { background: none; border: none; color: #f59e0b; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 4px; padding: 0; cursor: pointer; transition: gap 0.2s; }
.pro-read-btn .arrow { width: 16px; height: 16px; }
.pro-card:hover .pro-read-btn { gap: 8px; }

.favorite-action { padding: 4px; border-radius: 6px; transition: all 0.2s; cursor: pointer; }
.favorite-action:hover { transform: scale(1.1); }
.star-icon { width: 22px; height: 22px; }
.star-icon.active { color: #f59e0b; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 32px; margin-bottom: 20px; }
.page-btn, .page-num { min-width: 36px; height: 36px; padding: 0 12px; display: flex; align-items: center; justify-content: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; color: #475569; cursor: pointer; transition: all 0.2s ease; }
.page-btn:hover:not(:disabled), .page-num:hover:not(.active):not(.dots) { border-color: #f59e0b; color: #f59e0b; }
.page-num.active { background-color: #f59e0b; color: white; border-color: #f59e0b; font-weight: 600; }
.page-num.dots { border: none; background: transparent; cursor: default; color: #94a3b8; padding: 0 4px; min-width: auto; }
.page-btn:disabled { background-color: #f8fafc; color: #cbd5e1; border-color: #e2e8f0; cursor: not-allowed; }

/* 抽屉(Drawer) */
.drawer-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(2px); z-index: 1000; }
.drawer-wrapper { position: fixed; top: 0; right: 0; bottom: 0; width: 680px; max-width: 100vw; background: #ffffff; box-shadow: -8px 0 30px rgba(0, 0, 0, 0.1); z-index: 1001; display: flex; flex-direction: column; }
.drawer-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f1f5f9; background: #fff; }
.drawer-title { font-size: 18px; font-weight: 600; color: #1e293b; margin: 0; }
.drawer-actions { display: flex; gap: 12px; }
.icon-btn { background: #f8fafc; border: 1px solid transparent; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #64748b; transition: all 0.2s; }
.icon-btn:hover { background: #f1f5f9; color: #0f172a; }
.icon-btn svg { width: 18px; height: 18px; }
.drawer-content { flex: 1; overflow-y: auto; padding: 32px 32px 60px 32px; }
.detail-meta { margin-bottom: 24px; }
.detail-core { font-size: 26px; font-weight: 700; color: #0f172a; margin: 12px 0 0 0; line-height: 1.4; }
.question-box { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin-bottom: 40px; }
.box-label { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 8px; text-transform: uppercase; }
.box-text { font-size: 16px; color: #334155; line-height: 1.6; }
.divider { display: flex; align-items: center; margin-bottom: 24px; }
.divider::before, .divider::after { content: ''; flex: 1; border-top: 1px dashed #cbd5e1; }
.divider span { padding: 0 16px; font-size: 14px; font-weight: 600; color: #94a3b8; }
.answer-content { font-size: 15px; line-height: 1.8; color: #334155; white-space: pre-wrap; }
.loading-state { display: flex; justify-content: center; align-items: center; height: 200px; color: #94a3b8; font-size: 15px; }

/* 动画过渡 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-right-enter-active, .slide-right-leave-active { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(100%); }

/* ================= 新增：确认弹窗样式 ================= */
.confirm-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.confirm-modal-box {
  background: #ffffff;
  width: 360px;
  border-radius: 16px;
  padding: 32px 24px 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  text-align: center;
}
.modal-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-icon.warning {
  background: #fef3c7;
  color: #f59e0b;
}
.modal-icon svg { width: 28px; height: 28px; }
.modal-title { margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #1e293b; }
.modal-desc { margin: 0 0 24px 0; font-size: 14px; color: #64748b; line-height: 1.5; }
.modal-actions {
  display: flex;
  gap: 12px;
}
.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 10px 0;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.btn-cancel {
  background: #f1f5f9;
  color: #475569;
}
.btn-cancel:hover { background: #e2e8f0; color: #0f172a; }
.btn-confirm {
  background: #ef4444; /* 取消收藏带有一点破坏性，用红色更符合心智模型 */
  color: white;
}
.btn-confirm:hover { background: #dc2626; }

/* 弹窗动画 */
.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .confirm-modal-box, .modal-fade-leave-to .confirm-modal-box { transform: scale(0.95); opacity: 0; }
/* ======================================================= */

/* 响应式 */
@media (max-width: 768px) {
  .collect-page { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; padding: 16px; }
  .drawer-wrapper { width: 100%; }
}
.icon{ width: 100px; height: 100px; }
</style>