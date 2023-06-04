import os
import io
import json
import base64
import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from world_analytics.settings import BASE_DIR


class ExploratoryDataAnalysis():

    def __init__(self) -> None:
        file_path = os.path.join(BASE_DIR, 'tips_analysis', 'tips.csv')
        self.data = pd.read_csv(file_path, header=0)
        train, test = train_test_split(self.data, test_size = 0.05)
        self.train = train
        self.test = test

    def data_head(self):
        return self.data.head()

    def data_describe(self):
        return self.data.describe()   
    
    def train_head(self):
        return self.train.head()
    
    def test_head(self):
        return self.test.head()         

    def train_test_shape(self):
        return self.train.shape, self.test.shape
    
    def train_describe(self):
        return self.train.describe()
    
    def plot_counts_data(self):
        sns.countplot(self.data['day'], label='Count')
        return plt
    
    def heatmap_data(self):
        corr = self.data.corr()
        plt.figure(figsize=(7,7))
        sns.heatmap(corr, cbar=True, square=True, cmap='coolwarm')
        return plt
    
    def missing_train_data(self):
        missing = self.train.isnull().sum()
        percent = missing / self.train.shape[0] * 100
        return pd.concat([missing, percent], axis=1, keys=["Missing", "Percent"])
    
    def plot_histogram_train(self):
        self.train.hist(bins=80, figsize=(7,7), color="Crimson")
        return plt
    
    def plot_box_plot_train(self):
        self.train.boxplot(figsize=(5,5), rot=90)
        return plt
    
    def heatmap_train(self):
        corr = self.train.corr()
        sns.heatmap(corr, annot=True, cmap="Spectral")
        return plt
    

class GenderBasedPredictiveAnalysis(ExploratoryDataAnalysis):

    def __init__(self) -> None:
        super().__init__()
        pred_columns = self.data[:].copy()
        pred_columns.drop(['smoker'], axis=1, inplace=True)
        pred_columns.drop(['day'], axis=1, inplace=True)
        pred_columns.drop(['time'], axis=1, inplace=True)
        pred_columns.drop(['sex'], axis=1, inplace=True)
        prediction_var = pred_columns.columns # ['total_bill', 'tip', 'size']        
        self.train_x = self.train[prediction_var].copy()
        self.train_y = self.train['sex'].copy()
        self.test_x = self.test[prediction_var].copy()
        self.test_y = self.test['sex'].copy()

    def KNN_prediction(self):
        knn = KNeighborsClassifier()
        knn.fit(self.train_x, self.train_y)
        prediction = knn.predict(self.test_x)
        return prediction, accuracy_score(prediction, self.test_y), confusion_matrix(self.test_y, prediction)
    
    def RandomForest_prediction(self):
        random.seed(2)
        model = RandomForestClassifier(n_estimators=100)
        model.fit(self.train_x, self.train_y)
        prediction = model.predict(self.test_x)
        return prediction, accuracy_score(prediction, self.test_y), confusion_matrix(self.test_y, prediction)

    

@api_view(['GET'])
def get_exploratory_data_analysis(request):
    """
    Returns all analysed data and plots in json 
    format. The heatmat, histogram, count and box plots 
    are returned as base64 encoded strings.
    """
    eda = ExploratoryDataAnalysis()

    if eda is None:
        return Response({'error': 'Faulty class instance'}, status=400)

    response_data = {}

    ## Only available data is returned as JSON

    data_counts_plot = eda.plot_counts_data()
    if data_counts_plot is not None:
        data_counts_plot_image = io.BytesIO()
        data_counts_plot.savefig(data_counts_plot_image, format='png')
        data_counts_plot_image.seek(0)
        data_counts_plot_base64 = base64.b64encode(data_counts_plot_image.read()).decode('utf8')        
        response_data['data_counts_plot'] = data_counts_plot_base64

    data_heatmap = eda.heatmap_data()
    if data_heatmap is not None:
        data_heatmap_image = io.BytesIO()
        data_heatmap.savefig(data_heatmap_image, format='png')
        data_heatmap_image.seek(0)
        data_heatmap_base64 = base64.b64encode(data_heatmap_image.read()).decode('utf8')
        response_data['data_heatmap'] = data_heatmap_base64

    missing_train_data = eda.missing_train_data()
    if missing_train_data is not None:
        response_data['missing_train_data'] = missing_train_data.to_json()

    train_histogram_plot = eda.plot_histogram_train()
    if train_histogram_plot is not None:
        train_histogram_plot_image = io.BytesIO()
        train_histogram_plot.savefig(train_histogram_plot_image, format='png')
        train_histogram_plot_image.seek(0)
        train_histogram_plot_base64 = base64.b64encode(train_histogram_plot_image.read()).decode('utf8')
        response_data['train_histogram_plot'] = train_histogram_plot_base64

    train_box_plot = eda.plot_box_plot_train()
    if train_box_plot is not None:
        train_box_plot_image = io.BytesIO()
        train_box_plot.savefig(train_box_plot_image, format='png')
        train_box_plot_image.seek(0)
        train_box_plot_base64 = base64.b64encode(train_box_plot_image.read()).decode('utf8')
        response_data['train_box_plot'] = train_box_plot_base64

    train_heatmap = eda.heatmap_train()
    if train_heatmap is not None:
        train_heatmap_image = io.BytesIO()
        train_heatmap.savefig(train_heatmap_image, format='png')
        train_heatmap_image.seek(0)
        train_heatmap_base64 = base64.b64encode(train_heatmap_image.read()).decode('utf8')
        response_data['train_heat_map'] = train_heatmap_base64

    if not response_data:
        return Response({'error': 'Missing data'}, status=400)

    return Response(response_data)



@api_view(['GET'])
def get_predictive_analysis(request):
    """
    Returns all the prediction, accuracy score, 
    and confusion matrix in json format. 
    """

    ggbpa = GenderBasedPredictiveAnalysis()

    if ggbpa is None:
        return Response({'error': 'Faulty class instance'}, status=400)

    response_data = {}

    prediction_KNN, accuracy_KNN, confusion_matrix_KNN = ggbpa.KNN_prediction()
    prediction_RF, accuracy_RF, confusion_matrix_RF = ggbpa.RandomForest_prediction()

    if prediction_KNN is not None:
        response_data['prediction_KNN'] = prediction_KNN

    if accuracy_KNN is not None:
        response_data['accuracy_KNN'] = accuracy_KNN

    if confusion_matrix_KNN is not None:
        confusion_matrix_KNN = confusion_matrix_KNN.tolist()
        confusion_matrix_KNN = json.dumps(confusion_matrix_KNN)
        response_data['confusion_matrix_KNN'] = confusion_matrix_KNN

    if prediction_RF is not None:
        response_data['prediction_RF'] = prediction_RF

    if accuracy_RF is not None:
        response_data['accuracy_RF'] = accuracy_RF

    if confusion_matrix_RF is not None:
        confusion_matrix_RF = confusion_matrix_RF.tolist()
        confusion_matrix_RF = json.dumps(confusion_matrix_RF)
        response_data['confusion_matrix_RF'] = confusion_matrix_RF

    if not response_data:
        return Response({'error': 'Missing data'}, status=400)

    return Response(response_data)




