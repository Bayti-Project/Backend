from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import SocialIdentity, User
from .social_auth import verify_google_token
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import ChangePasswordSerializer


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    'message': 'Account created successfully.',
                    'user': {
                        'id': user.id,
                        'full_name': user.full_name,
                        'email': user.email,
                        'phone_number': user.phone_number,
                        'role': user.role,
                        'account_type': user.account_type,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'message': 'Login successful.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'full_name': user.full_name,
                        'email': user.email,
                        'role': user.role,
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            return Response(
                {'message': 'Password updated successfully. Please log in again.'},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class LogoutView(APIView):
        permission_classes = [IsAuthenticated]

def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('id_token')

        if not token:
            return Response(
                {'error': 'Google ID token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            google_data = verify_google_token(token)
        except ValueError as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        google_sub = google_data['sub']
        email = google_data['email'].lower()

        social_identity = SocialIdentity.objects.filter(
            provider=SocialIdentity.PROVIDER_GOOGLE,
            provider_user_id=google_sub,
        ).select_related('user').first()

        if social_identity:
            user = social_identity.user

        else:
            user = User.objects.filter(email__iexact=email).first()

            if not user:
                return Response(
                    {
                        'error': (
                            'No existing Bayti account is associated with '
                            'this Google account.'
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            SocialIdentity.objects.create(
                user=user,
                provider=SocialIdentity.PROVIDER_GOOGLE,
                provider_user_id=google_sub,
            )

        if not user.is_active:
            return Response(
                {'error': 'This account is inactive.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'Google login successful.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role,
                }
            },
            status=status.HTTP_200_OK
        )
