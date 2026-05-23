<template>
  <div class="ai-tutor">
    <el-card class="chat-container">
      <template #header>
        <div class="header">
          <div class="title">
            <el-icon :size="24"><Cpu /></el-icon>
            <span>AI智能导师</span>
          </div>
          <div class="header-actions">
            <el-tooltip v-if="!isTeacher" :content="aiMode === 'socratic' ? '当前：苏格拉底式引导' : '当前：直接回答模式'" placement="bottom">
              <el-button @click="toggleAiMode" :icon="aiMode === 'socratic' ? 'ChatLineSquare' : 'ChatDotRound'" circle :type="aiMode === 'socratic' ? '' : 'success'" :title="aiMode === 'socratic' ? '切换为直接回答' : '切换为苏格拉底引导'">
                <el-icon v-if="aiMode === 'socratic'"><ChatLineSquare /></el-icon>
                <el-icon v-else><ChatDotRound /></el-icon>
              </el-button>
            </el-tooltip>
            <el-button @click="goBack" :icon="Back" circle title="返回" />
            <el-button @click="clearChat" type="danger" :icon="Delete" circle title="清空对话" />
          </div>
        </div>
      </template>

      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="avatar">
            <el-avatar v-if="message.role === 'user'" :size="40">
              {{ userStore.user?.username?.charAt(0) || 'U' }}
            </el-avatar>
            <el-avatar v-else :size="40" style="background: #333333">
              <el-icon><Cpu /></el-icon>
            </el-avatar>
          </div>
          <div class="content">
            <div class="name">{{ message.role === 'user' ? '你' : 'AI导师' }}</div>
            <div v-if="message.imageUrl" class="message-image">
              <el-image :src="message.imageUrl" fit="contain" :preview-src-list="[message.imageUrl]" style="max-width: 280px; max-height: 200px; border-radius: 8px; margin-bottom: 8px;" />
            </div>
            <div v-if="message.fileName" class="message-file-tag">
              <el-icon><Document /></el-icon>
              <span>{{ message.fileName }}</span>
            </div>
            <div class="text" v-html="formatMessage(message.content)"></div>
            <div v-if="message.sources && message.sources.length" class="rag-sources">
              <el-collapse>
                <el-collapse-item :title="$t('aiTutor.sourcesTitle', { n: message.sources.length })">
                  <div v-for="(src, i) in message.sources" :key="i" class="rag-source-item">
                    <div class="rag-source-meta">
                      <el-icon><Document /></el-icon>
                      <strong>[{{ i + 1 }}]</strong>
                      <span>{{ src.file }}</span>
                      <span v-if="src.page" class="rag-source-page">{{ $t('aiTutor.page') }} {{ src.page }}</span>
                    </div>
                    <div class="rag-source-snippet">{{ src.snippet }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div v-if="message.agentSteps && message.agentSteps.length" class="rag-sources">
              <el-collapse>
                <el-collapse-item :title="$t('aiTutor.agentStepsTitle', { n: message.agentSteps.length })">
                  <div v-for="(step, i) in message.agentSteps" :key="i" class="rag-source-item">
                    <div class="rag-source-meta">
                      <el-icon><Cpu /></el-icon>
                      <strong>[{{ i + 1 }}]</strong>
                      <span>{{ step.tool }}</span>
                    </div>
                    <div class="rag-source-snippet">输入: {{ JSON.stringify(step.input) }}</div>
                    <div class="rag-source-snippet">输出: {{ step.output }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div class="time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message assistant">
          <div class="avatar">
            <el-avatar :size="40" style="background: #333333">
              <el-icon><Cpu /></el-icon>
            </el-avatar>
          </div>
          <div class="content">
            <div class="name">AI导师</div>
            <div class="loading-container">
              <div class="loading">
                <span></span><span></span><span></span>
              </div>
              <div class="loading-text">AI正在思考中，请稍候...</div>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="suggestions" v-if="messages.length === 0">
          <el-tag
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="sendMessage(suggestion)"
            class="suggestion-tag"
            type="info"
          >
            {{ suggestion }}
          </el-tag>
        </div>
        
        <!-- 学生端课程选择器 -->
        <div v-if="!isTeacher" class="course-selector-bar">
          <el-select
            v-model="selectedCourseId"
            :placeholder="$t('aiTutor.selectCoursePlaceholder')"
            clearable
            style="flex: 1"
            size="default"
          >
            <el-option
              v-for="course in enrolledCourses"
              :key="course.id"
              :label="course.title"
              :value="course.id"
            />
          </el-select>
          <el-tooltip :content="useRagMode ? $t('aiTutor.ragModeOn') : $t('aiTutor.ragModeOff')" placement="top">
            <el-switch
              v-model="useRagMode"
              :disabled="!selectedCourseId || useAgentMode"
              :active-text="$t('aiTutor.courseMaterialMode')"
              size="default"
              style="margin-left: 12px"
            />
          </el-tooltip>
          <el-tooltip :content="useAgentMode ? $t('aiTutor.agentModeOn') : $t('aiTutor.agentModeOff')" placement="top">
            <el-switch
              v-model="useAgentMode"
              :active-text="$t('aiTutor.agentMode')"
              size="default"
              style="margin-left: 12px"
              @change="onAgentModeChange"
            />
          </el-tooltip>
        </div>
        
        <div v-if="uploadedFileInfo" class="image-attachment-bar">
          <el-image v-if="uploadedFileInfo.isImage" :src="uploadedImagePreview" fit="cover" style="width: 48px; height: 48px; border-radius: 6px;" />
          <el-icon v-else :size="32" color="#333333"><Document /></el-icon>
          <span class="attachment-text">{{ uploadedFileInfo.isImage ? '图片' : uploadedFileInfo.name }} 已附加，发送后将一起提交</span>
          <el-button type="danger" :icon="Close" circle size="small" @click="removeImage" />
        </div>
        <div class="input-row">
          <el-input
            v-model="inputMessage"
            :placeholder="uploadedFileInfo ? '请输入关于文件的问题...' : (messages.length === 0 ? '试试问我一个学习问题...' : '输入你的问题...')"
            @keyup.enter="handleSend"
            :disabled="isLoading"
            type="textarea"
            :rows="2"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            @click="handleSend"
            :loading="isLoading"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 侧边栏 - Quiz生成与管理 -->
    <el-card class="sidebar">
      <template #header>
        <div class="sidebar-header">
          <el-icon><Upload /></el-icon>
          <span>{{ isTeacher ? '文件上传 & Quiz生成' : '文件上传 & 历史消息' }}</span>
        </div>
      </template>

      <!-- 教师端：上传PPT生成Quiz -->
      <div v-if="isTeacher" class="quiz-upload-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".ppt,.pptx,.pdf,.doc,.docx,.txt"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          drag
          class="upload-area"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">支持 PPT / PDF / Word / TXT 文件，最大100MB</div>
          </template>
        </el-upload>

        <el-form v-if="selectedFile" class="quiz-settings" label-position="top" size="small">
          <el-form-item label="Quiz标题">
            <el-input v-model="quizForm.title" placeholder="输入Quiz标题" />
          </el-form-item>
          <el-form-item label="题目数量">
            <el-input-number v-model="quizForm.questionCount" :min="1" :max="30" />
          </el-form-item>
          <el-form-item label="答题次数限制">
            <el-input-number v-model="quizForm.maxAttempts" :min="1" :max="99" />
            <div style="font-size: 12px; color: #909399; margin-top: 4px">每位学生最多可答题的次数</div>
          </el-form-item>
          <el-form-item label="截止时间">
            <el-date-picker
              v-model="quizForm.endTime"
              type="datetime"
              placeholder="选择截止时间"
              style="width: 100%"
              :disabled-date="(date) => date < new Date()"
            />
          </el-form-item>
          <el-form-item label="关联课程（可选）">
            <el-select v-model="quizForm.courseId" placeholder="选择课程" clearable style="width: 100%">
              <el-option
                v-for="course in myCourses"
                :key="course.id"
                :label="course.title"
                :value="course.id"
              />
            </el-select>
          </el-form-item>
          <el-button
            type="primary"
            @click="generateQuiz"
            :loading="isGenerating"
            :disabled="!selectedFile"
            style="width: 100%"
          >
            {{ isGenerating ? 'AI生成中...' : '生成Quiz' }}
          </el-button>
        </el-form>

        <el-divider>我的Quiz</el-divider>

        <div v-if="myQuizzes.length > 0" class="quiz-list">
          <div v-for="quiz in myQuizzes" :key="quiz.id" class="quiz-item">
            <div class="quiz-item-header">
              <h4>{{ quiz.title }}</h4>
              <el-tag :type="quiz.is_published ? 'success' : 'info'" size="small">
                {{ quiz.is_published ? '已发布' : '未发布' }}
              </el-tag>
            </div>
            <div class="quiz-item-info">
              <span>{{ quiz.question_count }}题</span>
              <span>限{{ quiz.max_attempts || 1 }}次</span>
              <span v-if="quiz.end_time">截止: {{ formatDateTime(quiz.end_time) }}</span>
              <span>{{ quiz.submission_count || 0 }}人提交</span>
            </div>
            <div class="quiz-item-actions">
              <el-button v-if="!quiz.is_published" type="primary" size="small" @click="showPublishDialog(quiz)">发布</el-button>
              <el-button size="small" @click="copyShareLink(quiz)" :disabled="!quiz.is_published">复制链接</el-button>
              <el-button size="small" @click="viewQuizDetail(quiz)">详情</el-button>
              <el-button v-if="quiz.is_published" size="small" type="warning" @click="sendReminder(quiz)" :loading="quiz._sendingReminder">发送提醒</el-button>
              <el-button size="small" type="danger" @click="deleteQuiz(quiz)">删除</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无Quiz" :image-size="60" />
      </div>

      <!-- 学生端：上传文件 & 历史消息 -->
      <div v-else class="student-upload-section">
        <div class="image-upload-area">
          <el-upload
            ref="imageUploadRef"
            :auto-upload="false"
            :limit="1"
            accept="image/*,.pdf,.ppt,.pptx,.doc,.docx,.txt"
            :on-change="handleImageChange"
            :on-remove="handleImageRemove"
            :show-file-list="false"
            class="image-upload"
          >
            <div v-if="!uploadedFileInfo" class="upload-trigger">
              <el-icon :size="40" color="#909399"><Upload /></el-icon>
              <div class="upload-trigger-text">点击或拖拽上传文件</div>
              <div class="upload-trigger-tip">支持图片 / PDF / PPT / Word / TXT，最大100MB</div>
            </div>
          </el-upload>

          <div v-if="uploadedFileInfo && uploadedFileInfo.isImage" class="image-preview-box">
            <el-image :src="uploadedImagePreview" fit="contain" class="preview-img" :preview-src-list="[uploadedImagePreview]" />
            <el-button type="danger" size="small" @click="removeImage" style="margin-top: 8px; width: 100%">
              <el-icon><Close /></el-icon> 移除文件
            </el-button>
          </div>

          <div v-if="uploadedFileInfo && !uploadedFileInfo.isImage" class="file-preview-box">
            <div class="file-icon-row">
              <el-icon :size="36" color="#333333"><Document /></el-icon>
              <div class="file-meta">
                <div class="file-name">{{ uploadedFileInfo.name }}</div>
                <div class="file-size">{{ uploadedFileInfo.sizeText }}</div>
              </div>
            </div>
            <el-button type="danger" size="small" @click="removeImage" style="margin-top: 8px; width: 100%">
              <el-icon><Close /></el-icon> 移除文件
            </el-button>
          </div>

          <p v-if="uploadedFileInfo" class="upload-hint">
            文件已就绪，请在左侧输入问题后发送
          </p>
        </div>

        <el-divider>历史消息</el-divider>

        <div class="chat-history-list">
          <div v-if="chatHistory.length > 0">
            <div
              v-for="conv in chatHistory"
              :key="conv.id"
              class="history-item"
              @click="loadConversation(conv)"
            >
              <div class="history-title">{{ conv.title }}</div>
              <div class="history-meta">
                <span>{{ conv.messages_count || 0 }}条消息</span>
                <span>{{ formatDateTime(conv.updated_at || conv.created_at) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无历史消息" :image-size="60" />
        </div>
      </div>
    </el-card>

    <!-- Quiz详情对话框（教师端） -->
    <el-dialog v-model="quizDetailVisible" title="Quiz详情" width="800px" top="5vh">
      <div v-if="currentQuizDetail">
        <div class="quiz-detail-header">
          <h3>{{ currentQuizDetail.title }}</h3>
          <div>
            <el-tag>{{ currentQuizDetail.question_count }}题</el-tag>
            <el-tag type="warning" style="margin-left:8px">限{{ currentQuizDetail.max_attempts || 1 }}次</el-tag>
            <el-tag v-if="currentQuizDetail.is_published" type="success" style="margin-left:8px">已发布</el-tag>
            <el-tag v-if="currentQuizDetail.course_title" type="info" style="margin-left:8px">{{ currentQuizDetail.course_title }}</el-tag>
          </div>
          <p v-if="currentQuizDetail.share_code && currentQuizDetail.is_published" class="share-info">
            分享码: <el-tag>{{ currentQuizDetail.share_code }}</el-tag>
            <el-button size="small" text @click="copyShareLink(currentQuizDetail)">复制链接</el-button>
            <el-button size="small" type="warning" @click="sendReminder(currentQuizDetail)" :loading="sendingReminder">发送提醒邮件</el-button>
          </p>
        </div>

        <el-tabs v-model="quizDetailTab">
          <!-- 题目预览 Tab -->
          <el-tab-pane label="题目预览" name="questions">
            <div v-for="(q, idx) in currentQuizDetail.questions" :key="q.id" class="quiz-question-preview">
              <p class="question-title">{{ idx + 1 }}. {{ q.question_text }}</p>
              <div class="question-options">
                <p :class="{ correct: q.correct_answer === 'A' }">A. {{ q.option_a }}</p>
                <p :class="{ correct: q.correct_answer === 'B' }">B. {{ q.option_b }}</p>
                <p :class="{ correct: q.correct_answer === 'C' }">C. {{ q.option_c }}</p>
                <p :class="{ correct: q.correct_answer === 'D' }">D. {{ q.option_d }}</p>
              </div>
              <p class="explanation" v-if="q.explanation">解析: {{ q.explanation }}</p>
            </div>
          </el-tab-pane>

          <!-- 数据分析 Tab -->
          <el-tab-pane label="数据分析" name="statistics">
            <div v-if="quizStats">
              <!-- 总体概览 -->
              <el-row :gutter="16" class="stats-overview">
                <el-col :span="6">
                  <el-statistic title="提交总数" :value="quizStats.total_submissions" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="参与学生" :value="quizStats.unique_students">
                    <template #suffix>人</template>
                  </el-statistic>
                </el-col>
                <el-col :span="6">
                  <el-statistic title="平均分" :value="quizStats.average_score" :precision="1">
                    <template #suffix>分</template>
                  </el-statistic>
                </el-col>
                <el-col :span="6">
                  <el-statistic title="最大答题次数" :value="quizStats.max_attempts">
                    <template #suffix>次</template>
                  </el-statistic>
                </el-col>
              </el-row>

              <!-- 分数分布 -->
              <el-divider>分数分布</el-divider>
              <div class="score-distribution">
                <div v-for="(count, range) in quizStats.score_distribution" :key="range" class="score-bar-row">
                  <span class="score-label">{{ range }}分</span>
                  <el-progress
                    :percentage="quizStats.total_submissions > 0 ? Math.round(count / quizStats.total_submissions * 100) : 0"
                    :stroke-width="20"
                    :color="getScoreColor(range)"
                    :format="() => count + '人'"
                    style="flex:1"
                  />
                </div>
              </div>

              <!-- 每题错误率统计 -->
              <el-divider>每题答题情况</el-divider>
              <el-table :data="quizStats.question_stats" size="small" stripe border>
                <el-table-column label="题号" width="60">
                  <template #default="{ row }">第{{ row.order }}题</template>
                </el-table-column>
                <el-table-column prop="question_text" label="题目" show-overflow-tooltip min-width="200" />
                <el-table-column label="正确答案" width="80" align="center">
                  <template #default="{ row }">{{ row.correct_answer }}</template>
                </el-table-column>
                <el-table-column label="作答人数" width="80" align="center">
                  <template #default="{ row }">{{ row.total_answers }}</template>
                </el-table-column>
                <el-table-column label="正确率" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.correct_rate >= 60 ? 'success' : 'danger'" size="small">{{ row.correct_rate }}%</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="错误率" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.wrong_rate > 40 ? 'danger' : 'info'" size="small">{{ row.wrong_rate }}%</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="选项分布" min-width="200">
                  <template #default="{ row }">
                    <div class="option-dist">
                      <span v-for="opt in ['A','B','C','D']" :key="opt"
                            :class="{ 'correct-opt': opt === row.correct_answer }"
                            class="opt-badge">
                        {{ opt }}: {{ row.option_distribution[opt] }}
                      </span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 学生提交列表 -->
              <el-divider>学生提交记录</el-divider>
              <el-table :data="quizStats.student_submissions" size="small" stripe>
                <el-table-column prop="student_name" label="学生" width="120" />
                <el-table-column label="得分" width="80">
                  <template #default="{ row }">{{ row.score }}分</template>
                </el-table-column>
                <el-table-column label="正确数" width="100">
                  <template #default="{ row }">{{ row.correct_count }}/{{ row.total_questions }}</template>
                </el-table-column>
                <el-table-column label="提交时间">
                  <template #default="{ row }">{{ formatDateTime(row.submitted_at) }}</template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无统计数据" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 发布Quiz对话框 -->
    <el-dialog v-model="publishDialogVisible" title="发布Quiz" width="400px">
      <el-form label-position="top">
        <el-form-item label="选择发布到的课程">
          <el-select v-model="publishCourseId" placeholder="选择课程" clearable style="width:100%">
            <el-option v-for="course in myCourses" :key="course.id" :label="course.title" :value="course.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPublish" :loading="isPublishing">发布</el-button>
      </template>
    </el-dialog>

    <!-- 学生答题对话框 -->
    <el-dialog v-model="quizTakingVisible" :title="currentTakingQuiz?.title || 'Quiz'" width="700px" top="5vh" :close-on-click-modal="false">
      <div v-if="currentTakingQuiz && !quizResult">
        <div v-for="(q, idx) in currentTakingQuiz.questions" :key="q.id" class="quiz-taking-question">
          <p class="question-title">{{ idx + 1 }}. {{ q.question_text }}</p>
          <el-radio-group v-model="studentAnswers[q.id]">
            <el-radio label="A" style="display:block;margin:6px 0">A. {{ q.option_a }}</el-radio>
            <el-radio label="B" style="display:block;margin:6px 0">B. {{ q.option_b }}</el-radio>
            <el-radio label="C" style="display:block;margin:6px 0">C. {{ q.option_c }}</el-radio>
            <el-radio label="D" style="display:block;margin:6px 0">D. {{ q.option_d }}</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div v-if="quizResult" class="quiz-result">
        <div class="result-score">
          <el-result :icon="quizResult.score >= 60 ? 'success' : 'warning'" :title="`得分: ${quizResult.score}分`" :sub-title="`正确 ${quizResult.correct_count}/${quizResult.total_questions} 题`" />
        </div>
        <el-divider />
        <div v-for="(q, idx) in quizResult.questions" :key="q.id" class="quiz-result-question">
          <p class="question-title">
            {{ idx + 1 }}. {{ q.question_text }}
            <el-icon v-if="q.is_correct" color="#67C23A"><CircleCheck /></el-icon>
            <el-icon v-else color="#F56C6C"><CircleClose /></el-icon>
          </p>
          <div class="question-options">
            <p :class="{ correct: q.correct_answer === 'A', wrong: q.your_answer === 'A' && !q.is_correct && q.correct_answer !== 'A' }">A. {{ q.option_a }}</p>
            <p :class="{ correct: q.correct_answer === 'B', wrong: q.your_answer === 'B' && !q.is_correct && q.correct_answer !== 'B' }">B. {{ q.option_b }}</p>
            <p :class="{ correct: q.correct_answer === 'C', wrong: q.your_answer === 'C' && !q.is_correct && q.correct_answer !== 'C' }">C. {{ q.option_c }}</p>
            <p :class="{ correct: q.correct_answer === 'D', wrong: q.your_answer === 'D' && !q.is_correct && q.correct_answer !== 'D' }">D. {{ q.option_d }}</p>
          </div>
          <p class="explanation" v-if="q.explanation">解析: {{ q.explanation }}</p>
        </div>
      </div>
      <template #footer>
        <template v-if="!quizResult">
          <el-button @click="quizTakingVisible = false">取消</el-button>
          <el-button type="primary" @click="submitQuiz" :loading="isSubmitting">提交答案</el-button>
        </template>
        <template v-else>
          <el-button @click="quizTakingVisible = false; quizResult = null">关闭</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { Delete, Promotion, Cpu, Back, Upload, CircleCheck, CircleClose, Picture, Close, Document, ChatLineSquare, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

// --- Chat state ---
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

const suggestions = ref([
  'Python中的列表和元组有什么区别？',
  '如何开始学习前端开发？',
  '解释一下Vue 3的Composition API',
  '什么是RESTful API？'
])

// --- File upload state (Student) ---
const uploadedImageFile = ref(null)
const uploadedImagePreview = ref(null)
const uploadedFileInfo = ref(null)
const imageUploadRef = ref(null)
const chatHistory = ref([])
const enrolledCourses = ref([])
const selectedCourseId = ref(null)
const currentConversationId = ref(null)
const aiMode = ref('socratic') // 'socratic' | 'direct'
const useRagMode = ref(false) // 课程材料模式（基于 RAG 索引回答）
const useAgentMode = ref(false) // 智能助手 Agent 模式（多步工具调用）

// --- Quiz state ---
const isTeacher = computed(() => userStore.user?.user_type === 'teacher')
const selectedFile = ref(null)
const uploadRef = ref(null)
const isGenerating = ref(false)
const myQuizzes = ref([])
const myCourses = ref([])
const availableQuizzes = ref([])
const shareCodeInput = ref('')

const quizForm = reactive({
  title: '',
  questionCount: 5,
  maxAttempts: 1,
  endTime: null,
  courseId: null,
})

const quizDetailVisible = ref(false)
const currentQuizDetail = ref(null)
const quizSubmissions = ref([])
const quizDetailTab = ref('questions')
const quizStats = ref(null)

const publishDialogVisible = ref(false)
const publishCourseId = ref(null)
const publishingQuiz = ref(null)
const isPublishing = ref(false)

const sendingReminder = ref(false)

const quizTakingVisible = ref(false)
const currentTakingQuiz = ref(null)
const studentAnswers = ref({})
const isSubmitting = ref(false)
const quizResult = ref(null)

// --- Chat methods ---
const formatMessage = (content) => marked(content)

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatDateTime = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  })
}

const handleSend = () => {
  if (!inputMessage.value.trim()) return
  sendMessage(inputMessage.value)
}

const sendMessage = async (message) => {
  const hasFile = !!uploadedImageFile.value
  const fileInfo = uploadedFileInfo.value
  const imagePreviewUrl = uploadedImagePreview.value

  messages.value.push({
    role: 'user',
    content: message,
    timestamp: Date.now(),
    imageUrl: (fileInfo?.isImage ? imagePreviewUrl : null),
    fileName: (fileInfo && !fileInfo.isImage) ? fileInfo.name : null
  })
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    let response
    if (useAgentMode.value && !hasFile) {
      // 智能助手 Agent 模式：后端自动调用工具
      response = await api.post('/api/ai/agent/run/', {
        message,
        history: messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))
      })
      const data = response.data || {}
      if (data.code) {
        messages.value.push({
          role: 'assistant',
          content: data.error || t('aiTutor.errors.agentFailed'),
          timestamp: Date.now()
        })
      } else {
        messages.value.push({
          role: 'assistant',
          content: data.output,
          agentSteps: data.steps || [],
          timestamp: Date.now()
        })
      }
    } else if (useRagMode.value && selectedCourseId.value && !hasFile) {
      // 课程材料模式：基于 RAG 索引回答
      response = await api.post('/api/ai/rag/ask/', {
        course_id: selectedCourseId.value,
        question: message
      })
      const data = response.data || {}
      if (data.code === 'NO_INDEX') {
        messages.value.push({
          role: 'assistant',
          content: t('aiTutor.errors.noIndex'),
          timestamp: Date.now()
        })
      } else if (data.code) {
        messages.value.push({
          role: 'assistant',
          content: data.error || t('aiTutor.errors.ragFailed'),
          timestamp: Date.now()
        })
      } else {
        messages.value.push({
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          timestamp: Date.now()
        })
      }
    } else if (aiMode.value === 'socratic' && selectedCourseId.value && !hasFile) {
      // 苏格拉底升级版 Agent：在选定课程的 RAG 知识库里查证 + 反问
      response = await api.post('/api/ai/agent/socratic/', {
        message,
        course_id: selectedCourseId.value,
        history: messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))
      })
      const data = response.data || {}
      if (data.code) {
        messages.value.push({
          role: 'assistant',
          content: data.error || t('aiTutor.errors.agentFailed'),
          timestamp: Date.now()
        })
      } else {
        messages.value.push({
          role: 'assistant',
          content: data.output,
          agentSteps: data.steps || [],
          timestamp: Date.now()
        })
      }
    } else if (hasFile) {
      const formData = new FormData()
      formData.append('message', message)
      formData.append('file', uploadedImageFile.value)
      formData.append('history', JSON.stringify(messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))))
      if (currentConversationId.value) formData.append('conversation_id', currentConversationId.value)
      formData.append('mode', aiMode.value)
      response = await api.post('/api/ai/chat-with-file/', formData, {
        timeout: 120000,
      })
      // Clear file after sending
      uploadedImageFile.value = null
      uploadedImagePreview.value = null
      uploadedFileInfo.value = null
      if (imageUploadRef.value) imageUploadRef.value.clearFiles()
      if (response.data.conversation_id) currentConversationId.value = response.data.conversation_id
      messages.value.push({ role: 'assistant', content: response.data.response, timestamp: Date.now() })
    } else {
      response = await api.post('/api/ai/chat/', {
        message,
        conversation_id: currentConversationId.value || null,
        history: messages.value.slice(-10),
        course_id: selectedCourseId.value || null,
        mode: aiMode.value
      })
      if (response.data.conversation_id) currentConversationId.value = response.data.conversation_id
      messages.value.push({ role: 'assistant', content: response.data.response, timestamp: Date.now() })
    }
  } catch (error) {
    console.error('AI chat error:', error)
    let errorContent = '抱歉，出现了一些问题。'
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      errorContent = '抱歉，AI思考时间过长导致超时。请稍后重试。'
    } else if (error.response) {
      errorContent = error.response.status === 401
        ? '您的登录已过期，请重新登录。'
        : `服务器返回错误 (${error.response.status})，请稍后重试。`
    }
    messages.value.push({ role: 'assistant', content: errorContent, timestamp: Date.now() })
    ElMessage.warning('AI响应失败')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const clearChat = () => {
  messages.value = []
  currentConversationId.value = null
  ElMessage.success('对话已清空')
}

