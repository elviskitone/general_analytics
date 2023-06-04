from django.urls import path
from iris_neuralnet import views

urlpatterns = [
    path("iris_neuralnet/", views.get_iris_neural_network, name='iris_neuralnet'),
]