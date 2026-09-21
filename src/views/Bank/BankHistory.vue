<template>
  <div class="history-page">
    
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack" title="返回题库">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 19l-7-7 7-7"/></svg>
        </button>
        
        <div class="icon-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <div>
          <h1 class="page-title">浏览历史</h1>
          <p class="page-subtitle">温故而知新，这里保存了你最近查看的 {{ localHistory.length }} 道题目</p>
        </div>
      </div>
      <button class="clear-btn" @click="askClearHistory" v-if="localHistory.length > 0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        清空记录
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">拼命加载中...</div>

    <div v-else-if="localHistory.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg t="1775121052251" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="12739" width="200" height="200"><path d="M925.952 744.96H170.24c-20.096 0-36.48-16.256-36.48-36.48V312.32c0-61.568 49.92-111.488 111.488-111.488h605.568c61.568 0 111.488 49.92 111.488 111.488v396.16c0 20.224-16.256 36.48-36.352 36.48z m0 0" fill="#F44336" p-id="12740"></path><path d="M343.552 713.856H190.08c-9.088 0-16.384-7.296-16.384-16.384v-358.4c0-51.456 41.728-93.056 93.184-93.056 51.456 0 93.056 41.728 93.056 93.056v358.4c0 9.088-7.296 16.384-16.384 16.384z m0 25.6" fill="#C62828" p-id="12741"></path><path d="M344.32 713.856H68.608V349.696h291.328v347.008c0 5.632-1.792 8.704-3.968 11.392-2.688 3.328-7.168 5.632-11.648 5.76z m0 0" fill="#F5F5F5" p-id="12742"></path><path d="M68.608 531.84v182.016H344.32c4.608-0.128 8.96-2.432 11.648-5.632 2.304-2.688 4.096-5.888 3.968-11.392V531.84H68.608z m0 0" fill="#D8D8D8" p-id="12743"></path><path d="M359.936 531.712L68.608 713.856V349.696l291.328 182.016z m0 0" fill="#E5E5E5" p-id="12744"></path><path d="M558.336 972.8c-17.152 0-31.104-13.952-31.104-31.104V744.96h62.08v196.736c0.128 17.152-13.696 31.104-30.976 31.104z m-83.072-457.472c10.112 0 18.176-8.192 18.176-18.176V90.752h-23.168c-10.112 0-18.176 8.192-18.176 18.176v388.224c0 10.112 8.192 18.176 18.176 18.176h4.992z m258.816-217.472c10.112 0 18.176-8.192 18.176-18.432V108.8c0-10.112-8.192-18.176-18.176-18.176h-245.76c-20.224 0-36.48 16.384-36.48 36.48v134.272c0 20.224 16.384 36.48 36.48 36.48h245.76z" fill="#FFCA28" p-id="12745"></path></svg>
      </div>
      <h3>暂无浏览记录</h3>
      <p>去题库多逛逛吧，看过的题目会自动出现在这里</p>
      <button @click="goBack" class="go-bank-btn">去刷题</button> 
    </div>

    <div v-else>
      <div class="articles-grid">
        <div class="pro-card" v-for="(item, i) in currentHistoryPageData" :key="i" @click="openDrawer(item)">
          <div class="pro-card-header">
            <h3 class="pro-title">{{ item.core_entity ? item.core_entity : (item.question ? item.question.substring(0, 20) : '无标题') }}</h3>
            <div class="favorite-action" @click.stop="toggleFavorite(item)">
              <svg v-if="item && item.isFavorited" class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <svg v-else class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
            </div>
          </div>
          <div class="pro-desc">{{ (item.question || '').substring(0, 60) }}...</div>
          <div class="pro-card-footer">
            <div class="pro-tags">
              <span class="pro-tag difficulty" :class="(item.difficulty || 'Medium').toLowerCase()">
                {{ item.difficulty === 'Easy' ? '简单' : item.difficulty === 'Hard' ? '困难' : '中等' }}
              </span>
            </div>
            <button class="pro-read-btn">再次复习 <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></button>
          </div>
        </div>
      </div>

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
              <button class="action-btn icon-btn" @click="currentDetail && toggleFavorite(currentDetail)" title="收藏">
                <svg v-if="currentDetail && currentDetail.isFavorited" class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                <svg v-else class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
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
                <div class="divider"><span>参考解析</span></div>
                <div class="answer-content">{{ currentDetail.answer || '暂无解析内容...' }}</div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <Teleport to="body">
      <transition name="modal-fade">
        <div class="confirm-modal-overlay" v-if="isClearModalVisible" @click.self="cancelClearHistory">
          <div class="confirm-modal-box">
            <div class="modal-icon danger">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/>
              </svg>
            </div>
            <h3 class="modal-title">清空浏览记录</h3>
            <p class="modal-desc">确定要清空所有的浏览历史吗？此操作不可恢复。</p>
            <div class="modal-actions">
              <button class="btn-cancel" @click="cancelClearHistory">取消</button>
              <button class="btn-confirm" @click="executeClearHistory">确定清空</button>
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
const localHistory = ref([])
const currentPage = ref(1)
const pageSize = ref(12) 
const isLoading = ref(false)

