import requests
from bs4 import BeautifulSoup
import csv
import os
from flask import Flask, request, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
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

data_sorted_by_date = sorted(data, key=lambda x: x[2], reverse=True)


# Assigning column names and reading in the data as a pandas dataframe
columns = ['Rank', 'Title', 'Year', 'Runtime', 'Rated', 'Rating']
movies_df = pd.read_csv('IMDb.csv', names=columns, encoding='latin-1') 

#Scatter plot 
def create_plot(): 
    year_rating = movies_df[['Year', 'Rating']]

    plt.figure(figsize=(10, 8))
    plt.scatter(year_rating['Year'], year_rating['Rating'], color='yellow')
    plt.xlabel('Year')
    plt.ylabel('Rating')
    plt.gca().set_facecolor('lightgray')
    plt.gci().set_facecolor('black')
    plt.gcf().set_facecolor('lightgray')
    plt.grid(True)
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

#Pie chart plot
def create_pie():
    rated_counts = movies_df['Rated'].value_counts()

    plt.figure(figsize=(10, 8))
    plt.pie(rated_counts, labels=rated_counts.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.gcf().set_facecolor('lightgray')
    plt.tight_layout()

    img2 = BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot2_url = base64.b64encode(img2.getvalue()).decode()

    return plot2_url

def create_bar(rating_category):
    filtered_data = movies_df[movies_df['Rated'] == rating_category]

    top_ten_movies = filtered_data.nlargest(10, 'Rating')

    plt.figure(figsize=(10, 6))
    plt.barh(top_ten_movies['Title'], top_ten_movies['Rating'], color='yellow')
    plt.gca().set_facecolor('lightgray')
    plt.gcf().set_facecolor('lightgray')
    plt.xlabel('Rating')
    plt.xlim(7.5, 9.4)
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot3_url = base64.b64encode(img.getvalue()).decode()

    return plot3_url

app = Flask(__name__)

sort_by = {
    'Ranking' : data,
    'Date' : data_sorted_by_date
}

#Home page
@app.route("/home", methods=['GET', 'POST'])
@app.route("/")
def main_display():
    display_table = request.method == 'POST'
    selected_option = request.form.get('sort_by','Ranking')
    current_option = sort_by[selected_option]
    print(current_option)
    return render_template('index.html', sort_by=sort_by, selected_option=selected_option, current_option=current_option, display_table=display_table)

#Visaul page
@app.route("/visual_display", methods=['GET', 'POST'])
def visual_display():
    # Fixes issues with displaying
    matplotlib.pyplot.switch_backend('Agg') 
    #creating the plots
    default_category = 'R'
    plot_url = create_plot()
    plot2_url = create_pie()

    if request.method == 'POST':
        selected_category = request.form['rating_category']
        plot3_url = create_bar(selected_category)
        return render_template('visual.html', plot_url=plot_url, plot2_url=plot2_url, plot3_url=plot3_url, default_category=selected_category)
    else:
        plot3_url = create_bar(default_category)
        return render_template('visual.html', plot_url=plot_url, plot2_url=plot2_url, plot3_url=plot3_url, default_category=default_category)

if __name__ =='__main__':
    app.run()