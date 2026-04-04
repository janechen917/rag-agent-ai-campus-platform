<template>
  <div class="colosseum-page">
    <div class="hero">
      <div class="hero-text">
        <p class="eyebrow">AI COLOSSEUM</p>
        <h1>AI 辩论场</h1>
        <p class="sub">不是考试，是挑战。用课程知识击碎 AI 的有争议立场，打出你的攻击力。</p>
      </div>
      <div class="hero-stats">
        <div class="stat">
          <span class="label">总场次</span>
          <span class="value">{{ summary.total_matches }}</span>
        </div>
        <div class="stat">
          <span class="label">胜场</span>
          <span class="value">{{ summary.wins }}</span>
        </div>
        <div class="stat">
          <span class="label">胜率</span>
          <span class="value">{{ summary.win_rate }}%</span>
        </div>
      </div>
    </div>

    <div class="arena-grid">
      <el-card class="battle-card">
        <template #header>
          <div class="card-title-row">
            <span>竞技场</span>
            <el-button size="small" @click="goBack">返回</el-button>
          </div>
        </template>

        <div class="start-panel" v-if="!currentMatch">
          <el-input v-model="topicInput" placeholder="输入你想挑战的争议话题（可选）" />
          <el-select v-model="courseId" clearable placeholder="关联课程（可选）" style="margin-top: 10px; width: 100%">
            <el-option v-for="course in enrolledCourses" :key="course.id" :label="course.title" :value="course.id" />
          </el-select>
          <el-button type="primary" class="start-btn" :loading="isStarting" @click="startMatch">开始挑战</el-button>
        </div>

        <div v-else class="battle-panel">
          <div class="topic-line">辩题：{{ currentMatch.topic }}</div>
          <div class="claim-box">
            <div class="claim-label">AI 观点</div>
            <div class="claim-text">{{ currentMatch.ai_claim }}</div>
          </div>

          <div class="attack-board">
            <div class="power-main">
              <span>攻击力</span>
              <strong>{{ latestAttack }}</strong>
            </div>
            <el-progress :percentage="latestAttack" :stroke-width="16" :show-text="false" />
            <div class="status-row">
              <el-tag :type="statusTagType(currentMatch.status)">{{ statusLabel(currentMatch.status) }}</el-tag>
              <span>累计攻击力：{{ currentMatch.total_attack }}</span>
              <span>最高攻击力：{{ currentMatch.best_attack }}</span>
            </div>
          </div>

          <el-input
            v-model="argumentInput"
            type="textarea"
            :rows="5"
            :disabled="currentMatch.status !== 'ongoing' || isAttacking"
            placeholder="请用课程知识进行反驳，越具体越有攻击力"
          />
          <div class="attack-actions">
            <el-button type="primary" :loading="isAttacking" :disabled="currentMatch.status !== 'ongoing'" @click="submitAttack">
              发动反驳
            </el-button>
            <el-button @click="startMatch(true)">再开一局</el-button>
            <el-button type="danger" plain :disabled="isAttacking || isStarting" @click="quitMatch">退出本局</el-button>
          </div>

          <div class="battle-log">
            <h3>对战日志</h3>
            <div v-if="!battleRounds.length" class="empty-hint">等待你的第一击...</div>
            <div v-for="round in battleRounds" :key="round.id" class="log-item">
              <div class="log-head">第 {{ round.round_number }} 回合 · 攻击力 {{ round.attack_power }}</div>
              <p><strong>你的反驳：</strong>{{ round.student_argument }}</p>
              <p><strong>AI 反击：</strong>{{ round.ai_counter }}</p>
              <p class="verdict">裁判：{{ round.verdict }}</p>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="badge-card">
        <template #header>
          <span>勋章墙</span>
        </template>

        <div class="badge-list" v-if="badges.length">
          <div class="badge-item" v-for="badge in badges" :key="badge.id">
            <div class="icon">{{ badge.icon }}</div>
            <div>
              <div class="name">{{ badge.title }}</div>
              <div class="desc">{{ badge.description }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="还没有勋章，先赢一局吧" :image-size="70" />

        <el-divider />

        <h4>最近战绩</h4>
        <div class="recent-list" v-if="recentMatches.length">
          <div class="recent-item" v-for="item in recentMatches" :key="item.id">
            <p class="topic">{{ item.topic }}</p>
            <div class="meta">
              <el-tag size="small" :type="statusTagType(item.status)">{{ statusLabel(item.status) }}</el-tag>
              <span>最高攻击力 {{ item.best_attack }}</span>
              <el-button size="small" text type="danger" @click="deleteRecentMatch(item)">删除</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无记录" :image-size="60" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()

const summary = ref({ total_matches: 0, wins: 0, win_rate: 0, average_best_attack: 0, badge_count: 0 })
const badges = ref([])
const recentMatches = ref([])
const enrolledCourses = ref([])

const currentMatch = ref(null)
const battleRounds = ref([])
const latestAttack = ref(0)

const topicInput = ref('')
const courseId = ref(null)
const argumentInput = ref('')

const isStarting = ref(false)
const isAttacking = ref(false)

const statusLabel = (status) => {
  if (status === 'won') return '胜利'
  if (status === 'lost') return '落败'
  return '进行中'
}

const statusTagType = (status) => {
  if (status === 'won') return 'success'
  if (status === 'lost') return 'danger'
  return 'warning'
}

const loadProfile = async () => {
  try {
    const res = await api.get('/api/ai/colosseum/profile/')
    summary.value = res.data.summary || summary.value
    badges.value = res.data.badges || []
    recentMatches.value = res.data.recent_matches || []

    if (res.data.current_match) {
      currentMatch.value = res.data.current_match
      battleRounds.value = res.data.current_match.rounds || []
      latestAttack.value = battleRounds.value.length ? battleRounds.value[battleRounds.value.length - 1].attack_power : 0
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '加载战绩失败')
  }
}

const loadEnrolledCourses = async () => {
  try {
    const res = await api.get('/api/courses/course-enrollments/')
    const enrollments = res.data.results || res.data || []
    enrolledCourses.value = enrollments.map(item => item.course).filter(Boolean)
  } catch (e) {
    console.error(e)
  }
}

const startMatch = async (forceNew = false) => {
  if (isStarting.value) return
  isStarting.value = true
  try {
    if (forceNew) {
      currentMatch.value = null
      battleRounds.value = []
      latestAttack.value = 0
    }
    const payload = {
      topic: topicInput.value.trim() || undefined,
      course_id: courseId.value || undefined
    }
    const res = await api.post('/api/ai/colosseum/match/start/', payload)
    currentMatch.value = {
      id: res.data.match_id,
      topic: res.data.topic,
      ai_claim: res.data.ai_claim,
      status: res.data.status,
      rounds_count: res.data.rounds_count,
      total_attack: res.data.total_attack,
      best_attack: res.data.best_attack
    }
    battleRounds.value = []
    latestAttack.value = 0
    argumentInput.value = ''
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '开局失败')
  } finally {
    isStarting.value = false
  }
}

