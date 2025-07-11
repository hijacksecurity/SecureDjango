from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from api.models import Comment, Post


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_post_creation(self):
        post = Post.objects.create(
            title="Test Post",
            content="This is a test post content",
            author=self.user,
            published=True,
        )

        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "This is a test post content")
        self.assertEqual(post.author, self.user)
        self.assertTrue(post.published)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_post_str_representation(self):
        post = Post.objects.create(
            title="Test Post", content="Content", author=self.user
        )
        expected_str = "Test Post"
        self.assertEqual(str(post), expected_str)

    def test_post_default_values(self):
        post = Post.objects.create(
            title="Test Post", content="Content", author=self.user
        )
        self.assertFalse(post.published)

    def test_post_author_relationship(self):
        post = Post.objects.create(
            title="Test Post", content="Content", author=self.user
        )
        self.assertIn(post, self.user.posts.all())


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post content", author=self.user
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            content="This is a test comment", post=self.post, author=self.user
        )

        self.assertEqual(comment.content, "This is a test comment")
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_representation(self):
        comment = Comment.objects.create(
            content="This is a test comment", post=self.post, author=self.user
        )
        expected_str = f"Comment by {self.user.username} on {self.post.title}"
        self.assertEqual(str(comment), expected_str)

    def test_comment_relationships(self):
        comment = Comment.objects.create(
            content="This is a test comment", post=self.post, author=self.user
        )

        self.assertIn(comment, self.post.comments.all())
        self.assertIn(comment, self.user.comments.all())

    def test_comment_ordering(self):
        comment1 = Comment.objects.create(
            content="First comment", post=self.post, author=self.user
        )
        comment2 = Comment.objects.create(
            content="Second comment", post=self.post, author=self.user
        )

        comments = Comment.objects.all()
        self.assertEqual(comments[0], comment2)
        self.assertEqual(comments[1], comment1)
