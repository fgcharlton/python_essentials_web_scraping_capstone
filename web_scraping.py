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

########################
#  Web Scraping
########################
def scrape_websites(url):
    # Load webpage
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    data = []
    try:
        driver.get(url)

        # Need to wait for table to load before pulling elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
             (By.CSS_SELECTOR, "table.fw.tb-theme tbody tr")
            )
        )

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
                data.append({
                    "City Name": city_name,
                    "City Time": city_time,
                    "City Weather": city_weather,
                    "City Temperature": city_temp
                })
    except Exception as e:
        print(f"Error: {url}: {e}")
    finally:
        driver.quit()
    return pd.DataFrame(data)

########################
# Data Cleaning 
########################
def clean_city_data(df):
    df = df.copy()
    print("Columns in DataFrame:", df.columns)
    print(df.head())

    # City Name
    df["Name"] = df["City Name"].str.strip()

    # City Time
    df[["Day", "Time"]] = df["City Time"].str.split(" ", n = 1, expand = True)

    df["Time"] = pd.to_datetime(df["Time"], format = "%I:%M %p").dt.time # Want to convert time to a time field

    # City Day
    day_map = {
        "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
        "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday"
    }

    df["Day"] = df["Day"].str.lower().map(day_map).fillna(df["Day"])

    # City Weather
    df[["Weather Conditions", "Temperature Category"]] = (df["City Weather"].str.rsplit(". ", n = 1, expand = True))

    no_weather = df["Temperature Category"].isna() # Need to handle cases where there were no weather conditions given 

    df.loc[no_weather, "Temperature Category"] = df.loc[no_weather, "Weather Conditions"] # if condition is given 
    df.loc[no_weather, "Weather Conditions"] = "No Weather Condition Given" # if no condition is given

    df["Temperature Category"] = df["Temperature Category"].str.rstrip(".") # Clean Temperature Category to remove '.'

    # City Temperature
    df[["Temperature","Temperature Scale"]] = df["City Temperature"].str.rsplit(" ", n = 1, expand = True)

    df["Temperature"] = df["Temperature"].astype(int)

    df["Temperature Scale"] = df["Temperature Scale"].replace({"°F": "Fahrenheit", "°C": "Celsius"})

    # Clean up unclean columns
    df.drop(["City Time", "City Name", "City Weather", "City Temperature"], axis = 1, inplace = True)

    return df

########################
# Data Transformation
########################
# Many useful categories are already included in the dataset, such as temperature category, but it would be useful to group by rain that day
def rain_categories(df):
    rain_words = ["thunderstorms","sprinkles","rain","showers"] # common words that are associated with rain

    unknown = "No Weather Condition Given" # handle cases that have no weather condition given 

    df["Rain"] = "Unknown" # set all values to Unknown at first 

    df.loc[df["Weather Conditions"].str.contains("|".join(rain_words), case = False, na = False), "Rain"] = "Rain" # Rain

    df.loc[df["Weather Conditions"].str.contains(unknown, case = False, na = False), "Rain"] = "Unknown" # Unknown Conditions

    df.loc[~df["Weather Conditions"].str.contains("|".join(rain_words), case = False, na = False)
        & ~df["Weather Conditions"].str.contains(unknown, case = False, na = False), "Rain"] = "No Rain" # No Rain

    return df

