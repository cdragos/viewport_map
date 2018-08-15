from unittest.mock import Mock, patch
import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from viewport_map.models import Location


class LocationViewsTests(TestCase):

    def setUp(self):
        self.location_1 = Location.objects.create(
            latitude=45.943161, longitude=24.966761, address='_address_1')
        self.location_2 = Location.objects.create(
            latitude=47.516232, longitude=14.550072, address='_address_2')

        session = self.client.session
        session[settings.CREDENTIALS_KEY] = True
        session.save()

    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_get_locations(self, mock_oauth):
        mock_oauth.return_value = Mock(access_token_expired=False)
        resp = self.client.get(reverse('locations'))
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertTrue(data)
        self.assertIn('locations', data)
        self.assertEqual(len(data['locations']), 2)

        self.assertEqual(data['locations'][0], {
            'latitude': self.location_1.latitude,
            'longitude': self.location_1.longitude,
            'address': self.location_1.address
        })
        self.assertEqual(data['locations'][1], {
            'latitude': self.location_2.latitude,
            'longitude': self.location_2.longitude,
            'address': self.location_2.address
        })

    @patch('viewport_map.views.LocationTable')
    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_post_new_location(self, mock_oauth, mock_fusiontable_service):
        mock_oauth.return_value = Mock(access_token_expired=False)
        service_mock = Mock()
        mock_fusiontable_service.build_service.return_value = service_mock

        data = {'latitude': 38.670049, 'longitude': -99.565798,
                'address': '_address_new'}
        resp = self.client.post(
            reverse('locations'), json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'location': data})

        location = Location.objects.filter(
            latitude=data['latitude'], longitude=data['longitude'],
            address=data['address']).first()
        self.assertTrue(location)

        mock_fusiontable_service.build_service.assert_called_once()
        service_mock.save.assert_called_once_with(location)

    @patch('viewport_map.views.LocationTable')
    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_post_duplicate_location(self, mock_oauth, mock_fusiontable_service):
        mock_oauth.return_value = Mock(access_token_expired=False)
        service_mock = Mock()
        mock_fusiontable_service.build_service.return_value = service_mock

        data = {'latitude': self.location_1.latitude,
                'longitude': self.location_1.longitude,
                'address': '_address_new'}
        resp = self.client.post(
            reverse('locations'), json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.json(), {
                '__all__': ['Location with this Latitude and Longitude already exists.']})

    @patch('viewport_map.views.LocationTable')
    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_post_service_fails_reverts_transaction(
            self, mock_oauth, mock_fusiontable_service):
        mock_oauth.return_value = Mock(access_token_expired=False)
        service_mock = Mock()
        service_mock.save.side_effect = ValueError()
        mock_fusiontable_service.build_service.return_value = service_mock

        data = {'latitude': 38.670049, 'longitude': -99.565798,
                'address': '_address_new'}

        with self.assertRaises(ValueError):
            self.client.post(
                reverse('locations'), json.dumps(data),
                content_type='application/json')

        self.assertEqual(Location.objects.count(), 2)

    @patch('viewport_map.views.LocationTable')
    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_clear_locations(self, mock_oauth, mock_fusiontable_service):
        mock_oauth.return_value = Mock(access_token_expired=False)
        service_mock = Mock()
        mock_fusiontable_service.build_service.return_value = service_mock

        resp = self.client.delete(reverse('clear_locations'))
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(Location.objects.count(), 0)

        mock_fusiontable_service.build_service.assert_called_once()
        service_mock.clear.assert_called_once()

    @patch('viewport_map.views.LocationTable')
    @patch('google_auth.decorators.OAuth2Credentials.from_json')
    def test_clear_service_fails_reverts_transaction(
            self, mock_oauth, mock_fusiontable_service):
        mock_oauth.return_value = Mock(access_token_expired=False)
        service_mock = Mock()
        service_mock.clear.side_effect = ValueError()
        mock_fusiontable_service.build_service.return_value = service_mock

        with self.assertRaises(ValueError):
            self.client.delete(reverse('clear_locations'))
        self.assertEqual(Location.objects.count(), 2)
