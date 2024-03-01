from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models 

class ModelTest(TestCase):
    """Test Models"""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email='test@examle.com'
        password='testpass123'
        user=get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_normalize(self):
        sample_emails=[
            ['test1@EXAMPLE.com','test1@example.com'],
            ['Test2@Example.com','Test2@example.com'],
            ['TEST3@EXAMPLE.COM','TEST3@example.com'],
            ['test4@example.COM','test4@example.com']
        ]
        for email,expected in sample_emails:
            user=get_user_model().objects.create_user(email,'sample123')
            self.assertEqual(user.email,expected)
            
    def test_new_user_without_email_raise_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')
            
    def test_create_superuser(self):
        """Test creating a superuser"""
        user=get_user_model().objects.create_superuser(
            'pillu@gmail.com',
            'Pillu@100'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
            
    def test_create_recipie(self):
        """Test creating a recipie is successful"""
        user=get_user_model().objects.create_user(
            'tester@example.com',
            'testpass123'
        )
        recipie=models.Recipie.objects.create(
            user=user,
            title='Sample recipie name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipie description',
        )
        self.assertEqual(str(recipie),recipie.title)