const submitAttack = async () => {
  const text = argumentInput.value.trim()
  if (text.length < 20) {
    ElMessage.warning('反驳太短，至少 20 字')
    return
  }
  if (!currentMatch.value) {
    ElMessage.warning('请先开始挑战')
    return
  }

  isAttacking.value = true
  try {
    const res = await api.post(`/api/ai/colosseum/match/${currentMatch.value.id}/attack/`, { argument: text })
    const round = {
      id: `${currentMatch.value.id}-${res.data.round_number}`,
      round_number: res.data.round_number,
      student_argument: text,
      ai_counter: res.data.ai_counter,
      attack_power: res.data.attack_power,
      verdict: res.data.verdict
    }
    battleRounds.value.push(round)
    latestAttack.value = res.data.attack_power
    currentMatch.value.status = res.data.match_status
    currentMatch.value.total_attack = res.data.total_attack
    currentMatch.value.best_attack = res.data.best_attack
    argumentInput.value = ''

    if (res.data.gained_badges?.length) {
      const names = res.data.gained_badges.map(b => b.title).join('、')
      ElMessage.success(`获得新勋章：${names}`)
    }

    if (res.data.match_status === 'won') {
      ElMessage.success('你击败了 AI，恭喜获胜！')
      await loadProfile()
    } else if (res.data.match_status === 'lost') {
      ElMessage.warning('本局失败，再来一局吧')
      await loadProfile()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '攻击失败')
  } finally {
    isAttacking.value = false
  }
}

