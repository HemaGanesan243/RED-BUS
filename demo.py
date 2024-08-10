import streamlit as st
import pandas as pd
import pymysql
from datetime import time

st.image("C:/Users/Lenovo/Desktop/redbus2.png")
st.title(":red[RED BUS]")

mydb = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='root',
    database='redbus'
)

mycursor = mydb.cursor()


mycursor.execute('SELECT DISTINCT route_name FROM bus')
route_names = mycursor.fetchall()
route_name_options = [route[0] for route in route_names]

def filter_route_name(search_term):
    if search_term == "":
        return route_name_options
    return [option for option in route_name_options if search_term.lower() in option.lower()]

search_term = st.text_input('Search:', '')

filtered_route_name = filter_route_name(search_term)


if filtered_route_name:
    selected_option = st.selectbox('Select an option:', filtered_route_name)
else:
    st.write('No options found.')

################## BUS_TYPE       

query_2 = '''
SELECT DISTINCT 
    bus_type,
    CASE 
        WHEN bus_type LIKE '%NON AC%'                 
             OR bus_type LIKE '%Non A/C%' 
             OR bus_type LIKE '%NON A/C%' 
             OR bus_type LIKE '%Non AC%' 
             OR LOWER(bus_type) LIKE '%non%'
             OR LOWER(bus_type) LIKE '%non a/c%' 
             OR LOWER(bus_type) LIKE '%non ac%'  THEN 'Non A/C'
        WHEN bus_type LIKE '%A/C%' 
             OR bus_type LIKE '%AC%' 
             OR bus_type LIKE '%a/c%' 
             OR bus_type LIKE '%ac%' THEN 'A/C'
        ELSE 'None of these'
    END AS category
FROM bus
ORDER BY category
'''

mycursor.execute(query_2)
#fetch2 = select * from bus 
fetch2 = mycursor.fetchall()
df_bus_type = pd.DataFrame(fetch2, columns=['bus_type', 'category'])
bus_type_list = df_bus_type['category'].unique().tolist()
bus_type_list.insert(0, "Choose your bus_type")
bus_type = st.selectbox(':red[Select Your Bus Type:]', bus_type_list)

####### DEPARTURE TIME ############   

query_3 = '''SELECT DISTINCT departure_time FROM bus'''
mycursor.execute(query_3)
fetch3 = mycursor.fetchall()
df_departure_time = pd.DataFrame(fetch3, columns=['departure_time'])
time_format = '%H:%M'
df_departure_time['departure_time'] = pd.to_datetime(df_departure_time['departure_time'], format=time_format, errors='coerce')
departure_times = [time_obj.time() for time_obj in df_departure_time['departure_time'].dropna()]
default_time = departure_times[0] if departure_times else time(0, 0)
departure_time = st.time_input(':red[Select Your Departure Time :]', default_time)

###############  ARRIVAL TIME ######################
query_4 = '''SELECT DISTINCT reaching_time FROM bus'''
mycursor.execute(query_4)
fetch4 = mycursor.fetchall()
df_reaching_time = pd.DataFrame(fetch4, columns=['reaching_time'])
time_format = '%H:%M'
df_reaching_time['reaching_time'] = pd.to_datetime(df_reaching_time['reaching_time'], format=time_format, errors='coerce')
reaching_times = [time_obj.time() for time_obj in df_reaching_time['reaching_time'].dropna()]
reaching_time = st.time_input(':red[Select Your Reaching Time :]', default_time)


########## STAR RATING

query_5 = '''
SELECT DISTINCT star_rating
FROM bus
ORDER BY star_rating DESC '''
mycursor.execute(query_5)
fetch5 = mycursor.fetchall()
df_star_rating = pd.DataFrame(fetch5, columns=['star_rating'])
min_star_rating = int(df_star_rating['star_rating'].min())
max_star_rating = int(df_star_rating['star_rating'].max())
star_rating_range = st.slider(
    ':red[Select Your Star Rating Range:]',
    min_value=min_star_rating,
    max_value=max_star_rating,
    value=(min_star_rating, max_star_rating),
    step=1
)
min_star_rating, max_star_rating = star_rating_range

########## PRICE

query_6 = '''SELECT MIN(CAST(REPLACE(REPLACE(price, 'INR ', ''), ',', '') AS DECIMAL(10, 2))) AS min_price, 
MAX(CAST(REPLACE(REPLACE(price, 'INR ', ''), ',', '') AS DECIMAL(10, 2))) AS max_price FROM bus'''
mycursor.execute(query_6)
fetch6 = mycursor.fetchall()
min_price = fetch6[0][0] if fetch6[0][0] is not None else 0
max_price = fetch6[0][1] if fetch6[0][1] is not None else 0
price_range = st.slider(':red[Select Price Range:]', min_value=float(min_price), max_value=float(max_price), value=(float(min_price), float(max_price)), step=0.1)

# Submit button
if st.button('Submit'):
    
    st.write(f'You selected Route: {selected_option}')
    st.write(f'Bus Type: {bus_type}')
    st.write(f'Departure Time: {departure_time.strftime("%H:%M")}')
    st.write(f'Reaching Time: {reaching_time.strftime("%H:%M")}')
    st.write(f'Star Rating: {star_rating_range}')
    st.write(f'Price Range: {price_range}')

    
    # Construct and execute the SQL query
    query = f'''
    SELECT * FROM bus
    WHERE route_name = '{selected_option}' 
    AND LOWER('{bus_type}') LIKE LOWER(CONCAT('%', '{bus_type}', '%'))
    AND star_rating BETWEEN {min_star_rating} AND {max_star_rating} 
    AND CAST(REPLACE(REPLACE(price, 'INR ', ''), ',', '') AS DECIMAL(10, 2)) BETWEEN {price_range[0]} AND {price_range[1]} 
    AND departure_time = '{departure_time.strftime("%H:%M")}'
    AND reaching_time = '{reaching_time.strftime("%H:%M")}' '''

    try:
        mycursor.execute(query)
        filtered_data = pd.DataFrame(mycursor.fetchall(), columns=[i[0] for i in mycursor.description])
        if filtered_data.empty:
            st.write('No results found.')
        else:
            st.write('Filtered Results:')
            st.dataframe(filtered_data)
    except Exception as e:
        st.error(f"An error occurred: {e}")


mydb.close()









    


