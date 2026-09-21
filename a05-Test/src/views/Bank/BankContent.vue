<template>
  <div class="content-hero">
    <div class="content-header">
      <div class="view-toggle">
        <span class="nav-item" :class="{ active: activeTab === 0 }" @click="switchTab(0)">技术知识</span>
        <span class="nav-item" :class="{ active: activeTab === 1 }" @click="switchTab(1)">项目经历深挖</span>
        <span class="nav-item" :class="{ active: activeTab === 2 }" @click="switchTab(2)">场景题</span>
        <span class="nav-item" :class="{ active: activeTab === 3 }" @click="switchTab(3)">行为题</span>
      </div>
    </div>
    
    <div class="filter-bar" v-show="activeTab !== 4">
      <div class="filter-left">
        <span class="filter-label">难度筛选：</span>
        <div class="filter-options">
          <span class="filter-tag" :class="{ active: currentDifficulty === 'all' }" @click="changeDifficulty('all')">全部</span>
          <span class="filter-tag" :class="{ active: currentDifficulty === 'Easy' }" @click="changeDifficulty('Easy')">简单</span>
          <span class="filter-tag" :class="{ active: currentDifficulty === 'Medium' }" @click="changeDifficulty('Medium')">中等</span>
          <span class="filter-tag" :class="{ active: currentDifficulty === 'Hard' }" @click="changeDifficulty('Hard')">困难</span>
        </div>
      </div>

      <div class="search-wrapper">
        <input 
          type="text" 
          class="search-input" 
          v-model="searchQuery" 
          @keyup.enter="handleSearch"
          placeholder="搜索题目、关键字..."
        />
        <button class="search-btn" @click="handleSearch" title="搜索">
          <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="isLoading" style="text-align: center; padding: 40px; color: #666;">
      数据加载中...
    </div>

    <div v-else>
      
      <div v-if="activeTab === 0">
        <div class="articles-grid">
          <div class="pro-card" v-for="(item, i) in techArticles" :key="i" @click="openDrawer(item)">
            <div class="pro-card-header">
              <h3 class="pro-title">{{ item.core_entity || '无标题' }}</h3>
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
              <button class="pro-read-btn">
                查看解析 <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 1" class="project-layout">
        <div class="project-main">
          <template v-if="paginatedProjectList.length > 0">
            <div class="article-detail clickable-card" v-for="(item, i) in paginatedProjectList" :key="i" style="margin-bottom: 20px;" @click="openDrawer(item)">
              <div class="detail-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <h2>{{ item.core_entity || '暂无项目记录' }}</h2>
                  <span class="pro-tag difficulty" :class="(item.difficulty || 'Medium').toLowerCase()" style="font-size: 12px;">
                    {{ item.difficulty === 'Easy' ? '简单' : item.difficulty === 'Hard' ? '困难' : '中等' }}
                  </span>
                </div>
                <div class="favorite-action" @click.stop="toggleFavorite(item)">
                   <svg v-if="item && item.isFavorited" class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                   <svg v-else class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                </div>
              </div>
              <div class="detail-content">
                <p>{{ item.question || item.answer || '暂无详情' }}</p>
              </div>
              
              <div style="display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap;">
                <span class="pro-tag" v-for="(tag, tIndex) in item.tags" :key="tIndex" style="font-size: 12px; padding: 2px 8px; border-radius: 4px; background: #f1f5f9; color: #64748b;">
                  {{ tag }}
                </span>
              </div>
            </div>
          </template>
          <div v-else style="padding: 60px 20px; text-align: center; color: #999;">
            <div style="font-size: 40px; margin-bottom: 12px;">
              <svg t="1775277352279" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4050" width="200" height="200"><path d="M512 858.3168c-194.816 0-352-166.2464-352-370.4832S317.184 117.3504 512 117.3504s352 166.2464 352 370.4832-157.184 370.4832-352 370.4832z m0-64c158.6688 0 288-136.8576 288-306.4832 0-169.6768-129.3312-306.4832-288-306.4832S224 318.1568 224 487.8336c0 169.6256 129.3312 306.4832 288 306.4832zM717.312 799.9488a32 32 0 0 1 46.4896-43.9808l91.4432 96.7168a32 32 0 0 1-46.4896 43.9808l-91.4432-96.768z" fill="#5A5A68" p-id="4051"></path></svg>
            </div>
            未找到匹配的项目深挖题，请尝试更换难度或清空搜索条件
          </div>
        </div>
        
        <div class="project-sidebar">
          <div class="sidebar-section">
            <div class="section-header">相关技术栈</div>
            <div class="action-buttons">
              <button class="action-icon" v-for="(tag, index) in currentProjectTags" :key="index">
                {{ tag }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 2" class="scene-list">
        <div class="scene-item clickable-card" v-for="(item, i) in sceneQuestions" :key="i" @click="openDrawer(item)">
          <div class="scene-title">
            <div style="display:flex; align-items:center;">
              {{ item.core_entity || '无标题' }}
              <span class="pro-tag difficulty" :class="(item.difficulty || 'Medium').toLowerCase()" style="margin-left: 12px; font-size: 12px;">
                {{ item.difficulty === 'Easy' ? '简单' : item.difficulty === 'Hard' ? '困难' : '中等'}}
              </span>
            </div>
            <div class="favorite-action" @click.stop="toggleFavorite(item)">
              <svg v-if="item && item.isFavorited" class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <svg v-else class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
            </div>
          </div>
          <div class="scene-desc">{{ (item.question || '').substring(0, 80) }}...</div>
          <button class="scene-btn orange" @click.stop="openDrawer(item)">查看参考答案</button>
        </div>
      </div>

      <div v-if="activeTab === 3" class="behavior-layout">
        <div class="behavior-item clickable-card" v-for="(item, i) in behaviorQuestions" :key="i" @click="openDrawer(item)">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="behavior-question">Q：{{ item.question }}</div>
            <div class="favorite-action" @click.stop="toggleFavorite(item)">
              <svg v-if="item && item.isFavorited" class="star-icon active" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <svg v-else class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
            </div>
          </div>
          <div class="behavior-answer">A：{{ item.answer }}</div>
        </div>
      </div>

      <div class="pagination" v-if="displayTotalPages > 1">
        <button class="page-btn" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">‹ 上一页</button>
        <button 
          v-for="(p, index) in visiblePages" 
          :key="index"
          class="page-num" 
          :class="{ active: currentPage === p, dots: p === '...' }"
          :disabled="p === '...'"
          @click="p !== '...' && changePage(p)"
        >{{ p }}</button>
        <button class="page-btn" @click="changePage(currentPage + 1)" :disabled="currentPage === displayTotalPages">下一页 ›</button>
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
                <div class="divider">
                  <span>参考解析</span>
                </div>
                <div class="answer-content" style="white-space: pre-wrap; line-height: 1.8;">
                  {{ currentDetail.answer || '暂无解析内容...' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getQuestionBank } from '@/api/bank'

const route = useRoute()
const router = useRouter()

// 1. 响应式状态管理
const activeTab = ref(0)
const isLoading = ref(false)
const currentDifficulty = ref('all') 
const searchQuery = ref('') 

// 分页控制
const currentPage = ref(1)
const pageSize = ref(12) 
const totalPages = ref(1) // 接口返回的总页数

// 数据容器
const techArticles = ref([])
const sceneQuestions = ref([])
const behaviorQuestions = ref([])

// ================= 💡 静态项目深挖数据源 =================
const staticProjectList = [
  // --- Java 领域 ---
  {
    id: 'java-p1',
    category: 'java',
    core_entity: '高并发秒杀系统架构设计',
    difficulty: 'Hard',
    tags: ['Redis', 'RabbitMQ', '分布式锁', 'MySQL'],
    question: '在你的电商秒杀项目中，如何解决超卖问题以及 Redis 集群崩溃时的雪崩效应？',
    answer: '【破题思路】考察高并发场景下的数据一致性与高可用设计。\n\n【核心回答】\n1. 解决超卖：依靠 Redis 的 Lua 脚本保证库存扣减的原子性，配合 RabbitMQ 异步落库。数据库层面在扣减时加上 where stock > 0 的乐观锁兜底。\n2. 雪崩应对：采用多级缓存（Caffeine + Redis）；热点 key 设置永不过期，通过后台任务更新；对接口使用 Sentinel 进行限流降级。'
  },
  {
    id: 'java-p2',
    category: 'java',
    core_entity: '分布式事务最终一致性落地',
    difficulty: 'Medium',
    tags: ['Spring Cloud', 'Seata', '消息队列'],
    question: '在微服务架构下，订单服务与库存服务分离，你们是如何保证跨服务数据一致性的？',
    answer: '【破题思路】考察微服务环境下的事务处理经验。\n\n【核心回答】\n采用基于本地消息表的可靠消息最终一致性方案：\n1. 订单写业务库时，在同一个本地事务写入“消息表”。\n2. 定时任务或 Canal 监听 binlog 推送 MQ。\n3. 库存服务消费 MQ，执行扣减，并记录消费流水保证幂等性。\n极少场景引入 Seata 的 AT 模式。'
  },
  {
    id: 'java-p3',
    category: 'java',
    core_entity: 'JVM 生产环境调优实战',
    difficulty: 'Hard',
    tags: ['JVM', 'GC', '性能监控'],
    question: '讲一次真实的 JVM OOM 或 CPU 飙高排查过程。',
    answer: '【核心回答】\n大促期间某个发券服务频繁 OOM。\n1. 排查：通过 top -Hp 定位异常线程，用 jstat -dump 导出堆快照。\n2. 根因：用 MAT 工具分析发现，某个老旧的 Excel 导出接口被大量调用，全量数据加载导致大对象进入老年代引发 Full GC。\n3. 优化：改为基于游标的流式查询（MyBatis Cursor），限制最大行数。调整 JVM 放大年轻代比例（-Xmn）。'
  },
  {
    id: 'java-p4',
    category: 'java',
    core_entity: 'MySQL 亿级数据分库分表实战',
    difficulty: 'Hard',
    tags: ['MySQL', 'ShardingSphere', '数据库优化'],
    question: '单表数据量千万级别，你们是如何进行平滑的分库分表迁移的？',
    answer: '【核心回答】\n采用“双写+异步校验”方案。\n1. 引入 ShardingSphere-JDBC 按 user_id Hash 分片。\n2. 通过 Canal 订阅老库 binlog，将存量数据同步到新库；开启业务双写（老库为主）。\n3. 编写校验脚本深夜核对数据补偿。\n4. 稳定后将读流量切到新库，停掉老库。'
  },
  {
    id: 'java-p5',
    category: 'java',
    core_entity: 'Redis 缓存穿透与大 Key 处理',
    difficulty: 'Medium',
    tags: ['Redis', '布隆过滤器', '高并发'],
    question: '项目中是如何应对 Redis 缓存穿透以及突然出现的大 Key 问题的？',
    answer: '【核心回答】\n1. 穿透：使用 Redisson 提供的布隆过滤器拦截不存在的非法请求；对少部分穿透的数据缓存空对象（设极短过期时间）。\n2. 大 Key：禁止使用 keys *，大集合数据拆分为多个小 key（如 Hash 分片存储）；定期使用 redis-cli --bigkeys 扫描清理，并在业务侧采用分段读取。'
  },

  // --- Frontend 领域 ---
  {
    id: 'fe-p1',
    category: 'frontend',
    core_entity: '复杂列表的长列表渲染优化',
    difficulty: 'Medium',
    tags: ['Vue3/React', '性能优化', '虚拟列表'],
    question: '遇到过上万条数据的表格渲染卡顿吗？你是如何解决的？',
    answer: '【核心回答】\n1. 虚拟列表：只渲染可视区域内的几十个 DOM，加上缓冲区域防白屏。\n2. 实现：监听 scroll 事件，计算 startIndex 和 endIndex，通过 transform 调整位置。\n3. 数据冻结：使用 Object.freeze() 冻结无需响应式的海量数据，减少 Vue 依赖收集开销。'
  },
  {
    id: 'fe-p2',
    category: 'frontend',
    core_entity: '大型项目首屏秒开优化',
    difficulty: 'Hard',
    tags: ['Webpack/Vite', '前端工程化', '首屏加载'],
    question: '首屏加载很慢，你做了哪些工程化层面上的构建与加载优化？',
    answer: '【核心回答】\n1. 体积压缩：SplitChunks 将 lodash 等单独打包利用强缓存；开启 gzip/brotli。\n2. 按需加载：路由组件动态 import；图片懒加载与 WebP 格式。\n3. 渲染优化：注入骨架屏，非核心 JS 加上 defer/async。最终首屏从 4s 降到 1.2s。'
  },
  {
    id: 'fe-p3',
    category: 'frontend',
    core_entity: '微前端架构落地踩坑',
    difficulty: 'Hard',
    tags: ['qiankun', '微前端', '架构设计'],
    question: '为什么选微前端？使用 qiankun 遇到了哪些样式隔离或状态共享的坑？',
    answer: '【核心回答】\n业务线技术栈不统一，为了独立部署。\n1. 样式污染：默认严格沙箱导致弹窗样式丢失，改用 experimentalStyleIsolation 加前缀，或约定 BEM。\n2. 全局状态：避免直接通信，通过主应用下发 props 或 initGlobalState 维护极少量全局状态。'
  },
  {
    id: 'fe-p4',
    category: 'frontend',
    core_entity: '前端监控与错误上报系统',
    difficulty: 'Medium',
    tags: ['埋点上报', 'Sentry', '性能监控'],
    question: '如何生产环境捕捉白屏或 JS 报错？',
    answer: '【核心回答】\n自研监控 SDK。\n1. 错误捕获：window.onerror 捕获同步错误，unhandledrejection 捕获 Promise 异常，Vue 的 errorHandler。\n2. 上报策略：navigator.sendBeacon 在页面卸载前可靠上报。\n3. 源码映射：SourceMap 传私有服务器，后台还原报错行数。'
  },
  {
    id: 'fe-p5',
    category: 'frontend',
    core_entity: 'Vue3 组合式 API 逻辑复用演进',
    difficulty: 'Easy',
    tags: ['Vue3', 'Composition API', '重构'],
    question: '将 Vue2 项目重构为 Vue3 的过程中，业务逻辑复用的体验有何提升？',
    answer: '【核心回答】\n放弃了容易引起命名冲突和来源不清的 Mixin。全面采用 Composition API (Hooks 模式) 提取通用逻辑（如表格分页加载 useTable、防抖 useDebounce），使得复杂组件内部代码按功能聚合，维护性和 TypeScript 类型推导极其丝滑。'
  },

  // --- Python 领域 ---
  {
    id: 'py-p1',
    category: 'python',
    core_entity: '大语言模型 RAG 应用落地',
    difficulty: 'Hard',
    tags: ['LLM', 'LangChain', '向量数据库'],
    question: '在企业知识库中，如何提升 RAG 检索的准确率？',
    answer: '【核心回答】\n1. 混合检索：关键字搜索 (BM25) 结合向量搜索，通过 RRF 算法重新打分。\n2. 预处理：语义分块 (Semantic Chunking) 并保留父文档元数据。\n3. Query 重写：检索前用小模型对用户的 Query 进行意图扩展。'
  },
  {
    id: 'py-p2',
    category: 'python',
    core_entity: '高并发爬虫与反爬对抗',
    difficulty: 'Medium',
    tags: ['Scrapy', '异步并发', '反爬虫'],
    question: '抓取海量数据时，如何提高效率并绕过风控？',
    answer: '【核心回答】\n1. 并发架构：aiohttp + asyncio 异步协程，结合 Redis 分布式队列。\n2. 代理池：自建动态代理池，请求前检测 IP，强制请求随机抖动。\n3. 突破风控：逆向分析 JS 破解签名；强验证码接入打码平台异步验证。'
  },
  {
    id: 'py-p3',
    category: 'python',
    core_entity: 'FastAPI 高性能接口调优',
    difficulty: 'Medium',
    tags: ['FastAPI', '异步编程', '数据库优化'],
    question: '处理高并发请求时，如何榨干 FastAPI 性能？',
    answer: '【核心回答】\n1. 避免阻塞：不在 async 视图写同步耗时操作，必须同步的库放入线程池 (run_in_threadpool)。\n2. 异步 DB：改用 asyncpg 等异步驱动并配置合理连接池。\n3. 部署：Gunicorn + Uvicorn worker 开启多进程利用多核。'
  },
  {
    id: 'py-p4',
    category: 'python',
    core_entity: '海量数据流处理与内存控制',
    difficulty: 'Hard',
    tags: ['Pandas', '生成器', '内存优化'],
    question: '在 8G 内存服务器上处理 50G 的 CSV 文件，代码该怎么写？',
    answer: '【核心回答】\n以时间换空间。\n1. 纯 Python：使用生成器 yield 逐行读取写入，内存 O(1)。\n2. Pandas：分块读取 chunksize；指定 dtype 降级 (float64 -> float32) 或用 category。\n3. 分布式：使用 Dask 并行计算。'
  },
  {
    id: 'py-p5',
    category: 'python',
    core_entity: 'Celery 分布式任务队列优化',
    difficulty: 'Medium',
    tags: ['Celery', 'Redis', '异步任务'],
    question: '使用 Celery 处理异步邮件发送和报表生成时，如何保证任务不丢失和队列不堆积？',
    answer: '【核心回答】\n1. 不丢失：开启 task_acks_late 让 worker 执行完毕后再应答，配置 Redis/RabbitMQ 作为可靠 broker。\n2. 防堆积：按业务优先级划分多个 Queue，单独分配 worker；对于报表耗时任务设置 soft_time_limit 防止僵死卡死其他任务。'
  }
];

// ===================================================================

// 💡 1. 动态过滤项目数据 (支持 分类 + 难度 + 搜索)
const currentSubjectStr = computed(() => {
  return (route.params && route.params.subject) ? route.params.subject.toLowerCase() : 'all';
});

const filteredProjectList = computed(() => {
  let list = staticProjectList;

  // 分类过滤
  if (currentSubjectStr.value !== 'all') {
    list = list.filter(item => item.category === currentSubjectStr.value);
  }
  // 难度过滤
  if (currentDifficulty.value !== 'all') {
    list = list.filter(item => item.difficulty === currentDifficulty.value);
  }
  // 关键字搜索过滤
  if (searchQuery.value && searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase();
    list = list.filter(item => 
      (item.core_entity && item.core_entity.toLowerCase().includes(q)) || 
      (item.question && item.question.toLowerCase().includes(q))
    );
  }
  
  return list;
});

// 💡 2. 项目深挖分页：根据当前页截取数据（每页 4 条）
const paginatedProjectList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredProjectList.value.slice(start, start + pageSize.value);
});

