import unittest
from unittest.mock import patch
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_history(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)

    @patch('app.get_health_advice')
    @patch('app.analyze_meal')
    def test_analyze(self, mock_analyze, mock_advice):
        mock_analyze.return_value = {
            "calories": 400, "protein_g": 30.5, "carbs_g": 40.0,
            "fat_g": 10.0, "fiber_g": 5.0, "sugar_g": 2.0, "meal_summary": "Test summary"
        }
        mock_advice.return_value = "Great job eating protein!"

        response = self.client.post('/analyze', data={
            'meal_description': 'Chicken and rice',
            'calorie_goal': '2000',
            'protein_goal': '150',
            'water_goal': '2'
        })
        
        self.assertEqual(response.status_code, 200)

    def test_analyze_empty_input(self):
        # Empty string should fail due to validation
        response = self.client.post('/analyze', data={
            'meal_description': '    ', 
            'calorie_goal': '2000',
            'protein_goal': '150',
            'water_goal': '2'
        })
        self.assertEqual(response.status_code, 400)
        
        # HTML strings that get stripped completely should fail
        response = self.client.post('/analyze', data={
            'meal_description': '<script>alert()</script>', 
            'calorie_goal': '2000',
            'protein_goal': '150',
            'water_goal': '2'
        })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
