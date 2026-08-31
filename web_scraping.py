## Import Selenium, Webdriver_manager, pandas, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sqlite3 
import pandas as pd
import json 

## Web Scraping
# Load web page
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

try:
    driver.get("https://www.timeanddate.com/weather/")

    # Need to wait for table to load before pulling elements
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.fw.tb-theme tbody tr")
        )
    )
    # Get local time and weather from most popular cities around the world
    popular_cities = []

    cities = driver.find_elements(By.CSS_SELECTOR, "table.fw.tb-theme tbody tr")

    for city in cities:
        city_cell = city.find_elements(By.TAG_NAME,"td")

        for i in range(0, len(city_cell), 4):
            if i + 3 < len(city_cell): 
                city_name = city_cell[i].find_element(By.TAG_NAME, "a").text
                city_time = city_cell[i+1].text
                city_weather = city_cell[i+2].find_element(By.TAG_NAME, "img").get_attribute("alt")
                city_temp = city_cell[i+3].text

            # Create city cells
            city_all = {
                "City Name": city_name,
                "City Time": city_time,
                "City Weather": city_weather,
                "City Temperature": city_temp
            }

            # Add each city to popular_cites
            popular_cities.append(city_all)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
finally:
    driver.quit()

# Create DataFrame
df = pd.DataFrame(popular_cities)

# Create CSV file
df.to_csv('popular_cities.csv', index=False)

## Data Cleaning 
# Investigate the data
print("--------------Original DataFrame--------------")
print(df.head())

print("--------------Original DataFrame Info--------------")
df.info()

print("--------------Original DataFrame Shape--------------")
print(df.shape)

print("--------------Missing Data in Original DataFrame--------------")
print(df.isnull().sum())

print("--------------Duplicate Data in Original DataFrame--------------")
print(df.duplicated().sum())

print("--------------Original DataFrame Contents--------------")
print(df.describe())

print("--------------Original DataFrame Data Types--------------")
print(df.dtypes)

# Make a copy of the original DataFrame to avoid writing over original dataset
df1 = df.copy()

# Based on Investigation
# There are 137 rows with four columns describing the name, time, weather, and temperature in the most populat cities.
# There is no missing data.
# There is no duplicate data. 
# There is some text cleaning that needs to be done within each column. 
# There are also some columns (like temperature) that would be more useful as a numeric field. 

# Cleaning column names and changing data types when necessary
# City Name
df1["Name"] = df1["City Name"].str.strip()

# City Time
df1[["Day", "Time"]] = df1["City Time"].str.split(" ", n = 1, expand = True)

df1["Time"] = pd.to_datetime(df1["Time"], format = "%I:%M %p").dt.time # Want to convert time to a time field

# City Weather
df1[["Weather Conditions", "Temperature Category"]] = (df1["City Weather"].str.rsplit(". ", n = 1, expand = True))

no_weather = df1["Temperature Category"].isna() # Need to handle cases where there were no weather conditions given 

df1.loc[no_weather, "Temperature Category"] = df1.loc[no_weather, "Weather Conditions"] # if condition is given 
df1.loc[no_weather, "Weather Conditions"] = "No Weather Condition Given" # if no condition is given

df1["Temperature Category"] = df1["Temperature Category"].str.rstrip(".") # Clean Temperature Category to remove '.'

# City Temperature
df1[["Temperature","Temperature Scale"]] = df1["City Temperature"].str.rsplit(" ", n = 1, expand = True)

df1["Temperature"] = df1["Temperature"].astype(int)

df1["Temperature Scale"] = df1["Temperature Scale"].replace({"°F": "Fahrenheit", "°C": "Celsius"})

# Clean up unclean columns
df1.drop(["City Time", "City Name", "City Weather", "City Temperature"], axis = 1, inplace = True)

print("--------------Updated DataFrame--------------")
print(df1.head())

print("--------------Updated DataFrame Info--------------")
df1.info()

print("--------------Updated DataFrame Contents--------------")
print(df1.describe())

# Some extreme temperatures, but will leave in for analysis 

## Data Transformation
# Many useful categories are already included in the dataset, such as temperature category, but it would be useful to group by rain that day

# Group Weather Patterns into Rain / No Rain / Unknown 
print("--------------Weather Condition Categories--------------")
print(df1["Weather Conditions"].value_counts()) # See weather condition categories 

rain_words = ["thunderstorms","sprinkles","rain","showers"] # common words that are associated with rain

unknown = "No Weather Condition Given" # handle cases that have no weather condition given 

df1["Rain"] = "Unknown" # set all values to Unknown at first 

df1.loc[df1["Weather Conditions"].str.contains("|".join(rain_words), case = False, na = False), "Rain"] = "Rain" # Rain

df1.loc[df1["Weather Conditions"].str.contains(unknown, case = False, na = False), "Rain"] = "Unknown" # Unknown Conditions

df1.loc[~df1["Weather Conditions"].str.contains("|".join(rain_words), case = False, na = False)
        & ~df1["Weather Conditions"].str.contains(unknown, case = False, na = False), "Rain"] = "No Rain" # No Rain

# Show updated DataFrame, info, and shape after data transformations
print("--------------Updated DataFrame--------------")
print(df1.head())

print("--------------Updated DataFrame Info--------------")
df1.info()

print("--------------Original DataFrame Shape--------------")
print(df.shape)

# Create SQLite Database
try:
    with sqlite3.connect("weather_database.db") as conn:
        df1.to_sql(name="weather", con=conn, if_exists="replace", index=False);
except Exception as e:
    print(f"Exception caught: {e}")