const goBack = () => {
  router.push(userStore.user?.user_type === 'teacher' ? '/teacher-home' : '/student-home')
}

const toggleAiMode = () => {
  aiMode.value = aiMode.value === 'socratic' ? 'direct' : 'socratic'
  ElMessage.info(aiMode.value === 'socratic' ? '已切换为苏格拉底式引导模式' : '已切换为直接回答模式')
}

const onAgentModeChange = (val) => {
  if (val) {
    useRagMode.value = false
  }
}

// --- File upload methods (Student) ---
const allowedTypes = ['image/', '.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt']
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

const handleImageChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  const ext = ('.' + file.name.split('.').pop()).toLowerCase()
  const allowedExts = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt']
  if (!isImage && !allowedExts.includes(ext)) {
    ElMessage.error('仅支持图片 / PDF / PPT / Word / TXT 文件')
    return false
  }
  const isLt100M = file.raw.size / 1024 / 1024 < 100
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过 100MB')
    return false
  }
  uploadedImageFile.value = file.raw
  uploadedFileInfo.value = {
    name: file.name,
    size: file.raw.size,
    sizeText: formatFileSize(file.raw.size),
    isImage,
  }
  if (isImage) {
    uploadedImagePreview.value = URL.createObjectURL(file.raw)
  } else {
    uploadedImagePreview.value = null
  }
}

