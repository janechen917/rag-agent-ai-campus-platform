<template>
  <div class="edit-course">
    <el-card class="form-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Edit /></el-icon>
          <span>编辑课程</span>
        </div>
      </template>

      <el-form
        v-if="!loading"
        ref="courseFormRef"
        :model="courseForm"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="课程标题" prop="title">
          <el-input v-model="courseForm.title" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" :rows="5" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程类型" prop="category">
              <el-select v-model="courseForm.category" style="width: 100%">
                <el-option label="必修" value="required" />
                <el-option label="选修" value="elective" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程时长(小时)">
              <el-input-number v-model="courseForm.duration_hours" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">文件替换（可选）</el-divider>

        <el-form-item label="课程封面">
          <el-upload :auto-upload="false" :show-file-list="false" :on-change="handleCoverChange" accept="image/*">
            <img v-if="coverPreview" :src="coverPreview" class="cover-preview" />
            <el-button v-else type="primary">选择新封面</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item label="课程大纲">
          <el-upload :auto-upload="false" :on-change="handleSyllabusChange" :file-list="syllabusFileList" accept=".pdf,.doc,.docx">
            <el-button type="primary">替换大纲文件</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item label="课程资料">
          <el-upload :auto-upload="false" :on-change="handleMaterialsChange" :file-list="materialsFileList" accept=".pdf,.doc,.docx,.zip">
            <el-button type="primary">替换课程资料</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="courseForm.is_published">发布课程</el-checkbox>
        </el-form-item>

        <el-alert
          title="当前编辑页支持基础信息与主文件替换，章节课时请在创建页维护后再调整。"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />

        <el-form-item>
          <el-space>
            <el-button type="primary" :loading="submitting" @click="submitCourse">保存修改</el-button>
            <el-button @click="$router.back()">取消</el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import api, { buildApiUrl } from '@/api'

const route = useRoute()
const router = useRouter()
const courseFormRef = ref(null)
const loading = ref(true)
const submitting = ref(false)

const courseForm = reactive({
  title: '',
  description: '',
  category: '',
  duration_hours: 0,
  is_published: false,
  image: null,
  syllabus: null,
  materials: null
})

const coverPreview = ref('')
const syllabusFileList = ref([])
const materialsFileList = ref([])

const rules = {
  title: [{ required: true, message: '请输入课程标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入课程描述', trigger: 'blur' }],
  category: [{ required: true, message: '请选择课程类型', trigger: 'change' }]
}

const resolveMediaUrl = (url) => {
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  return buildApiUrl(url)
}

const loadCourse = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/api/courses/course/${route.params.id}/`)
    courseForm.title = data.title || ''
    courseForm.description = data.description || ''
    courseForm.category = data.category || ''
    courseForm.duration_hours = Number(data.duration_hours || 0)
    courseForm.is_published = Boolean(data.is_published)
    coverPreview.value = resolveMediaUrl(data.image)
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '加载课程信息失败')
    router.push('/my-courses')
  } finally {
    loading.value = false
  }
}

const handleCoverChange = (file) => {
  courseForm.image = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    coverPreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const handleSyllabusChange = (file) => {
  courseForm.syllabus = file.raw
  syllabusFileList.value = [file]
}

const handleMaterialsChange = (file) => {
  courseForm.materials = file.raw
  materialsFileList.value = [file]
}

const submitCourse = async () => {
  try {
    await courseFormRef.value.validate()
    submitting.value = true

    const formData = new FormData()
    formData.append('title', courseForm.title)
    formData.append('description', courseForm.description)
    formData.append('category', courseForm.category)
    formData.append('duration_hours', String(courseForm.duration_hours || 0))
    formData.append('is_published', String(courseForm.is_published))

    if (courseForm.image) formData.append('image', courseForm.image)
    if (courseForm.syllabus) formData.append('syllabus', courseForm.syllabus)
    if (courseForm.materials) formData.append('materials', courseForm.materials)

    await api.patch(`/api/courses/course/${route.params.id}/`, formData)
    ElMessage.success('课程修改成功')
    router.push('/my-courses')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '保存失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(loadCourse)
</script>

<style scoped>
.edit-course {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.form-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.cover-preview {
  width: 280px;
  height: 160px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}
</style>
