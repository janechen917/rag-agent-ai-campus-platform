<template>
  <div class="quiz-page">
    <el-card v-if="quiz && !quizResult" class="quiz-card">
      <template #header>
        <div class="quiz-header">
          <h2>{{ quiz.title }}</h2>
          <div class="quiz-meta">
            <el-tag>{{ quiz.question_count }}题</el-tag>
            <span v-if="quiz.creator_name">出题人: {{ quiz.creator_name }}</span>
            <span v-if="quiz.end_time">截止: {{ formatDateTime(quiz.end_time) }}</span>
          </div>
        </div>
      </template>

      <div v-if="quiz.has_submitted" class="already-submitted">
        <el-result icon="info" title="您已完成此Quiz" sub-title="每位同学只能提交一次" />
        <el-button @click="router.push('/ai-tutor')">返回AI导师</el-button>
      </div>

      <div v-else>
        <div v-for="(q, idx) in quiz.questions" :key="q.id" class="quiz-question">
          <p class="question-title">{{ idx + 1 }}. {{ q.question_text }}</p>
          <el-radio-group v-model="answers[q.id]">
            <el-radio label="A" style="display:block;margin:8px 0">A. {{ q.option_a }}</el-radio>
            <el-radio label="B" style="display:block;margin:8px 0">B. {{ q.option_b }}</el-radio>
            <el-radio label="C" style="display:block;margin:8px 0">C. {{ q.option_c }}</el-radio>
            <el-radio label="D" style="display:block;margin:8px 0">D. {{ q.option_d }}</el-radio>
          </el-radio-group>
        </div>
        <div class="submit-area">
          <el-button type="primary" size="large" @click="submitQuiz" :loading="isSubmitting">提交答案</el-button>
        </div>
      </div>
    </el-card>

    <!-- 结果 -->
    <el-card v-if="quizResult" class="quiz-card">
      <div class="result-score">
        <el-result
          :icon="quizResult.score >= 60 ? 'success' : 'warning'"
          :title="`得分: ${quizResult.score}分`"
          :sub-title="`正确 ${quizResult.correct_count}/${quizResult.total_questions} 题`"
        />
      </div>
      <el-divider />
      <div v-for="(q, idx) in quizResult.questions" :key="q.id" class="quiz-question">
        <p class="question-title">
          {{ idx + 1 }}. {{ q.question_text }}
          <el-icon v-if="q.is_correct" color="#67C23A"><CircleCheck /></el-icon>
          <el-icon v-else color="#F56C6C"><CircleClose /></el-icon>
        </p>
        <div class="options">
          <p :class="{ correct: q.correct_answer === 'A', wrong: q.your_answer === 'A' && !q.is_correct && q.correct_answer !== 'A' }">A. {{ q.option_a }}</p>
          <p :class="{ correct: q.correct_answer === 'B', wrong: q.your_answer === 'B' && !q.is_correct && q.correct_answer !== 'B' }">B. {{ q.option_b }}</p>
          <p :class="{ correct: q.correct_answer === 'C', wrong: q.your_answer === 'C' && !q.is_correct && q.correct_answer !== 'C' }">C. {{ q.option_c }}</p>
          <p :class="{ correct: q.correct_answer === 'D', wrong: q.your_answer === 'D' && !q.is_correct && q.correct_answer !== 'D' }">D. {{ q.option_d }}</p>
        </div>
        <p class="explanation" v-if="q.explanation">解析: {{ q.explanation }}</p>
      </div>
      <div class="submit-area">
        <el-button @click="router.push('/ai-tutor')">返回AI导师</el-button>
      </div>
    </el-card>

    <el-card v-if="errorMsg" class="quiz-card">
      <el-result icon="error" :title="errorMsg">
        <template #extra>
          <el-button @click="router.push('/ai-tutor')">返回AI导师</el-button>
        </template>
      </el-result>
    </el-card>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const quiz = ref(null)
const answers = ref({})
const quizResult = ref(null)
const isSubmitting = ref(false)
const loading = ref(true)
const errorMsg = ref('')

const formatDateTime = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const loadQuiz = async () => {
  const shareCode = route.params.shareCode
  try {
    const response = await api.get(`/api/ai/quiz/share/${shareCode}/`)
    quiz.value = response.data
  } catch (error) {
    errorMsg.value = error.response?.data?.error || 'Quiz不存在或已截止'
  } finally {
    loading.value = false
  }
}

const submitQuiz = async () => {
  if (!quiz.value) return
  const totalQ = quiz.value.questions?.length || 0
  const answeredQ = Object.keys(answers.value).length
  if (answeredQ < totalQ) {
    try {
      await ElMessageBox.confirm(`您还有 ${totalQ - answeredQ} 题未作答，确定提交吗？`, '提示', { type: 'warning' })
    } catch { return }
  }

  isSubmitting.value = true
  try {
    const response = await api.post(`/api/ai/quiz/${quiz.value.id}/submit/`, { answers: answers.value })
    quizResult.value = response.data
    quiz.value = null
    ElMessage.success(`提交成功！得分: ${response.data.score}分`)
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '提交失败')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadQuiz)
</script>

<style scoped>
.quiz-page {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}
.quiz-card { margin-bottom: 20px; }
.quiz-header h2 { margin: 0 0 8px 0; }
.quiz-meta { display: flex; gap: 12px; align-items: center; font-size: 13px; color: #909399; }
.quiz-question { margin-bottom: 24px; padding: 16px; background: #f9f9fb; border-radius: 8px; }
.question-title { font-weight: bold; margin-bottom: 10px; font-size: 15px; }
.options p { margin: 4px 0; padding: 6px 10px; border-radius: 4px; }
.options p.correct { background: #f0f9eb; color: #67C23A; font-weight: bold; }
.options p.wrong { background: #fef0f0; color: #F56C6C; text-decoration: line-through; }
.explanation { margin-top: 8px; font-size: 12px; color: #909399; font-style: italic; }
.submit-area { text-align: center; margin-top: 20px; }
.result-score { text-align: center; }
.already-submitted { text-align: center; }
.loading-state { text-align: center; padding: 60px 0; color: #909399; }
</style>
