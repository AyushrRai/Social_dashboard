from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, ScheduledPost

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'scheduled_time']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class SchedulePostForm(forms.ModelForm):
    class Meta:
        model = ScheduledPost
        fields = ['social_accounts']
        widgets = {
            'social_accounts': forms.CheckboxSelectMultiple(),
        }