from rest_framework import serializers
from auth_user.serializers import UserCommentSerializer
from .models import Comments, Like, Dislike, Reply
from book_list.models import Book


class LikeSerializer(serializers.ModelSerializer):
    comment = UserCommentSerializer()
    reply = UserCommentSerializer()
    user = UserCommentSerializer()

    class Meta:
        model = Like
        fields = ['id', 'comment', 'reply', 'user']


class DisLikeSerializer(serializers.ModelSerializer):
    comment = UserCommentSerializer()
    reply = UserCommentSerializer()
    user = UserCommentSerializer()


class Meta:
    model = Dislike
    fields = ['id', 'comment', 'reply', 'user']


class ReplySerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'sender', 'recipient', 'text', 'replies']

    def get_like_count(self, obj):
        return obj.like_count()

    def get_dislike_count(self, obj):
        return obj.dislike_count()

    def get_reply_count(self, obj):
        return obj.reply_count()

    def get_replies(self, obj):
        replies = obj.replies_replies.all().order_by('id')[:3]
        serializer = ReplySerializer(replies, many=True)
        return serializer.data


class CommentsSerializer(serializers.ModelSerializer):
    user = UserCommentSerializer()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comments
        fields = ['id', 'user', 'rating', 'text', 'like_count', 'dislike_count', 'reply_count', 'replies']

    def get_like_count(self, obj):
        return obj.like_count()

    def get_dislike_count(self, obj):
        return obj.dislike_count()

    def get_reply_count(self, obj):
        return obj.reply_count()

    def get_replies(self, obj):
        replies = obj.comment_replies.all().order_by('id')[:3]
        serializer = ReplySerializer(replies, many=True)
        return serializer.data
