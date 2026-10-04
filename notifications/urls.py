from django.urls import path

from notifications.views import (
    CreateNotificationView,
    NotificationListView,
    NotificationReadStatusView,
)


urlpatterns = [
    path(
        'create/',
        CreateNotificationView.as_view(),
        name='create-notification',
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