import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, OnlineUser, ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天WebSocket消费者"""
    
    async def connect(self):
        """WebSocket连接"""
        self.room_name = 'global'  # 默认全局聊天室
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # 加入聊天室组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
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
    
    async def receive(self, text_data):
        """接收消息"""
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            content = data.get('content', '')
            
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
                    'timestamp': message.created_at.isoformat()
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
            'timestamp': event['timestamp']
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
    
    @database_sync_to_async
    def save_message(self, content):
        """保存消息到数据库"""
        return Message.objects.create(
            sender=self.user,
            content=content,
            message_type='text'
        )
    
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