const handleImageRemove = () => {
  removeImage()
}

const removeImage = () => {
  if (uploadedImagePreview.value) {
    URL.revokeObjectURL(uploadedImagePreview.value)
  }
  uploadedImageFile.value = null
  uploadedImagePreview.value = null
  uploadedFileInfo.value = null
  if (imageUploadRef.value) imageUploadRef.value.clearFiles()
}

const loadChatHistory = async () => {
  try {
    const res = await api.get('/api/ai/conversations/')
    chatHistory.value = res.data.results || res.data || []
  } catch (e) { console.error(e) }
}

const loadConversation = async (conv) => {
  try {
    const res = await api.get(`/api/ai/conversations/${conv.id}/`)
    const convData = res.data
    currentConversationId.value = conv.id
    messages.value = (convData.messages || []).map(m => ({
      role: m.role,
      content: m.content,
      timestamp: new Date(m.created_at).getTime()
    }))
    scrollToBottom()
  } catch (e) { ElMessage.error('加载对话失败') }
}

// --- Quiz methods (Teacher) ---
const handleFileChange = (uploadFile) => {
  // Element Plus el-upload on-change 回调参数是 UploadFile 对象
  // 原始 File 对象在 uploadFile.raw 中
  const rawFile = uploadFile.raw || uploadFile
  if (!rawFile || !(rawFile instanceof File)) {
    console.error('无效的文件对象:', uploadFile)
    ElMessage.warning('文件读取失败，请重新上传')
    return
  }
  selectedFile.value = rawFile
  if (!quizForm.title) {
    quizForm.title = (uploadFile.name || rawFile.name || '').replace(/\.(pptx?|pdf|docx?|txt)$/i, '')
  }
}

