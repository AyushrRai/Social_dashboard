from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SocialAccount, Post, ScheduledPost, Analytics
from .forms import CustomUserCreationForm, PostForm, SchedulePostForm
from .utils import get_facebook_posts, get_twitter_posts, post_to_facebook, post_to_twitter
from datetime import datetime, timedelta
import json

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    accounts = SocialAccount.objects.filter(user=request.user, is_active=True)
    
    # Get posts from connected accounts
    facebook_posts = []
    twitter_posts = []
    
    for account in accounts:
        if account.platform == 'facebook':
            facebook_posts = get_facebook_posts(account)
        elif account.platform == 'twitter':
            twitter_posts = get_twitter_posts(account)
    
    # Get allauth connected accounts
    allauth_accounts = request.user.socialaccount_set.all()
    
    # Get scheduled posts
    scheduled_posts = ScheduledPost.objects.filter(post__user=request.user, posted=False)
    
    # Get analytics data
    analytics_data = Analytics.objects.filter(user=request.user).order_by('-date')[:7]
    
    context = {
        'facebook_posts': facebook_posts[:5],
        'twitter_posts': twitter_posts[:5],
        'scheduled_posts': scheduled_posts,
        'analytics_data': analytics_data,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            
            if post.scheduled_time:
                schedule_form = SchedulePostForm(request.POST)
                if schedule_form.is_valid():
                    scheduled_post = schedule_form.save(commit=False)
                    scheduled_post.post = post
                    scheduled_post.save()
                    schedule_form.save_m2m()
                    messages.success(request, 'Post scheduled successfully!')
            else:
                # Post immediately
                accounts = SocialAccount.objects.filter(user=request.user, is_active=True)
                for account in accounts:
                    if account.platform == 'facebook':
                        post_to_facebook(account, post.content, post.image.path if post.image else None)
                    elif account.platform == 'twitter':
                        post_to_twitter(account, post.content, post.image.path if post.image else None)
                post.is_published = True
                post.save()
                messages.success(request, 'Post published successfully!')
            
            return redirect('dashboard')
    else:
        post_form = PostForm()
        schedule_form = SchedulePostForm()
    
    context = {
        'post_form': post_form,
        'schedule_form': schedule_form,
    }
    return render(request, 'dashboard/create_post.html', context)

@login_required
def scheduled_posts(request):
    scheduled_posts = ScheduledPost.objects.filter(post__user=request.user).order_by('post__scheduled_time')
    return render(request, 'dashboard/scheduled_posts.html', {'scheduled_posts': scheduled_posts})

@login_required
def analytics(request):
    accounts = SocialAccount.objects.filter(user=request.user, is_active=True)
    
    # Generate some sample analytics data if none exists
    if not Analytics.objects.filter(user=request.user).exists():
        for account in accounts:
            for i in range(7):
                date = timezone.now() - timedelta(days=i)
                Analytics.objects.create(
                    user=request.user,
                    social_account=account,
                    date=date,
                    followers=1000 + i * 10,
                    likes=50 + i * 5,
                    comments=10 + i,
                    shares=5 + i,
                )
    
    analytics_data = Analytics.objects.filter(user=request.user).order_by('-date')
    
    # Prepare data for charts
    dates = [data.date.strftime('%Y-%m-%d') for data in analytics_data]
    followers = [data.followers for data in analytics_data]
    likes = [data.likes for data in analytics_data]
    comments = [data.comments for data in analytics_data]
    shares = [data.shares for data in analytics_data]
    
    context = {
        'analytics_data': analytics_data,
        'dates_json': json.dumps(dates),
        'followers_json': json.dumps(followers),
        'likes_json': json.dumps(likes),
        'comments_json': json.dumps(comments),
        'shares_json': json.dumps(shares),
    }
    return render(request, 'dashboard/analytics.html', context)

@login_required
def social_accounts(request):
    accounts = SocialAccount.objects.filter(user=request.user)
    return render(request, 'dashboard/social_accounts.html', {'accounts': accounts})

@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm(instance=request.user)
    
    return render(request, 'dashboard/profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})