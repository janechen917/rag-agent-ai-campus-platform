"""
AI服务核心功能
集成LangChain、Transformers和FAISS
支持OpenAI API和GitHub Models
"""
import os
from typing import List, Dict, Optional
from django.conf import settings

# LangChain相关导入
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"Warning: LangChain not available: {e}")
    print("Install with: pip install langchain langchain-community langchain-openai openai")

# Transformers相关导入
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: Transformers not available. Install with: pip install transformers sentence-transformers")


class AIService:
    """AI服务主类"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.AI_MODEL_NAME
        self.vector_db_path = settings.VECTOR_DB_PATH
        self.api_base = getattr(settings, 'OPENAI_API_BASE', None)
        self.use_github_models = getattr(settings, 'USE_GITHUB_MODELS', False)
        
        # 初始化LangChain
        self.llm = None
        self.embeddings = None
        
        if LANGCHAIN_AVAILABLE and self.api_key:
            try:
                llm_config = {
                    'model': self.model_name,
                    'temperature': 0.7,
                    'api_key': self.api_key,
                }
                
                # 如果使用GitHub Models，配置API Base
                if self.use_github_models and self.api_base:
                    llm_config['base_url'] = self.api_base
                    print(f"✓ 使用GitHub Models: {self.model_name}")
                elif self.api_key and self.api_key != 'your-openai-api-key-here':
                    print(f"✓ 使用OpenAI API: {self.model_name}")
                else:
                    print("⚠ API密钥未配置，AI功能将使用备用模式")
                    raise ValueError("API key not configured")
                
                self.llm = ChatOpenAI(**llm_config)
                
                # 嵌入模型配置（GitHub Models可能不提供embeddings）
                if not self.use_github_models:
                    self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
                else:
                    print("⚠ GitHub Models不支持embeddings，将使用本地模型")
                    
            except Exception as e:
                print(f"⚠ AI模型初始化失败: {e}")
                self.llm = None
                self.embeddings = None
        
        # 初始化向量数据库
        self.vector_store = None
        self._load_vector_store()
        
        # 初始化本地模型（备用方案）
        self.local_embeddings = None
        if TRANSFORMERS_AVAILABLE:
            try:
                self.local_embeddings = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                print(f"Warning: Failed to load local embedding model: {e}")
    
    def _load_vector_store(self):
        """加载FAISS向量数据库"""
        if not self.embeddings:
            return
        
        try:
            if os.path.exists(self.vector_db_path):
                self.vector_store = FAISS.load_local(
                    self.vector_db_path,
                    self.embeddings
                )
            else:
                # 创建新的向量数据库
                os.makedirs(self.vector_db_path, exist_ok=True)
        except Exception as e:
            print(f"Error loading vector store: {e}")
    
    def _build_system_prompt(self, course_context: Optional[Dict] = None, mode: str = 'socratic') -> str:
        """
        构建系统提示词
        
        Args:
            course_context: 课程上下文信息，包含课程名称、文件列表等
            mode: 回答模式，'socratic'（苏格拉底引导）或 'direct'（直接回答）
        
        Returns:
            系统提示词
        """
        if mode == 'direct':
            base_prompt = """# 角色
你是一位知识渊博的AI学习助手，专门为大学生提供清晰、准确、详尽的知识解答。

# 语言政策
- 识别学生消息的语言，并以**相同语言**进行回复。
- 如果学生在对话过程中切换语言，则你也跟着切换。

# 回答风格：直接回答模式
你应该直接、清晰、全面地回答学生的问题。

## 核心回答流程：
1. **理解学生问题**：仔细分析学生的提问，确定知识点领域
2. **直接解答**：用清晰准确的语言直接回答问题，提供完整的解释
3. **举例说明**：使用具体的例子和类比帮助学生理解
4. **总结要点**：在回答末尾简洁地总结关键知识点
5. **延伸建议**：适当提供相关知识点的延伸阅读建议

## 回答完成后的流程：
1. 总结关键知识点
2. 询问学生是否还有疑问，或是否需要练习题巩固

## 练习设计规则：
当学生需要练习时，生成三个难度级别的练习题：
- **[基础级]** 测试对定义或原理的直接理解
- **[应用级]** 需要运用该概念来分析一个场景
- **[综合级]** 需要将多个概念或相关内容联系起来

