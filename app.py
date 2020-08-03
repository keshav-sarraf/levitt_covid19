from flask import Flask, render_template, jsonify, request

from data_util import get_national_ts, get_formatted_cases_data, add_levitt_score, get_formatted_levitt_data, \
    fit_linear_estimator, get_formatted_estimates, get_location_list, get_filtered_location_ts

app = Flask(__name__)


@app.route('/')
def landing_page():
    return render_template('landing.html')


@app.route('/api/locations')
def get_location_list_route():
    query = request.args.get('q')
    loc_list = get_location_list(query)
    return jsonify(loc_list)


@app.route('/api/cases/<area>')
def get_cases_data(area):
    if area == "india":
        df = get_national_ts()
        json = get_formatted_cases_data(df)
    else:
        df = get_filtered_location_ts(area)
        json = get_formatted_cases_data(df)

    return jsonify(json)


@app.route('/api/levitt/<area>')
def get_levitt_data(area):
    if area == "india":
        df = get_national_ts()
    else:
        df = get_filtered_location_ts(area)

    levitt_df = add_levitt_score(df)
    json = get_formatted_levitt_data(levitt_df)

    return jsonify(json)


@app.route('/api/levitt/fit/<area>/<int:num_past_days>')
def get_estimated_time(area, num_past_days):
    if area == "india":
        df = get_national_ts()
    else:
        df = get_filtered_location_ts(area)

    levitt_df = add_levitt_score(df)
    estimated_results = fit_linear_estimator(levitt_df, N_past_days=num_past_days)
    json = get_formatted_estimates(estimated_results)
    print(json)
    for key, val in json.items():
        print("Key " + key + " type " + str(type(key)))
        print("Val " + " type " + str(type(val)))

    return jsonify(json)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
