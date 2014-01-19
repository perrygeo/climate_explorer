#!flask/bin/python
from flask import Flask, jsonify, redirect
from query_climate import query_climate

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def base_climate():
    return redirect("/static/map.html")
    #return redirect("/climate/-122.722/45.514")

@app.route('/climate/<lon>/<lat>', methods = ['GET'])
def get_climate(lon, lat):
    pt = (float(lon), float(lat))
    data = query_climate(pt)
    return jsonify( data )

if __name__ == '__main__':
    app.run(debug = True)