from flask import Flask, render_template, request, jsonify

import pandas as pd
import numpy as np
import re

import json

app = Flask(__name__)


#==============================================================================#
#=                                 Data Funcs                                 =#
#==============================================================================#

def get_json(dist_type="normal", arg1=100, arg2=35, size=20,
             feat_name="obv_", sort=True, reverse=False):
    """
    dist_type="normal":
        The following are examples of np.random.<dist_type> that will
        successfully generate data:
            "normal":  (loc=arg1,   scale=arg2, size=size)
            "uniform": (low=arg1,   high=arg2,  size=size)
            "randint": (low=arg1,   high=arg2,  size=size)
            "beta":    (a=arg1,     b=arg2,     size=size)
            "gamma":   (shape=arg1, scale=arg2, size=size)
    
    arg1=100:
        first arg in np.random.<dist_type>
    
    arg2=35:
        second arg in np.random.<dist_type>
    
    size=20:
        Number of observations in the distribution
    
    feat_name="obv_":
        Name to be used in the observation
    
    sort=True:
        Whether or not to sort the data
    
    reverse=False
        Wether to sort in reverse
    """

    feats = eval(f"np.random.{dist_type}({arg1}, {arg2}, {size})")
    if sort:
        feats = sorted(feats, reverse=reverse)

    labels = [feat_name + str(x + 1) for x in range(size)]
    
    data = {k: f'{v:.2f}' for k, v in zip(labels, feats)}
    json_data = json.dumps(data)

    return json_data

def get_md_json(size=20, feat_name="obv_", n_dims=5):
    """
    Used to create multi-demensional data for scatter splot
    Scale is different for dimensions 4 and 5
    """
    
    def create_feat(n_dims):
        loc = [0, 0, 0, 1, 7]
        scale = [2, 2, 2, 0.33, 3.5]
        feat = [np.random.normal(loc[i], scale[i]) for i in range(n_dims)]
        return feat
    
    feats = [create_feat(n_dims) for i in range(size)]
    labels = [feat_name + str(x + 1) for x in range(size)]
    
    data = {k: {i: f'{feat[i]:.2f}' for i in range(n_dims)} for k, feat in zip(labels, feats)}
    
    json_data = json.dumps(data)
    
    return json_data    

#==============================================================================#
#=                            Component Renderers                             =#
#==============================================================================#

@app.route("/show_csv", methods=["POST"])
def show_csv():
    """
    Renders the file selected by the user
    Note that this is for demo purpose and has a static directory
    """

    file_name = request.form['file_name']

    if file_name:
        df = pd.read_csv("demo_upload/" + file_name)
        JSON_data = df.T.to_json()
    else:
        JSON_data = jsonify({"error" : "Missing Data !"})

    return JSON_data

#==============================================================================#
#=                             Template Renderers                             =#
#==============================================================================#

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/results')

def results():
    data = pd.read_excel('demo_upload/btc_data.xlsx')
    data.set_index(['datetime'], inplace=True)
    data.index.name=None
    return render_template('results.html')


@app.route('/analytics')
def analytics():
    df = pd.read_csv("demo_upload/LogitSimulation.csv")
    data1 = df.groupby("State").predprob.mean().sort_values(ascending=False)[:20].to_json()
    state_bool =  df['State']=='CA'
    data2 = df[state_bool].to_json()
   

    return render_template('analytics.html',
                           graphJSON1=data1,
                           graphJSON2=data2)

@app.route('/sand_box')
def sandbox():
    return render_template('sand_box.html')

if __name__ == '__main__':
    app.run(debug=True)