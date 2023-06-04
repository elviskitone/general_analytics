import io
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
import googleapiclient.discovery
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import environ

env = environ.Env()
environ.Env.read_env()


## HELPER FUNCTIONS ##

def data_api():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = env('API_KEY')

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
    return youtube

def get_video_comments_helper(video_id):
    """
    Retrieves YouTube comments for analysis
    """
    youtube = data_api()
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=30,
    ).execute()
    
    comments = []
    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]         
        comments.append(comment)

    return comments
    
    
def analyze_sentiment(text):     
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    compound_score = sentiment_scores["compound"]

    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"
    
def search_videos_and_get_ids(team, league, time_duration_days):
    youtube = data_api()
    current_date = datetime.now()
    start_date = current_date - timedelta(days=time_duration_days)
    formatted_start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    search_response = youtube.search().list(
        q=f"{team} {league}",
        part="id",
        type="video",
        maxResults=100,
        publishedAfter=formatted_start_date,
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    return video_ids

def retrieve_and_analyze_comments(team, league, time_duration_days):
    comments = []
    video_ids = search_videos_and_get_ids(team, league, time_duration_days)

    for video_id in video_ids:
        try:
            _comments = get_video_comments_helper(video_id)            
            comments.append(_comments)            

        except googleapiclient.errors.HttpError as e: # type: ignore
            error_message = e.content.decode("utf8")
            if "commentsDisabled" in error_message:
                continue
            else:
                raise e 

    return comments

def compute_counts_and_percentages(team, league, time_duration_days):
    comments = retrieve_and_analyze_comments(team, league, time_duration_days)

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for comment in comments:                
        sentiment = analyze_sentiment(comment)
        if sentiment == "Positive":
            positive_count += 1
        elif sentiment == "Negative":
            negative_count += 1
        else:
            neutral_count += 1

    total_count = positive_count + negative_count + neutral_count
    positive_percentage = (positive_count / total_count) * 100
    negative_percentage = (negative_count / total_count) * 100
    neutral_percentage = (neutral_count / total_count) * 100
    
    return positive_count, negative_count, neutral_count, positive_percentage, negative_percentage, neutral_percentage


def plot_pie_chart(team, league, time_duration_days):
    _,_,_,positive_percentage, negative_percentage, neutral_percentage = compute_counts_and_percentages(team, league, time_duration_days)
    
    labels = ["Positive", "Negative", "Neutral"]
    values = [positive_percentage, negative_percentage, neutral_percentage]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, title="Sentiment Analysis")])
   
    fig.update_layout(
        title="Sentiment Analysis",
        showlegend=False,        
    )

    return fig


def plot_bar_chart(team, league, time_duration_days):
    positive_count,negative_count,neutral_count,_,_,_ = compute_counts_and_percentages(team, league, time_duration_days)
    labels = ["Positive", "Negative", "Neutral"]
    counts = [positive_count, negative_count, neutral_count]

    fig = go.Figure(data=[go.Bar(x=labels, y=counts)])

    fig.update_layout(
        xaxis=dict(title="Sentiment"),
        yaxis=dict(title="Count"),
        title="Sentiment Analysis",
        width=500,
        height=500
    )

    return fig


def display_word_cloud(team, league, time_duration_days):
    """
    Returns image that contains common words in comments
    """
    comments = retrieve_and_analyze_comments(team, league, time_duration_days)      
    all_comments = " ".join(str(comment) for comment in comments)   

    wordcloud = WordCloud(width=800, height=400).generate(all_comments)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Common Words in the YouTube video Comments")

    return plt


## VIEWS ##

@api_view(['POST'])
def youtube_sentiment_analysis(request):
    """
    Receives the posted data from the body, calls
    the piechart, barchart and wordcloud, whose 
    results are sent back as a reponse
    """
    team = request.data.get('team')
    league = request.data.get('league')
    time_duration_days = int(request.data.get('time_duration_days'))

    if team and league and time_duration_days:
        piechart = plot_pie_chart(team, league, time_duration_days)
        barchart = plot_bar_chart(team, league, time_duration_days)
        wordcloud = display_word_cloud(team, league, time_duration_days)

        piechart_json = piechart.to_json()
        barchart_json = barchart.to_json()
        wordcloud_image = io.BytesIO()
        wordcloud.savefig(wordcloud_image, format='png')
        wordcloud_image.seek(0)
        wordcloud_base64 = base64.b64encode(wordcloud_image.read()).decode('utf8')

        response_data = {
            'piechart': piechart_json,
            'barchart': barchart_json,
            'wordcloud': wordcloud_base64
        }

        return Response(response_data)
    else:
        return Response({'error': 'Missing or invalid data'}, status=400)
       