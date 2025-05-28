import requests
from django.conf import settings
from .models import SocialAccount

def get_facebook_posts(account):
    url = f"https://graph.facebook.com/v12.0/me/feed?access_token={account.access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('data', [])
    return []

def get_twitter_posts(account):
    import twitter
    api = twitter.Api(
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token_key=account.access_token,
        access_token_secret=account.token_secret
    )
    try:
        statuses = api.GetUserTimeline()
        return [status.AsDict() for status in statuses]
    except:
        return []

def post_to_facebook(account, message, image_path=None):
    url = f"https://graph.facebook.com/v12.0/me/feed"
    params = {
        'access_token': account.access_token,
        'message': message,
    }
    if image_path:
        files = {'source': open(image_path, 'rb')}
        response = requests.post(url, params=params, files=files)
    else:
        response = requests.post(url, params=params)
    return response.status_code == 200

def post_to_twitter(account, message, image_path=None):
    import twitter
    api = twitter.Api(
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token_key=account.access_token,
        access_token_secret=account.token_secret
    )
    try:
        if image_path:
            with open(image_path, 'rb') as image_file:
                media_id = api.UploadMediaSimple(image_file)
            api.PostUpdate(message, media=media_id)
        else:
            api.PostUpdate(message)
        return True
    except:
        return False