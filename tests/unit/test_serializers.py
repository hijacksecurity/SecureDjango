from django.contrib.auth.models import User
from django.test import TestCase

from api.models import Comment, Post
from api.serializers import (CommentSerializer, PostListSerializer,
                             PostSerializer, UserSerializer)


class PostSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post content",
            author=self.user,
            published=True,
        )

    def test_post_serializer_fields(self):
        serializer = PostSerializer(self.post)
        data = serializer.data

        self.assertEqual(data["title"], "Test Post")
        self.assertEqual(data["content"], "This is a test post content")
        self.assertEqual(data["published"], True)
        self.assertIn("author", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("comments", data)
        self.assertIn("comments_count", data)

    def test_post_list_serializer_fields(self):
        serializer = PostListSerializer(self.post)
        data = serializer.data

        self.assertEqual(data["title"], "Test Post")
        self.assertEqual(data["published"], True)
        self.assertIn("author", data)
        self.assertIn("created_at", data)
        self.assertIn("comments_count", data)
        self.assertNotIn("comments", data)
        self.assertNotIn("content", data)

    def test_post_serializer_validation(self):
        valid_data = {
            "title": "Valid Title",
            "content": "Valid content",
            "published": True,
            "author_id": self.user.id,
        }
        serializer = PostSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_post_serializer_invalid_data(self):
        invalid_data = {"title": "", "content": "Valid content"}
        serializer = PostSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)


class CommentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="Content", author=self.user
        )
        self.comment = Comment.objects.create(
            content="Test comment", post=self.post, author=self.user
        )

    def test_comment_serializer_fields(self):
        serializer = CommentSerializer(self.comment)
        data = serializer.data

        self.assertEqual(data["content"], "Test comment")
        self.assertEqual(data["post"], self.post.id)
        self.assertIn("author", data)
        self.assertIn("created_at", data)

    def test_comment_serializer_validation(self):
        valid_data = {
            "content": "Valid comment content",
            "post": self.post.id,
            "author_id": self.user.id,
        }
        serializer = CommentSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_comment_serializer_invalid_data(self):
        invalid_data = {"content": "", "post": self.post.id}
        serializer = CommentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_user_serializer_fields(self):
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")
        self.assertNotIn("password", data)

    def test_user_serializer_excludes_sensitive_fields(self):
        serializer = UserSerializer(self.user)
        data = serializer.data

        sensitive_fields = [
            "password",
            "is_staff",
            "is_superuser",
            "user_permissions",
            "groups",
        ]
        for field in sensitive_fields:
            self.assertNotIn(field, data)