########################
# Create files
########################
if __name__ == "__main__":
    # URLs
    url1 = "https://www.timeanddate.com/weather/"
    url2 = "https://www.timeanddate.com/weather/?low=c"
    url3 = "https://www.timeanddate.com/weather/?low=5"
    url4 = "https://www.timeanddate.com/weather/?low=4"

    # Scrape data
    df_most_popular_cities = scrape_websites(url1)
    df_capital_cities = scrape_websites(url2)
    df_popular_cities = scrape_websites(url3)
    df_somewhat_popular_cities = scrape_websites(url4)

    #Clean data
    df_most_popular_cities_clean = clean_city_data(df_most_popular_cities)
    df_capital_cities_clean = clean_city_data(df_capital_cities)
    df_popular_cities_clean = clean_city_data(df_popular_cities)
    df_somewhat_popular_cities_clean = clean_city_data(df_somewhat_popular_cities)

    #Add rain categories
    df_most_popular_cities_clean = rain_categories(df_most_popular_cities_clean)
    df_capital_cities_clean = rain_categories(df_capital_cities_clean)
    df_popular_cities_clean = rain_categories(df_popular_cities_clean)
    df_somewhat_popular_cities_clean = rain_categories(df_somewhat_popular_cities_clean)

    #Save to CSV
    df_most_popular_cities_clean.to_csv('most_popular_cities.csv', index = False)
    df_capital_cities_clean.to_csv('capital_cities.csv', index = False)
    df_popular_cities_clean.to_csv('popular_cities.csv', index = False)
    df_somewhat_popular_cities_clean.to_csv('somewhat_popular_cities.csv', index = False)

###########################################
# Look at Overall Data Transformations 
###########################################

################################
# Most Popular Cities
################################
# Investigate Most Popular Cities
print("--------------Most Popular Cities Original DataFrame--------------")
print(df_most_popular_cities.head())

print("--------------Most. Popular Cities Original DataFrame Info--------------")
df_most_popular_cities.info()

print("--------------Most Popular Cities Original DataFrame Shape--------------")
print(df_most_popular_cities.shape)

print("--------------Missing Data in Most Popular Cities Original DataFrame--------------")
print(df_most_popular_cities.isnull().sum())

print("--------------Duplicate Data in Most Popular Cities Original DataFrame--------------")
print(df_most_popular_cities.duplicated().sum())

print("--------------Most Popular Cities Original DataFrame Contents--------------")
print(df_most_popular_cities.describe())

print("--------------Most Popular Cities Original DataFrame Data Types--------------")
print(df_most_popular_cities.dtypes)

# Based on Investigation
# There are ~140 rows with four columns describing the name, time, weather, and temperature in the most popular cities.
# There is no missing data.
# There is no duplicate data. 
# There is some text cleaning that needs to be done within each column. 
# There are also some columns (like temperature) that would be more useful as a numeric field. 

# See updated Most Popular Cities 
print("--------------Most Popular Cities Updated DataFrame--------------")
print(df_most_popular_cities_clean.head())

print("--------------Most Popular Cities Updated DataFrame Info--------------")
df_most_popular_cities_clean.info()

print("--------------Most Popular Cities Updated DataFrame Contents--------------")
print(df_most_popular_cities_clean.describe())

print("--------------Most Popular Cities Updated DataFrame--------------")
print(df_most_popular_cities_clean.head())

print("--------------Most Popular Cities Updated DataFrame Info--------------")
df_most_popular_cities_clean.info()

print("--------------Most Popular Cities Original DataFrame Shape--------------")
print(df_most_popular_cities_clean.shape)

################################
# Capital Cities
################################
# Investigate Capital Cities
print("--------------Capital Cities Original DataFrame--------------")
print(df_capital_cities.head())

print("--------------Capital Cities Original DataFrame Info--------------")
df_capital_cities.info()

print("--------------Capital Cities Original DataFrame Shape--------------")
print(df_capital_cities.shape)

print("--------------Missing Data in Capital Cities Original DataFrame--------------")
print(df_capital_cities.isnull().sum())

print("--------------Duplicate Data in Capital Cities Original DataFrame--------------")
print(df_capital_cities.duplicated().sum())

print("--------------Capital Cities Original DataFrame Contents--------------")
print(df_capital_cities.describe())

print("--------------Capital Cities Original DataFrame Data Types--------------")
print(df_capital_cities.dtypes)

# Based on Investigation
# There are four columns describing the name, time, weather, and temperature in capital cities.
# There is no missing data.
# There is no duplicate data. 
# There is some text cleaning that needs to be done within each column. 
# There are also some columns (like temperature) that would be more useful as a numeric field. 

