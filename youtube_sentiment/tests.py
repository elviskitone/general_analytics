from unittest import mock
from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go
from . import views
import environ
import json

env = environ.Env()
environ.Env.read_env()


class DataAPITestCase(TestCase):
    def test_data_api(self):
        with patch("googleapiclient.discovery.build") as mock_build:
            api_key = env('API_KEY')            
            result = views.data_api()            
            
            mock_build.assert_called_with("youtube", "v3", developerKey=api_key)         
            self.assertEqual(result, mock_build.return_value)


class GetVideoCommentsHelperTestCase(TestCase):
    @patch("googleapiclient.discovery.build")   
    def test_get_video_comments_helper(self, mock_build):
        mock_response = {
            "items": [
                {
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "textDisplay": "Comment 1"
                            }
                        }
                    }
                },
                {
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "textDisplay": "Comment 2"
                            }
                        }
                    }
                }
            ]
        }
        mock_execute = mock_build.return_value.commentThreads.return_value.list.return_value.execute
        mock_execute.return_value = mock_response        
        
        video_id = "your_video_id"
        result = views.get_video_comments_helper(video_id)        
        
        mock_build.assert_called_once_with(
            "youtube",
            "v3",
            developerKey=env('API_KEY'),
        )        
        
        mock_build.return_value.commentThreads.return_value.list.assert_called_once_with(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=30,
        )        
        
        expected_comments = ["Comment 1", "Comment 2"]
        self.assertEqual(result, expected_comments)


class AnalyzeSentimentTestCase(TestCase):
    def test_analyze_positive_sentiment(self):        
        text = "This is a positive sentence."
        result = views.analyze_sentiment(text)        

        self.assertEqual(result, "Positive")

    def test_analyze_negative_sentiment(self):        
        text = "This is a negative sentence."
        result = views.analyze_sentiment(text)        

        self.assertEqual(result, "Negative")

    def test_analyze_neutral_sentiment(self):        
        text = "So, this must be neutral."
        result = views.analyze_sentiment(text)        

        self.assertEqual(result, "Neutral")


class SearchVideosAndGetIdsTestCase(TestCase):
    @patch("googleapiclient.discovery.build")
    def test_search_videos_and_get_ids(self, mock_data_api):        
        mock_youtube_instance = mock_data_api.return_value
        mock_search_list = mock_youtube_instance.search.return_value.list        
       
        mock_search_response = {
            "items": [
                {"id": {"videoId": "video_id_1"}},
                {"id": {"videoId": "video_id_2"}},
                {"id": {"videoId": "video_id_3"}},
            ]
        }        
       
        mock_search_list.return_value.execute.return_value = mock_search_response        
       
        team = "Barcelona"
        league = "La Liga"
        time_duration_days = 7
        video_ids = views.search_videos_and_get_ids(team, league, time_duration_days)
        
        mock_data_api.assert_called_once()        
        
        mock_search_list.assert_called_once_with(
            q=f"{team} {league}",
            part="id",
            type="video",
            maxResults=100,
            publishedAfter=mock.ANY,  # This is dynamically generated, so we use mock.ANY
        )        
      
        expected_video_ids = ["video_id_1", "video_id_2", "video_id_3"]
        self.assertEqual(video_ids, expected_video_ids)


class RetrieveAndAnalyzeCommentsTestCase(TestCase):
    @patch("youtube_sentiment.views.search_videos_and_get_ids")
    @patch("youtube_sentiment.views.get_video_comments_helper")
    def test_retrieve_and_analyze_comments(self, mock_get_comments_helper, mock_search_videos):        
        mock_search_videos.return_value = ["video_id_1", "video_id_2", "video_id_3"]        
        mock_comments_helper = MagicMock(side_effect=("comment_" + str(i) for i in range(1, 4)))
        mock_get_comments_helper.side_effect = mock_comments_helper
                
        team = "Barcelona"
        league = "La Liga"
        time_duration_days = 7
        comments = views.retrieve_and_analyze_comments(team, league, time_duration_days)
        
        
        mock_search_videos.assert_called_once_with(team, league, time_duration_days)        
        
        expected_calls = [mock.call("video_id_1"), mock.call("video_id_2"), mock.call("video_id_3")]
        mock_get_comments_helper.assert_has_calls(expected_calls)        
       
        expected_comments = ["comment_1", "comment_2", "comment_3"]        
        for expected_comment in expected_comments:
            self.assertIn(expected_comment, comments)


