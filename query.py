from flask import Flask, request, url_for, render_template, make_response, jsonify
import os
import requests
import boto3
import json
from boto3.session import Session

# import ipdb
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

DEBUG = True
SECRET_KEY = 'development key'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

session = Session(aws_access_key_id='****************',
                  aws_secret_access_key='****************')

sagemaker = boto3.client('runtime.sagemaker', aws_access_key_id='*************',
                  aws_secret_access_key='***************', region_name='us-east-1')

app = Flask(__name__, template_folder=".")
app.config.from_object(__name__)
app.config['GOOGLEMAPS_KEY'] = "AIzaSyC7wkldmBPYef_tBhIQgkMujph7jBQSj-8"
GoogleMaps(app)

@app.route('/query', methods=['POST'])
def request_predict():
    print(request.form['url'])
    # return render_template('query.html', title='flask test', url=request.form['city1'])
    # return "The cities are: {}, {}, {}".format(request.form['city1'], request.form['city2'], request.form['city3'])

    # r = requests.post('http://172.17.0.2:8080/invocations', json = { 'url':request.form['url'] })

    data = {'url': request.form['url'] }
    res_invoke = sagemaker.invoke_endpoint(
        EndpointName='predict',
        Body=json.dumps(data)
    )
    streamingBody = res_invoke['Body'] 
    r = json.loads(streamingBody.read())

    print(r)

    # ipdb.set_trace()
    # r.json()
    result = r[0:3]
    print(result)
    response = jsonify(result)
    response.status_code = 200
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=result[0][0],
        lng=result[0][1],
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': result[0][0],
             'lng': result[0][1],
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': result[1][0],
             'lng': result[1][1],
             'infobox': "<b>Hello World from other place</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             'lat': result[2][0],
             'lng': result[2][1],
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('example.html', mymap=mymap, sndmap=sndmap)
    # return response

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def show_index():
    return render_template('query.html', title='flask test')

# @app.route('/upload', methods=['POST'])
# def do_upload():
#     file = request.files['xhr2upload']
#     if file and allowed_file(file.filename):
#         filename = file.filename
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     response = make_response(url_for('static', filename='uploads/'+filename, _external=True))
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
