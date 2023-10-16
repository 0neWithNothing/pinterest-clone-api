from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from user.models import Profile
from user.token import email_verification_token


User = get_user_model()

class TestRegisterUser(APITestCase):

    def test_register_user(self):
        user_json = {
            "email": "test@test.test",
            "password": "qweasdzxc22",
            "password2": "qweasdzxc22",
        }
        response = self.client.post(reverse('register'), data=user_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all()[0].email, user_json["email"])


class TestUser(APITestCase):

    def setUp(self):
        self.user_json = {
            "email": "test@test.test",
            "password": "qweasdzxc22",
        }
        self.user = User.objects.create_user(**self.user_json)
    
    def test_activate_user(self):
        token = email_verification_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.assertFalse(self.user.is_active)
        response = self.client.get(reverse('activate', kwargs={'uidb64':uid, 'token':token}), format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)
    
    def test_login_valid_user(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post(reverse('login'), data=self.user_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_login_invalid_user(self):
        self.user.is_active = True
        self.user.save()
        invalid_data = {
            'email': self.user_json['email'],
            'password': 'wrong_pass'
        }
        response = self.client.post(reverse('login'), data=invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_non_activ_user(self):
        response = self.client.post(reverse('login'), data=self.user_json, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('logout'), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_not_authenticated_user(self):
        response = self.client.post(reverse('logout'), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestProfile(APITestCase):

    def setUp(self):
        self.user_json = {
            "email": "test@test.test",
            "password": "qweasdzxc22",
        }
        self.user = User.objects.create_user(**self.user_json)

    def test_create_profile_on_user_create(self):
        self.assertEqual(Profile.objects.all()[0].user.id, self.user.id)
    
    def test_get_profile(self):
        response = self.client.get(reverse('profile', kwargs={'slug': self.user.profile.slug}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_partial_update_profile(self):
        self.client.force_authenticate(self.user)
        data = {
            'first_name': 'First Name'
        }
        response = self.client.patch(reverse('profile', kwargs={'slug': self.user.profile.slug}), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], data["first_name"])
    
    def test_update_profile(self):
        self.client.force_authenticate(self.user)
        new_data = {
            'username': 'test',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'bio': 'Bio',
            'avatar': None
        }
        response = self.client.put(reverse('profile', kwargs={'slug': self.user.profile.slug}), data=new_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], new_data["first_name"])
    

class TestFollow(APITestCase):

    def setUp(self):
        self.user_json = {
            "email": "test@test.test",
            "password": "qweasdzxc22",
        }
        self.user = User.objects.create_user(**self.user_json)

    def test_get_follow(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('follows', kwargs={'slug': self.user.profile.slug}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])
    
    def test_post_follow(self):
        user2_data = {
            "email": "test222@test.test",
            "password": "qweasdzxc22",
        }
        user2 = User.objects.create_user(**user2_data)
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('follows', kwargs={'slug': user2.profile.slug}), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user2.followers.all()[0].user, self.user)
        self.assertEqual(self.user.following.all()[0].following_user, user2)
    
    def test_delete_follow(self):
        user2_data = {
            "email": "test222@test.test",
            "password": "qweasdzxc22",
        }
        user2 = User.objects.create_user(**user2_data)
        self.client.force_authenticate(self.user)
        self.client.post(reverse('follows', kwargs={'slug': user2.profile.slug}), format="json")
        self.assertEqual(user2.followers.count(), 1)
        response = self.client.delete(reverse('follows', kwargs={'slug': user2.profile.slug}), format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user2.followers.count(), 0)
