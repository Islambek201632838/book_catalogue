from django.db import models
from django.core.validators import MaxValueValidator
from auth_user.models import CustomUser
from book_list.models import Book


class Comments(models.Model):
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=False, blank=False, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(null=False, blank=False, validators=[MaxValueValidator(10)])
    text = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f"{self.user} commented on {self.book}"

    def like_count(self):
        return self.likes.count()

    def dislike_count(self):
        return self.dislikes.count()

    def reply_count(self):
        return self.replies.count()


class Reply(models.Model):
    comment = models.ForeignKey(Comments, related_name='replies', null=True, blank=True, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', related_name='replies_replies', null=True, blank=True, on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_replies', null=False, blank=False, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_replies', null=False, blank=False, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f"{self.sender} replied to {self.recipient}"

    def like_count(self):
        return self.likes.count()

    def dislike_count(self):
        return self.dislikes.count()

    def reply_count(self):
        return self.replies.count()


class Like(models.Model):
    comment = models.ForeignKey(Comments, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    reply = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f"{self.user} liked {self.comment or self.reply}"


class Dislike(models.Model):
    comment = models.ForeignKey(Comments, null=True, blank=True, on_delete=models.CASCADE, related_name='dislikes')
    reply = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE, related_name='dislikes')

    def __str__(self):
        return f"{self.user} disliked {self.comment or self.reply}"



