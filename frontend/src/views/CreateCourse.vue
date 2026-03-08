<template>
  <div class="create-course">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DocumentAdd /></el-icon>
          <span>创建新课程</span>
        </div>
      </template>

      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">
          <el-icon><InfoFilled /></el-icon> 基本信息
        </el-divider>

        <el-form-item label="课程标题" prop="title">
          <el-input
            v-model="courseForm.title"
            placeholder="请输入课程标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="5"
            placeholder="请输入详细的课程描述"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程类型" prop="category">
              <el-select v-model="courseForm.category" placeholder="选择课程类型" style="width: 100%">
                <el-option label="必修" value="required" />
                <el-option label="选修" value="elective" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程时长(小时)">
              <el-input-number
                v-model="courseForm.duration_hours"
                :min="0"
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 课程资料 -->
        <el-divider content-position="left">
          <el-icon><FolderOpened /></el-icon> 课程资料
        </el-divider>

        <el-form-item label="课程封面">
          <el-upload
            class="cover-uploader"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleCoverChange"
            accept="image/*"
          >
            <img v-if="coverPreview" :src="coverPreview" class="cover-preview" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">建议尺寸：800x450，支持jpg、png格式</div>
        </el-form-item>

        <el-form-item label="课程大纲">
          <el-upload
            :auto-upload="false"
            :on-change="handleSyllabusChange"
            :file-list="syllabusFileList"
            accept=".pdf,.doc,.docx"
          >
            <el-button type="primary" :icon="Upload">上传大纲文件</el-button>
          </el-upload>
          <div class="upload-tip">支持PDF、Word格式</div>
        </el-form-item>

        <el-form-item label="课程资料">
          <el-upload
            :auto-upload="false"
            :on-change="handleMaterialsChange"
            :file-list="materialsFileList"
            accept=".pdf,.doc,.docx,.zip"
          >
            <el-button type="primary" :icon="Upload">上传课程资料</el-button>
          </el-upload>
          <div class="upload-tip">支持PDF、Word、压缩包格式</div>
        </el-form-item>

        <!-- 章节内容 -->
        <el-divider content-position="left">
          <el-icon><Reading /></el-icon> 章节内容
        </el-divider>

        <div class="chapters-section">
          <div v-for="(chapter, chapterIndex) in courseForm.chapters" :key="chapterIndex" class="chapter-block">
            <el-card>
              <template #header>
                <div class="chapter-header">
                  <span>第 {{ chapterIndex + 1 }} 章</span>
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="removeChapter(chapterIndex)"
                  >
                    删除章节
                  </el-button>
                </div>
              </template>

              <el-form-item label="章节标题">
                <el-input v-model="chapter.title" placeholder="请输入章节标题" />
              </el-form-item>

              <el-form-item label="章节描述">
                <el-input
                  v-model="chapter.description"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入章节描述"
                />
              </el-form-item>

              <!-- 课时列表 -->
              <div class="lessons-section">
                <div class="section-label">课时列表</div>
                <div v-for="(lesson, lessonIndex) in chapter.lessons" :key="lessonIndex" class="lesson-item">
                  <el-card shadow="hover">
                    <div class="lesson-header">
                      <span>课时 {{ lessonIndex + 1 }}</span>
                      <el-button
                        type="danger"
                        size="small"
                        text
                        @click="removeLesson(chapterIndex, lessonIndex)"
                      >
                        删除
                      </el-button>
                    </div>

                    <el-form-item label="课时标题">
                      <el-input v-model="lesson.title" placeholder="请输入课时标题" />
                    </el-form-item>

                    <el-form-item label="课时内容">
                      <el-input
                        v-model="lesson.content"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入课时内容描述"
                      />
                    </el-form-item>

                    <el-row :gutter="10">
                      <el-col :span="12">
                        <el-form-item label="视频地址">
                          <el-input v-model="lesson.video_url" placeholder="视频URL（可选）" />
                        </el-form-item>
                      </el-col>
                      <el-col :span="12">
                        <el-form-item label="时长(分钟)">
                          <el-input-number
                            v-model="lesson.duration_minutes"
                            :min="0"
                            style="width: 100%"
                          />
                        </el-form-item>
                      </el-col>
                    </el-row>

                    <el-form-item label="视频文件">
                      <el-upload
                        :auto-upload="false"
                        :on-change="(file) => handleVideoChange(file, chapterIndex, lessonIndex)"
                        :file-list="lesson.videoFileList || []"
                        accept="video/*"
                      >
                        <el-button size="small" :icon="VideoCamera">上传视频</el-button>
                      </el-upload>
                    </el-form-item>

                    <el-form-item label="课时附件">
                      <el-upload
                        :auto-upload="false"
                        :on-change="(file) => handleAttachmentChange(file, chapterIndex, lessonIndex)"
                        :file-list="lesson.attachmentFileList || []"
                      >
                        <el-button size="small" :icon="Paperclip">上传附件</el-button>
                      </el-upload>
                    </el-form-item>

                    <el-form-item>
                      <el-checkbox v-model="lesson.is_free">免费试看</el-checkbox>
                    </el-form-item>
                  </el-card>
                </div>

                <el-button
                  type="primary"
                  plain
                  :icon="Plus"
                  @click="addLesson(chapterIndex)"
                  style="width: 100%; margin-top: 10px;"
                >
                  添加课时
                </el-button>
              </div>
            </el-card>
          </div>

          <el-button
            type="success"
            :icon="Plus"
            @click="addChapter"
            style="width: 100%; margin-top: 20px;"
          >
            添加章节
          </el-button>
        </div>

        <!-- 发布设置 -->
        <el-divider content-position="left">
          <el-icon><Setting /></el-icon> 发布设置
        </el-divider>

        <el-form-item>
          <el-checkbox v-model="courseForm.is_published">立即发布课程</el-checkbox>
          <div class="form-tip">取消勾选将保存为草稿，稍后可以编辑后再发布</div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-space>
            <el-button type="primary" size="large" :loading="submitting" @click="submitCourse">
              {{ courseForm.is_published ? '创建并发布' : '保存草稿' }}
            </el-button>
            <el-button size="large" @click="$router.back()">取消</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import {
  DocumentAdd, InfoFilled, FolderOpened, Reading, Setting,
  Plus, Delete, Upload, VideoCamera, Paperclip
} from '@element-plus/icons-vue'