# See updated Capital Cities 
print("--------------Capital Cities Updated DataFrame--------------")
print(df_capital_cities_clean.head())

print("--------------Capital Cities Updated DataFrame Info--------------")
df_capital_cities_clean.info()

print("--------------Capital Cities Updated DataFrame Contents--------------")
print(df_capital_cities_clean.describe())

print("--------------Capital Cities Updated DataFrame--------------")
print(df_capital_cities_clean.head())

print("--------------Capital Cities Updated DataFrame Info--------------")
df_capital_cities_clean.info()

print("--------------Capital Cities Original DataFrame Shape--------------")
print(df_capital_cities_clean.shape)

################################
# Popular Cities
################################
# Investigate Popular Cities
print("--------------Popular Cities Original DataFrame--------------")
print(df_popular_cities.head())

print("--------------Popular Cities Original DataFrame Info--------------")
df_popular_cities.info()

print("--------------Popular Cities Original DataFrame Shape--------------")
print(df_popular_cities.shape)

print("--------------Missing Data in Popular Cities Original DataFrame--------------")
print(df_popular_cities.isnull().sum())

print("--------------Duplicate Data in Popular Cities Original DataFrame--------------")
print(df_popular_cities.duplicated().sum())

print("--------------Popular Cities Original DataFrame Contents--------------")
print(df_popular_cities.describe())

print("--------------Popular Cities Original DataFrame Data Types--------------")
print(df_popular_cities.dtypes)

# Based on Investigation
# There are four columns describing the name, time, weather, and temperature in the most popular cities.
# There is no missing data.
# There is no duplicate data. 
# There is some text cleaning that needs to be done within each column. 
# There are also some columns (like temperature) that would be more useful as a numeric field. 

# See updated Popular Cities 
print("--------------Popular Cities Updated DataFrame--------------")
print(df_popular_cities_clean.head())

print("--------------Popular Cities Updated DataFrame Info--------------")
df_popular_cities_clean.info()

print("--------------Popular Cities Updated DataFrame Contents--------------")
print(df_popular_cities_clean.describe())

print("--------------Popular Cities Updated DataFrame--------------")
print(df_popular_cities_clean.head())

print("--------------Popular Cities Updated DataFrame Info--------------")
df_popular_cities_clean.info()

print("--------------Popular Cities Original DataFrame Shape--------------")
print(df_popular_cities_clean.shape)

################################
# Somewhat Popular Cities
################################
# Investigate Somewhat Popular Cities
print("--------------Somewhat Popular Cities Original DataFrame--------------")
print(df_somewhat_popular_cities.head())

print("--------------Somewhat Popular Cities Original DataFrame Info--------------")
df_somewhat_popular_cities.info()

print("--------------Somewhat Popular Cities Original DataFrame Shape--------------")
print(df_somewhat_popular_cities.shape)

print("--------------Missing Data in Somewhat Popular Cities Original DataFrame--------------")
print(df_somewhat_popular_cities.isnull().sum())

print("--------------Duplicate Data in Somewhat Popular Cities Original DataFrame--------------")
print(df_somewhat_popular_cities.duplicated().sum())

print("--------------Somewhat Popular Cities Original DataFrame Contents--------------")
print(df_somewhat_popular_cities.describe())

print("--------------Somewhat Popular Cities Original DataFrame Data Types--------------")
print(df_somewhat_popular_cities.dtypes)

# Based on Investigation
# There are four columns describing the name, time, weather, and temperature in the most popular cities.
# There is no missing data.
# There is no duplicate data. 
# There is some text cleaning that needs to be done within each column. 
# There are also some columns (like temperature) that would be more useful as a numeric field. 

# See updated Somewhat Popular Cities 
print("--------------Somewhat Popular Cities Updated DataFrame--------------")
print(df_somewhat_popular_cities_clean.head())

