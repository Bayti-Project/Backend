from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.interest_requests.models import InterestRequest
from apps.properties.models import Property

User = get_user_model()


class SendInterestRequestTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            full_name='Owner One',
            password='testpass123',
            phone_number='0599000001',
            role='owner',
        )
        self.tenant = User.objects.create_user(
            email='tenant@example.com',
            full_name='Tenant One',
            password='testpass123',
            phone_number='0599000002',
            role='tenant',
        )
        self.property = Property.objects.create(
            title='Apartment in Gaza City',
            description='Nice apartment',
            price=Decimal('500'),
            address='Gaza',
            owner=self.owner,
            status=Property.STATUS_AVAILABLE,
        )

    def get_url(self, property_id=None):
        return reverse(
            'interest_requests:interest-request-create',
            kwargs={'pk': property_id or self.property.id},
        )

    def test_tenant_can_send_interest_request(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['tenant'], self.tenant.id)
        self.assertEqual(response.data['owner'], self.owner.id)
        self.assertEqual(response.data['property'], self.property.id)
        self.assertEqual(InterestRequest.objects.count(), 1)

    def test_unauthenticated_user_cannot_send_request(self):
        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(InterestRequest.objects.count(), 0)

    def test_duplicate_request_is_rejected(self):
        self.client.force_authenticate(user=self.tenant)
        first = self.client.post(self.get_url())
        second = self.client.post(self.get_url())

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(InterestRequest.objects.count(), 1)

    def test_rented_property_is_rejected(self):
        self.property.status = Property.STATUS_RENTED
        self.property.save()

        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(InterestRequest.objects.count(), 0)

    def test_reserved_property_is_allowed(self):
        self.property.status = Property.STATUS_RESERVED
        self.property.save()

        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_tenant_role_is_forbidden(self):
        other_owner = User.objects.create_user(
            email='owner2@example.com',
            full_name='Owner Two',
            password='testpass123',
            phone_number='0599000003',
            role='owner',
        )
        self.client.force_authenticate(user=other_owner)
        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(InterestRequest.objects.count(), 0)

    def test_tenant_cannot_request_own_property(self):
        own_property = Property.objects.create(
            title='Tenant own property',
            description='Owned by a tenant-role user',
            price=Decimal('400'),
            address='Gaza',
            owner=self.tenant,
        )
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.get_url(own_property.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(InterestRequest.objects.count(), 0)

    def test_nonexistent_property_returns_404(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.get_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ManageInterestRequestTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            full_name='Owner One',
            password='testpass123',
            phone_number='0599000001',
            role='owner',
        )
        self.other_owner = User.objects.create_user(
            email='owner2@example.com',
            full_name='Owner Two',
            password='testpass123',
            phone_number='0599000003',
            role='owner',
        )
        self.tenant = User.objects.create_user(
            email='tenant@example.com',
            full_name='Tenant One',
            password='testpass123',
            phone_number='0599000002',
            role='tenant',
        )
        self.property = Property.objects.create(
            title='Apartment in Gaza City',
            description='Nice apartment',
            price=Decimal('500'),
            address='Gaza',
            owner=self.owner,
        )
        self.interest_request = InterestRequest.objects.create(
            tenant=self.tenant,
            property=self.property,
            owner=self.owner,
        )

    def get_url(self, request_id=None):
        return reverse(
            'interest_requests:interest-request-status',
            kwargs={'pk': request_id or self.interest_request.id},
        )

    def test_owner_can_approve_request(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(), {'status': 'approved'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        self.interest_request.refresh_from_db()
        self.assertEqual(self.interest_request.status, 'approved')

    def test_owner_can_reject_request(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(), {'status': 'rejected'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.interest_request.refresh_from_db()
        self.assertEqual(self.interest_request.status, 'rejected')

    def test_updated_at_changes_after_update(self):
        old_updated_at = self.interest_request.updated_at
        self.client.force_authenticate(user=self.owner)
        self.client.put(self.get_url(), {'status': 'approved'}, format='json')

        self.interest_request.refresh_from_db()
        self.assertGreater(self.interest_request.updated_at, old_updated_at)

    def test_other_owner_cannot_change_status(self):
        self.client.force_authenticate(user=self.other_owner)
        response = self.client.put(self.get_url(), {'status': 'approved'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.interest_request.refresh_from_db()
        self.assertEqual(self.interest_request.status, 'pending')

    def test_tenant_cannot_change_status(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.put(self.get_url(), {'status': 'approved'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.interest_request.refresh_from_db()
        self.assertEqual(self.interest_request.status, 'pending')

    def test_invalid_status_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(), {'status': 'accepted'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.interest_request.refresh_from_db()
        self.assertEqual(self.interest_request.status, 'pending')

    def test_pending_status_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(), {'status': 'pending'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_status_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(), {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_gets_401(self):
        response = self.client.put(self.get_url(), {'status': 'approved'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_request_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.get_url(99999), {'status': 'approved'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)