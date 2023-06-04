from django.test import RequestFactory, TestCase
from tips_analysis import views

class ExploratoryDataAnalysisTestCase(TestCase):
    def setUp(self):
        self.eda = views.ExploratoryDataAnalysis()

    def test_data_head(self):
        result = self.eda.data_head()
        self.assertIsNotNone(result)

    def test_data_describe(self):
        result = self.eda.data_describe()
        self.assertIsNotNone(result)

    def test_train_head(self):
        result = self.eda.train_head()
        self.assertIsNotNone(result)

    def test_test_head(self):
        result = self.eda.test_head()
        self.assertIsNotNone(result)

    def test_train_test_shape(self):
        result = self.eda.train_test_shape()
        self.assertIsNotNone(result)

    def test_train_describe(self):
        result = self.eda.train_describe()
        self.assertIsNotNone(result)

    def test_plot_counts_data(self):
        result = self.eda.plot_counts_data()
        self.assertIsNotNone(result)

    def test_heatmap_data(self):
        result = self.eda.heatmap_data()
        self.assertIsNotNone(result)

    def test_missing_train_data(self):
        result = self.eda.missing_train_data()
        self.assertIsNotNone(result)

    def test_plot_histogram_train(self):
        result = self.eda.plot_histogram_train()
        self.assertIsNotNone(result)

    def test_plot_box_plot_train(self):
        result = self.eda.plot_box_plot_train()
        self.assertIsNotNone(result)

    def test_heatmap_train(self):
        result = self.eda.heatmap_train()
        self.assertIsNotNone(result)


class GenderBasedPredictiveAnalysisTestCase(TestCase):
    def setUp(self):
        self.gpa = views.GenderBasedPredictiveAnalysis()

    def test_KNN_prediction(self):
        result = self.gpa.KNN_prediction()
        prediction, accuracy, confusion_matrix = result
        self.assertIsNotNone(prediction)
        self.assertIsNotNone(accuracy)
        self.assertIsNotNone(confusion_matrix)

    def test_RandomForest_prediction(self):
        result = self.gpa.RandomForest_prediction()
        prediction, accuracy, confusion_matrix = result
        self.assertIsNotNone(prediction)
        self.assertIsNotNone(accuracy)
        self.assertIsNotNone(confusion_matrix)


class GetExploratoryDataAnalysisTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_exploratory_data_analysis(self):
        request = self.factory.get('data_analysis/tips_data_analysis/')
        response = views.get_exploratory_data_analysis(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.data)
        self.assertIn('data_counts_plot', response.data)
        self.assertIn('data_heatmap', response.data)
        self.assertIn('missing_train_data', response.data)
        self.assertIn('train_histogram_plot', response.data)
        self.assertIn('train_box_plot', response.data)
        self.assertIn('train_heat_map', response.data)


class GetPredictiveAnalysisTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_predictive_data_analysis(self):
        request = self.factory.get('data_analysis/tips_predictive_analysis/')
        response = views.get_predictive_analysis(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', response.data)
        self.assertIn('prediction_KNN', response.data)
        self.assertIn('prediction_RF', response.data)
        self.assertIn('accuracy_KNN', response.data)
        self.assertIn('accuracy_RF', response.data)
        self.assertIn('confusion_matrix_KNN', response.data)
        self.assertIn('confusion_matrix_RF', response.data)