"""world_analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("sentiment_analysis/", include("youtube_sentiment.urls")),
    path("data_analysis/", include("tips_analysis.urls")),
    path("neural_network/", include("iris_neuralnet.urls")),
    path('docs/', include_docs_urls(title='YouTube Sentiment API')),
    
]
