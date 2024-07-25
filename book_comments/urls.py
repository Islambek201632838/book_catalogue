from django.urls import path
from .views import BookDetailView, CommentRepliesView, ReplyRepliesView

urlpatterns = [
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('comments/<int:pk>/replies/', CommentRepliesView.as_view(), name='comment-replies'),
    path('replies/<int:pk>/replies/', ReplyRepliesView.as_view(), name='reply-replies'),
]
