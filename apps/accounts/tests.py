from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from apps.properties.models import Property
from apps.interest_requests.models import InterestRequest
from apps.saved_properties.models import SavedProperty

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


class OwnerProfileTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='profile_owner@example.com',
            full_name='Profile Owner',
            password='testpass123',
            phone_number='0599200001',
            role='owner',
        )
        self.other_owner = User.objects.create_user(
            email='profile_owner2@example.com',
            full_name='Other Owner',
            password='testpass123',
            phone_number='0599200002',
            role='owner',
        )
        self.tenant = User.objects.create_user(
            email='profile_tenant@example.com',
            full_name='Profile Tenant',
            password='testpass123',
            phone_number='0599200003',
            role='tenant',
        )
        self.url = reverse('owner-profile')

    def test_tenant_cannot_access_owner_profile(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_gets_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_with_no_data_gets_zero_stats(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stats']['total_properties'], 0)
        self.assertEqual(response.data['stats']['active_properties'], 0)
        self.assertEqual(response.data['stats']['rented_properties'], 0)
        self.assertEqual(response.data['stats']['total_interest_requests'], 0)
        self.assertEqual(response.data['recent_interest_requests'], [])
        self.assertEqual(response.data['recent_properties'], [])

    def test_stats_counts_are_correct(self):
        Property.objects.create(
            title='Available 1', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner, status=Property.STATUS_AVAILABLE,
        )
        Property.objects.create(
            title='Available 2', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner, status=Property.STATUS_AVAILABLE,
        )
        Property.objects.create(
            title='Reserved 1', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner, status=Property.STATUS_RESERVED,
        )
        rented_property = Property.objects.create(
            title='Rented 1', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner, status=Property.STATUS_RENTED,
        )
        # property belonging to a different owner - must not be counted
        Property.objects.create(
            title='Other owner property', description='d', price=Decimal('100'),
            address='Gaza', owner=self.other_owner, status=Property.STATUS_AVAILABLE,
        )

        tenant2 = User.objects.create_user(
            email='profile_tenant2@example.com',
            full_name='Profile Tenant 2',
            password='testpass123',
            phone_number='0599200004',
            role='tenant',
        )

        InterestRequest.objects.create(
            tenant=self.tenant, property=rented_property, owner=self.owner,
            status=InterestRequest.STATUS_PENDING,
        )
        InterestRequest.objects.create(
            tenant=tenant2, property=rented_property, owner=self.owner,
            status=InterestRequest.STATUS_APPROVED,
        )

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.data['stats']['total_properties'], 4)
        self.assertEqual(response.data['stats']['active_properties'], 2)
        self.assertEqual(response.data['stats']['rented_properties'], 1)
        self.assertEqual(response.data['stats']['total_interest_requests'], 2)

    def test_recent_properties_limited_to_three_and_ordered(self):
        for i in range(5):
            Property.objects.create(
                title=f'Property {i}', description='d', price=Decimal('100'),
                address='Gaza', owner=self.owner, status=Property.STATUS_AVAILABLE,
            )

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data['recent_properties']), 3)
        self.assertEqual(response.data['recent_properties'][0]['title'], 'Property 4')

    def test_recent_interest_requests_include_tenant_and_property_info(self):
        prop = Property.objects.create(
            title='Test Property', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner, status=Property.STATUS_AVAILABLE,
        )
        InterestRequest.objects.create(
            tenant=self.tenant, property=prop, owner=self.owner,
        )

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data['recent_interest_requests']), 1)
        req_data = response.data['recent_interest_requests'][0]
        self.assertEqual(req_data['tenant_name'], 'Profile Tenant')
        self.assertEqual(req_data['property_title'], 'Test Property')
        self.assertEqual(req_data['status'], 'pending')

    def test_owner_cannot_see_other_owners_data(self):
        Property.objects.create(
            title='Other property', description='d', price=Decimal('100'),
            address='Gaza', owner=self.other_owner, status=Property.STATUS_AVAILABLE,
        )

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.data['stats']['total_properties'], 0)
        self.assertEqual(response.data['recent_properties'], [])


class TenantProfileTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='tp_owner@example.com',
            full_name='TP Owner',
            password='testpass123',
            phone_number='0599300001',
            role='owner',
        )
        self.tenant = User.objects.create_user(
            email='tp_tenant@example.com',
            full_name='TP Tenant',
            password='testpass123',
            phone_number='0599300002',
            role='tenant',
        )
        self.url = reverse('tenant-profile')

    def test_owner_cannot_access_tenant_profile(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_gets_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_with_no_data_gets_zero_stats(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stats']['total_interest_requests'], 0)
        self.assertEqual(response.data['stats']['approved_requests'], 0)
        self.assertEqual(response.data['stats']['rejected_requests'], 0)
        self.assertEqual(response.data['stats']['pending_requests'], 0)
        self.assertEqual(response.data['stats']['saved_properties_count'], 0)
        self.assertEqual(response.data['recent_interest_requests'], [])
        self.assertEqual(response.data['recent_saved_properties'], [])

    def test_request_stats_are_correct(self):
        prop1 = Property.objects.create(
            title='P1', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        prop2 = Property.objects.create(
            title='P2', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        prop3 = Property.objects.create(
            title='P3', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        InterestRequest.objects.create(
            tenant=self.tenant, property=prop1, owner=self.owner,
            status=InterestRequest.STATUS_APPROVED,
        )
        InterestRequest.objects.create(
            tenant=self.tenant, property=prop2, owner=self.owner,
            status=InterestRequest.STATUS_REJECTED,
        )
        InterestRequest.objects.create(
            tenant=self.tenant, property=prop3, owner=self.owner,
            status=InterestRequest.STATUS_PENDING,
        )

        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)

        self.assertEqual(response.data['stats']['total_interest_requests'], 3)
        self.assertEqual(response.data['stats']['approved_requests'], 1)
        self.assertEqual(response.data['stats']['rejected_requests'], 1)
        self.assertEqual(response.data['stats']['pending_requests'], 1)

    def test_recent_interest_requests_show_property_info(self):
        prop = Property.objects.create(
            title='Test Prop', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        InterestRequest.objects.create(
            tenant=self.tenant, property=prop, owner=self.owner,
        )

        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)

        req_data = response.data['recent_interest_requests'][0]
        self.assertEqual(req_data['property_title'], 'Test Prop')
        self.assertEqual(req_data['status'], 'pending')

    def test_saved_properties_count_and_recent_list(self):
        prop1 = Property.objects.create(
            title='Saved 1', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        prop2 = Property.objects.create(
            title='Saved 2', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        SavedProperty.objects.create(user=self.tenant, property=prop1)
        SavedProperty.objects.create(user=self.tenant, property=prop2)

        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)

        self.assertEqual(response.data['stats']['saved_properties_count'], 2)
        self.assertEqual(len(response.data['recent_saved_properties']), 2)
        self.assertEqual(
            response.data['recent_saved_properties'][0]['property']['title'], 'Saved 2'
        )

    def test_another_tenants_data_not_mixed(self):
        other_tenant = User.objects.create_user(
            email='tp_tenant2@example.com',
            full_name='Other Tenant',
            password='testpass123',
            phone_number='0599300003',
            role='tenant',
        )
        prop = Property.objects.create(
            title='Other tenant prop', description='d', price=Decimal('100'),
            address='Gaza', owner=self.owner,
        )
        InterestRequest.objects.create(
            tenant=other_tenant, property=prop, owner=self.owner,
        )
        SavedProperty.objects.create(user=other_tenant, property=prop)

        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.url)

        self.assertEqual(response.data['stats']['total_interest_requests'], 0)
        self.assertEqual(response.data['stats']['saved_properties_count'], 0)