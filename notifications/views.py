from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.services import create_notification


class CreateNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('type')

        if not title or not message or not notification_type:
            return Response(
                {
                    'message': 'title, message and type are required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = create_notification(
            user=request.user,
            title=title,
            message=message,
            type=notification_type,
        )

        serializer = NotificationSerializer(notification)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            {
                'notifications': serializer.data
            },
            status=status.HTTP_200_OK
        )


class NotificationReadStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        notification = Notification.objects.filter(
            pk=pk,
            user=request.user
        ).first()

        if not notification:
            return Response(
                {
                    'message': 'Notification not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        is_read = request.data.get('is_read')

        if not isinstance(is_read, bool):
            return Response(
                {
                    'message': 'is_read must be true or false.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        notification.is_read = is_read
        notification.save(update_fields=['is_read'])

        serializer = NotificationSerializer(notification)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )