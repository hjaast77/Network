from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    postContent= models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
       max_length = 10
       truncated_content = self.postContent[:max_length]

       if len(self.postContent) > max_length:
           truncated_content += "..."
       return f"{self.user.username} posted: {truncated_content}"
        
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.follower.username} follows {self.followed_user.username}"

class Like(models.Model):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} likes {self.post}"
