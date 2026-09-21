<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { importCheck, importConfirmed } from '@/api'

const props = defineProps({
  visible: { type: Boolean, default: false },
})
const emit = defineEmits(['update:visible', 'success'])

const isChecking = ref(false)
const isSubmitting = ref(false)
const checkReport = ref(null)
const currentFileName = ref('')

const resetModal = () => {
  checkReport.value = null
  isChecking.value = false
  isSubmitting.value = false
  currentFileName.value = ''
}

// Element Plus 的 upload 组件 change 事件回调
const handleFileUpload = async (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return

  currentFileName.value = file.name
  isChecking.value = true

  try {
    const response = await importCheck(file)
    const resData = response.data
    if (resData.status === 'success') {
      checkReport.value = resData.data
      checkReport.value.conflict_items.forEach((item) => (item.resolution = 'skip'))
    } else {
      alert('查重失败：' + resData.message)
    }
  } catch (error) {
    const msg = error.response?.data?.detail || '网络请求失败，请检查后端服务。'
    alert(msg)
  } finally {
    isChecking.value = false
  }
}

const setAllResolutions = (actionType) => {
  if (!checkReport.value) return
  checkReport.value.conflict_items.forEach((item) => {
    item.resolution = actionType
  })
}

const submitFinalImport = async () => {
  isSubmitting.value = true
  const finalData = {
    valid_items: checkReport.value.valid_items,
    resolved_conflicts: checkReport.value.conflict_items.map((item) => ({
      new_question: item.new_question,
      conflict_with_db: item.conflict_with_db,
      action: item.resolution,
    })),
  }

  try {
    const res = await importConfirmed(finalData)
    if (res.data?.status === 'success') {
      emit('success')
      emit('update:visible', false)
    } else {
      alert('导入失败：' + (res.data?.message || '未知错误'))
    }
  } catch (error) {
    const msg = error.response?.data?.detail || '执行导入失败！'
    alert(msg)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <el-dialog
    title="导入并智能校验题库"
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    width="850px"
    destroy-on-close
    @closed="resetModal"
  >
    <div v-loading="isChecking" element-loading-text="AI 正在进行全库语义比对，请稍候...">
      <div v-if="!checkReport" class="upload-container">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileUpload"
          accept=".json"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">将题库文件拖到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip text-center">
              支持 .json 格式，系统将自动调用 DeepSeek 与向量模型进行语义查重
            </div>
          </template>
        </el-upload>
      </div>

      <div v-if="checkReport" class="report-container">
        <el-alert type="success" :closable="false" class="mb-4">
          <template #title>
            <div class="custom-alert-title">
              <svg
                viewBox="0 0 24 24"
                width="18"
                height="18"
                stroke="#10b981"
                stroke-width="2"
                fill="none"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <span class="title-text">智能查重分析完成</span>
            </div>
          </template>

          <template #default>
            本次共读取 <strong>{{ checkReport.total }}</strong> 题，

            <span style="color: #219e62; font-weight: bold"
              >{{ checkReport.valid_items.length }} 题</span
            >
            可直接导入， 发现相似冲突

            <span style="color: #ef4444; font-weight: bold"
              >{{ checkReport.conflict_items.length }} 题</span
            >。
            <br />

            <span style="color: #94a3b8; font-size: 12px">来源文件: {{ currentFileName }}</span>
          </template>
        </el-alert>

        <div v-if="checkReport.conflict_items.length > 0" class="batch-action-bar">
          <span style="font-size: 14px; font-weight: bold; color: #606266">批量处理冲突：</span>
          <el-button-group>
            <el-button size="small" @click="setAllResolutions('skip')" class="btn-sky-hover"
              >全部跳过</el-button
            >
            <el-button class="btn-sky-hover" size="small" @click="setAllResolutions('overwrite')"
              >全部覆盖</el-button
            >
            <el-button class="btn-sky-hover" size="small" @click="setAllResolutions('keep_both')"
              >全部保留</el-button
            >
          </el-button-group>
        </div>

        <div class="conflict-list">
          <el-card
            v-for="(item, index) in checkReport.conflict_items"
            :key="index"
            shadow="never"
            class="conflict-card"
          >
            <div class="compare-box">
              <div class="side">
                <el-tag type="info" effect="plain" class="mb-2">题库原有题</el-tag>
                <p>{{ item.conflict_with_db }}</p>
              </div>

              <div class="vs-badge">
                <span class="vs-text">相似度</span>
                <span class="vs-score">{{ (item.similarity_score * 100).toFixed(1) }}%</span>
              </div>

              <div class="side">
                <el-tag type="danger" effect="plain" class="mb-2">本次导入题</el-tag>
                <p>{{ item.new_question.question || item.new_question }}</p>
              </div>
            </div>

            <el-divider border-style="dashed" style="margin: 15px 0" />

            <div class="action-bar">
              <span style="font-size: 14px; color: #606266">处理方式：</span>
              <el-radio-group v-model="item.resolution">
                <el-radio class="row-btn" label="skip">跳过 (保留原题)</el-radio>
                <el-radio class="row-btn" label="overwrite">覆盖 (替换原题)</el-radio>
                <el-radio class="row-btn" label="keep_both">均保留 (作为变体)</el-radio>
              </el-radio-group>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer" v-if="checkReport">
        <el-button class="reupload-btn" @click="resetModal">重新上传</el-button>
        <el-button
          class="submit-btn"
          type="primary"
          @click="submitFinalImport"
          :loading="isSubmitting"
        >
          确认执行导入
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>
/* 使用了 Element Plus，CSS 从之前的 150 行直接缩减到不到 50 行！ */
.upload-container {
  padding: 20px;
}

.text-center {
  text-align: center;
}

.mb-4 {
  margin-bottom: 16px;
}

.mb-2 {
  margin-bottom: 8px;
}

.batch-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.conflict-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 5px;
}

.conflict-card {
  margin-bottom: 15px;
  border-color: #e4e7ed;
}

.compare-box {
  display: flex;
  align-items: stretch;
}

.side {
  flex: 1;
  padding: 10px;
}

.side p {
  margin: 0;
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.vs-badge {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 15px;
  border-left: 1px dashed #dcdfe6;
  border-right: 1px dashed #dcdfe6;
  background-color: #fafafa;
}

.vs-text {
  font-size: 12px;
  color: #909399;
}

.vs-score {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
  margin-top: 4px;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 自定义 Alert 标题的样式：让 SVG 和文字垂直居中对齐 */
.custom-alert-title {
  display: flex;
  align-items: center;
  gap: 8px; /* 图标和文字的间距 */
  font-size: 14px;
  font-weight: bold;
  color: #28d39a; /* 标题整体的颜色 */
  margin-bottom: 5px;
}
.title-text {
  color: #303133; /* 让文字保持深灰色，只有图标带颜色 */
}

/* 2. Hover 和 获焦状态：天际青背景，白色文字 */
.btn-sky-hover:hover,
.btn-sky-hover:focus {
  background-color: #e4fcfc !important; /* 这里就是天际青 */
  border-color: #49b6d4 !important;
  color: #49b6d4 !important; /* 强制锁死白字，防止出现奇怪的橘色字 */
}

/* 只需要通过自定义类名，重写底层的 CSS 变量即可 */
.row-btn {
  /* 把这个单选框组的“局部主题色”直接替换成天际青 */
  --el-color-primary: #3eb3c2;
}

.reupload-btn:hover {
  background-color: #d3f4fd !important;
  border-color: #49b6d4 !important;
  color: #3899b4 !important;
}
.submit-btn {
  background: #5baee1;
  border: 1px solid#5baee1;
}
.submit-btn:hover {
  background-color: #2d8fc0;
  border: 1px solid#2d8fc0;
}

/* ==========================================
   🌟 修改 Loading 动画和文字的颜色 (青蓝色)
   ========================================== */
/* 1. 修改旋转圆圈的颜色 (通过 SVG 的 stroke 属性) */
:deep(.el-loading-spinner .path) {
  stroke: #49b6d4 !important;
}

/* 2. 修改下面那行提示文字的颜色 */
:deep(.el-loading-spinner .el-loading-text) {
  color: #49b6d4 !important;
}

:deep(.el-upload__text em) {
  color: #49b6d4 !important; /* 天际青色 */
  font-style: normal; /* 如果你不喜欢默认的斜体，可以加上这行变成正体 */
  font-weight: bold; /* 加粗一点更醒目 */
}

:deep(.el-upload-dragger:hover) {
  border-color: #49b6d4 !important;
}

/* 当文件被拖拽到框上方悬停时的状态 */
:deep(.el-upload-dragger.is-dragover) {
  border-color: #49b6d4 !important;
  background-color: #e4fcfc !important; /* 顺便加个极浅的青色背景，体验极佳 */
}
</style>
