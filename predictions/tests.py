from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import Resolver404, resolve, reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from backend.predictions.views import hv_predict, prediction_under_development


DEVELOPING_ENDPOINTS = (
    '/api/v1/prediction/yield_strength',
    '/api/v1/prediction/tensile_strength',
    '/api/v1/prediction/phase',
    '/api/v1/prediction/irradiation_hardening',
    '/api/v1/prediction/irradiation_embrittlement',
)

DEVELOPING_RESPONSE = {
    'code': 200,
    'status': 'developing',
    'message': 'Prediction model is under development',
}


class VersionedPredictionApiTests(SimpleTestCase):
    """Isolated endpoint tests: no database or real prediction model is used."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = SimpleNamespace(
            is_authenticated=True,
            pk=7,
            username='prediction-test-user',
        )

    def _call(self, path, method='post', authenticated=True, data=None):
        request = getattr(self.factory, method)(path, data or {}, format='json')
        if authenticated:
            force_authenticate(request, user=self.user)
        return resolve(path).func(request)

    def test_developing_endpoints_return_the_shared_response(self):
        for path in DEVELOPING_ENDPOINTS:
            with self.subTest(path=path):
                self.assertIs(resolve(path).func, prediction_under_development)
                response = self._call(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, DEVELOPING_RESPONSE)

    def test_developing_endpoints_require_authentication_and_post(self):
        for path in DEVELOPING_ENDPOINTS:
            with self.subTest(path=path, case='authentication'):
                response = self._call(path, authenticated=False)
                self.assertEqual(response.status_code, 401)
            with self.subTest(path=path, case='method'):
                response = self._call(path, method='get')
                self.assertEqual(response.status_code, 405)

    def test_versioned_paths_are_exactly_defined_without_trailing_slashes(self):
        expected_paths = {
            'prediction-hardness': '/api/v1/prediction/hardness',
            'prediction-yield-strength': '/api/v1/prediction/yield_strength',
            'prediction-tensile-strength': '/api/v1/prediction/tensile_strength',
            'prediction-phase': '/api/v1/prediction/phase',
            'prediction-irradiation-hardening': '/api/v1/prediction/irradiation_hardening',
            'prediction-irradiation-embrittlement': '/api/v1/prediction/irradiation_embrittlement',
        }
        for route_name, path in expected_paths.items():
            with self.subTest(route_name=route_name):
                self.assertEqual(reverse(route_name), path)
                with self.assertRaises(Resolver404):
                    resolve(f'{path}/')

    @patch('backend.predictions.views._insert_prediction_record')
    @patch('backend.predictions.views.predict_hv')
    def test_versioned_hardness_alias_reuses_the_legacy_view(
        self,
        mock_predict_hv,
        mock_insert_record,
    ):
        new_path = '/api/v1/prediction/hardness'
        legacy_path = '/api/predictions/hv/'
        self.assertIs(resolve(new_path).func, hv_predict)
        self.assertIs(resolve(legacy_path).func, hv_predict)

        mock_predict_hv.return_value = {
            'Pred_HV': 321.5,
            'model_path': 'mock-model.pkl',
            'runtime': {'python': 'test'},
            'normalized_composition': {'Al': 1.0},
        }

        def prediction_record(**kwargs):
            return {
                'id': 1,
                'prediction_type': 'hv',
                'input_data': {'composition': kwargs['composition']},
                'output_data': {'Pred_HV': kwargs['pred_hv']},
                'created_by_id': kwargs['user_id'],
                'created_at': None,
            }

        mock_insert_record.side_effect = prediction_record
        request_body = {'composition': {'Al': 100}}

        new_response = self._call(new_path, data=request_body)
        legacy_response = self._call(legacy_path, data=request_body)

        self.assertEqual(new_response.status_code, 201)
        self.assertEqual(legacy_response.status_code, 201)
        self.assertEqual(new_response.data, legacy_response.data)
        self.assertEqual(new_response.data['output_data']['Pred_HV'], 321.5)
        self.assertEqual(mock_predict_hv.call_count, 2)
        self.assertEqual(mock_insert_record.call_count, 2)
