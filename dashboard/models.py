from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SocialAccount(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='dashboard_social_accounts'  # Changed this line
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=100)
    access_token = models.CharField(max_length=255)
    token_secret = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.platform} account"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

class ScheduledPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    social_accounts = models.ManyToManyField(SocialAccount)
    posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Scheduled post for {self.post.user.username}"

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    date = models.DateField()
    followers = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Analytics"
    
    def __str__(self):
        return f"Analytics for {self.social_account.account_name} on {self.date}"