const handleFileRemove = () => { selectedFile.value = null }

const generateQuiz = async () => {
  // 验证文件
  if (!selectedFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  // 确保selectedFile是有效的File对象
  if (!(selectedFile.value instanceof File)) {
    console.error('selectedFile不是有效的File对象:', selectedFile.value)
    ElMessage.error('文件格式异常，请重新上传')
    selectedFile.value = null
    if (uploadRef.value) uploadRef.value.clearFiles()
    return
  }

  isGenerating.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value, selectedFile.value.name)
  formData.append('title', quizForm.title || 'Quiz')
  formData.append('question_count', String(quizForm.questionCount))
  formData.append('max_attempts', String(quizForm.maxAttempts))
  if (quizForm.endTime) formData.append('end_time', new Date(quizForm.endTime).toISOString())
  if (quizForm.courseId) formData.append('course_id', String(quizForm.courseId))

  try {
    const response = await api.post('/api/ai/quiz/generate/', formData, {
      timeout: 120000,  // AI生成需要较长时间
    })
    ElMessage.success('Quiz生成成功！')
    selectedFile.value = null
    Object.assign(quizForm, { title: '', questionCount: 5, maxAttempts: 1, endTime: null, courseId: null })
    if (uploadRef.value) uploadRef.value.clearFiles()
    loadMyQuizzes()
    currentQuizDetail.value = response.data
    quizDetailVisible.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'Quiz生成失败，请重试')
  } finally {
    isGenerating.value = false
  }
}

