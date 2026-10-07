from django.urls import path

from notifications.views import (
    CreateNotificationView,
    NotificationListView,
    NotificationReadStatusView,
    MarkAllNotificationsReadView,
)


urlpatterns = [
    path(
        'create/',
        CreateNotificationView.as_view(),
        name='create-notification',
    ),
    path(
        'mark-all-read/',
        MarkAllNotificationsReadView.as_view(),
        name='mark-all-notifications-read',
    ),
    path(
        '',
        NotificationListView.as_view(),
        name='notification-list',
    ),
    path(
        '<int:pk>/',
        NotificationReadStatusView.as_view(),
        name='notification-read-status',
    ),
]