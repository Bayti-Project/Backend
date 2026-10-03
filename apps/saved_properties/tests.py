from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.properties.models import Property
from apps.saved_properties.models import SavedProperty

User = get_user_model()


class SavePropertyTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='sp_owner@example.com',
            full_name='SP Owner',
            password='testpass123',
            phone_number='0599400001',
            role='owner',
        )
        self.tenant = User.objects.create_user(
            email='sp_tenant@example.com',
            full_name='SP Tenant',
            password='testpass123',
            phone_number='0599400002',
            role='tenant',
        )
        self.property = Property.objects.create(
            title='Save Test Property', description='d', price=Decimal('500'),
            address='Gaza', owner=self.owner,
        )
        self.save_url = reverse('save-property', kwargs={'pk': self.property.id})
        self.list_url = reverse('saved-properties')

    def test_authenticated_user_can_save_property(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(self.save_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavedProperty.objects.count(), 1)

    def test_unauthenticated_user_cannot_save(self):
        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_saving_same_property_twice_fails(self):
        self.client.force_authenticate(user=self.tenant)
        self.client.post(self.save_url)
        response = self.client.post(self.save_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SavedProperty.objects.count(), 1)

    def test_user_can_unsave_property(self):
        self.client.force_authenticate(user=self.tenant)
        self.client.post(self.save_url)
        response = self.client.delete(self.save_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SavedProperty.objects.count(), 0)

    def test_unsaving_not_saved_property_returns_404(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.delete(self.save_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_returns_only_own_saved_properties(self):
        other_tenant = User.objects.create_user(
            email='sp_tenant2@example.com',
            full_name='Other SP Tenant',
            password='testpass123',
            phone_number='0599400003',
            role='tenant',
        )
        SavedProperty.objects.create(user=self.tenant, property=self.property)
        SavedProperty.objects.create(user=other_tenant, property=self.property)

        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['saved_properties']), 1)

    def test_list_empty_returns_message(self):
        self.client.force_authenticate(user=self.tenant)
        response = self.client.get(self.list_url)

        self.assertEqual(response.data['saved_properties'], [])
        self.assertIn('message', response.data)


class SharePropertyTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='share_owner@example.com',
            full_name='Share Owner',
            password='testpass123',
            phone_number='0599400004',
            role='owner',
        )
        self.property = Property.objects.create(
            title='Share Test Property', description='d', price=Decimal('500'),
            address='Gaza', owner=self.owner,
        )
        self.share_url = reverse('share-property', kwargs={'pk': self.property.id})

    def test_anyone_can_get_share_link(self):
        response = self.client.get(self.share_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['link'], f'https://bayti.ps/property/{self.property.id}'
        )

    def test_rented_property_cannot_be_shared(self):
        self.property.status = Property.STATUS_RENTED
        self.property.save()

        response = self.client.get(self.share_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)