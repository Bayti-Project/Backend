from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

User = get_user_model()


class NotificationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='notif_user@example.com',
            full_name='Notif User',
            password='testpass123',
            phone_number='0599600001',
        )
        self.other_user = User.objects.create_user(
            email='notif_other@example.com',
            full_name='Notif Other',
            password='testpass123',
            phone_number='0599600002',
        )

    def test_list_returns_only_own_notifications(self):
        Notification.objects.create(
            user=self.user, title='T1', message='M1', type='interest_request',
        )
        Notification.objects.create(
            user=self.other_user, title='T2', message='M2', type='interest_request',
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['notifications']), 1)

    def test_list_empty_returns_empty_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notifications'], [])

    def test_filter_unread_only(self):
        Notification.objects.create(
            user=self.user, title='Read', message='M', type='interest_request',
            is_read=True,
        )
        Notification.objects.create(
            user=self.user, title='Unread', message='M', type='interest_request',
            is_read=False,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/?filter=unread')

        self.assertEqual(len(response.data['notifications']), 1)
        self.assertEqual(response.data['notifications'][0]['title'], 'Unread')

    def test_filter_by_type(self):
        Notification.objects.create(
            user=self.user, title='Request', message='M', type='interest_request',
        )
        Notification.objects.create(
            user=self.user, title='Status', message='M', type='interest_request_status',
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/?filter=interest_request_status')

        self.assertEqual(len(response.data['notifications']), 1)
        self.assertEqual(response.data['notifications'][0]['title'], 'Status')

    def test_filter_all_returns_everything(self):
        Notification.objects.create(
            user=self.user, title='A', message='M', type='interest_request',
        )
        Notification.objects.create(
            user=self.user, title='B', message='M', type='interest_request_status',
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/?filter=all')

        self.assertEqual(len(response.data['notifications']), 2)

    def test_mark_all_as_read(self):
        Notification.objects.create(
            user=self.user, title='A', message='M', type='interest_request',
            is_read=False,
        )
        Notification.objects.create(
            user=self.user, title='B', message='M', type='interest_request',
            is_read=False,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/notifications/mark-all-read/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread_count = Notification.objects.filter(
            user=self.user, is_read=False
        ).count()
        self.assertEqual(unread_count, 0)

    def test_mark_all_as_read_does_not_affect_other_users(self):
        Notification.objects.create(
            user=self.other_user, title='Other', message='M', type='interest_request',
            is_read=False,
        )

        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/notifications/mark-all-read/')

        other_notification = Notification.objects.get(user=self.other_user)
        self.assertFalse(other_notification.is_read)

    def test_mark_all_read_requires_authentication(self):
        response = self.client.patch('/api/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
