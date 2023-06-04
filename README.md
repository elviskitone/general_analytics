# General analytics

General analytics is a Django project that provides analytics functionality through three apps: youtube_sentiment, tips_analysis, and iris_neuralnet. This project allows users to perform sentiment analysis on YouTube comments,InstallationTo get started with the General analytics project, follow these steps:


## Installation

To get started with the General analytics project, follow these steps:

1. Create a virtual environment using virtualenv:

   ```
   virtualenv env
   ```

2. Activate the virtual environment: 
   * For Windows:
     ```
     env\Scripts\activate
     ```

   * For macOS and Linux:
     ```
     source env/bin/activate
     ```

3. Clone the GitHub repository within the virtual environment:
   ```
   git clone https://github.com/elviskitone/general_analytics.git
   ```

4. Change into the project directory:
   ```
   cd world_analytics
   ```

5. Install the dependencies for each app you want to run:

   * For youtube_sentiment:   
     ```
     pip install -r youtube_sentiment/requirements.txt
     ```

   * For tips_analysis:
     ```
     pip install -r tips_analysis/requirements.txt
     ```

   * For iris_neuralnet:
     ```
     pip install -r iris_neuralnet/requirements.txt
     ```

6. Apply the database migrations:
   ```
   python manage.py migrate
   ```


## Testing

To run tests for all apps, use the following command:
```
python manage.py test
```
To run tests for a specific app, for example, iris_neuralnet, use the following command:
```
python manage.py test iris_neuralnet
```


## Running the App

To start the General Analytics project, use the following command in the root directory:
```
python manage.py runserver
```

Once the server is running, you can access the app by opening your web browser and navigating to http://localhost:8000/.

Remember to activate the virtual environment and ensure that all necessary dependencies are installed before running the app.


## License

This project is licensed under the MIT License. Feel free to use and modify it according to your needs.


## Contributing

If you would like to contribute to this project, please follow the contribution guidelines.


## Contact

If you have any questions or feedback, please don't hesitate to reach out to us. You can contact the project maintainer at elviskitone@gmail.com.

Thank you for using General Analytics! I hope you have fun experimenting with the code, and making tweaks to suit your expectations.