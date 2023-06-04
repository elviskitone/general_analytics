from django.urls import path
from youtube_sentiment import views


urlpatterns = [
    path("youtube_sentiment/", views.youtube_sentiment_analysis, name='youtube_sentiment_analysis'),
]