每道题后附上答案和简要解析。"""
        else:
            base_prompt = """# 角色
你是一位经验丰富的AI学习导师（苏格拉底式教学助手），专门通过引导式提问帮助大学生深入理解知识。

# 语言政策
- 识别学生消息的语言，并以**相同语言**进行回复。
- 如果学生在对话过程中切换语言，则你也跟着切换。

# 绝对规则：禁止直接作答
你被**禁止**直接回答涉及概念性、分析性或解决性的问题。
你必须始终通过提问、引导和逐步推理来帮助学生自己得出答案。

# 苏格拉底式教学法——大学水平（严格模式）

## 核心教学流程：
1. **理解学生问题**：仔细分析学生的提问，确定知识点领域
2. **引导式提问**：不直接给出答案，而是通过一系列循序渐进的问题引导学生思考
3. **逐步推理**：每次只推进一小步，用生动易理解的类比和例子帮助学生理解
4. **鼓励独立思考**：在学生回答后给予肯定或纠正，继续引导直到学生自己得出答案
5. **验证理解**：在引导结束后，确认学生是否真正理解了概念

## 引导技巧：
- 使用生动的类比和现实生活中的例子
- 将复杂问题拆解为简单的子问题
- 鼓励学生回顾已知知识并建立联系
- 在学生卡住时给予适度的提示，但不要直接揭示答案
- 使用反问句激发思考

## 回答完成后的流程：
当你通过引导帮助学生得到最终答案后：
1. 总结关键知识点
2. 询问学生："你现在理解了吗？需要我生成一些类似的练习题来巩固吗？"
3. 如果学生需要练习，生成有针对性的练习题

## 练习设计规则：
当学生表示已理解并需要练习时，生成三个难度级别的练习题：
- **[基础级]** 测试对定义或原理的直接理解
- **[应用级]** 需要运用该概念来分析一个场景
- **[综合级]** 需要将多个概念或相关内容联系起来

每道题后附上简短提示（不是答案），引导学生独立完成。"""

        if course_context:
            course_name = course_context.get('course_name', '')
            course_files = course_context.get('course_files', [])
            
            # 筛选 PPT 文件
            ppt_files = [f for f in course_files if f.get('file_name', '').lower().endswith(('.ppt', '.pptx'))]
            
            if ppt_files:
                files_info = '\n'.join([f"- {f['file_name']}（{f.get('description', '无描述')}）" for f in ppt_files])
                base_prompt += f"""\n\n# 当前课程上下文
学生正在学习课程：**{course_name}**

该课程包含以下PPT课件：
{files_info}

## 课件引用规则：
- 当学生的问题涉及某个知识点时，如果该知识点可能包含在上述PPT课件中，请在回答末尾推荐相关的PPT课件，格式为：\n  📎 **推荐课件**：`课件名称` — 该课件包含了本知识点的详细讲解，建议结合课件复习。
- 如果问题与课件内容无明显关联，则无需推荐。"""
            else:
                base_prompt += f"""\n\n# 当前课程上下文
学生正在学习课程：**{course_name}**

该课程暂无PPT课件。请着重通过苏格拉底式引导帮助学生理解，培养学生的独立思考能力和精确推理能力。"""
        else:
            base_prompt += """\n\n# 未选择课程
