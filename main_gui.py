import requests
from bs4 import BeautifulSoup
import csv
import os
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO
import base64



# Scraping IMDb website and creating CSV file with the data
url = 'https://www.imdb.com/chart/top/'
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
response = requests.get(url, headers = headers)



soup = BeautifulSoup(response.content, "html.parser")
movies = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-between sc-9d2f6de0-0 iMNUXk compact-list-view ipc-metadata-list--base')

data = []
for movie in movies:
    rank = movie.find('h3', class_='ipc-title__text').text.split(' ')[0]
    title = ' '.join(movie.find('h3', class_='ipc-title__text').text.split(' ')[1:])
    try:
        year, length, rated = movie.find_all('span', class_='sc-479faa3c-8 bNrEFi cli-title-metadata-item')
        year = year.text
        length = length.text
        rated = rated.text
    except:
        year, length = movie.find_all('span', class_='sc-479faa3c-8 bNrEFi cli-title-metadata-item')
        year = year.text
        length = length.text
        rated = 'Not Found'
    rating = movie.find('span', class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating').text.split('\xa0')[0]
    data.append([rank, title, year, length, rated, rating])

current_dir = os.getcwd()
file_name = 'IMDb.csv'
file_path = os.path.join(current_dir, file_name)

with open(file_path, 'w', newline='') as csvfile:

    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(data)




app = Flask(__name__)

@app.route("/home")
@app.route("/")
def main_display():
    return render_template('index.html')

@app.route("/visual")
def visual_display():
    columns = ['Rank', 'Title', 'Year', 'Runtime', 'Rated', 'Rating']
    movies_df = pd.read_csv('IMDb.csv', names=columns)

    return render_template('visual.html')

if __name__ =='__main__':
    app.run()