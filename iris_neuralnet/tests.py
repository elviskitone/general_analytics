from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
import numpy as np
from iris_neuralnet import views


class ArtificialNeuralNetworkTestCase(TestCase):

    def setUp(self):
        self.url = reverse('iris_neuralnet')  # Assuming you have defined the URL pattern for this view
        self.ann = views.ArtificialNeuralNetwork()

    def test_evaluate_classifier(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accuracy', response.data)
        self.assertIsInstance(response.data['accuracy'], float)

    def test_confusion_matrix_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('confusion_matrix_data', response.data)

    def test_plot_confusion_matrix(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('confusion_matrix_plot', response.data)

    def test_create_train_predict(self):
        y_pred = self.ann.create_train_predict()
        self.assertIsNotNone(y_pred)
        self.assertIsInstance(y_pred, np.ndarray)


class IrisNeuralNetworkTestCase(APITestCase):

    def test_get_iris_neural_network(self):
        url = reverse('iris_neuralnet')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accuracy', response.data)    
        self.assertIn('confusion_matrix_data', response.data)
        self.assertIn('confusion_matrix_plot', response.data)
