 #!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")


# In[2]:


Types_of_Features = ("acousticness", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "valence")

st.title("Spotify Groovy App")
Name_of_Artist = st.text_input("Artist Name")

button_clicked = st.button("Groovyfy")


# In[3]:


from Spotify_API import *
import pandas as pd

client_id = '899c5682bb7945988e16c573f0f492aa'
client_secret = '721c6ac9cd8e4bc39fb7907ebe01d146'

spotify = SpotifyAPI(client_id, client_secret)


# In[4]:


Data = spotify.search({"artist": f"{Name_of_Artist}"}, search_type="track")

need = []
for i, item in enumerate(Data['tracks']['items']):
    track = item['album']
    track_id = item['id']
    song_name = item['name']
    popularity = item['popularity']
    need.append((i, track['artists'][0]['name'], track['name'], track_id, song_name, track['release_date'], popularity))
 
Track_df = pd.DataFrame(need, index=None, columns=('Item', 'Artist', 'Album Name', 'Id', 'Song Name', 'Release Date', 'Popularity'))


# In[5]:


access_token = spotify.access_token

headers = {
    "Authorization": f"Bearer {access_token}"
}
endpoint = "https://api.spotify.com/v1/audio-features/"

Feat_df = pd.DataFrame()
for id in Track_df['Id'].iteritems():
    track_id = id[1]
    lookup_url = f"{endpoint}{track_id}"
    ra = requests.get(lookup_url, headers=headers)
    audio_feat = ra.json()
    Features_df = pd.DataFrame(audio_feat, index=[0])
    Feat_df = Feat_df.append(Features_df)


# In[6]:


Full_Data = Track_df.merge(Feat_df, left_on="Id", right_on="id")

Full_Data['year'] = (pd.to_datetime(Full_Data['Release Date'])).dt.year

features = ['acousticness', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness',
            'loudness', 'mode', 'speechiness', 'valence', 'year']

X = Full_Data[features]

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X)
X_scaled = scaler.transform(X)

import pickle

forest = pickle.load(open( "forest.p", "rb" ))

result = forest.predict_proba(X_scaled)[:,1] > 0.3

X['preds'] = result

Final_table = pd.merge(Full_Data, X['preds'], how = 'left',left_index = True, right_index = True)

Final_table_clean = Final_table[Final_table.preds == True]

Final = Final_table_clean[['Song Name', 'Album Name', 'Release Date']]

Sort_DF = Full_Data.sort_values(by=['Popularity'], ascending=False)

st.header("Table of Groovy Songs")
st.table(Final)


# In[7]:


Name_of_Feat = st.selectbox("Feature", Types_of_Features)

chart_df = Final_table_clean[[ 'Song Name', 'Album Name', 'Release Date', 'Popularity', f'{Name_of_Feat}']]

import altair as alt

feat_header = Name_of_Feat.capitalize()

st.header(f'{feat_header}' " vs. Popularity")
c = alt.Chart(chart_df).mark_circle().encode(
    alt.X('Popularity', scale=alt.Scale(zero=False)), y=f'{Name_of_Feat}', color=alt.Color('Popularity', scale=alt.Scale(zero=False)), 
    size=alt.value(200), tooltip=['Popularity', f'{Name_of_Feat}', 'Song Name', 'Album Name'])

st.altair_chart(c, use_container_width=True)

st.header("Table of Groovy Song Attributes")
st.table(chart_df)


# In[8]:


st.write("acousticness: Confidence measure from 0.0 to 1.0 on if a track is acoustic.")
st.write("energy: Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.")
st.write("instrumentalness: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.")
st.write("liveness: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.")
st.write("loudness: The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.")
st.write("speechiness: Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.")
st.write("valence: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).")


st.write("Information about features is from:  https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/")


# In[ ]:




