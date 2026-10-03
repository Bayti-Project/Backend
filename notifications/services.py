from notifications.models import Notification


def create_notification(user, title, message, type):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type,
    )