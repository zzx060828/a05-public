<template>
  <div v-if="visible" class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
      <h3>新建面试场次</h3>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>岗位名称 <span class="required">*</span></label>
          <input
            v-model="formData.name"
            type="text"
            placeholder="如：高级Java后端工程师"
            required
          />
        </div>
        <div class="form-group">
          <label>部门</label>
          <input
            v-model="formData.department"
            type="text"
            placeholder="如：技术部"
          />
        </div>
        <div class="form-group">
          <label>关联 RAG 题库</label>
          <div class="select-wrapper">
            <select v-model="formData.ragId">
              <option value="java_v2">Java全栈核心能力库 (V2)</option>
              <option value="fe_v1">大前端工程化题库 (V1)</option>
              <option value="llm_rag">大语言模型与RAG专属库</option>
            </select>
            <svg class="select-arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
        </div>
        <div class="form-group">
          <label>难度</label>
          <div class="select-wrapper">
            <select v-model="formData.difficulty">
              <option value="Easy">初级</option>
              <option value="Medium">中级</option>
              <option value="Hard">高级</option>
            </select>
            <svg class="select-arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
        </div>
        <div class="form-group">
          <label>面试人数上限</label>
          <input
            v-model.number="formData.total"
            type="number"
            min="1"
            max="500"
            placeholder="如：50"
          />
        </div>
        <div class="form-group">
          <label>CMCI 敏感度 (0~1)</label>
          <input
            v-model.number="formData.cmci"
            type="number"
            step="0.05"
            min="0.1"
            max="1.0"
            placeholder="0.85"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeModal">取消</button>
          <button type="submit" class="btn-confirm">确认创建</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'create'])

const formData = reactive({
  name: '',
  department: '',
  ragId: 'java_v2',
  difficulty: 'Medium',
  total: 50,
  cmci: 0.85,
})

const closeModal = () => {
  emit('update:visible', false)
}

const handleSubmit = () => {
  if (!formData.name) return
  emit('create', { ...formData })

  formData.name = ''
  formData.department = ''
  formData.total = 50
  formData.cmci = 0.85
  formData.difficulty = 'Medium'

  closeModal()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.modal-card h3 {
  margin: 0 0 24px;
  font-size: 20px;
  color: #1e293b;
  font-weight: 700;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #475569;
  margin-bottom: 6px;
  font-weight: 500;
}

.required {
  color: #ef4444;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #ff8c42;
  box-shadow: 0 0 0 3px rgba(255, 140, 66, 0.1);
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  width: 100%;
  padding: 10px 36px 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
  appearance: none;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s;
  color: #1e293b;
}

.select-wrapper select:focus {
  border-color: #ff8c42;
  box-shadow: 0 0 0 3px rgba(255, 140, 66, 0.1);
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  flex: 1;
  padding: 10px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-confirm {
  flex: 2;
  padding: 10px;
  background: #ff8c42;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm:hover {
  background: #e67e22;
}
</style>
