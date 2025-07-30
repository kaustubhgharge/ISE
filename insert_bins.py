import sqlite3
import json

# Your JSON data (as a string)
bin_json = '''
[
  {"id": 0, "location": "PreZero Service HUB", "type": "HUB", "lat": 52.038469, "lon": 8.882418, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 1, "location": "Market Square", "type": "Paper", "lat": 52.025718240748674, "lon": 8.896963685279172, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 2, "location": "Central Park", "type": "Plastic", "lat": 52.03116888899511, "lon": 8.897377570056012, "fill": 77, "last_emptied_days_ago": 3},
  {"id": 3, "location": "Train Station", "type": "Organic", "lat": 52.02559066194947, "lon": 8.894857483868558, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 4, "location": "City Library", "type": "Paper", "lat": 52.027906439366724, "lon": 8.894750649666664, "fill": 46, "last_emptied_days_ago": 5},
  {"id": 5, "location": "Town Hall", "type": "Paper", "lat": 52.02456125878634, "lon": 8.901784445795998, "fill": 46, "last_emptied_days_ago": 1},
  {"id": 6, "location": "Museum", "type": "Paper", "lat": 52.030951845433854, "lon": 8.896510223058367, "fill": 57, "last_emptied_days_ago": 0},
  {"id": 7, "location": "University Campus", "type": "Paper", "lat": 52.03017310672835, "lon": 8.894260024640303, "fill": 39, "last_emptied_days_ago": 1},
  {"id": 8, "location": "Sports Arena", "type": "Paper", "lat": 52.03091563291016, "lon": 8.900117589221269, "fill": 32, "last_emptied_days_ago": 2},
  {"id": 9, "location": "Shopping Center", "type": "Organic", "lat": 52.0267847808568, "lon": 8.896680852785632, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 10, "location": "Hospital", "type": "Paper", "lat": 52.02441098896897, "lon": 8.895208467656222, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 11, "location": "Post Office", "type": "Organic", "lat": 52.02609773571731, "lon": 8.900811914951895, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 12, "location": "Fire Station", "type": "Plastic", "lat": 52.02925479890575, "lon": 8.897725539931923, "fill": 65, "last_emptied_days_ago": 3},
  {"id": 13, "location": "Police Station", "type": "Organic", "lat": 52.02838063103391, "lon": 8.89611038120881, "fill": 64, "last_emptied_days_ago": 0},
  {"id": 14, "location": "Community Center", "type": "Paper", "lat": 52.02666423279544, "lon": 8.894989656726434, "fill": 75, "last_emptied_days_ago": 7},
  {"id": 15, "location": "Cinema", "type": "Organic", "lat": 52.02502012959175, "lon": 8.899486214192404, "fill": 56, "last_emptied_days_ago": 0},
  {"id": 16, "location": "Bus Station", "type": "Plastic", "lat": 52.028434846177696, "lon": 8.898136865871246, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 17, "location": "Parking Lot", "type": "Organic", "lat": 52.02863562177322, "lon": 8.899929977909043, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 18, "location": "City Square", "type": "Organic", "lat": 52.03087719536091, "lon": 8.899077333581186, "fill": 35, "last_emptied_days_ago": 6},
  {"id": 19, "location": "Railway Crossing", "type": "Plastic", "lat": 52.03069973714554, "lon": 8.90017420104486, "fill": 0, "last_emptied_days_ago": 0},
  {"id": 20, "location": "Main Street", "type": "Paper", "lat": 52.03121167746142, "lon": 8.896803973820637, "fill": 0, "last_emptied_days_ago": 0}
]
'''

# Parse JSON data
bins = json.loads(bin_json)

# Connect to (or create) SQLite database
conn = sqlite3.connect('bins.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bins (
    id INTEGER PRIMARY KEY,
    location TEXT NOT NULL,
    type TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    fill INTEGER NOT NULL,
    last_emptied_days_ago INTEGER NOT NULL
)
''')

# Insert data into table
for bin in bins:
    cursor.execute('''
    INSERT OR REPLACE INTO bins (id, location, type, lat, lon, fill, last_emptied_days_ago)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (bin['id'], bin['location'], bin['type'], bin['lat'], bin['lon'], bin['fill'], bin['last_emptied_days_ago']))

# Commit and close
conn.commit()
conn.close()

print("Data inserted successfully!")
