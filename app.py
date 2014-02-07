#!flask/bin/python
from flask import Flask, jsonify, redirect
from query_climate import query_climate
from climate_analogs import query_analog

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

@app.route('/current_analog/<lon>/<lat>', methods = ['GET'])
def get_analog(lon, lat):
    pt = (float(lon), float(lat))
    data = query_analog(pt)
    print "!!!!!!!!!!!!!", data
    return jsonify({'point': data})

if __name__ == '__main__':
    app.run(debug = True)