print("--------------Somewhat Popular Cities Updated DataFrame Info--------------")
df_somewhat_popular_cities_clean.info()

print("--------------Somewhat Popular Cities Updated DataFrame Contents--------------")
print(df_somewhat_popular_cities_clean.describe())

print("--------------Somewhat Popular Cities Updated DataFrame--------------")
print(df_somewhat_popular_cities_clean.head())

print("--------------Somewhat Popular Cities Updated DataFrame Info--------------")
df_somewhat_popular_cities_clean.info()

print("--------------Somewhat Popular Cities Original DataFrame Shape--------------")
print(df_somewhat_popular_cities_clean.shape)

################################
# Create SQLite Database
################################
try:
    with sqlite3.connect("weather_database.db") as conn:
        df_most_popular_cities_clean.to_sql(name="most_popular_cities", con=conn, if_exists="replace", index=False)
        df_capital_cities_clean.to_sql(name="capital_cities", con=conn, if_exists="replace", index=False)
        df_popular_cities_clean.to_sql(name="popular_cities", con=conn, if_exists="replace", index=False)
        df_somewhat_popular_cities_clean.to_sql(name="somewhat_popular_cities", con=conn, if_exists="replace", index=False)
except Exception as e:
    print(f"Exception caught: {e}")

################################
# Create new columns in SQL
################################

# Capital query
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

capital_query = """
ALTER TABLE capital_cities
ADD [city_category] TEXT DEFAULT 'Capital Cities' NOT NULL;"""

cursor.execute(capital_query)
rows = cursor.fetchall()
print(rows)
conn.close()

# Most Popular query
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

most_popular_query = """
ALTER TABLE most_popular_cities
ADD [city_category] TEXT DEFAULT 'Most Popular Cities' NOT NULL;"""

cursor.execute(most_popular_query)
rows = cursor.fetchall()
print(rows)
conn.close()

# Somewhat Popular query
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

somewhat_popular_query = """
ALTER TABLE somewhat_popular_cities
ADD [city_category] TEXT DEFAULT 'Somewhat Popular Cities' NOT NULL;"""

cursor.execute(somewhat_popular_query)
rows = cursor.fetchall()
print(rows)
conn.close()

# Popular query
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

popular_query = """
ALTER TABLE popular_cities
ADD [city_category] TEXT DEFAULT 'Popular Cities' NOT NULL;"""

cursor.execute(popular_query)
rows = cursor.fetchall()
print(rows)
conn.close()

################################
# Analyses
################################
# How many cities are across all 4 lists?
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

multiple_lists_query = """
SELECT COUNT(*)
FROM capital_cities AS c
INNER JOIN most_popular_cities AS mp
    ON c.name = mp.name
INNER JOIN popular_cities AS p
    ON c.name = p.name
INNER JOIN somewhat_popular_cities AS sp
    ON c.name = sp.name
"""

cursor.execute(multiple_lists_query)
print("-------------------Number of Cities in All 4 Lists-------------------")
print(cursor.fetchall())

# What are some of the cities that are on all 4 lists?
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

multiple_lists_names_query = """
SELECT c.name
FROM capital_cities AS c
INNER JOIN most_popular_cities AS mp
    ON c.name = mp.name
INNER JOIN popular_cities AS p
    ON c.name = p.name
INNER JOIN somewhat_popular_cities AS sp
    ON c.name = sp.name
ORDER BY c.name
LIMIT 5;
"""

cursor.execute(multiple_lists_names_query)
print("-------------------First 5 Cities That Are in All Tables-------------------")
print(cursor.fetchall())

# What is the average temperature across all cities?
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

all_city_temps_query = """
SELECT AVG(Temperature)
FROM (
    SELECT Temperature FROM capital_cities
    UNION
    SELECT Temperature FROM most_popular_cities 
    UNION
    SELECT Temperature FROM popular_cities
    UNION
    SELECT Temperature FROM somewhat_popular_cities
    );
"""