// 💡 3. 通用计算总页数（如果 tab 是项目深挖，用静态数据的数量算；否则用接口返回的 totalPages）
const displayTotalPages = computed(() => {
  if (activeTab.value === 1) {
    return Math.ceil(filteredProjectList.value.length / pageSize.value) || 1;
  }
  return totalPages.value;
});

// 💡 4. 智能截取侧边栏标签
const currentProjectTags = computed(() => {
  const tagsSet = new Set();
  filteredProjectList.value.forEach(project => {
    if (project.tags) {
      project.tags.forEach(tag => tagsSet.add(tag));
    }
  });
  
  const tagsArray = Array.from(tagsSet);
  // 当题目为“全部”且标签极多时，最多只展示 7 个核心标签，保持版面清爽
  if (currentSubjectStr.value === 'all') {
    return tagsArray.slice(0, 7);
  }
  return tagsArray;
});


// ================= 抽屉组件专属状态与方法 =================
const isDrawerVisible = ref(false)
const currentDetail = ref(null)
const isDetailLoading = ref(false)

const openDrawer = async (item) => {
  if (!item) return
  isDrawerVisible.value = true
  isDetailLoading.value = true
  currentDetail.value = item 
  
  try {
    const historyStr = localStorage.getItem('bank_view_history')
    let history = historyStr ? JSON.parse(historyStr) : []
    if (!Array.isArray(history)) history = []
    
    history = history.filter(h => {
      if (h.id && item.id) return h.id !== item.id
      return h.question !== item.question
    })
    
    history.unshift(item)
    if (history.length > 50) history.pop() 
    localStorage.setItem('bank_view_history', JSON.stringify(history))
  } catch (e) {
    console.error('保存历史记录失败', e)
  }
  
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
  } catch (error) {
    console.error('获取详情失败', error)
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

// 智能分页视图
const visiblePages = computed(() => {
  const total = displayTotalPages.value
  const current = currentPage.value
  
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', total]
  if (current >= total - 3) return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  return [1, '...', current - 1, current, current + 1, '...', total]
})

// 收藏功能
const toggleFavorite = (item) => {
  if (!item) return
  item.isFavorited = !item.isFavorited
  
  try {
    const collectStr = localStorage.getItem('bank_collections')
    let collections = collectStr ? JSON.parse(collectStr) : []
    if (!Array.isArray(collections)) collections = []

    if (item.isFavorited) {
      const exists = collections.find(c => (c.id && c.id === item.id) || (c.question === item.question))
      if (!exists) collections.unshift(item)
    } else {
      collections = collections.filter(c => {
        if (c.id && item.id) return c.id !== item.id
        return c.question !== item.question
      })
    }
    
    localStorage.setItem('bank_collections', JSON.stringify(collections))
  } catch (e) {
    console.error('收藏同步失败', e)
  }
}

const syncFavoritesState = (list) => {
  if (!list || list.length === 0) return
  try {
    const collectStr = localStorage.getItem('bank_collections')
    const collections = collectStr ? JSON.parse(collectStr) : []
    if (!Array.isArray(collections)) return
    
    list.forEach(item => {
      item.isFavorited = collections.some(c => (c.id && c.id === item.id) || (c.question === item.question))
    })
  } catch(e) {}
}

const handleSearch = () => {
  currentPage.value = 1 
  if (activeTab.value !== 4) {
    fetchBankData()
  }
}

// 核心请求逻辑 
const fetchBankData = async () => {
  if (activeTab.value === 4) return 
  
  // 如果是静态项目深挖，跳过网络请求，但依然同步一次本地收藏状态
  if (activeTab.value === 1) {
    syncFavoritesState(filteredProjectList.value);
    return;
  }

  isLoading.value = true
  try {
    const currentSubject = (route.params && route.params.subject) ? route.params.subject : 'all'
    const tabSuffixMap = { 0: 'knowledge', 1: 'project', 2: 'scenario', 3: 'common_behavior' }

    let targetCategory = ''
    if (activeTab.value === 3) targetCategory = 'common_behavior' 
    else if (currentSubject === 'all') targetCategory = tabSuffixMap[activeTab.value] 
    else targetCategory = `${currentSubject}_${tabSuffixMap[activeTab.value]}`

    const params = {
      difficulty: currentDifficulty.value, 
      page: currentPage.value,
      limit: pageSize.value 
    }
    
    if (searchQuery.value && searchQuery.value.trim()) {
      params.keyword = searchQuery.value.trim() 
    }
    if (targetCategory) params.category = targetCategory
    
    const res = await getQuestionBank(params)

    const dataList = res.data || [] 
    syncFavoritesState(dataList)
    const totalCount = res.total || 0 
    
    totalPages.value = Math.ceil(totalCount / pageSize.value) || 1

    if (activeTab.value === 0) techArticles.value = dataList
    else if (activeTab.value === 2) sceneQuestions.value = dataList
    else if (activeTab.value === 3) behaviorQuestions.value = dataList

  } catch (error) {
    console.error('获取题库数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 用户交互事件
const switchTab = (index) => {
  if (activeTab.value === index) return
  activeTab.value = index
  currentPage.value = 1 
  
  // 💡 如果是项目深挖，一页只展示 4 条；其他栏目照常
  if (index === 1) {
    pageSize.value = 4
  } else {
    pageSize.value = index === 0 ? 12 : 10 
  }
  searchQuery.value = '' 
  
  if (index === 4) {
    router.push('/bank/history')
    return 
  }
  fetchBankData()
}

const changeDifficulty = (diff) => {
  if (currentDifficulty.value === diff) return
  currentDifficulty.value = diff
  currentPage.value = 1 
  if (activeTab.value !== 4) fetchBankData()
}

const changePage = (page) => {
  // 💡 使用通用的 displayTotalPages 防止翻页出界
  if (page < 1 || page > displayTotalPages.value || page === currentPage.value) return
  currentPage.value = page
  if (activeTab.value !== 4) fetchBankData()
}

// 生命周期与监听
watch(
  () => route.params?.subject,
  (newSubject, oldSubject) => {
    if (newSubject !== oldSubject && newSubject !== undefined) {
      currentPage.value = 1 
      if (activeTab.value !== 4) fetchBankData()
    }
  }
)

watch(
  () => route.query?.tab,
  (newQuery) => {
    if (newQuery === 'history') {
      switchTab(4)
    }
  }
)

onMounted(() => {
  if (route.query && route.query.tab === 'history') {
    activeTab.value = 4
  } else {
    fetchBankData()
  }
})
</script>

<style scoped>
/* 全局基础 */
.content-hero { padding: 0 24px; background-color: #f5f7fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

/* 顶部导航栏 */
.content-header { display: flex; align-items: center; justify-content: center; margin-bottom: 24px; padding: 15px; }
.view-toggle { display: flex; gap: 80px; background: #b3c7d9; padding: 15px 50px; border-radius: 25px; font-size: 18px; font-weight: bold; color: #6e6e6e; }
.view-toggle .nav-item { position: relative; cursor: pointer; display: inline-block; transition: color 0.5s ease; }
.view-toggle .nav-item::after { content: ''; position: absolute; left: 0; bottom: -2px; width: 0; height: 1px; background-color: #000; transition: width 0.4s ease; }
.view-toggle .nav-item:hover, .view-toggle .nav-item.active { color: #000; text-shadow: 0 0 20px #fff; }
.view-toggle .nav-item:hover::after, .view-toggle .nav-item.active::after { width: 100%; }

/* ================= 难度筛选栏及搜索栏样式 ================= */
.filter-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; background: white; padding: 12px 20px; border-radius: 12px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); }
.filter-left { display: flex; align-items: center; }
.filter-label { color: #64748b; font-size: 15px; font-weight: 600; margin-right: 12px; }
.filter-options { display: flex; gap: 12px; }
.filter-tag { padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; background: #f1f5f9; color: #64748b; transition: all 0.2s ease; }
.filter-tag:hover { background: #e2e8f0; }
.filter-tag.active { background: #639fe0; color: white; }

.search-wrapper { display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 20px; padding: 4px 14px; transition: all 0.3s ease; }
.search-wrapper:focus-within { border-color: #639fe0; background: #fff; box-shadow: 0 0 0 2px rgba(99, 159, 224, 0.1); }
.search-input { border: none; background: transparent; outline: none; font-size: 14px; color: #334155; padding: 4px 8px; width: 220px; transition: width 0.3s ease; }
.search-btn { background: none; border: none; cursor: pointer; color: #94a3b8; display: flex; align-items: center; padding: 2px; }
.search-btn:hover { color: #639fe0; }

/* 收藏按钮通用 */
.favorite-action { padding: 4px; border-radius: 6px; color: #cbd5e1; transition: all 0.2s; cursor: pointer; }
.favorite-action:hover { background: #f1f5f9; color: #94a3b8; }
.star-icon { width: 20px; height: 20px; }
.star-icon.active { color: #f59e0b; }

/* ================= 高级纯文本知识卡片 ================= */
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

/* ================= 2. 项目经历深挖布局 ================= */
.project-layout { display: grid; grid-template-columns: 3fr 1fr; gap: 24px; }
.project-main { width: 100%; }
.project-sidebar { display: flex; flex-direction: column; gap: 16px; }
.sidebar-section { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); }
.section-header { font-weight: 600; margin-bottom: 12px; font-size: 16px; color: #333; }
.action-buttons { display: flex; flex-wrap: wrap; gap: 8px; }
.action-icon { padding: 6px 12px; border: 1px solid #e5e7eb; border-radius: 4px; background: white; cursor: pointer; font-size: 14px; color: #666; }

/* ================= 3. 场景题布局 ================= */
.scene-list { display: flex; flex-direction: column; gap: 16px; }
.scene-item { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); display: flex; justify-content: space-between; align-items: center; }
.scene-title { font-weight: 600; font-size: 16px; color: #333; flex: 1; display: flex; align-items: center; justify-content: space-between; padding-right: 16px;}
.scene-desc { font-size: 14px; color: #666; margin: 0 16px; flex: 2; }
.scene-btn { padding: 8px 16px; border: none; border-radius: 4px; color: white; cursor: pointer; background-color: #68b6d7; transition: background-color 0.3s ease; }
.scene-btn:hover { background-color: #4197af; }

/* ================= 4. 行为题布局 ================= */
.behavior-layout { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); }
.behavior-item { margin-bottom: 12px; padding: 16px; border-bottom: 1px solid #f0f0f0; border-radius: 8px; transition: all 0.3s ease; }
.behavior-item:last-child { margin-bottom: 0; border-bottom: none; }
.behavior-question { font-weight: 600; font-size: 16px; color: #333; margin-bottom: 8px; transition: color 0.3s ease; }
.behavior-answer { font-size: 14px; color: #666; line-height: 1.8; }
.behavior-item.clickable-card:hover { transform: none; border-left: none; background-color: #f8fafc; border-bottom-color: transparent; }
.behavior-item.clickable-card:hover .behavior-question { color: #639fe0; }

/* 通用详情区样式 */
.article-detail { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.detail-header h2 { font-size: 18px; font-weight: 600; margin: 0; color: #333; }
.detail-content { font-size: 14px; line-height: 1.8; color: #333; margin-bottom: 20px; }

/* 可点击卡片的悬浮效果 */
.clickable-card { cursor: pointer; transition: all 0.2s ease; }
.clickable-card:hover { transform: translateX(4px); border-left: 4px solid #639fe0; }

/* ================= 分页器 ================= */
.pagination { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 32px; margin-bottom: 20px; }
.page-btn, .page-num { min-width: 36px; height: 36px; padding: 0 12px; display: flex; align-items: center; justify-content: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; color: #475569; cursor: pointer; transition: all 0.2s ease; }
.page-btn:hover:not(:disabled), .page-num:hover:not(.active):not(.dots) { border-color: #67a3d7; color: #67a3d7; }
.page-num.active { background-color: #67a3d7; color: white; border-color: #67a3d7; font-weight: 600; }
.page-num.dots { border: none; background: transparent; cursor: default; color: #94a3b8; padding: 0 4px; min-width: auto; }
.page-btn:disabled { background-color: #f8fafc; color: #cbd5e1; border-color: #e2e8f0; cursor: not-allowed; }

/* ================= 抽屉(Drawer)专属样式 ================= */
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

/* 响应式适配 */
@media (max-width: 1200px) { .project-layout { grid-template-columns: 1fr; } .scene-item { flex-direction: column; align-items: flex-start; gap: 8px; } }
@media (max-width: 768px) { .view-toggle { gap: 40px; padding: 12px 30px; } .filter-bar { flex-direction: column; align-items: flex-start; gap: 16px; } .search-input { width: 100%; } .drawer-wrapper { width: 100%; } .drawer-content { padding: 20px; } }

.icon{
  width: 100px;
  height: 100px;
}
</style>