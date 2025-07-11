from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Comment, Post


class PermissionTest(APITestCase):
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

    def test_anonymous_can_read_posts(self):
        response = self.client.get("/api/v1/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_posts(self):
        data = {"title": "New Post", "content": "New content"}
        response = self.client.post("/api/v1/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_update_posts(self):
        data = {"title": "Updated Post", "content": "Updated content"}
        response = self.client.put(f"/api/v1/posts/{self.post.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_delete_posts(self):
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_posts(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Post", "content": "New content"}
        response = self.client.post("/api/v1/posts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_author_can_update_posts(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Updated Post", "content": "Updated content"}
        response = self.client.put(f"/api/v1/posts/{self.post.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_author_can_delete_posts(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_can_read_comments(self):
        response = self.client.get("/api/v1/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"/api/v1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_comments(self):
        data = {"content": "New comment", "post": self.post.id}
        response = self.client.post("/api/v1/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create_comments(self):
        self.client.force_authenticate(user=self.user)
        data = {"content": "New comment", "post": self.post.id}
        response = self.client.post("/api/v1/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_only_author_can_update_comments(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"content": "Updated comment", "post": self.post.id}
        response = self.client.put(f"/api/v1/comments/{self.comment.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_author_can_delete_comments(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/v1/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_can_read_users(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"/api/v1/users/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_publish_actions_require_authentication(self):
        response = self.client.post(f"/api/v1/posts/{self.post.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_publish_actions_require_ownership(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(f"/api/v1/posts/{self.post.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_publish_post(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/v1/posts/{self.post.id}/publish/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
