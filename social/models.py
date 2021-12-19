from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey


class SpecificUser(AbstractUser):

    GENDER = (
        ('male', 'male'),
        ('female', 'female')
    )
    phone = models.CharField(max_length=14, blank=True, null=True)
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDER, default='male')

    def get_absolute_url(self):
        return reverse('profile', args=[self.id])

    @property
    def subscribers_count(self):
        return Follower.objects.filter(user__id=self.id).count()


class Follower(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner'
    )
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscribers'
    )

    def __str__(self):
        return f'{self.user.username} follower'


class Post(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField(max_length=1024)
    create_date = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts'
    )

    class Meta:
        ordering = ['-create_date']

    def __str__(self):
        return f'id {self.id}'

    def comments_count(self):
        return self.comments.count()

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.id])


class Comment(MPTTModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    text = models.TextField(max_length=1024)

    def __str__(self):
        return self.id
