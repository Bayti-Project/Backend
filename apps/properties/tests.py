from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.properties.models import Property

User = get_user_model()


class PropertySearchTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner1@example.com',
            full_name='Owner One',
            password='testpass123',
            phone_number='0599000001',
        )
        self.search_url = reverse('properties:property-search')

        self.p_available_gaza = Property.objects.create(
            title='Apartment in Gaza City',
            description='Nice apartment',
            price=Decimal('500'),
            address='Gaza',
            owner=self.owner,
            status=Property.STATUS_AVAILABLE,
            governorate=Property.GOVERNORATE_GAZA,
            area='gaza_city',
            property_type=Property.TYPE_APARTMENT,
            bedrooms=2,
            has_solar=True,
            has_water_tank=True,
        )
        self.p_reserved_gaza = Property.objects.create(
            title='Villa in Gaza City',
            description='Big villa',
            price=Decimal('1500'),
            address='Gaza',
            owner=self.owner,
            status=Property.STATUS_RESERVED,
            governorate=Property.GOVERNORATE_GAZA,
            area='gaza_city',
            property_type=Property.TYPE_VILLA,
            bedrooms=4,
            has_generator_line=True,
        )
        self.p_rented_gaza = Property.objects.create(
            title='Rented apartment',
            description='Not available',
            price=Decimal('600'),
            address='Gaza',
            owner=self.owner,
            status=Property.STATUS_RENTED,
            governorate=Property.GOVERNORATE_GAZA,
            area='gaza_city',
            property_type=Property.TYPE_APARTMENT,
            bedrooms=2,
        )
        self.p_khanyounis = Property.objects.create(
            title='Land in Khan Younis',
            description='Empty land',
            price=Decimal('300'),
            address='Khan Younis',
            owner=self.owner,
            status=Property.STATUS_AVAILABLE,
            governorate=Property.GOVERNORATE_KHAN_YOUNIS,
            area='khan_younis_city',
            property_type=Property.TYPE_LAND,
            has_main_grid=True,
            has_private_well=True,
        )

    # ---------- US-11 ----------

    def test_search_by_governorate(self):
        response = self.client.get(self.search_url, {'governorate': 'gaza'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.p_available_gaza.id, ids)
        self.assertIn(self.p_reserved_gaza.id, ids)
        self.assertNotIn(self.p_khanyounis.id, ids)

    def test_search_by_property_type(self):
        response = self.client.get(self.search_url, {'property_type': 'land'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_khanyounis.id])

    def test_search_by_governorate_and_property_type(self):
        response = self.client.get(
            self.search_url, {'governorate': 'gaza', 'property_type': 'apartment'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_available_gaza.id])

    def test_search_without_authentication(self):
        self.client.credentials()
        response = self.client.get(self.search_url, {'governorate': 'gaza'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_no_results(self):
        response = self.client.get(
            self.search_url, {'governorate': 'gaza', 'bedrooms': 99}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_rented_properties_excluded(self):
        response = self.client.get(self.search_url, {'governorate': 'gaza'})
        ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(self.p_rented_gaza.id, ids)

    def test_available_properties_appear(self):
        response = self.client.get(self.search_url, {'governorate': 'gaza'})
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.p_available_gaza.id, ids)

    def test_reserved_properties_appear(self):
        response = self.client.get(self.search_url, {'governorate': 'gaza'})
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.p_reserved_gaza.id, ids)

    # ---------- US-12 ----------

    def test_filter_min_price(self):
        response = self.client.get(self.search_url, {'min_price': 1000})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_reserved_gaza.id])

    def test_filter_max_price(self):
        response = self.client.get(self.search_url, {'max_price': 400})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_khanyounis.id])

    def test_filter_min_and_max_price(self):
        response = self.client.get(
            self.search_url, {'min_price': 400, 'max_price': 600}
        )
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.p_available_gaza.id, ids)

    def test_filter_bedrooms(self):
        response = self.client.get(self.search_url, {'bedrooms': 4})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_reserved_gaza.id])

    def test_filter_electricity_solar(self):
        response = self.client.get(self.search_url, {'electricity': 'solar'})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_available_gaza.id])

    def test_filter_electricity_multiple_is_or(self):
        response = self.client.get(
            self.search_url, {'electricity': 'solar,main_grid'}
        )
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.p_available_gaza.id, ids)
        self.assertIn(self.p_khanyounis.id, ids)

    def test_filter_water_tank(self):
        response = self.client.get(self.search_url, {'water': 'tank'})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_available_gaza.id])

    def test_filter_water_well(self):
        response = self.client.get(self.search_url, {'water': 'well'})
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_khanyounis.id])

    def test_multiple_filters_together(self):
        response = self.client.get(
            self.search_url,
            {'governorate': 'gaza', 'property_type': 'apartment', 'max_price': 550},
        )
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.p_available_gaza.id])

    def test_invalid_negative_price(self):
        response = self.client.get(self.search_url, {'min_price': -5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_numeric_value(self):
        response = self.client.get(self.search_url, {'min_price': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_choice_value(self):
        response = self.client.get(self.search_url, {'property_type': 'castle'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_min_greater_than_max(self):
        response = self.client.get(
            self.search_url, {'min_price': 1000, 'max_price': 500}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_request_zero_results(self):
        response = self.client.get(self.search_url, {'bedrooms': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    # ---------- US-15 ----------

    def test_no_results_with_nearby_area_shows_suggestions(self):
        response = self.client.get(
            self.search_url, {'area': 'gaza_city', 'bedrooms': 99}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])
        self.assertTrue(len(response.data['suggestions']) > 0)

    def test_results_exist_no_suggestions(self):
        response = self.client.get(self.search_url, {'area': 'gaza_city'})
        self.assertNotEqual(response.data['results'], [])
        self.assertEqual(response.data['suggestions'], [])

    def test_suggestions_not_in_results(self):
        response = self.client.get(
            self.search_url, {'area': 'gaza_city', 'bedrooms': 99}
        )
        result_ids = [item.get('id') for item in response.data['results']]
        self.assertEqual(result_ids, [])

    def test_invalid_area_for_governorate(self):
        response = self.client.get(
            self.search_url, {'governorate': 'rafah', 'area': 'gaza_city'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