学生尚未选择具体课程。如果学生提出了学习相关的问题，请先友好地询问学生的问题来自于哪门课程，以便提供更精确的帮助。
如果学生的问题是通用性的（如问候、闲聊），可以直接回应。"""
        
        return base_prompt

    def chat(self, message: str, history: List[Dict] = None, course_context: Optional[Dict] = None, mode: str = 'socratic') -> str:
        """
        AI聊天功能
        
        Args:
            message: 用户消息
            history: 对话历史
            course_context: 课程上下文 {course_name, course_files: [{file_name, description}]}
            mode: 回答模式，'socratic' 或 'direct'
        
        Returns:
            AI回复
        """
        if not self.llm:
            print("⚠ LLM未初始化，使用备用响应模式")
            return self._fallback_chat(message)
        
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(course_context, mode=mode)
            messages = [SystemMessage(content=system_prompt)]
            
            # 添加历史对话
            if history:
                for msg in history[-10:]:  # 保留最近10条对话以支持多轮引导
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))
            
            # 添加当前消息
            messages.append(HumanMessage(content=message))
            
            # 调用LLM
            response = self.llm.invoke(messages)
            return response.content
        
        except Exception as e:
            print(f"⚠ AI服务调用失败: {type(e).__name__}: {e}")
            print("  ↳ 使用备用响应模式")
            return self._fallback_chat(message)
    
    def chat_with_image(self, message: str, image_base64: str, content_type: str, history: List[Dict] = None, mode: str = 'socratic') -> str:
        """
        AI图片问答功能
        
        Args:
            message: 用户消息
            image_base64: 图片的base64编码
            content_type: 图片MIME类型
            history: 对话历史
            mode: 回答模式，'socratic' 或 'direct'
        
        Returns:
            AI回复
        """
        if not self.llm:
            return self._fallback_chat(message or "请描述这张图片")
        
        try:
            system_prompt = self._build_system_prompt(course_context=None, mode=mode)
            if mode == 'direct':
                system_prompt += """\n\n# 图片分析补充说明
学生可能会向你发送图片（如课件截图、代码截图、题目截图等）。
请仔细分析图片中的内容，然后直接给出清晰、完整的解答。"""
            else:
                system_prompt += """\n\n# 图片分析补充说明
