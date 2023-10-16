from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Board, Pin, Like, Comment


User = get_user_model()

class TestBoards(APITestCase):

    def setUp(self):
        self.user_json = {
            'email': 'test@test.test',
            'password': 'qweasdzxc22',
        }
        self.user = User.objects.create_user(**self.user_json)
        self.client.force_authenticate(self.user)

    def test_create_board(self):
        data_json = {
            'title': 'Test Board',
            'description': 'Test descrioption'
        }
        response = self.client.post(reverse('add_board'), data=data_json, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data_json['title'])
        self.assertEqual(Board.objects.count(), 1)
    
    def test_get_boards_through_profile(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        response = self.client.get(reverse('profile', kwargs={'slug': self.user.profile.slug}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['boards'][0]['id'], board.id)
    
    def test_get_single_board(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        response = self.client.get(reverse('boards', kwargs={'slug': self.user.profile.slug, 'pk': board.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], board.title)
    
    def test_get_invalid_single_board(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        response = self.client.get(reverse('boards', kwargs={'slug': self.user.profile.slug, 'pk': 10}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_board(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        data = {
            'title': 'Board 1',
            'description': 'New description'
        }
        response = self.client.put(reverse('boards', kwargs={'slug': self.user.profile.slug, 'pk': board.id}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], data['description'])

    def test_partial_update_board(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        data = {
            'description': 'New description'
        }
        response = self.client.patch(reverse('boards', kwargs={'slug': self.user.profile.slug, 'pk': board.id}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], data['description'])
    
    def test_delete_board(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        response = self.client.delete(reverse('boards', kwargs={'slug': self.user.profile.slug, 'pk': board.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)


class TestPins(APITestCase):

    def temporary_image(self):
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile("test.jpg", bts.getvalue())
    
    def setUp(self):
        self.user_json = {
            'email': 'test@test.test',
            'password': 'qweasdzxc22',
        }
        self.user = User.objects.create_user(**self.user_json)
        self.client.force_authenticate(self.user)
        self.image = self.temporary_image()

    def test_get_all_pins(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        pin2 = Pin.objects.create(user=self.user, board=board, title='Pin 2')
        response = self.client.get(reverse('pins-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], pin.title)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_pin(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        data = {
            'user':self.user.id,
            'board':board.id,
            'title':'Pin 1',
            'image':self.image
        }
        response = self.client.post(reverse('pins-list'), data=data, format='multipart')
        pin = Pin.objects.all()[0]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pin.objects.count(), 1)
        self.assertEqual(response.data['id'], pin.id)
        pin.image.delete(True)

    def test_get_single_pin(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        response = self.client.get(reverse('pins-detail', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], pin.id)

    def test_update_pin(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        data = {
            'title':'Updated Pin 1',
        }
        response = self.client.put(reverse('pins-detail', kwargs={'pk': pin.id}), data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
    
    def test_delete_pin(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')

        response = self.client.delete(reverse('pins-detail', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Pin.objects.count(), 0)


class TestLikePin(APITestCase):

    def setUp(self):
        self.user_json = {
            'email': 'test@test.test',
            'password': 'qweasdzxc22',
        }
        self.user = User.objects.create_user(**self.user_json)
        self.client.force_authenticate(self.user)

    def test_get_all_likes(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        response = self.client.get(reverse('likes', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_create_like(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        response = self.client.post(reverse('likes', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pin.likes.count(), 1)
    
    def test_create_second_like_by_same_user(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        Like.objects.create(user=self.user, pin=pin)
        response = self.client.post(reverse('likes', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(pin.likes.count(), 1)
    
    def test_delete_like(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        Like.objects.create(user=self.user, pin=pin)
        response = self.client.delete(reverse('likes', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(pin.likes.count(), 0)


class TestComments(APITestCase):

    def setUp(self):
        self.user_json = {
            'email': 'test@test.test',
            'password': 'qweasdzxc22',
        }
        self.user = User.objects.create_user(**self.user_json)
        self.client.force_authenticate(self.user)

    def test_create_comment(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        data = {
            'content': 'Test Comment'
        }
        response = self.client.post(reverse('add_comment', kwargs={'pk': pin.id}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pin.comments.count(), 1)

    def test_get_all_comments_through_pin(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        comment = Comment.objects.create(content='Test Comment', pin=pin, user=self.user)
        response = self.client.get(reverse('pins-detail', kwargs={'pk': pin.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['content'], comment.content)
    
    def test_get_single_comment(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        comment = Comment.objects.create(content='Test Comment', pin=pin, user=self.user)
        response = self.client.get(reverse('comments', kwargs={'pk': comment.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], comment.content)
    
    def test_update_comment(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        comment = Comment.objects.create(content='Test Comment', pin=pin, user=self.user)
        data = {
            'content': 'Updated Test Comment'
        }
        response = self.client.put(reverse('comments', kwargs={'pk': comment.id}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], data['content'])
    
    def test_delete_comment(self):
        board = Board.objects.create(user=self.user, title='Board 1')
        pin = Pin.objects.create(user=self.user, board=board, title='Pin 1')
        comment = Comment.objects.create(content='Test Comment', pin=pin, user=self.user)
        response = self.client.delete(reverse('comments', kwargs={'pk': comment.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(pin.comments.count(), 0)
