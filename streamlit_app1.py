# import the needed libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# dataset location
DATA_URL = (
    "Tweets.csv"
)


# main section
st.title("Sentiment Analysis of Tweets about US Airlines")
st.markdown("Use this dashboard to "
            "analyze sentiments of tweets 🐦")

# sidebar section
st.sidebar.title("Analysis Section")
st.sidebar.markdown("You can select the desired filters here")


# this is a function used to load the dataset into a pandas dataframe and correct wrong datatypes
# we have a decorator at the beginning to use cached data instead of reloading data unnecessarily
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    # correct the data type of tweet_created from object to datetime
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data


# load the data into a variable called data
data = load_data()


# we will add a section in the sidebar where the user can select a sentiment and a random tweet will be displayed
st.sidebar.subheader("Show random tweet")
random_tweet = st.sidebar.radio('Select the desired Sentiment', ('positive', 'neutral', 'negative'))
# This part will query the data from the dataframe which fulfils the desired sentiment
# data.query("airline_sentiment == @random_tweet")
# then "text" will get only the text column that includes the description
# then sample(n=1) will get only one random sample from all of the retreived data
# the data returend is a dataframe with one text column, but we want only the value of text hence use iat[0,0] will get the value of column 0 and row 0
st.sidebar.markdown(data.query("airline_sentiment == @random_tweet")[["text"]].sample(n=1).iat[0, 0])



# we will add a section in the sidebar where the user can show/hide either a bar or pie chart for the count of each sentiment
# first we will add a checkbox to show or hide this section
if st.sidebar.checkbox("Show number of tweets by sentiment", False, key='1'):
    # this is used to show a selection box for the user to choose the type of chart
    select = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='2')
    # this counts the sum of each sentiment and create a series
    sentiment_count = data['airline_sentiment'].value_counts()
    # create a dataframe with 2 columns, sentiment and tweets because the drawing function "plotly" expect a dataframe as input
    sentiment_count = pd.DataFrame({'Sentiment':sentiment_count.index, 'Tweets':sentiment_count.values})
    # this will appear above the chart
    st.markdown("### Number of tweets by sentiment")
    if select == 'Bar plot':
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)




# we will add a section in the sidebar to show a map that illustrate when and where users are tweeting from
# create a checkbox to show/hide this section
if st.sidebar.checkbox("Show when and where tweets where made", False, key='3'):
    # create a slider to filter by tweet hour
    hour = st.sidebar.slider("Select an Hour to look at", 0, 23)
    # filter the dataframe by hour
    modified_data = data[data['tweet_created'].dt.hour == hour]
    st.markdown("### Tweet locations based on time of day")
    # this will show the selected time range
    st.markdown("%i tweets between %i:00 and %i:00" % (len(modified_data), hour, (hour + 1) % 24))
    # this will draw the map
    st.map(modified_data)
    # add a checkbox to show raw data = dataframe if the user wants to
    if st.sidebar.checkbox("Show raw data", False):
        st.write(modified_data)




# we will add a section to breakdown airlines by sentiment
st.sidebar.subheader("Breakdown airline by sentiment")
# get the list of airlines
airlines_list = list(data['airline'].unique())
# list airlines to the user to select from
choice = st.sidebar.multiselect('Pick airlines', airlines_list)
# if the user has selected at least one airline
if len(choice) > 0:
    # show a title in the chart area
    st.subheader("Breakdown airline by sentiment")
    # the user can select the type of chart
    breakdown_type = st.sidebar.selectbox('Visualization type', ['Pie chart', 'Bar plot', ], key='4')
    # get a subset of the dataframe based on the selected airlines
    choice_data = data[data.airline.isin(choice)]
    # facet_col is used to have a separate chart for each sentiment
    fig_0 = px.histogram(
                        choice_data, x='airline', y='airline_sentiment',
                         histfunc='count', color='airline_sentiment',
                         facet_col='airline_sentiment', labels={'airline_sentiment':'tweets'},
                          height=600, width=800)
    st.plotly_chart(fig_0)





# we will add a word cloud section
st.sidebar.header("Word Cloud")
# get the list of sentiments
sentiment_list = list(data['airline_sentiment'].unique())

df = pd.DataFrame(sentiment_list)
# Remove NaN values from the dataframe
cleaned_df = df[df[0] != 'NaN']
# Convert the result back to a list
cleaned_list = cleaned_df[0].tolist()


#cleaned_list = [x for x in sentiment_list if not np.isnan(x)]
st.write(sentiment_list)
st.write(cleaned_list)
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', sentiment_list)
if not st.sidebar.checkbox("Close", True, key='5'):
    st.subheader('Word cloud for %s sentiment' % (word_sentiment))
    # get a subset of the dataframe based on the selected sentiment
    df = data[data['airline_sentiment']==word_sentiment]
    # create a list of words from df and adding a space between words
    words = ' '.join(df['text'])
    # remove the words that are not meaningful (RT is used to retweet)
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    # stopword removes common words like articles
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=640).generate(processed_words)
    plt.imshow(wordcloud)
    # we dont want x axis or y axis so set them to empty
    plt.xticks([])
    plt.yticks([])
    st.pyplot()






st.sidebar.subheader("Total number of tweets for each airline2")
each_airline = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='6')
airline_sentiment_count = data.groupby('airline')['airline_sentiment'].count().sort_values(ascending=False)
airline_sentiment_count = pd.DataFrame({'Airline':airline_sentiment_count.index, 'Tweets':airline_sentiment_count.values.flatten()})
if not st.sidebar.checkbox("Close", True, key='2'):
    if each_airline == 'Bar plot':
        st.subheader("Total number of tweets for each airline")
        fig_1 = px.bar(airline_sentiment_count, x='Airline', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig_1)
    if each_airline == 'Pie chart':
        st.subheader("Total number of tweets for each airline")
        fig_2 = px.pie(airline_sentiment_count, values='Tweets', names='Airline')
        st.plotly_chart(fig_2)
