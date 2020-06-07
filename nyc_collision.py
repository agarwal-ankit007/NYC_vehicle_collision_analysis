import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px

DATA_URL = ("./Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor vehicle collisions in New York City")
st.markdown("This application is a streamlit dashboard that can be used to analyze motor vehicle collisions in NYC")

@st.cache(persist = True)
def load_data(nrows):
	data = pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH DATE','CRASH TIME']])
	data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
	lowercase = lambda x:str(x).lower()
	data.rename(lowercase,axis='columns',inplace=True)
	data.rename(columns={'crash date_crash time':'date/time'},inplace=True)
	data.rename(columns={'number of persons injured':'injured_persons'},inplace=True)
	data.rename(columns={'number of pedestrians injured':'injured_pedestrians'},inplace=True)
	data.rename(columns={'number of cyclist injured':'injured_cyclists'},inplace=True)
	data.rename(columns={'number of motorist injured':'injured_motorists'},inplace=True)
	return data


data = load_data(70000)
original_data = data

st.header("where are the most people injured in NYC ?")
injured_people = st.slider("No. of persons injured in vehicle collisions",0,19)

st.map(data.query("injured_persons >= @injured_people")[['latitude','longitude']].dropna(how="any"))

st.header("How many collisions occur during a given time of a day?")
hour = st.slider("Hour to look at ",0,23)
data = data[data['date/time'].dt.hour==hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour,(hour+1) %24))

midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
	map_style = "mapbox://styles/mapbox/light-v9",
	initial_view_state = {"latitude":midpoint[0],"longitude":midpoint[1],"zoom":11,"pitch":50,
	},
	layers = [
	pdk.Layer(
		"HexagonLayer",
		data = data[['date/time','latitude','longitude']],
		get_position = ['longitude','latitude'],
		radius = 100,
		extruded = True,
		pickable = True,
		elevation_scale = 4,
		elevation_range = [0,1000],
		),
	],
))


st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour,(hour+1) %24))
filtered = data[
	(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]

hist = np.histogram(filtered['date/time'].dt.minute , bins=60, range = (0,60))[0]

chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})

fig = px.bar(chart_data,x='minute',y='crashes',hover_data = ['minute','crashes'],height = 400)
st.write(fig)

st.header("Top 5 Dangerous streets by affected people")
select = st.selectbox('Affected type of people',['pedestrians','cyclists','motorists'])

if select == 'pedestrians':
	st.write(original_data.query("injured_pedestrians >= 1")[["on street name","injured_pedestrians"]].sort_values(by = ['injured_pedestrians'],ascending = False).dropna(how='any')[:5])
elif select == 'cyclists':
	st.write(original_data.query("injured_cyclists >= 1")[["on street name","injured_cyclists"]].sort_values(by = ['injured_cyclists'],ascending = False).dropna(how='any')[:5])
else:
	st.write(original_data.query("injured_motorists >= 1")[["on street name","injured_motorists"]].sort_values(by = ['injured_motorists'],ascending = False).dropna(how='any')[:5])

if st.checkbox("show raw data",False):
	st.subheader('Raw Data')
	st.write(data)