class ComputeCountsAndPercentagesTestCase(TestCase):
    @patch("youtube_sentiment.views.retrieve_and_analyze_comments")
    @patch("youtube_sentiment.views.analyze_sentiment")
    def test_compute_counts_and_percentages(self, mock_analyze_sentiment, mock_retrieve_comments):        
        mock_comments = ["comment_1", "comment_2", "comment_3", "comment_4", "comment_5"]
        mock_retrieve_comments.return_value = mock_comments        
       
        sentiment_mapping = {
            "comment_1": "Positive",
            "comment_2": "Positive",
            "comment_3": "Negative",
            "comment_4": "Neutral",
            "comment_5": "Negative",
        }
        mock_analyze_sentiment.side_effect = lambda comment: sentiment_mapping[comment]        
       
        team = "Barcelona"
        league = "La Liga"
        time_duration_days = 7
        result = views.compute_counts_and_percentages(team, league, time_duration_days)        
        
        expected_result = (2, 2, 1, 40.0, 40.0, 20.0)
        self.assertEqual(result, expected_result)        
       
        mock_retrieve_comments.assert_called_once_with(team, league, time_duration_days)        
        
        expected_calls = [
            mock.call("comment_1"),
            mock.call("comment_2"),
            mock.call("comment_3"),
            mock.call("comment_4"),
            mock.call("comment_5"),
        ]
        mock_analyze_sentiment.assert_has_calls(expected_calls)


class PieChartCase(TestCase):
    @patch("youtube_sentiment.views.compute_counts_and_percentages")
    def test_plotPieChart(self, mock_compute_counts_and_percentages):       
        mock_compute_counts_and_percentages.return_value = (
            10, 5, 3, 50.0, 25.0, 15.0
        )      
        chart = views.plot_pie_chart("Team", "League", 7)

        
        self.assertIsInstance(chart, go.Figure)
       
        expected_labels = ["Positive", "Negative", "Neutral"]
        expected_values = [50.0, 25.0, 15.0]
        self.assertEqual(list(chart.data[0].labels), expected_labels) # type: ignore
        self.assertEqual(list(chart.data[0].values), expected_values) # type: ignore
       
        self.assertEqual(chart.layout.title.text, "Sentiment Analysis")
        self.assertFalse(chart.layout.showlegend)


class BarChartCase(TestCase):
    @patch("youtube_sentiment.views.compute_counts_and_percentages")
    def test_plotBarChart(self, mock_compute_counts_and_percentages):        
        mock_compute_counts_and_percentages.return_value = (
            10, 5, 3, 50.0, 25.0, 15.0
        )        
        chart = views.plot_bar_chart("Team", "League", 7)
        
        self.assertIsInstance(chart, go.Figure)
        
        expected_labels = ["Positive", "Negative", "Neutral"]
        expected_counts = [10, 5, 3]
        self.assertEqual(list(chart.data[0].x), expected_labels) # type: ignore
        self.assertEqual(list(chart.data[0].y), expected_counts) # type: ignore
        
        self.assertEqual(chart.layout.title.text, "Sentiment Analysis")
        self.assertEqual(chart.layout.xaxis.title.text, "Sentiment")
        self.assertEqual(chart.layout.yaxis.title.text, "Count")
        self.assertEqual(chart.layout.width, 500)
        self.assertEqual(chart.layout.height, 500)


class WordCloudTestCase(TestCase):
    @patch("youtube_sentiment.views.retrieve_and_analyze_comments")
    @patch("youtube_sentiment.views.WordCloud")
    @patch("youtube_sentiment.views.plt.imshow")
    def test_displayWordCloud(self, mock_imshow, mock_WordCloud, mock_retrieve_and_analyze_comments):        
        mock_retrieve_and_analyze_comments.return_value = ["Great video","Awesome content","Amazing work"]        
        mock_wordcloud = mock_WordCloud.return_value
        
        with patch.object(mock_wordcloud, "generate") as mock_generate:            
            mock_generate.return_value = None  # Set to None since we are only interested in mocking the method call            
            mock_imshow.return_value = MagicMock()            
            plt_obj = views.display_word_cloud("Team", "League", 7)
            
            assert plt_obj is not None
            
            mock_WordCloud.assert_called_once_with(width=800, height=400)
            mock_generate.assert_called_once_with("Great video Awesome content Amazing work")
            mock_imshow.assert_called_once()

            # gca() gets current axes
            # this checks if the frame is turned on using get_frame_on()
            self.assertEqual(plt_obj.gca().get_frame_on(), True)


class YouTubeSentimentAnalysisTest(TestCase):
    @patch('youtube_sentiment.views.compute_counts_and_percentages')
    @patch('youtube_sentiment.views.retrieve_and_analyze_comments')
    def test_youtube_sentiment_analysis(self, mock_retrieve_and_analyze_comments, mock_compute_counts_and_percentages):
        mock_compute_counts_and_percentages.return_value = (1, 2, 3, 0.2, 0.3, 0.5)
        mock_retrieve_and_analyze_comments.return_value = ['comment1', 'comment2', 'comment3']       
        factory = RequestFactory()
        data = {
            "team": "example_team",
            "league": "example_league",
            "time_duration_days": 7
        }
        request = factory.post('sentiment_analysis/youtube_sentiment/', data=data)
        
        response = views.youtube_sentiment_analysis(request)        
        response.render() # type: ignore
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('piechart', response_data)
        self.assertIn('barchart', response_data)
        self.assertIn('wordcloud', response_data)
        
        mock_compute_counts_and_percentages.assert_called_with('example_team', 'example_league', 7)
        mock_retrieve_and_analyze_comments.assert_called_with('example_team', 'example_league', 7)
        self.assertEqual(mock_compute_counts_and_percentages.call_count, 2)
        self.assertEqual(mock_retrieve_and_analyze_comments.call_count, 1)