const router = useRouter()
const courseFormRef = ref(null)
const submitting = ref(false)

const courseForm = reactive({
  title: '',
  description: '',
  category: '',
  duration_hours: 0,
  is_published: false,
  image: null,
  syllabus: null,
  materials: null,
  chapters: []
})

const coverPreview = ref('')
const syllabusFileList = ref([])
const materialsFileList = ref([])

const rules = {
  title: [{ required: true, message: '请输入课程标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入课程描述', trigger: 'blur' }],
  category: [{ required: true, message: '请选择课程类型', trigger: 'change' }]
}

// 处理封面上传
const handleCoverChange = (file) => {
  courseForm.image = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    coverPreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 处理大纲上传
const handleSyllabusChange = (file) => {
  courseForm.syllabus = file.raw
  syllabusFileList.value = [file]
}

// 处理资料上传
const handleMaterialsChange = (file) => {
  courseForm.materials = file.raw
  materialsFileList.value = [file]
}

// 处理视频文件上传
const handleVideoChange = (file, chapterIndex, lessonIndex) => {
  const lesson = courseForm.chapters[chapterIndex].lessons[lessonIndex]
  lesson.video_file = file.raw
  lesson.videoFileList = [file]
}

// 处理附件上传
const handleAttachmentChange = (file, chapterIndex, lessonIndex) => {
  const lesson = courseForm.chapters[chapterIndex].lessons[lessonIndex]
  lesson.attachment = file.raw
  lesson.attachment_name = file.name
  lesson.attachmentFileList = [file]
}

// 添加章节
const addChapter = () => {
  courseForm.chapters.push({
    title: '',
    description: '',
    order: courseForm.chapters.length,
    lessons: []
  })
}

// 删除章节
const removeChapter = (index) => {
  courseForm.chapters.splice(index, 1)
  // 更新排序
  courseForm.chapters.forEach((chapter, i) => {
    chapter.order = i
  })
}

// 添加课时
const addLesson = (chapterIndex) => {
  const chapter = courseForm.chapters[chapterIndex]
  chapter.lessons.push({
    title: '',
    content: '',
    video_url: '',
    video_file: null,
    duration_minutes: 0,
    order: chapter.lessons.length,
    is_free: false,
    attachment: null,
    attachment_name: '',
    videoFileList: [],
    attachmentFileList: []
  })
}

// 删除课时
const removeLesson = (chapterIndex, lessonIndex) => {
  const chapter = courseForm.chapters[chapterIndex]
  chapter.lessons.splice(lessonIndex, 1)
  // 更新排序
  chapter.lessons.forEach((lesson, i) => {
    lesson.order = i
  })
}

// 提交课程
const submitCourse = async () => {
  try {
    await courseFormRef.value.validate()
    
    submitting.value = true
    
    // 构建FormData以支持文件上传
    const formData = new FormData()
    
    // 基本信息
    formData.append('title', courseForm.title)
    formData.append('description', courseForm.description)
    formData.append('category', courseForm.category)
    formData.append('duration_hours', courseForm.duration_hours)
    formData.append('is_published', courseForm.is_published)
    
    // 文件
    if (courseForm.image) {
      formData.append('image', courseForm.image)
    }
    if (courseForm.syllabus) {
      formData.append('syllabus', courseForm.syllabus)
    }
    if (courseForm.materials) {
      formData.append('materials', courseForm.materials)
    }
    
    // 章节和课时数据（使用JSON）
    const chaptersData = courseForm.chapters.map(chapter => ({
      title: chapter.title,
      description: chapter.description,
      order: chapter.order,
      lessons: chapter.lessons.map(lesson => ({
        title: lesson.title,
        content: lesson.content,
        video_url: lesson.video_url,
        duration_minutes: lesson.duration_minutes,
        order: lesson.order,
        is_free: lesson.is_free,
        attachment_name: lesson.attachment_name
      }))
    }))
    
    formData.append('chapters', JSON.stringify(chaptersData))
    
    // 添加视频和附件文件
    courseForm.chapters.forEach((chapter, chIndex) => {
      chapter.lessons.forEach((lesson, lIndex) => {
        if (lesson.video_file) {
          formData.append(`chapter_${chIndex}_lesson_${lIndex}_video`, lesson.video_file)
        }
        if (lesson.attachment) {
          formData.append(`chapter_${chIndex}_lesson_${lIndex}_attachment`, lesson.attachment)
        }
      })
    })
    
    const response = await api.post('/api/courses/course/', formData)
    
    ElMessage.success(courseForm.is_published ? '课程创建并发布成功！' : '课程草稿保存成功！')
    router.push('/teacher-home')
  } catch (error) {
    console.error('创建课程失败:', error)
    ElMessage.error(error.response?.data?.error || '创建课程失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-course {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.form-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.cover-uploader .cover-preview {
  width: 300px;
  height: 169px;
  object-fit: cover;
  border-radius: 4px;
}

.cover-uploader-icon {
  font-size: 50px;
  width: 300px;
  height: 169px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.cover-uploader-icon:hover {
  border-color: #333333;
  color: #333333;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.chapters-section {
  margin-top: 20px;
}

.chapter-block {
  margin-bottom: 20px;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.lessons-section {
  margin-top: 15px;
}

.section-label {
  font-weight: 500;
  margin-bottom: 10px;
  color: #606266;
}

.lesson-item {
  margin-bottom: 15px;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
}
</style>
