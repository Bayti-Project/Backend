from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.properties.models import Property  

User = get_user_model()

class PropertyFeaturesTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='features_owner@example.com',
            full_name='Features Owner',
            password='testpass123',
            phone_number='0599100001',
        )
        self.create_url = reverse('properties:property-create')

    def base_payload(self):
        return {
            'title': 'Feature Test Property',
            'description': 'Testing features',
            'price': '1000',
            'address': 'Gaza',
        }

    # TEST 1: create without any features
    def test_create_without_features(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.create_url, self.base_payload(), format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        prop = Property.objects.get(id=response.data['id'])
        self.assertFalse(prop.has_solar)
        self.assertFalse(prop.is_furnished)
        self.assertFalse(prop.has_gym)

    # TEST 2: create with old features only
    def test_create_with_old_features_only(self):
        payload = self.base_payload()
        payload.update({'has_solar': True, 'has_water_tank': True})
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.create_url, payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        prop = Property.objects.get(id=response.data['id'])
        self.assertTrue(prop.has_solar)
        self.assertTrue(prop.has_water_tank)
        self.assertFalse(prop.is_furnished)

    # TEST 3: create with new features only
    def test_create_with_new_features_only(self):
        payload = self.base_payload()
        payload.update({'is_furnished': True, 'has_balcony': True})
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.create_url, payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        prop = Property.objects.get(id=response.data['id'])
        self.assertTrue(prop.is_furnished)
        self.assertTrue(prop.has_balcony)
        self.assertFalse(prop.has_solar)

    # TEST 4: create with all features (old + new)
    def test_create_with_all_features(self):
        payload = self.base_payload()
        payload.update({
            'has_solar': True,
            'has_generator_line': True,
            'has_main_grid': True,
            'has_water_tank': True,
            'has_private_well': True,
            'is_furnished': True,
            'has_elevator': True,
            'has_balcony': True,
            'has_parking': True,
            'has_central_ac': True,
            'has_shared_pool': True,
            'has_gym': True,
        })
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.create_url, payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        prop = Property.objects.get(id=response.data['id'])
        for field in [
            'has_solar', 'has_generator_line', 'has_main_grid',
            'has_water_tank', 'has_private_well', 'is_furnished',
            'has_elevator', 'has_balcony', 'has_parking',
            'has_central_ac', 'has_shared_pool', 'has_gym',
        ]:
            self.assertTrue(getattr(prop, field), f'{field} should be True')

    # TEST 5: GET property returns each feature with correct value
    def test_get_property_returns_features_correctly(self):
        prop = Property.objects.create(
            title='Detail Feature Test',
            description='desc',
            price=Decimal('700'),
            address='Gaza',
            owner=self.owner,
            has_solar=True,
            has_balcony=True,
            has_gym=False,
        )
        url = reverse('properties:property-detail', kwargs={'pk': prop.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_solar'])
        self.assertTrue(response.data['has_balcony'])
        self.assertFalse(response.data['has_gym'])
        self.assertFalse(response.data['is_furnished'])

    # TEST 6: property created before the new fields existed still works
    def test_old_property_without_new_fields_still_works(self):
        old_prop = Property.objects.create(
            title='Old Property',
            description='Created before feature migration (simulated)',
            price=Decimal('300'),
            address='Gaza',
            owner=self.owner,
        )
        url = reverse('properties:property-detail', kwargs={'pk': old_prop.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_furnished'])
        self.assertFalse(response.data['has_elevator'])
        self.assertFalse(response.data['has_gym'])

    # TEST 7: search/list results also expose the features
    def test_search_results_include_features(self):
        Property.objects.create(
            title='Searchable Feature Property',
            description='desc',
            price=Decimal('450'),
            address='Gaza',
            owner=self.owner,
            status=Property.STATUS_AVAILABLE,
            governorate=Property.GOVERNORATE_GAZA,
            has_parking=True,
            has_central_ac=True,
        )
        search_url = reverse('properties:property-search')
        response = self.client.get(search_url, {'governorate': 'gaza'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        matching = [r for r in results if r['title'] == 'Searchable Feature Property']
        self.assertEqual(len(matching), 1)
        self.assertTrue(matching[0]['has_parking'])
        self.assertTrue(matching[0]['has_central_ac'])
        self.assertFalse(matching[0]['has_gym'])

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