const loadMyQuizzes = async () => {
  try { myQuizzes.value = (await api.get('/api/ai/quiz/my/')).data } catch (e) { console.error(e) }
}

const loadMyCourses = async () => {
  try {
    const res = await api.get('/api/courses/course/my_courses/')
    myCourses.value = res.data.results || res.data || []
  } catch (e) { console.error(e) }
}

const viewQuizDetail = async (quiz) => {
  try {
    const [detailRes, subsRes, statsRes] = await Promise.all([
      api.get(`/api/ai/quiz/${quiz.id}/`),
      api.get(`/api/ai/quiz/${quiz.id}/submissions/`),
      api.get(`/api/ai/quiz/${quiz.id}/statistics/`)
    ])
    currentQuizDetail.value = detailRes.data
    quizSubmissions.value = subsRes.data
    quizStats.value = statsRes.data
    quizDetailTab.value = 'questions'
    quizDetailVisible.value = true
  } catch (e) { ElMessage.error('获取Quiz详情失败') }
}

const getScoreColor = (range) => {
  const colors = { '0-59': '#F56C6C', '60-69': '#E6A23C', '70-79': '#333333', '80-89': '#67C23A', '90-100': '#529b2e' }
  return colors[range] || '#333333'
}

const showPublishDialog = (quiz) => {
  publishingQuiz.value = quiz
  publishCourseId.value = quiz.course || null
  publishDialogVisible.value = true
}

