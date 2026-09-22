from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class LogoutTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="logouttest@example.com",
            full_name="Logout Test User",
            phone_number="0599999999",
            password="TestPassword123!"
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

        self.url = "/api/auth/logout/"

    def authenticate(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_logout_with_valid_refresh_token(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Logout successful."
        )

    def test_logout_without_refresh_token(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Refresh token is required."
        )

    def test_logout_with_invalid_refresh_token(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {"refresh": "invalid-refresh-token"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Invalid or expired refresh token."
        )

    def test_logout_without_authentication(self):
        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_is_blacklisted_after_logout(self):
        self.authenticate()

        first_response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK
        )

        second_response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
