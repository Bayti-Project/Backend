from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SocialIdentity


User = get_user_model()


class GoogleLoginTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='google_user@example.com',
            full_name='Google User',
            phone_number='0599000011',
            password='testpass123',
            role='tenant',
            account_type='individual',
        )

        self.url = '/api/auth/google/'

    @patch('apps.accounts.views.verify_google_token')
    def test_existing_user_can_login_with_google(self, mock_verify):
        mock_verify.return_value = {
            'sub': 'google-sub-123',
            'email': 'google_user@example.com',
            'email_verified': True,
        }

        response = self.client.post(
            self.url,
            {'id_token': 'fake-google-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(
            response.data['user']['email'],
            self.user.email,
        )

        self.assertTrue(
            SocialIdentity.objects.filter(
                user=self.user,
                provider=SocialIdentity.PROVIDER_GOOGLE,
                provider_user_id='google-sub-123',
            ).exists()
        )

    @patch('apps.accounts.views.verify_google_token')
    def test_google_login_does_not_create_new_user(self, mock_verify):
        mock_verify.return_value = {
            'sub': 'new-google-sub-456',
            'email': 'new_google@example.com',
            'email_verified': True,
        }

        before_count = User.objects.count()

        response = self.client.post(
            self.url,
            {'id_token': 'fake-google-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.count(), before_count)

    @patch('apps.accounts.views.verify_google_token')
    def test_invalid_google_token_is_rejected(self, mock_verify):
        mock_verify.side_effect = ValueError('Invalid Google token.')

        response = self.client.post(
            self.url,
            {'id_token': 'invalid-token'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_missing_google_token_is_rejected(self):
        response = self.client.post(
            self.url,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

class NormalLoginTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='normal_user@example.com',
            full_name='Normal User',
            phone_number='0599000033',
            password='testpass123',
            role='owner',
            account_type='office',
        )

        self.url = '/api/auth/login/'

    def test_normal_login_still_works(self):
        response = self.client.post(
            self.url,
            {
                'email': 'normal_user@example.com',
                'password': 'testpass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(
            response.data['user']['email'],
            self.user.email,
        )
        self.assertEqual(
            response.data['user']['role'],
            self.user.role,
        )