学生可能会向你发送图片（如课件截图、代码截图、题目截图等）。
请先仔细分析图片中的内容，然后通过苏格拉底式引导帮助学生理解。
不要直接给出答案，而是通过提问引导学生自己得出结论。"""
            messages_list = [SystemMessage(content=system_prompt)]
            
            if history:
                for msg in history[-5:]:
                    if msg.get('role') == 'user':
                        messages_list.append(HumanMessage(content=msg['content']))
                    elif msg.get('role') == 'assistant':
                        messages_list.append(AIMessage(content=msg['content']))
            
            # Build multimodal content
            content = []
            if image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{content_type};base64,{image_base64}"}
                })
            text = message if message else "请分析这张图片的内容，并提供学习建议。"
            content.append({"type": "text", "text": text})
            
            messages_list.append(HumanMessage(content=content))
            
            response = self.llm.invoke(messages_list)
            return response.content
        
        except Exception as e:
            print(f"⚠ AI图片问答服务调用失败: {type(e).__name__}: {e}")
            return self._fallback_chat(message or "请描述这张图片")
    
    def _fallback_chat(self, message: str) -> str:
        """备用聊天响应 - 当AI服务不可用时提供有用的回答"""
        message_lower = message.lower()
        
        # 问候语
        greetings = ['你好', 'hello', 'hi', '您好', '嗨']
        if any(g in message_lower for g in greetings):
            return '''你好！👋 我是AI学习导师。

虽然当前AI智能服务暂时不可用，但我仍可以为你提供基础的学习建议：

📚 **学习建议：**
• 浏览课程页面，查找感兴趣的主题
• 从基础课程开始，循序渐进
• 遇到问题时，尝试查阅官方文档
• 多动手实践，理论结合实际

如果你有具体的技术问题，可以详细描述，我会尽力提供帮助！'''
        
        # 技术关键词匹配
        tech_responses = {
            'python': '''**关于Python学习：** 🐍

Python是一门优秀的编程语言，适合初学者入门。建议学习路径：

1. **基础语法**：变量、数据类型、控制流
2. **函数与模块**：函数定义、模块导入
3. **面向对象**：类、继承、多态
4. **常用库**：NumPy、Pandas、Requests
5. **项目实践**：做小项目巩固知识

**推荐资源：**
• Python官方教程：https://docs.python.org/zh-cn/3/tutorial/
• 菜鸟教程：实用的中文入门教程
• 项目练习：LeetCode、牛客网''',
            
            'javascript': '''**关于JavaScript学习：** 📜

JavaScript是Web开发的核心，学习路线建议：

1. **语法基础**：变量、函数、对象
2. **DOM操作**：选择器、事件处理
3. **ES6+特性**：箭头函数、Promise、async/await
4. **前端框架**：Vue、React、Angular
5. **Node.js**：后端JavaScript开发

**学习建议：**
• 从基础开始，不要急于学框架
• 多在浏览器控制台练习
• 做小项目加深理解
• 关注MDN文档（权威参考）''',
            
            'vue': '''**关于Vue.js学习：** 💚

Vue是一个渐进式前端框架，易学易用：

**Vue 3核心概念：**
1. **Composition API**：更灵活的代码组织
2. **响应式系统**：ref、reactive
3. **组件通信**：props、emit、provide/inject
4. **生命周期**：setup、onMounted等
5. **路由与状态管理**：Vue Router、Pinia

**学习建议：**
• 先掌握JavaScript基础
• 跟着官方文档学习
• 做实战项目加深理解
• 参考Vue Mastery视频教程''',
            
            'django': '''**关于Django学习：** 🎸

Django是Python的全功能Web框架：

**核心概念：**
1. **MTV模式**：Model-Template-View
2. **ORM系统**：数据库操作
3. **路由配置**：URL映射
4. **模板引擎**：动态HTML生成
5. **表单处理**：数据验证

**学习路径：**
• 完成官方Tutorial
• 理解Django的设计哲学
• 学习Django REST framework（API开发）
• 部署到生产环境

**推荐资源：**
• Django官方文档（必读）
• Django Girls教程（适合初学者）''',
            
            'react': '''**关于React学习：** ⚛️

React是流行的前端库：

**核心概念：**
1. **组件化**：函数组件、Class组件
2. **JSX语法**：JavaScript + XML
3. **Hooks**：useState、useEffect等
4. **状态管理**：Redux、Context API
5. **路由**：React Router

**学习建议：**
• 理解虚拟DOM概念
• 掌握Hooks用法
• 练习组件设计
• 学习状态管理最佳实践''',
            
            'html': '''**关于HTML学习：** 📄

HTML是网页的骨架：

**学习要点：**
• 常用标签：div、p、a、img、form等
• 语义化标签：header、nav、article、section
• 表单元素：input、select、textarea
• HTML5新特性：video、canvas、本地存储

建议配合CSS和JavaScript一起学习，形成完整的前端知识体系。''',
            
            'css': '''**关于CSS学习：** 🎨

CSS美化网页外观：

**学习路径：**
1. **基础**：选择器、盒模型、定位
2. **布局**：Flexbox、Grid
3. **响应式**：媒体查询、移动优先
4. **动画**：transition、animation
5. **预处理器**：Sass、Less

**实践建议：**
• 多看优秀网站设计
• 尝试重现经典布局
• 学习CSS Tricks网站''',
            
            'git': '''**关于Git学习：** 🌳

Git是必备的版本控制工具：

**核心命令：**
• git init / clone - 初始化仓库
• git add / commit - 提交代码
• git push / pull - 同步远程
• git branch / merge - 分支管理
• git rebase - 变基操作

**学习建议：**
• 理解Git工作流
• 多练习分支操作
• 学习解决冲突
• 参考Git官方文档''',
            
            'sql': '''**关于SQL学习：** 🗄️

SQL是数据库查询语言：

**核心概念：**
• SELECT - 查询数据
• INSERT / UPDATE / DELETE - 增删改
• JOIN - 表连接
• GROUP BY - 分组统计
• 子查询和视图

**实践建议：**
• 在MySQL或PostgreSQL上练习
• LeetCode数据库题目
• 理解索引和性能优化''',
            
            'api': '''**关于API开发：** 🔌

API是系统间通信的桥梁：

**RESTful API设计：**
• HTTP方法：GET、POST、PUT、DELETE
• 状态码：200、201、400、404、500
• 认证：JWT、OAuth
• 文档：Swagger、Postman

**学习建议：**
• 理解REST架构风格
• 实践API设计原则
• 学习接口安全
• 做好错误处理和日志记录''',
        }
        
        # 检查是否匹配技术关键词
        for keyword, response in tech_responses.items():
            if keyword in message_lower:
                return response
        
        # 学习相关问题
        learning_keywords = ['怎么学', '如何学', '学习方法', '入门', '开始学']
        if any(k in message_lower for k in learning_keywords):
            return '''**学习建议：** 📚

无论学习什么技术，都可以遵循这些步骤：

**1. 明确目标**
• 确定要学什么、为什么学

**2. 找好资源**
• 官方文档是最权威的资料
• 视频教程适合入门
• 书籍适合系统学习

**3. 动手实践**
• 边学边做，理论结合实际
• 从简单项目开始
• 多看别人的代码

**4. 持续学习**
• 技术更新快，保持学习
• 关注技术社区和博客
• 参与开源项目

如果你想学具体的技术（如Python、JavaScript、Vue等），可以告诉我，我会给你更详细的建议！'''
        
        # 错误排查
        error_keywords = ['错误', 'error', 'bug', '问题', '报错', '不工作', '失败']
        if any(k in message_lower for k in error_keywords):
            return '''**调试建议：** 🔍

遇到错误时，可以按这些步骤排查：

**1. 阅读错误信息**
• 仔细看错误提示，通常会指出问题所在
• 注意错误类型和行号

**2. 检查代码**
• 检查语法错误（拼写、标点）
• 确认变量是否定义
• 验证数据类型是否正确

**3. 搜索解决方案**
• Google搜索错误信息
• Stack Overflow查找类似问题
• 查阅官方文档

**4. 调试工具**
• 使用print/console.log输出
• 使用IDE调试器
• 逐步排查问题

**5. 寻求帮助**
• 在技术论坛提问
• 描述问题时提供完整信息
• 包含错误信息和代码片段

如果能提供具体的错误信息，我可以给出更针对性的建议。'''
        
        # 默认响应
        return '''你好！我是AI学习导师。👨‍🏫

**当前状态：** AI智能服务暂时运行在基础模式下。

我可以为你提供以下帮助：

**💡 提供学习建议**
• Python、JavaScript、Vue、Django等技术的学习路径
• 编程入门指导和最佳实践

**🔍 解答常见问题**
• 技术选型建议
• 学习方法和资源推荐
• 调试技巧

**📚 推荐学习资源**
• 官方文档链接
• 优质教程推荐
• 实战项目建议

**请告诉我：**
• 你想学习什么技术？
• 遇到了什么具体问题？
• 需要什么学习建议？

我会尽力提供有用的帮助！✨'''
    
    def recommend_courses(self, user_profile: Dict, num_recommendations: int = 5) -> List[Dict]:
        """
        基于用户画像推荐课程
        
        Args:
            user_profile: 用户画像数据
            num_recommendations: 推荐数量
        
        Returns:
            推荐课程列表
        """
        # 这里可以集成更复杂的推荐算法
        # 目前使用简单的基于兴趣的推荐
        
        recommendations = []
        
        # 示例：基于用户学习历史推荐
        if 'learning_history' in user_profile:
            categories = user_profile.get('preferred_categories', [])
            # 这里可以查询数据库获取相关课程
            # 暂时返回模拟数据
            recommendations = [
                {
                    'id': 1,
                    'title': '推荐课程示例',
                    'reason': '基于您的学习历史推荐'
                }
            ]
        
        return recommendations[:num_recommendations]
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        语义搜索
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=top_k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in results
            ]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def add_to_knowledge_base(self, texts: List[str], metadatas: List[Dict] = None):
        """
        添加内容到知识库
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
        """
        if not self.embeddings:
            return
        
        try:
            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            documents = []
            for i, text in enumerate(texts):
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(chunk)
            
            # 创建或更新向量数据库
            if self.vector_store is None:
                self.vector_store = FAISS.from_texts(
                    documents,
                    self.embeddings,
                    metadatas=metadatas
                )
            else:
                self.vector_store.add_texts(documents, metadatas=metadatas)
            
            # 保存到磁盘
            self.vector_store.save_local(self.vector_db_path)
        
        except Exception as e:
            print(f"Error adding to knowledge base: {e}")
    
    def get_embeddings(self, text: str) -> Optional[List[float]]:
        """
        获取文本的向量表示
        
        Args:
            text: 输入文本
        
        Returns:
            向量表示
        """
        try:
            if self.embeddings:
                return self.embeddings.embed_query(text)
            elif self.local_embeddings:
                return self.local_embeddings.encode(text).tolist()
        except Exception as e:
            print(f"Error getting embeddings: {e}")
        
        return None


# 全局AI服务实例
ai_service = AIService()