const confirmPublish = async () => {
  if (!publishingQuiz.value) return
  isPublishing.value = true
  try {
    await api.post(`/api/ai/quiz/${publishingQuiz.value.id}/publish/`, { course_id: publishCourseId.value })
    ElMessage.success('Quiz发布成功！')
    publishDialogVisible.value = false
    loadMyQuizzes()
  } catch (e) { ElMessage.error(e.response?.data?.error || '发布失败') }
  finally { isPublishing.value = false }
}

const copyShareLink = (quiz) => {
  const link = `${window.location.origin}/quiz/${quiz.share_code}`
  navigator.clipboard.writeText(link).then(() => {
    ElMessage.success(`链接已复制: ${link}`)
  }).catch(() => {
    ElMessage({ message: `分享链接: ${link}`, type: 'info', duration: 5000 })
  })
}

const sendReminder = async (quiz) => {
  quiz._sendingReminder = true
  sendingReminder.value = true
  try {
    const res = await api.post(`/api/ai/quiz/${quiz.id}/send-reminders/`)
    const { sent, skipped, failed } = res.data
    ElMessage.success(`提醒邮件已发送：成功 ${sent} 人，跳过 ${skipped} 人${failed ? `，失败 ${failed} 人` : ''}`)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '发送提醒邮件失败')
  } finally {
    quiz._sendingReminder = false
    sendingReminder.value = false
  }
}

