import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Comment, Post


class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="Test content", author=self.user, published=True
        )

    def test_get_posts_list(self):
        response = self.client.get("/api/v1/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Post")

    def test_get_post_detail(self):
        response = self.client.get(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Post")

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Post", "content": "New content", "published": True}
        response = self.client.post("/api/v1/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Post")
        self.assertEqual(response.data["author"]["username"], "testuser")

    def test_create_post_unauthenticated(self):
        data = {"title": "New Post", "content": "New content", "published": True}
        response = self.client.post("/api/v1/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Updated Post",
            "content": "Updated content",
            "published": False,
        }
        response = self.client.put(f"/api/v1/posts/{self.post.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Post")

    def test_update_post_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Updated Post", "content": "Updated content"}
        response = self.client.put(f"/api/v1/posts/{self.post.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_post_action(self):
        self.client.force_authenticate(user=self.user)
        self.post.published = False
        self.post.save()

        response = self.client.post(f"/api/v1/posts/{self.post.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertTrue(self.post.published)

    def test_unpublish_post_action(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/v1/posts/{self.post.id}/unpublish/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertFalse(self.post.published)


class CommentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="Test content", author=self.user
        )
        self.comment = Comment.objects.create(
            content="Test comment", post=self.post, author=self.user
        )

    def test_get_comments_list(self):
        response = self.client.get("/api/v1/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Test comment")

    def test_get_comment_detail(self):
        response = self.client.get(f"/api/v1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Test comment")

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {"content": "New comment", "post": self.post.id}
        response = self.client.post("/api/v1/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "New comment")

    def test_create_comment_unauthenticated(self):
        data = {"content": "New comment", "post": self.post.id}
        response = self.client.post("/api/v1/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {"content": "Updated comment", "post": self.post.id}
        response = self.client.put(f"/api/v1/comments/{self.comment.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Updated comment")

    def test_update_comment_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"content": "Updated comment", "post": self.post.id}
        response = self.client.put(f"/api/v1/comments/{self.comment.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/v1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_users_list(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "testuser")

    def test_get_user_detail(self):
        response = self.client.get(f"/api/v1/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_user_create_not_allowed(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
        }
        response = self.client.post("/api/v1/users/", data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update_not_allowed(self):
        data = {"username": "updateduser", "email": "updated@example.com"}
        response = self.client.put(f"/api/v1/users/{self.user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_delete_not_allowed(self):
        response = self.client.delete(f"/api/v1/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
