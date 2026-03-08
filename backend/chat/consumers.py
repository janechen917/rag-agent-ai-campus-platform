import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from courses.models import Course, Enrollment

from .models import Message, OnlineUser


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天 WebSocket 消费者。"""

    async def connect(self):
        self.current_course_id = None
        self.course_room_group_name = None
        self.user_group_name = None
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.set_user_online()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'userId': self.user.id,
            'username': self.user.username,
        }))

        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'count': len(online_users),
            'users': online_users,
        }))

    async def disconnect(self, close_code):
        await self.set_user_offline()

        if self.course_room_group_name:
            await self.channel_layer.group_discard(self.course_room_group_name, self.channel_name)

        if self.user_group_name:
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'join_course_room':
            await self.handle_join_course_room(data)
            return

        if message_type == 'leave_course_room':
            await self.handle_leave_course_room()
            return

        if message_type == 'chat_message':
            await self.handle_public_message(data)
            return

        if message_type == 'private_message':
            await self.handle_private_message(data)
            return

        if message_type == 'mark_private_read':
            peer_id = data.get('peerId')
            if peer_id:
                await self.mark_private_read(peer_id)
                await self.channel_layer.group_send(
                    f'user_{self.user.id}',
                    {'type': 'private_read_event', 'peerId': int(peer_id)},
                )
                await self.channel_layer.group_send(
                    f'user_{peer_id}',
                    {'type': 'private_read_event', 'peerId': self.user.id},
                )

    async def handle_join_course_room(self, data):
        course_id = data.get('courseId')
        if not course_id:
            await self.send(text_data=json.dumps({'type': 'error', 'message': '缺少 courseId'}))
            return

        has_access = await self.validate_course_access(course_id)
        if not has_access:
            await self.send(text_data=json.dumps({'type': 'error', 'message': '无权限访问该课程聊天室'}))
            return

        if self.course_room_group_name:
            await self.channel_layer.group_discard(self.course_room_group_name, self.channel_name)

        self.current_course_id = int(course_id)
        self.course_room_group_name = f'course_chat_{self.current_course_id}'
        await self.channel_layer.group_add(self.course_room_group_name, self.channel_name)

        await self.send(text_data=json.dumps({
            'type': 'joined_course_room',
            'courseId': self.current_course_id,
        }))

    async def handle_leave_course_room(self):
        if self.course_room_group_name:
            await self.channel_layer.group_discard(self.course_room_group_name, self.channel_name)
        self.current_course_id = None
        self.course_room_group_name = None
        await self.send(text_data=json.dumps({'type': 'left_course_room'}))

    async def handle_public_message(self, data):
        content = (data.get('content') or '').strip()
        client_message_id = data.get('clientMessageId')

        if not content:
            return

        if not self.current_course_id or not self.course_room_group_name:
            await self.send(text_data=json.dumps({'type': 'error', 'message': '请先加入课程聊天室'}))
            return

        sender_user_type = await self.get_user_type(self.user.id)
        message = await self.save_public_message(content, self.current_course_id)

        await self.channel_layer.group_send(
            self.course_room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': content,
                'username': self.user.username,
                'userId': self.user.id,
                'timestamp': message.created_at.isoformat(),
                'clientMessageId': client_message_id,
                'userType': sender_user_type,
                'courseId': self.current_course_id,
            },
        )

    async def handle_private_message(self, data):
        receiver_id = data.get('receiverId')
        content = (data.get('content') or '').strip()
        client_message_id = data.get('clientMessageId')

        if not receiver_id or not content:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'receiverId 和 content 不能为空'}))
            return

        receiver = await self.get_user_by_id(receiver_id)
        if not receiver:
            await self.send(text_data=json.dumps({'type': 'error', 'message': '接收方不存在'}))
            return

        pair_error = await self.validate_private_pair(self.user.id, receiver.id)
        if pair_error:
            await self.send(text_data=json.dumps({'type': 'error', 'message': pair_error}))
            return

        message = await self.save_private_message(receiver.id, content)
        sender_user_type = await self.get_user_type(self.user.id)
        receiver_user_type = await self.get_user_type(receiver.id)

        payload = {
            'type': 'private_message',
            'id': message.id,
            'content': message.content,
            'sender': {
                'id': self.user.id,
                'username': self.user.username,
                'user_type': sender_user_type,
            },
            'receiver': {
                'id': receiver.id,
                'username': receiver.username,
                'user_type': receiver_user_type,
            },
            'is_read': message.is_read,
            'timestamp': message.created_at.isoformat(),
            'clientMessageId': client_message_id,
        }

        await self.channel_layer.group_send(
            f'user_{receiver.id}',
            {'type': 'private_message_event', 'payload': payload},
        )
        await self.channel_layer.group_send(
            f'user_{self.user.id}',
            {'type': 'private_message_event', 'payload': payload},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event['message_id'],
            'content': event['content'],
            'username': event['username'],
            'userId': event['userId'],
            'timestamp': event['timestamp'],
            'clientMessageId': event.get('clientMessageId'),
            'userType': event.get('userType'),
            'courseId': event.get('courseId'),
        }))

    async def private_message_event(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def private_read_event(self, event):
        await self.send(text_data=json.dumps({'type': 'private_read', 'peerId': event['peerId']}))

    @database_sync_to_async
    def save_public_message(self, content, course_id):
        course = Course.objects.get(id=course_id)
        return Message.objects.create(
            sender=self.user,
            course=course,
            content=content,
            message_type='text',
        )

    @database_sync_to_async
    def validate_course_access(self, course_id):
        try:
            course = Course.objects.get(id=course_id)
            if course.instructor_id == self.user.id:
                return True
            return Enrollment.objects.filter(
                course=course,
                user=self.user,
            ).exists()
        except Course.DoesNotExist:
            return False

    @database_sync_to_async
    def save_private_message(self, receiver_id, content):
        receiver = User.objects.get(id=receiver_id)
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content,
            message_type='text',
        )

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_type(self, user_id):
        try:
            user = User.objects.select_related('profile').get(id=user_id)
            if hasattr(user, 'profile') and user.profile.user_type:
                return user.profile.user_type
        except User.DoesNotExist:
            pass
        return 'student'

    @database_sync_to_async
    def validate_private_pair(self, sender_id, receiver_id):
        if int(sender_id) == int(receiver_id):
            return '不能给自己发送私信'

        try:
            sender = User.objects.select_related('profile').get(id=sender_id)
            receiver = User.objects.select_related('profile').get(id=receiver_id)
        except User.DoesNotExist:
            return '用户不存在'

        if not hasattr(sender, 'profile') or not hasattr(receiver, 'profile'):
            return '用户资料不完整，无法发送私信'

        if sender.profile.user_type == receiver.profile.user_type:
            return '仅支持教师与学生之间私信'

        return None

    @database_sync_to_async
    def mark_private_read(self, peer_id):
        Message.objects.filter(
            sender_id=peer_id,
            receiver=self.user,
            receiver__isnull=False,
            is_read=False,
        ).update(is_read=True)

    @database_sync_to_async
    def set_user_online(self):
        OnlineUser.objects.update_or_create(
            user=self.user,
            defaults={'channel_name': self.channel_name},
        )

    @database_sync_to_async
    def set_user_offline(self):
        OnlineUser.objects.filter(user=self.user).delete()

    @database_sync_to_async
    def get_online_users(self):
        online_users = OnlineUser.objects.select_related('user').all()
        return [
            {'id': ou.user.id, 'username': ou.user.username}
            for ou in online_users
        ]
