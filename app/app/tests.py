from django.test import SimpleTestCase 
from app import calc 

class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        res=calc.add(98,67)
        self.assertEqual(res,165)
        
    def test_multiply_numbers(self):
        res=calc.multiply(10,15)
        self.assertEqual(res,150)