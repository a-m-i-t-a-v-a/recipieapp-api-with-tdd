"""Test for recipie APIs"""
from decimal import Decimal 
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse 
from rest_framework import status 
from rest_framework.test import APIClient
from core.models import Recipie,Tag,Ingredient
from recipie.serializers import RecipieSerializer ,RecipieDetailSerializer
import tempfile
import os 
from PIL import Image 

RECIPIES_URL=reverse('recipie:recipie-list')

def detail_url(recipie_id):
    """Create and return a recipie detail URL"""
    return reverse('recipie:recipie-detail',args=[recipie_id])

def image_upload_url(recipie_id):
    """Create and return an image upload URL."""
    return reverse('recipie:recipie-upload-image',args=[recipie_id])

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
        
    def test_update_user_returns_error(self):
        """Test changing the recipie user results in an error"""
        new_user=create_user(email='test4@example.com',password='testpass123')
        recipie=create_recipie(user=self.user)
        
        payload={'user':new_user.id}
        url=detail_url(recipie.id)
        self.client.patch(url,payload)
        
        recipie.refresh_from_db()
        self.assertEqual(recipie.user,self.user)
        
    def test_delete_recipie(self):
        """Test deleting a recipie successful"""
        recipie=create_recipie(user=self.user)
        url=detail_url(recipie.id)
        res=self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipie.objects.filter(id=recipie.id).exists())
        
    def test_delete_recipie_other_users_recipie_errors(self):
        """Test trying to delete another users recipie gives error"""
        new_user=create_user(email='testuser@example.com',password='testpass123')
        recipie=create_recipie(user=new_user)
        url=detail_url(recipie.id)
        res=self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipie.objects.filter(id=recipie.id).exists())
        
    def test_create_recipie_with_new_tags(self):
        """Test creating a recipie with new tags"""
        payload={
            'title':'Chocolate Cake',
            'time_minutes':30,
            'price':Decimal('8.99'),
            'tags':[{'name':'Chocolate'},{'name':'Dinner'}]
        }        
        res=self.client.post(RECIPIES_URL,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipies=Recipie.objects.filter(user=self.user)
        self.assertEqual(recipies.count(),1)
        recipie=recipies[0]
        self.assertEqual(recipie.tags.count(),2) # line 192 there are 2 tags
        for tag in payload['tags']:
            exists=recipie.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipie_with_existing_tags(self):
        """Test creating a recipie with existing tag"""
        tag_american=Tag.objects.create(user=self.user,name='American')
        payload={
            'title':'Veg Burger',
            'time_minutes':10,
            'price':Decimal('4.50'),
            'tags':[{'name':'American'},{'name':'Breakfast'}]
        }
        res=self.client.post(RECIPIES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipies=Recipie.objects.filter(user=self.user)
        self.assertEqual(recipies.count(),1)
        recipie=recipies[0]
        self.assertEqual(recipie.tags.count(),2)
        self.assertIn(tag_american,recipie.tags.all())
        for tag in payload['tags']:
            exists=recipie.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipie"""
        recipie=create_recipie(user=self.user)
        payload={
            'tags':[{'name':'Lunch'}]
        }
        url=detail_url(recipie.id)
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_tag=Tag.objects.get(user=self.user,name='Lunch')
        self.assertIn(new_tag,recipie.tags.all())
        
    def test_update_recipie_assign_tag(self):
        """Test assigning an existing tag when updating a recipie"""
        tag_breakfast=Tag.objects.create(user=self.user,name='Breakfast')
        recipie=create_recipie(user=self.user)
        recipie.tags.add(tag_breakfast)
        
        tag_lunch=Tag.objects.create(user=self.user,name='Lunch')
        payload={'tags':[{'name':'Lunch'}]}
        url=detail_url(recipie.id)
        
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(tag_lunch,recipie.tags.all())
        self.assertNotIn(tag_breakfast,recipie.tags.all())
        
    def test_clear_recipie_tags(self):
        """Test clearing a recipie tags"""
        tag=Tag.objects.create(user=self.user,name='Dessert')
        recipie=create_recipie(user=self.user)
        recipie.tags.add(tag)
        
        payload={'tags':[]}
        url=detail_url(recipie.id)
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipie.tags.count(),0)
        
    def test_create_recipie_with_new_ingredients(self):
        """Test creating a recipie with new ingredients"""
        payload={
            'title':'Paneer Tacos',
            'time_minutes':60,
            'price':Decimal('7.55'),
            'ingredients':[{'name':'Paneer'},{'name':'Salt'}]
        }
        res=self.client.post(RECIPIES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipies=Recipie.objects.filter(user=self.user)
        self.assertEqual(recipies.count(),1)
        recipie=recipies[0]
        self.assertEqual(recipie.ingredients.count(),2)
        for ingredient in payload['ingredients']:
            exists=recipie.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipie_with_existing_ingredients(self):
        """Test creating a new recipie with existing ingredient"""
        ingredient=Ingredient.objects.create(user=self.user,name='Potato')
        payload={
            'title':'German Soup',
            'time_minutes':25,
            'price':Decimal('5.25'),
            'ingredients':[{'name':'Potato'},{'name':'Mashed'}],
        }
        res=self.client.post(RECIPIES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipies=Recipie.objects.filter(user=self.user)
        self.assertEqual(recipies.count(),1)
        recipie=recipies[0]
        self.assertEqual(recipie.ingredients.count(),2)
        self.assertIn(ingredient,recipie.ingredients.all())
        for ingredient in payload['ingredients']:
            exists=recipie.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipie"""
        recipie=create_recipie(user=self.user)
        payload={'ingredients':[{'name':'Limes'}]}
        url=detail_url(recipie.id)
        
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_ingredient=Ingredient.objects.get(user=self.user,name='Limes')
        self.assertIn(new_ingredient,recipie.ingredients.all())
        
    def test_update_recipie_assign_ingredient(self):
        """Test assigning an existing ingredient when assigning a recipie"""
        ingredient1=Ingredient.objects.create(user=self.user,name='Pepper')
        recipie=create_recipie(user=self.user)
        recipie.ingredients.add(ingredient1)
        
        ingredient2=Ingredient.objects.create(user=self.user,name='Sugar')
        payload={'ingredients':[{'name':'Sugar'}]}
        url=detail_url(recipie.id)
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(ingredient2,recipie.ingredients.all())
        self.assertNotIn(ingredient1,recipie.ingredients.all())
        
    def test_clear_recipie_ingredients(self):
        """Test clearing a recipies ingredient"""
        ingredient=Ingredient.objects.create(user=self.user,name='Garlic')
        recipie=create_recipie(user=self.user)
        recipie.ingredients.add(ingredient)
        
        payload={'ingredients':[]}
        url=detail_url(recipie.id)
        res=self.client.patch(url,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipie.ingredients.count(),0)
        
    def test_filter_by_tags(self):
        """Test filtering recipies by tags."""
        r1=create_recipie(user=self.user,title='Hobbit Mushroom Curry')
        r2=create_recipie(user=self.user,title='Elvish Lambas Bread')
        tag1=Tag.objects.create(user=self.user,name='Vegan')
        tag2=Tag.objects.create(user=self.user,name='Vegetarian')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3=create_recipie(user=self.user,title='Choco Lava Cake')
        
        params={'tags':f'{tag1.id},{tag2.id}'}
        res=self.client.get(RECIPIES_URL,params)
        
        s1=RecipieSerializer(r1)
        s2=RecipieSerializer(r2)
        s3=RecipieSerializer(r3)
        self.assertIn(s1.data,res.data)
        self.assertIn(s2.data,res.data)
        self.assertNotIn(s3.data,res.data)
        
    def test_filter_by_ingredients(self):
        """Test filtering recipies by ingredients"""
        r1=create_recipie(user=self.user,title='Posh Beans on Toast')
        r2=create_recipie(user=self.user,title='Sahi Paneer')
        in1=Ingredient.objects.create(user=self.user,name='Feta Cheese')
        in2=Ingredient.objects.create(user=self.user,name='Paneer')
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3=create_recipie(user=self.user,title='American Veg Chopsuey')
        
        params={'ingredients':f'{in1.id},{in2.id}'}
        res=self.client.get(RECIPIES_URL,params)
        
        s1=RecipieSerializer(r1)
        s2=RecipieSerializer(r2)
        s3=RecipieSerializer(r3)
        self.assertIn(s1.data,res.data)
        self.assertIn(s2.data,res.data)
        self.assertNotIn(s3.data,res.data)
        
class ImageUploadTests(TestCase):
    """Tests for the image upload API."""
    def setUp(self):
        self.client=APIClient()
        self.user=get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )
        self.client.force_authenticate(self.user)
        self.recipie=create_recipie(user=self.user)
        
    def tearDown(self): #this runs AFTER test runs
        self.recipie.image.delete()
        
    def test_upload_image(self):
        """Test uploading image to a recipie"""
        url=image_upload_url(self.recipie.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img=Image.new('RGB',(10,10))
            img.save(image_file,format='JPEG')
            image_file.seek(0)
            payload={'image':image_file}
            res=self.client.post(url,payload,format='multipart')
            
        self.recipie.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipie.image.path))
        
    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url=image_upload_url(self.recipie.id)
        payload={'image':'notanimage'}
        res=self.client.post(url,payload,format='multipart')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
            
    
        
    
        
        
        
        
            
            
        
        