const deleteQuiz = async (quiz) => {
  try {
    await ElMessageBox.confirm('确定要删除此Quiz吗？', '确认删除', { type: 'warning' })
    await api.delete(`/api/ai/quiz/${quiz.id}/delete/`)
    ElMessage.success('Quiz已删除')
    loadMyQuizzes()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      console.error('删除Quiz失败:', e)
      ElMessage.error(e.response?.data?.error || '删除失败，请稍后重试')
    }
  }
}

// --- Quiz methods (Student) ---
const joinQuizByCode = async () => {
  const code = shareCodeInput.value.trim()
  if (!code) { ElMessage.warning('请输入分享码'); return }
  try {
    const response = await api.get(`/api/ai/quiz/share/${code}/`)
    currentTakingQuiz.value = response.data
    studentAnswers.value = {}
    quizResult.value = null
    quizTakingVisible.value = true
    shareCodeInput.value = ''
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Quiz不存在或已截止') }
}

const loadAvailableQuizzes = async () => {
  try {
    const enrollRes = await api.get('/api/courses/course-enrollments/')
    const courses = enrollRes.data.results || enrollRes.data || []
    const allQuizzes = []
    for (const enrollment of courses) {
      const courseId = enrollment.course?.id || enrollment.course
      if (!courseId) continue
      try {
        const qRes = await api.get(`/api/ai/quiz/course/${courseId}/`)
        allQuizzes.push(...qRes.data)
      } catch (e) { /* no quizzes */ }
    }
    availableQuizzes.value = allQuizzes
  } catch (e) { console.error(e) }
}

const startQuiz = async (quiz) => {
  try {
    const response = await api.get(`/api/ai/quiz/${quiz.id}/`)
    currentTakingQuiz.value = response.data
    studentAnswers.value = {}
    quizResult.value = null
    quizTakingVisible.value = true
  } catch (e) { ElMessage.error(e.response?.data?.error || '无法加载Quiz') }
}

const submitQuiz = async () => {
  if (!currentTakingQuiz.value) return
  const totalQ = currentTakingQuiz.value.questions?.length || 0
  const answeredQ = Object.keys(studentAnswers.value).length
  if (answeredQ < totalQ) {
    try {
      await ElMessageBox.confirm(`您还有 ${totalQ - answeredQ} 题未作答，确定提交吗？`, '提示', { type: 'warning' })
    } catch { return }
  }

  isSubmitting.value = true
  try {
    const response = await api.post(`/api/ai/quiz/${currentTakingQuiz.value.id}/submit/`, { answers: studentAnswers.value })
    quizResult.value = response.data
    ElMessage.success(`提交成功！得分: ${response.data.score}分`)
    if (!isTeacher.value) loadAvailableQuizzes()
  } catch (e) { ElMessage.error(e.response?.data?.error || '提交失败') }
  finally { isSubmitting.value = false }
}

const loadEnrolledCourses = async () => {
  try {
    const res = await api.get('/api/courses/course-enrollments/')
    const enrollments = res.data.results || res.data || []
    enrolledCourses.value = enrollments.map(e => e.course).filter(Boolean)
  } catch (e) { console.error(e) }
}

onMounted(() => {
  if (isTeacher.value) {
    aiMode.value = 'direct'
    loadMyQuizzes()
    loadMyCourses()
  } else {
    loadChatHistory()
    loadEnrolledCourses()
  }
})
</script>

<style scoped>
.ai-tutor {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 180px);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 400px;
  max-height: calc(100vh - 400px);
}

