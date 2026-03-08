from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message
from .serializers import MessageSerializer, UserSerializer, ConversationSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """Private message APIs."""

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver').order_by('-created_at')

    def _validate_private_pair(self, sender, receiver):
        if sender == receiver:
            return '不能给自己发送私信'

        if not hasattr(sender, 'profile') or not hasattr(receiver, 'profile'):
            return '用户资料不完整，无法发送私信'

        # Restrict private messaging to teacher-student pairing.
        if sender.profile.user_type == receiver.profile.user_type:
            return '仅支持教师与学生之间私信'

        return None

    @action(detail=False, methods=['get'])
    def users(self, request):
        """List users available for private chat."""
        me = request.user
        if not hasattr(me, 'profile'):
            return Response([], status=status.HTTP_200_OK)

        if me.profile.user_type == 'teacher':
            qs = User.objects.filter(profile__user_type='student').exclude(id=me.id)
        else:
            qs = User.objects.filter(profile__user_type='teacher').exclude(id=me.id)

        serializer = UserSerializer(qs.order_by('username'), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get private conversation history with one user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': '缺少 user_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': '目标用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        pair_error = self._validate_private_pair(request.user, target_user)
        if pair_error:
            return Response({'error': pair_error}, status=status.HTTP_400_BAD_REQUEST)

        messages = Message.objects.filter(
            Q(sender=request.user, receiver=target_user) |
            Q(sender=target_user, receiver=request.user)
        ).select_related('sender', 'receiver').order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Conversation summary list for current user."""
        me = request.user
        private_msgs = Message.objects.filter(
            Q(sender=me) | Q(receiver=me),
            receiver__isnull=False
        ).select_related('sender', 'receiver').order_by('-created_at')

        seen = set()
        items = []

        for msg in private_msgs:
            peer = msg.receiver if msg.sender_id == me.id else msg.sender
            if not peer:
                continue
            if peer.id in seen:
                continue
            seen.add(peer.id)

            unread_count = Message.objects.filter(
                sender=peer,
                receiver=me,
                is_read=False,
                receiver__isnull=False
            ).count()

            items.append({
                'user': peer,
                'last_message': msg.content,
                'last_message_at': msg.created_at,
                'unread_count': unread_count,
            })

        serializer = ConversationSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark one message as read."""
        msg = self.get_object()
        if msg.receiver_id != request.user.id:
            return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)

        msg.is_read = True
        msg.save(update_fields=['is_read'])
        return Response({'message': '已标记为已读'})

    @action(detail=False, methods=['post'])
    def mark_conversation_read(self, request):
        """Mark all messages in one conversation as read."""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': '缺少 user_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            peer = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': '目标用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        Message.objects.filter(
            sender=peer,
            receiver=request.user,
            is_read=False,
            receiver__isnull=False
        ).update(is_read=True)

        return Response({'message': '会话已全部标记已读'})

    def create(self, request, *args, **kwargs):
        """Send a private message via HTTP (fallback for WebSocket)."""
        receiver_id = request.data.get('receiver_id')
        content = (request.data.get('content') or '').strip()

        if not receiver_id or not content:
            return Response({'error': 'receiver_id 和 content 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': '接收方不存在'}, status=status.HTTP_404_NOT_FOUND)

        pair_error = self._validate_private_pair(request.user, receiver)
        if pair_error:
            return Response({'error': pair_error}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            message_type='text',
            content=content,
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