// 2. 抽屉专属状态
const isDrawerVisible = ref(false)
const currentDetail = ref(null)
const isDetailLoading = ref(false)

// 💡 新增：控制清空确认弹窗的状态
const isClearModalVisible = ref(false)

// 3. 返回上一级路由
const goBack = () => {
  router.push('/bank')
}

// 4. 读取本地历史记录
const loadHistory = () => {
  isLoading.value = true
  try {
    const historyStr = localStorage.getItem('bank_view_history')
    let parsed = historyStr ? JSON.parse(historyStr) : []
    if (!Array.isArray(parsed)) parsed = []
    
    localHistory.value = parsed
  } catch (e) {
    console.error('读取历史记录失败', e)
    localHistory.value = []
  } finally {
    isLoading.value = false
  }
}

// ================== 新增：清空历史弹窗交互 ==================
const askClearHistory = () => {
  isClearModalVisible.value = true
}

const cancelClearHistory = () => {
  isClearModalVisible.value = false
}

const executeClearHistory = () => {
  localStorage.removeItem('bank_view_history')
  localHistory.value = []
  currentPage.value = 1
  isClearModalVisible.value = false // 关闭弹窗
}
// ==========================================================

// 6. 分页逻辑计算
const totalPages = computed(() => Math.ceil(localHistory.value.length / pageSize.value) || 1)

const currentHistoryPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const safeHistory = Array.isArray(localHistory.value) ? localHistory.value : []
  return safeHistory.slice(start, start + pageSize.value)
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

// 7. 交互事件
const toggleFavorite = (item) => {
  if (!item) return
  item.isFavorited = !item.isFavorited
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
  loadHistory()
})
</script>

<style scoped>
/* =========== 页面级基础布局 =========== */
.history-page { padding: 32px 40px; background-color: #f5f7fa; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

/* =========== 独立版头部设计 =========== */
.page-header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 24px 32px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02); margin-bottom: 32px; }
.header-left { display: flex; align-items: center; gap: 20px; }