const quitMatch = async () => {
  if (!currentMatch.value) return
  if (currentMatch.value.status !== 'ongoing') {
    currentMatch.value = null
    battleRounds.value = []
    latestAttack.value = 0
    argumentInput.value = ''
    return
  }

  try {
    await api.post(`/api/ai/colosseum/match/${currentMatch.value.id}/quit/`)
    ElMessage.success('已退出当前对战，你可以重新开局')
    currentMatch.value = null
    battleRounds.value = []
    latestAttack.value = 0
    argumentInput.value = ''
    await loadProfile()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '退出失败')
  }
}

const deleteRecentMatch = async (match) => {
  try {
    await ElMessageBox.confirm(
      `确认删除这条战绩吗？\n辩题：${match.topic}`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/api/ai/colosseum/match/${match.id}/delete/`)
    ElMessage.success('战绩已从最近列表移除')

    if (currentMatch.value?.id === match.id) {
      currentMatch.value = null
      battleRounds.value = []
      latestAttack.value = 0
      argumentInput.value = ''
    }

    await loadProfile()
  } catch (e) {
    if (e === 'cancel' || e === 'close') return
    ElMessage.error(e.response?.data?.error || '删除失败')
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  await Promise.all([loadProfile(), loadEnrolledCourses()])
})
</script>

<style scoped>
.colosseum-page {
  --sand: #efe3c4;
  --iron: #2e3138;
  --blood: #ad2f2f;
  --gold: #cf9b2e;
  max-width: 1400px;
  margin: 0 auto;
  padding: 8px;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  background: radial-gradient(circle at 10% 20%, #f5e4bf, #ddc79a 45%, #c8ac75 100%);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 12px 30px rgba(72, 51, 16, 0.22);
}

.eyebrow {
  font-size: 12px;
  letter-spacing: 0.3em;
  color: #6d4e1f;
  margin-bottom: 8px;
}

.hero h1 {
  font-size: 36px;
  color: var(--iron);
  margin-bottom: 8px;
}

.sub {
  color: #4f3a16;
}

.hero-stats {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.stat {
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(110, 81, 28, 0.2);
  border-radius: 14px;
  min-width: 90px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
}

.stat .label {
  font-size: 12px;
  color: #7a5e2e;
}

.stat .value {
  font-size: 26px;
  font-weight: 700;
  color: #2c2f36;
}

.arena-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.battle-card,
.badge-card {
  border-radius: 18px;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.start-btn {
  width: 100%;
  margin-top: 12px;
}

.claim-box {
  background: linear-gradient(135deg, #2e3138, #4f5660);
  color: #fff;
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 12px;
}

.claim-label {
  color: #ffd58a;
  font-size: 12px;
  margin-bottom: 4px;
}

.topic-line {
  font-weight: 700;
  margin-bottom: 10px;
  color: #4f3a16;
}

.attack-board {
  border: 1px solid #eedeb8;
  background: #fffaf0;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.power-main {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.power-main strong {
  color: var(--blood);
  font-size: 28px;
}

.status-row {
  display: flex;
  gap: 10px;
  font-size: 12px;
  margin-top: 8px;
  color: #6c5a33;
  flex-wrap: wrap;
}

.attack-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.battle-log {
  margin-top: 16px;
}

.log-item {
  border-left: 4px solid #d4a141;
  background: #fffaf3;
  border-radius: 10px;
  padding: 10px;
  margin-top: 10px;
}

.log-head {
  font-weight: 700;
  color: #6a4d1f;
  margin-bottom: 6px;
}

.verdict {
  color: #2f4f4f;
}

.badge-item {
  display: flex;
  gap: 10px;
  align-items: center;
  border: 1px solid #efe0ba;
  background: #fff9eb;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 8px;
}

.badge-item .icon {
  font-size: 24px;
}

.badge-item .name {
  font-weight: 700;
  color: #6a4d1f;
}

.badge-item .desc {
  font-size: 12px;
  color: #7d6d45;
}

.recent-item {
  margin-top: 10px;
  padding: 10px;
  border-radius: 10px;
  background: #f7f8fa;
}

.recent-item .topic {
  margin-bottom: 6px;
}

.recent-item .meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

@media (max-width: 960px) {
  .hero {
    flex-direction: column;
  }

  .arena-grid {
    grid-template-columns: 1fr;
  }
}
</style>
