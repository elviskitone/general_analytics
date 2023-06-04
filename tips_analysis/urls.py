from django.urls import path
from tips_analysis import views


urlpatterns = [    
        path("tips_data_analysis/", views.get_exploratory_data_analysis, name='tips_data_analysis'),
        path("tips_predictive_analysis/", views.get_predictive_analysis, name='tips_predictive_analysis'),
]