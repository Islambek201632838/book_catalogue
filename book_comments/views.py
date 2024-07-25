from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from book_list.serializers import BookSerializer, BookShortSerializer
from .models import Book, Comments, Reply
from .serializers import CommentsSerializer, ReplySerializer


class StandardBookSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = self.get_serializer(book)

        # Paginate comments
        paginator = StandardBookSetPagination()
        paginated_comments = paginator.paginate_queryset(book.comments_set.all(), request)

        # Serialize paginated comments
        comment_serializer = CommentsSerializer(paginated_comments, many=True)

        # Create response data
        response_data = serializer.data
        response_data['comments'] = comment_serializer.data

        return paginator.get_paginated_response(response_data)


class StandardCommentPagination2(StandardBookSetPagination):
    page_size = 3


class CommentRepliesView(generics.ListAPIView):
    serializer_class = ReplySerializer
    pagination_class = StandardBookSetPagination

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        comment = get_object_or_404(Comments, pk=comment_id)
        return comment.replies.all().order_by('id')


class ReplyRepliesView(generics.ListAPIView):
    serializer_class = ReplySerializer
    pagination_class = StandardBookSetPagination

    def get_queryset(self):
        reply_id = self.kwargs['pk']
        reply = get_object_or_404(Reply, pk=reply_id)
        return reply.replies_replies.all().order_by('id')
