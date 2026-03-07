<template>
  <div class="quiz-page">
    <!-- 答题卡 -->
    <el-card v-if="quiz && !quizResult && !viewingHistory" class="quiz-card">
      <template #header>
        <div class="quiz-header">
          <h2>{{ quiz.title }}</h2>
          <div class="quiz-meta">
            <el-tag>{{ quiz.question_count }}题</el-tag>
            <el-tag type="warning">限{{ quiz.max_attempts || 1 }}次</el-tag>
            <span v-if="quiz.creator_name">出题人: {{ quiz.creator_name }}</span>
            <span v-if="quiz.end_time">截止: {{ formatDateTime(quiz.end_time) }}</span>
            <span v-if="quiz.attempts_used > 0">已答{{ quiz.attempts_used }}次 / 剩余{{ quiz.remaining_attempts }}次</span>
          </div>
        </div>
      </template>

      <!-- 已用完次数 -->
      <div v-if="quiz.remaining_attempts <= 0" class="already-submitted">
        <el-result icon="info" title="答题次数已用完" :sub-title="`您已完成${quiz.attempts_used}次答题（最多${quiz.max_attempts}次）`" />
        <div style="display:flex;gap:10px;justify-content:center">
          <el-button type="primary" @click="loadMySubmissions">查看答题记录</el-button>
          <el-button @click="router.push('/ai-tutor')">返回AI导师</el-button>
        </div>
      </div>

      <!-- 可以答题 -->
      <div v-else>
        <div v-if="quiz.attempts_used > 0" style="margin-bottom:16px">
          <el-alert type="info" :closable="false">
            <template #title>
              您已答过{{ quiz.attempts_used }}次，还可答{{ quiz.remaining_attempts }}次。
              <el-button type="primary" link @click="loadMySubmissions">查看历史答题记录</el-button>
            </template>
          </el-alert>
        </div>
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

    <!-- 提交结果 -->
    <el-card v-if="quizResult && !viewingHistory" class="quiz-card">
      <div class="result-score">
        <el-result
          :icon="quizResult.score >= 60 ? 'success' : 'warning'"
          :title="`得分: ${quizResult.score}分`"
          :sub-title="`正确 ${quizResult.correct_count}/${quizResult.total_questions} 题（第${quizResult.attempt_number}次答题）`"
        />
        <p v-if="quizResult.remaining_attempts > 0" style="color:#909399;font-size:13px">
          还可以再答{{ quizResult.remaining_attempts }}次
        </p>
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
      <div class="submit-area" style="display:flex;gap:10px;justify-content:center">
        <el-button v-if="quizResult.remaining_attempts > 0" type="primary" @click="retryQuiz">再答一次</el-button>
        <el-button @click="loadMySubmissions">查看所有答题记录</el-button>
        <el-button @click="router.push('/ai-tutor')">返回AI导师</el-button>
      </div>
    </el-card>

    <!-- 历史答题记录 -->
    <el-card v-if="viewingHistory" class="quiz-card">
      <template #header>
        <div class="quiz-header">
          <h2>{{ submissionHistory.quiz_title }} — 答题记录</h2>
          <div class="quiz-meta">
            <span>已答{{ submissionHistory.attempts_used }}次 / 最多{{ submissionHistory.max_attempts }}次</span>
            <span v-if="submissionHistory.remaining_attempts > 0">还可答{{ submissionHistory.remaining_attempts }}次</span>
          </div>
        </div>
      </template>

      <el-tabs v-model="historyTab">
        <el-tab-pane
          v-for="(sub, idx) in submissionHistory.submissions"
          :key="sub.id"
          :label="`第${idx + 1}次 (${sub.score}分)`"
          :name="String(idx)"
        >
          <div class="result-score" style="margin-bottom:16px">
            <el-result
              :icon="sub.score >= 60 ? 'success' : 'warning'"
              :title="`得分: ${sub.score}分`"
              :sub-title="`正确 ${sub.correct_count}/${sub.total_questions} 题 · ${formatDateTime(sub.submitted_at)}`"
            />
          </div>
          <div v-for="(q, qIdx) in sub.questions" :key="q.id" class="quiz-question">
            <p class="question-title">
              {{ qIdx + 1 }}. {{ q.question_text }}
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
        </el-tab-pane>
      </el-tabs>

      <div class="submit-area" style="display:flex;gap:10px;justify-content:center;margin-top:20px">
        <el-button v-if="submissionHistory.remaining_attempts > 0" type="primary" @click="retryQuiz">再答一次</el-button>
        <el-button @click="viewingHistory = false; quiz ? null : router.push('/ai-tutor')">
          {{ quiz ? '返回答题' : '返回AI导师' }}
        </el-button>
      </div>
    </el-card>

    <el-card v-if="errorMsg && !quiz && !quizResult && !viewingHistory" class="quiz-card">
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
const viewingHistory = ref(false)
const submissionHistory = ref({ submissions: [] })
const historyTab = ref('0')
const currentQuizId = ref(null)

const formatDateTime = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const loadQuiz = async () => {
  const shareCode = route.params.shareCode
  try {
    const response = await api.get(`/api/ai/quiz/share/${shareCode}/`)
    quiz.value = response.data
    currentQuizId.value = response.data.id
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

const retryQuiz = async () => {
  viewingHistory.value = false
  quizResult.value = null
  answers.value = {}
  loading.value = true
  await loadQuiz()
}

const loadMySubmissions = async () => {
  const qId = currentQuizId.value
  if (!qId) return
  try {
    const response = await api.get(`/api/ai/quiz/${qId}/my-submissions/`)
    submissionHistory.value = response.data
    historyTab.value = '0'
    viewingHistory.value = true
  } catch (error) {
    ElMessage.error('获取答题记录失败')
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
