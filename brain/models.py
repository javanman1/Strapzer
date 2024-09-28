from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blanck-profile-picture.jpg')
    location = models.CharField(max_length=100, blank=True)

    def _str_(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    
    def _str_(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def _str_(self):
        return self.username
        
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def _str_(self):
        return self.user



class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)

# class Conversation(models.Model):
#     participants = models.ManyToManyField(User, related_name='conversations')

# class Message(models.Model):
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

# class UserConversation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
#     last_read = models.DateTimeField(null=True, blank=True)

# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.CharField(max_length=255)
#     created_at = models.DateTimeField(default=datetime.now)
#     viewed = models.BooleanField(default=False)

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'