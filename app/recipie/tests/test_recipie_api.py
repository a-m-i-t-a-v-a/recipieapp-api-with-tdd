"""Test for recipie APIs"""
from decimal import Decimal 
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 
from rest_framework import status 
from rest_framework.test import APIClient
from core.models import Recipie 
from recipie.serializers import RecipieSerializer ,RecipieDetailSerializer

RECIPIES_URL=reverse('recipie:recipie-list')

def detail_url(recipie_id):
    """Create and return a recipie detail URL"""
    return reverse('recipie:recipie-detail',args=[recipie_id])

def create_recipie(user,**params):
    """Create and return a sample recipie"""
    defaults={
        'title':'Sample recipie title',
        'time_minutes':22,
        'price':Decimal('5.25'),
        'description':'Sample description',
        'link':'https://example.com/recipie.pdf'
    }
    defaults.update(params)
    recipie=Recipie.objects.create(user=user,**defaults)
    return recipie 

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicRecipieAPITests(TestCase):
    """Test unauthenticated API requests"""
    
    def setUp(self):
        self.client=APIClient()
        
    def test_auth_required(self):
        """Test auth is required to call API"""
        res=self.client.get(RECIPIES_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipieAPITests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client=APIClient()
        self.user=create_user(email='user@example.com',password='testpass123')
        #self.user=get_user_model().objects.create_user(
        #    'user@example.com',
        #    'testpass123'
        #)
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipies(self):
        """Test retrieveing a list of recipies."""
        create_recipie(user=self.user)
        create_recipie(user=self.user)
        
        res=self.client.get(RECIPIES_URL)
        
        recipies=Recipie.objects.all().order_by('-id')
        serializer=RecipieSerializer(recipies,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        
    def test_recipie_list_limited_to_user(self):
        """Test list of recipies is limited to authenticated users only"""
        #other_user=get_user_model().objects.create_user(
        #    'other@example.com',
        #    'password123',
        #)
        other_user=create_user(email='other@example.com',password='password123')        
        create_recipie(user=other_user)
        create_recipie(user=self.user)
        
        res=self.client.get(RECIPIES_URL)
        
        recipies=Recipie.objects.filter(user=self.user)
        serializer=RecipieSerializer(recipies,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        
    def test_create_recipie(self):
        """Test creating a recipie"""
        payload={
            'title':'Sample Recipie',
            'time_minutes':30,
            'description':'Sample description',
            'price':Decimal('5.99')
        }        
        res=self.client.post(RECIPIES_URL,payload) #api/recipies/recipie 
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipie=Recipie.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipie,k),v)
        self.assertEqual(recipie.user,self.user)
        
    def test_get_recipie_detail(self):
        """Test to get recipie detail"""
        recipie=create_recipie(user=self.user)
        
        url=detail_url(recipie.id)
        res=self.client.get(url)
        
        print("Actual data:", res.data)
        print("Expected data:", RecipieDetailSerializer(recipie).data)
        
        serializer=RecipieDetailSerializer(recipie)
        self.assertEqual(res.data,serializer.data)
        
    def test_partial_update(self):
        """Test partial update of the recipie"""
        original_link='https://example.com/recipie.pdf'
        recipie=create_recipie(
            user=self.user,
            title='Sample recipie title',
            link=original_link
        )
        payload={'title':'New recipie title'}
        url=detail_url(recipie.id)
        res=self.client.patch(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipie.refresh_from_db()
        self.assertEqual(recipie.title,payload['title'])
        self.assertEqual(recipie.link,original_link)
        self.assertEqual(recipie.user,self.user)
        
    def test_full_update(self):
        """Test full update of recipie"""
        recipie=create_recipie(
            user=self.user,
            title='Sample Recipie title 2',
            link='https://sample.com/recipie.pdf',
            description='Sample tasty new recipie by mom'
        )              
        payload={
            'title':'New recipie title by mom',
            'link':'https://example.com/new-recipie.pdf',
            'description':'Mom has made a new recipie',
            'time_minutes':10,
            'price':Decimal('8.99')
        }
        url=detail_url(recipie.id)
        res=self.client.put(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipie.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(recipie,k),v)
        self.assertEqual(recipie.user,self.user)
        
        