.back-btn { background: #f1f5f9; border: none; width: 40px; height: 40px; border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; color: #475569; transition: all 0.2s; margin-right: 8px; }
.back-btn:hover { background: #e2e8f0; color: #0f172a; }
.back-btn svg { width: 20px; height: 20px; }

.icon-wrapper { width: 56px; height: 56px; background: #eef2ff; color: #639fe0; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.icon-wrapper svg { width: 28px; height: 28px; }
.page-title { margin: 0 0 4px 0; font-size: 24px; font-weight: 700; color: #1e293b; }
.page-subtitle { margin: 0; font-size: 14px; color: #64748b; }

.clear-btn { display: flex; align-items: center; gap: 8px; background: #fef2f2; color: #ef4444; border: 1px solid #fee2e2; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.clear-btn:hover { background: #fee2e2; border-color: #fca5a5; }
.clear-btn svg { width: 16px; height: 16px; }

/* =========== 空状态设计 =========== */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; background: white; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.empty-icon { font-size: 64px; margin-bottom: 16px; }
.empty-state h3 { font-size: 20px; color: #1e293b; margin: 0 0 8px 0; }
.empty-state p { color: #64748b; margin: 0 0 24px 0; font-size: 15px; }
.go-bank-btn { background: #639fe0; border: none; color: white; cursor: pointer; padding: 10px 24px; border-radius: 8px; font-weight: 500; transition: background 0.2s; font-size: 15px; }
.go-bank-btn:hover { background: #5085c4; }

/* =========== 卡片复用样式 =========== */
.articles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px; }
.pro-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; transition: all 0.3s ease; position: relative; cursor: pointer; }
.pro-card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.06); border-color: #bae6fd; }
.pro-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; }
.pro-title { font-size: 16px; font-weight: 600; color: #1e293b; margin: 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.pro-desc { font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 20px; flex-grow: 1; }
.pro-card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 16px; }
.pro-tags { display: flex; gap: 8px; }
.pro-tag { font-size: 12px; padding: 4px 8px; border-radius: 4px; font-weight: 500; background: #f1f5f9; color: #64748b; }
.pro-tag.easy { color: #10b981; background: #d1fae5; }
.pro-tag.medium { color: #f59e0b; background: #fef3c7; }
.pro-tag.hard { color: #ef4444; background: #fee2e2; }
.pro-read-btn { background: none; border: none; color: #0ea5e9; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 4px; padding: 0; cursor: pointer; transition: gap 0.2s; }
.pro-read-btn .arrow { width: 16px; height: 16px; }
.pro-card:hover .pro-read-btn { gap: 8px; }
.favorite-action { padding: 4px; border-radius: 6px; color: #cbd5e1; transition: all 0.2s; cursor: pointer; }
.favorite-action:hover { background: #f1f5f9; color: #94a3b8; }
.star-icon { width: 20px; height: 20px; }
.star-icon.active { color: #f59e0b; }

/* =========== 分页器 =========== */
.pagination { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 32px; margin-bottom: 20px; }
.page-btn, .page-num { min-width: 36px; height: 36px; padding: 0 12px; display: flex; align-items: center; justify-content: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; color: #475569; cursor: pointer; transition: all 0.2s ease; }
.page-btn:hover:not(:disabled), .page-num:hover:not(.active):not(.dots) { border-color: #67a3d7; color: #67a3d7; }
.page-num.active { background-color: #67a3d7; color: white; border-color: #67a3d7; font-weight: 600; }
.page-num.dots { border: none; background: transparent; cursor: default; color: #94a3b8; padding: 0 4px; min-width: auto; }
.page-btn:disabled { background-color: #f8fafc; color: #cbd5e1; border-color: #e2e8f0; cursor: not-allowed; }

/* =========== 抽屉(Drawer) =========== */
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
.question-box { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #67a3d7; padding: 20px; border-radius: 8px; margin-bottom: 40px; }
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
.modal-icon.danger {
  background: #fee2e2;
  color: #ef4444;
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
  background: #ef4444; 
  color: white;
}
.btn-confirm:hover { background: #dc2626; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: all 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .confirm-modal-box, .modal-fade-leave-to .confirm-modal-box { transform: scale(0.95); opacity: 0; }
/* ======================================================= */

/* 响应式 */
@media (max-width: 768px) {
  .history-page { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; padding: 16px; }
  .drawer-wrapper { width: 100%; }
}
.icon{
  width: 100px;
  height: 100px;
}
</style>