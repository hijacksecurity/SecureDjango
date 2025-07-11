from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment, Post


class UserSerializer(serializers.ModelSerializer):
    """User serializer for API responses"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer with nested author info"""

    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ["id", "content", "post", "author", "author_id", "created_at"]
        read_only_fields = ["id", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    """Post serializer with nested author and comments"""

    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_id",
            "created_at",
            "updated_at",
            "published",
            "comments",
            "comments_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for post list view"""

    author = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "created_at",
            "updated_at",
            "published",
            "comments_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_comments_count(self, obj):
        return obj.comments.count()
