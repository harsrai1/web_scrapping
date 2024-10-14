from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
import logging
import pymongo
import os



base_directory = r"C:\college\SEM5\ITL\project\Image-Scraper-Selenium"


logging.basicConfig(filename=os.path.join(base_directory, "scrapper.log"), level=logging.INFO)

app = Flask(__name__)


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(base_directory, "images"), filename)

@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            
            query = request.form['content'].replace(" ", "")

           
            save_directory = os.path.join(base_directory, "images")

            
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

         
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

           
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch", headers=headers)

            
            if response.status_code != 200:
                logging.error(f"Failed to fetch page: {response.status_code}")
                return 'Failed to fetch page'

           
            soup = BeautifulSoup(response.content, "html.parser")

           
            image_tags = soup.find_all("img")

            if not image_tags:
                logging.info("No images found")
                return 'No images found'

            
            if image_tags:
                del image_tags[0]

            img_data = []
            image_filenames = []  

            for index, image_tag in enumerate(image_tags):
                try:
                    
                    image_url = image_tag.get('src')
                    if not image_url:
                        continue

                    
                    image_data = requests.get(image_url).content
                    image_filename = f"{query}_{index}.jpg"

                   
                    with open(os.path.join(save_directory, image_filename), "wb") as f:
                        f.write(image_data)

                  
                    image_filenames.append(image_filename)

                    
                    mydict = {"Index": index, "Image": image_data}
                    img_data.append(mydict)

                except Exception as img_exception:
                    logging.error(f"Error processing image {index}: {img_exception}")

            
            client = pymongo.MongoClient("mongodb+srv://harsrai89:hars0602%40I@cluster0.fzgil.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

            db = client['image_scrap']
            review_col = db['image_scrap_data']
            review_col.insert_many(img_data)

            
            return render_template("index.html", image_filenames=image_filenames, query=query)

        except Exception as e:
            logging.error(f"Error in index function: {e}")
            return 'Something went wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
