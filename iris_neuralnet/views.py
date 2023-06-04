import io
import json
import base64
import random
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


class ArtificialNeuralNetwork():

    def __init__(self) -> None:
        self.iris = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(self.iris.data, self.iris.target, test_size=0.25)
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    
    def create_train_predict(self):
        # Create classifier
        clf = MLPClassifier(hidden_layer_sizes=(10,10), activation='relu', solver='adam', max_iter=1000)
        # Train
        clf.fit(self.X_train, self.y_train)
        # Predict
        y_pred = clf.predict(self.X_test)
        return y_pred
    
    def evaluate_classifier(self):
        accuracy = accuracy_score(self.y_test, self.create_train_predict())
        return accuracy
    
    def confusion_matrix_data(self):
        return confusion_matrix(self.y_test, self.create_train_predict())
    
    def plot_confusion_matrix(self):
        plt.figure()
        plt.imshow(confusion_matrix(self.y_test, self.create_train_predict()), interpolation='nearest', cmap=plt.cm.gray)
        plt.title('Confusion matrix')
        plt.xlabel('Predicted label')
        plt.ylabel('True label')
        return plt
    

@api_view(['GET'])
def get_iris_neural_network(request):
    """
    Returns accuracy, confusion_matrix data and
    confusion_matrix plots are all returned in json 
    format. The matplotlib plots are returned
    as base64 encoded strings.
    """
    ann = ArtificialNeuralNetwork()

    if ann is None:
        return Response({'error': 'Faulty class instance'}, status=400)

    response_data = {}

    ## Only available data is returned as JSON

    accuracy = ann.evaluate_classifier()
    if accuracy is not None:
        response_data['accuracy'] = accuracy

    confusion_matrix_data = ann.confusion_matrix_data()    
    if confusion_matrix_data is not None:
        confusion_matrix_data = confusion_matrix_data.tolist()
        confusion_matrix_data = json.dumps(confusion_matrix_data)
        response_data['confusion_matrix_data'] = confusion_matrix_data

    confusion_matrix_plot = ann.plot_confusion_matrix()
    if confusion_matrix_plot is not None:
        confusion_matrix_plot_image = io.BytesIO()
        confusion_matrix_plot.savefig(confusion_matrix_plot_image, format='png')
        confusion_matrix_plot_image.seek(0)
        confusion_matrix_plot_base64 = base64.b64encode(confusion_matrix_plot_image.read()).decode('utf8')
        response_data['confusion_matrix_plot'] = confusion_matrix_plot_base64    


    if not response_data:
        return Response({'error': 'Missing data'}, status=400)

    return Response(response_data)
  