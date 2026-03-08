import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, OnlineUser, ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天WebSocket消费者"""
    
    async def connect(self):
        """WebSocket连接"""
        self.room_name = 'global'  # 默认全局聊天室
        self.room_group_name = f'chat_{self.room_name}'
        self.user_group_name = None
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # 加入聊天室组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Join private user channel.
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'userId': self.user.id,
            'username': self.user.username
        }))
        
        # 记录在线用户
        await self.set_user_online()
        
        # 广播用户加入消息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
        
        # 发送在线用户列表
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'count': len(online_users),
            'users': online_users
        }))
    
    async def disconnect(self, close_code):
        """WebSocket断开连接"""
        # 移除在线记录
        await self.set_user_offline()
        
        # 广播用户离开消息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.user.username if not self.user.is_anonymous else 'Anonymous',
                'user_id': self.user.id if not self.user.is_anonymous else None
            }
        )
        
        # 离开聊天室组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """接收消息"""
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            content = data.get('content', '')
            client_message_id = data.get('clientMessageId')
            sender_user_type = await self.get_user_type(self.user.id)
            
            # 保存消息到数据库
            message = await self.save_message(content)
            
            # 广播消息到聊天室
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'content': content,
                    'username': self.user.username,
                    'userId': self.user.id,
                    'timestamp': message.created_at.isoformat(),
                    'clientMessageId': client_message_id,
                    'userType': sender_user_type
                }
            )
        elif message_type == 'private_message':
            receiver_id = data.get('receiverId')
            content = (data.get('content') or '').strip()
            client_message_id = data.get('clientMessageId')

            if not receiver_id or not content:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'receiverId 和 content 不能为空'
                }))
                return

            receiver = await self.get_user_by_id(receiver_id)
            if not receiver:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '接收方不存在'
                }))
                return

            pair_error = await self.validate_private_pair(self.user.id, receiver.id)
            if pair_error:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': pair_error
                }))
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
                'clientMessageId': client_message_id
            }

            await self.channel_layer.group_send(
                f'user_{receiver.id}',
                {
                    'type': 'private_message_event',
                    'payload': payload
                }
            )

            await self.channel_layer.group_send(
                f'user_{self.user.id}',
                {
                    'type': 'private_message_event',
                    'payload': payload
                }
            )
        elif message_type == 'mark_private_read':
            peer_id = data.get('peerId')
            if peer_id:
                await self.mark_private_read(peer_id)

                await self.channel_layer.group_send(
                    f'user_{self.user.id}',
                    {
                        'type': 'private_read_event',
                        'peerId': int(peer_id)
                    }
                )

                await self.channel_layer.group_send(
                    f'user_{peer_id}',
                    {
                        'type': 'private_read_event',
                        'peerId': self.user.id
                    }
                )
    
    async def chat_message(self, event):
        """处理聊天消息"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event['message_id'],
            'content': event['content'],
            'username': event['username'],
            'userId': event['userId'],
            'timestamp': event['timestamp'],
            'clientMessageId': event.get('clientMessageId'),
            'userType': event.get('userType')
        }))
    
    async def user_joined(self, event):
        """处理用户加入"""
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'online_count': len(online_users),
            'online_users': online_users
        }))
    
    async def user_left(self, event):
        """处理用户离开"""
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'online_count': len(online_users),
            'online_users': online_users
        }))

    async def private_message_event(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def private_read_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'private_read',
            'peerId': event['peerId']
        }))
    
    @database_sync_to_async
    def save_message(self, content):
        """保存消息到数据库"""
        return Message.objects.create(
            sender=self.user,
            content=content,
            message_type='text'
        )

    @database_sync_to_async
    def save_private_message(self, receiver_id, content):
        receiver = User.objects.get(id=receiver_id)
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content,
            message_type='text'
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
            is_read=False
        ).update(is_read=True)
    
    @database_sync_to_async
    def set_user_online(self):
        """设置用户在线状态"""
        OnlineUser.objects.update_or_create(
            user=self.user,
            defaults={'channel_name': self.channel_name}
        )
    
    @database_sync_to_async
    def set_user_offline(self):
        """设置用户离线状态"""
        OnlineUser.objects.filter(user=self.user).delete()
    
    @database_sync_to_async
    def get_online_users(self):
        """获取在线用户列表"""
        online_users = OnlineUser.objects.select_related('user').all()
        return [
            {
                'id': ou.user.id,
                'username': ou.user.username,
            }
            for ou in online_users
        ]