.message {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message .content {
  max-width: 70%;
  min-width: 0;
}

.message.user .content {
  background: #333333;
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
}

.message.assistant .content {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message .name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.message.user .name {
  color: rgba(255, 255, 255, 0.8);
}

.message .text {
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.message .text :deep(p),
.message .text :deep(ul),
.message .text :deep(ol),
.message .text :deep(li),
.message .text :deep(blockquote) {
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.message .text :deep(ul),
.message .text :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.4em;
}

.message .text :deep(li) {
  margin: 0.25em 0;
}

.message .text :deep(pre) {
  background: #f4f4f4;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.message .text :deep(code) {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.message .time {
  font-size: 11px;
  color: #C0C4CC;
  margin-top: 5px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading {
  display: flex;
  gap: 5px;
  padding: 10px 0;
}

.loading span {
  width: 8px;
  height: 8px;
  background: #333333;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #EBEEF5;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.course-selector-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.rag-sources {
  margin-top: 8px;
}
.rag-source-item {
  margin-bottom: 10px;
  padding: 8px 10px;
  background: #fafafa;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}
.rag-source-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
}
.rag-source-page {
  color: #909399;
  font-size: 12px;
}
.rag-source-snippet {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-row .el-input {
  flex: 1;
}

.sidebar {
  width: 380px;
  height: 100%;
  overflow-y: auto;
  background: white;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #303133;
  background: #f5f7fa;
  padding: 16px;
  margin: -20px -20px 16px -20px;
  border-radius: 8px 8px 0 0;
}

.upload-area { width: 100%; background: white; border-radius: 8px; padding: 16px; }
.upload-area :deep(.el-upload-dragger) { padding: 20px; background: white; }
.quiz-settings { margin-top: 16px; }

.quiz-list { max-height: 400px; overflow-y: auto; }

.quiz-item {
  padding: 12px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  margin-bottom: 10px;
  transition: box-shadow 0.3s;
}
.quiz-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

.quiz-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.quiz-item-header h4 { margin: 0; font-size: 14px; color: #303133; }

.quiz-item-info {
  display: flex; gap: 10px;
  font-size: 12px; color: #909399;
  flex-wrap: wrap;
}

.quiz-item-actions {
  display: flex; gap: 6px;
  margin-top: 8px; flex-wrap: wrap;
}

.share-code-input { margin-bottom: 12px; }

.quiz-detail-header h3 { margin: 0 0 8px 0; }
.share-info { margin-top: 8px; font-size: 13px; color: #606266; }

.quiz-question-preview,
.quiz-taking-question,
.quiz-result-question {
  margin-bottom: 20px;
  padding: 12px;
  background: #f9f9fb;
  border-radius: 8px;
}

.question-title { font-weight: bold; margin-bottom: 8px; font-size: 14px; }
.question-options p {
  margin: 4px 0; padding: 4px 8px;
  border-radius: 4px; font-size: 13px;
}
.question-options p.correct { background: #f0f9eb; color: #67C23A; font-weight: bold; }
.question-options p.wrong { background: #fef0f0; color: #F56C6C; text-decoration: line-through; }

.explanation { margin-top: 8px; font-size: 12px; color: #909399; font-style: italic; }
.result-score { text-align: center; }

/* Student image upload section */
.student-upload-section { padding: 4px 0; }

.image-upload-area { text-align: center; }

.image-upload { width: 100%; }
.image-upload :deep(.el-upload) { width: 100%; }

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.3s;
}
.upload-trigger:hover { border-color: #333333; }
.upload-trigger-text { margin-top: 10px; font-size: 14px; color: #606266; }
.upload-trigger-tip { margin-top: 4px; font-size: 12px; color: #606266; }

.image-preview-box {
  margin-top: 12px;
  text-align: center;
}
.preview-img {
  max-height: 200px;
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.upload-hint {
  margin-top: 10px;
  font-size: 13px;
  color: #67C23A;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
}

.chat-history-list { max-height: 300px; overflow-y: auto; }

.history-item {
  padding: 10px 12px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}
.history-item:hover {
  background: #f5f5f5;
  border-color: #333333;
}
.history-title {
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.history-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.image-attachment-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: #ecf5ff;
  border-radius: 8px;
  border: 1px solid #d9ecff;
}
.attachment-text {
  flex: 1;
  font-size: 13px;
  color: #333333;
}

.message-image {
  margin-bottom: 4px;
}

.message-file-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 6px;
  font-size: 13px;
  color: #333333;
  margin-bottom: 6px;
}

.file-preview-box {
  margin-top: 12px;
  padding: 14px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}
.file-icon-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.file-meta { flex: 1; overflow: hidden; }
.file-name {
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-size { font-size: 12px; color: #909399; margin-top: 2px; }

/* Statistics styles */
.stats-overview { margin-bottom: 16px; text-align: center; }
.score-distribution { padding: 0 10px; }
.score-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.score-label { width: 65px; font-size: 13px; color: #606266; text-align: right; }
.option-dist { display: flex; gap: 8px; flex-wrap: wrap; }
.opt-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: #f4f4f5;
  color: #909399;
}
.opt-badge.correct-opt {
  background: #f0f9eb;
  color: #67C23A;
  font-weight: bold;
}
</style>