cursor.execute(all_city_temps_query)
print("-------------------Average Temperature Across All Cities-------------------")
print(cursor.fetchall())

# What is the frequency of temperature categories?
all_city_temp_cats_query = """
SELECT "Temperature Category", COUNT(*) as total_count
FROM (SELECT Name, "Temperature Category"
    FROM (
    SELECT Name, "Temperature Category" FROM capital_cities
    UNION
    SELECT Name, "Temperature Category" FROM most_popular_cities 
    UNION
    SELECT Name, "Temperature Category" FROM popular_cities
    UNION
    SELECT Name, "Temperature Category" FROM somewhat_popular_cities
    )
    GROUP BY Name
)
GROUP BY "Temperature Category"
ORDER BY total_count DESC;
"""

cursor.execute(all_city_temp_cats_query)
print("-------------------Number of Cities by Temperature Category-------------------")
print(cursor.fetchall())

# What is the frequency of weather conditions? 
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

all_city_weather_cats_query = """
SELECT "Weather Conditions", COUNT(*) as total_count
FROM (SELECT Name, "Weather Conditions"
    FROM (
    SELECT Name, "Weather Conditions" FROM capital_cities
    UNION 
    SELECT Name, "Weather Conditions" FROM most_popular_cities 
    UNION 
    SELECT Name, "Weather Conditions" FROM popular_cities
    UNION 
    SELECT Name, "Weather Conditions" FROM somewhat_popular_cities
    )
    GROUP BY Name
)
GROUP BY "Weather Conditions"
ORDER BY total_count DESC;
"""

cursor.execute(all_city_weather_cats_query)
print("-------------------Number of Cities by Weather Conditions-------------------")
print(cursor.fetchall())

# What is the frequency of rain across cities?
import sqlite3

conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

all_city_rain_query = """
SELECT Rain, COUNT(*) as total_count
FROM (SELECT Name, Rain
    FROM (
    SELECT Name, Rain FROM capital_cities
    UNION 
    SELECT Name, Rain FROM most_popular_cities 
    UNION 
    SELECT Name, Rain FROM popular_cities
    UNION 
    SELECT Name, Rain FROM somewhat_popular_cities
    )
    GROUP BY Name
)
GROUP BY Rain
ORDER BY total_count DESC;
"""

cursor.execute(all_city_rain_query)
print("-------------------Number of Cities by Rain Conditions-------------------")
print(cursor.fetchall())

# Where could I go for a vacation that has good weather (warm and clear skies)?
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

good_vacation_spots = """
SELECT Name, "Weather Conditions", Temperature
FROM (
    SELECT Name, "Weather Conditions", Temperature FROM capital_cities
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM most_popular_cities 
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM popular_cities
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM somewhat_popular_cities
    )
WHERE (Temperature > 75 AND Temperature < 85) AND ("Weather Conditions" = "Clear" OR "Weather Conditions" = "Sunny" OR "Weather Conditions" = "Partly sunny")
ORDER BY Temperature DESC
LIMIT 10;
"""

cursor.execute(good_vacation_spots)
print("-------------------Good Vacation Spots-------------------")
print(cursor.fetchall())

# Where should I avoid a vacation because of bad weather (not warm and clear skies)?
conn = sqlite3.connect("weather_database.db")
cursor = conn.cursor()

bad_vacation_spots = """
SELECT Name, "Weather Conditions", Temperature
FROM (
    SELECT Name, "Weather Conditions", Temperature FROM capital_cities
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM most_popular_cities 
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM popular_cities
    UNION
    SELECT Name, "Weather Conditions", Temperature FROM somewhat_popular_cities
    )
WHERE Temperature < 40 AND "Weather Conditions" != "Clear" AND "Weather Conditions" != "Sunny" AND "Weather Conditions" != "Partly sunny"
ORDER BY Temperature DESC
LIMIT 10;
"""

cursor.execute(bad_vacation_spots)
print("-------------------Bad Vacation Spots-------------------")
print(cursor.fetchall())