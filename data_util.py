import requests
import pandas as pd
from scipy import optimize
import cachetools.func


# TODO: add clear cache functionality
# TODO: add active cases
@cachetools.func.ttl_cache(maxsize=1, ttl=5 * 60 * 60)
def get_national_ts():
    national_data_raw = requests.get('https://api.covid19india.org/data.json')
    # TODO: depending on response return json or throw error
    national_data_raw = national_data_raw.json()
    df = pd.DataFrame(national_data_raw['cases_time_series'])
    df['dailyconfirmed'] = df['dailyconfirmed'].astype(int)
    df['dailydeceased'] = df['dailydeceased'].astype(int)
    df['dailyrecovered'] = df['dailyrecovered'].astype(int)
    df['totalconfirmed'] = df['totalconfirmed'].astype(int)
    df['totaldeceased'] = df['totaldeceased'].astype(int)
    df['totalrecovered'] = df['totalrecovered'].astype(int)
    df['date'] = pd.to_datetime(df['date'] + " 2020", format='%d %B %Y')
    return df


@cachetools.func.ttl_cache(maxsize=1, ttl=10 * 60 * 60)
def get_state_ts():
    state_code_raw = requests.get("https://api.covid19india.org/state_district_wise.json")
    state_code = state_code_raw.json()

    state_code_map = dict()

    for state, state_dict in state_code.items():
        state_code_map[state_dict['statecode']] = state

    state_data_raw = requests.get("https://api.covid19india.org/v4/data-all.json")
    state_data_raw = state_data_raw.json()

    data_raw = []

    for date, states_dict in state_data_raw.items():
        for state_code, state_dict in states_dict.items():
            data = dict()
            data['date'] = date
            data['state_code'] = state_code
            data['population'] = state_dict.get('meta', dict()).get('population', None)
            data['totalconfirmed'] = state_dict.get('total', dict()).get('confirmed', None)
            data['totalrecovered'] = state_dict.get('total', dict()).get('recovered', None)
            data['totaldeceased'] = state_dict.get('total', dict()).get('deceased', None)
            data['type'] = 'state'
            data['district_name'] = None
            data['state'] = state_code_map.get(state_code, state_code)
            data_raw.append(data)

            if "districts" in state_dict:
                for district_name, district_dict in state_dict['districts'].items():
                    data = dict()
                    data['date'] = date
                    data['state_code'] = state_code
                    data['population'] = district_dict.get('meta', dict()).get('population', None)
                    data['totalconfirmed'] = district_dict.get('total', dict()).get('confirmed', None)
                    data['totalrecovered'] = district_dict.get('total', dict()).get('recovered', None)
                    data['totaldeceased'] = district_dict.get('total', dict()).get('deceased', None)
                    data['type'] = 'district'
                    data['district_name'] = district_name
                    data['state'] = state_code_map.get(state_code, state_code)
                    data_raw.append(data)

    df = pd.DataFrame(data_raw)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df


@cachetools.func.ttl_cache(maxsize=128, ttl=1 * 60 * 60)
def get_filtered_location_ts(location_identifier):
    df = get_state_ts()

    if "state" in location_identifier:
        state = location_identifier.split("-")[1].strip()
        print(state)
        df = df[(df.state == state) & (df.type == 'state')]
        df = df.sort_values(by=['date'])
        print(df.tail())
    elif "dist" in location_identifier:
        district = location_identifier.split("-")[1].strip()
        print(district)
        df = df[(df.district_name == district) & (df.type == 'district')]
        df = df.sort_values(by=['date'])
        print(df.tail())
    else:
        raise (Exception("unknown location identifier"))

    return df


@cachetools.func.ttl_cache(maxsize=128, ttl=15 * 60 * 60)
def get_location_list(query):
    df = get_state_ts()
    if query:
        state_df = df[(df.type == 'state') & (df.state != None) & (df.state.str.contains(query, case=False))]
    else:
        state_df = df[(df.type == 'state') & (df.state != None)]
    state_names = state_df.state.unique().tolist()
    state_names = list(map(lambda x: "state - " + x, state_names))

    if query:
        district_df = df[(df.type == 'district') &
                         (df.state != None) &
                         (df.district_name != None) &
                         (df.district_name.str.contains(query, case=False))]
    else:
        district_df = df[(df.type == 'district') & (df.state != None) & (df.district_name != None)]
    district_names = district_df.district_name.unique().tolist()
    district_names = list(map(lambda x: "dist - " + x, district_names))

    return state_names + district_names + ['india']


def get_formatted_cases_data(df):
    df['date'] = df['date'].astype(str)

    df['totalconfirmed'] = df['totalconfirmed'].fillna(0)
    df['totaldeceased'] = df['totaldeceased'].fillna(0)
    df['totalrecovered'] = df['totalrecovered'].fillna(0)

    data = dict()
    data['dates'] = df['date'].values.tolist()
    data['totalconfirmed'] = df['totalconfirmed'].values.tolist()
    data['totaldeceased'] = df['totaldeceased'].values.tolist()
    data['totalrecovered'] = df['totalrecovered'].values.tolist()

    return data


# TODO: add dropdown for different metrics
def add_levitt_score(df, metric='totalconfirmed'):
    ts = df[['date', metric]]
    prev_metric_col = 'prev_' + metric
    ts[prev_metric_col] = ts[metric]
    prev_metric = ts[prev_metric_col].shift(1)
    ts[prev_metric_col] = prev_metric
    ts = ts.fillna(1)
    ts['levitt_score'] = ts[metric] / ts[prev_metric_col]
    ts = ts.iloc[1:]
    ts = ts[ts.levitt_score < 2]
    ts = ts[ts.date > '2020-04-01']
    return ts


def get_formatted_levitt_data(df):
    df['datestr'] = df['date'].astype(str)
    data = dict()
    data['dates'] = df['datestr'].values.tolist()
    data['levitt_score'] = list(map(lambda x: float(x), df['levitt_score'].values.tolist()))
    return data


def get_formatted_estimates(input_dict):
    df = input_dict['df']
    levitt_data = get_formatted_levitt_data(df)
    levitt_data['linear_fit'] = df['linear_fit'].values.tolist()
    levitt_data['num_days_estimated'] = int(input_dict['num_days_estimated'])
    return levitt_data


def find_soln(fn, param1, param2):
    l = 0
    r = 1 * 365

    if fn(r, param1, param2) > 1:
        return -1

    tol = 1e-6
    soln = 1
    max_iter = 5e6
    iter = 0

    while (l <= r) and (iter < max_iter):
        m = (l + r) / 2
        s = fn(m, param1, param2)
        e = s - soln

        if abs(e) < tol:
            return m
        elif e > 0:
            l = m + tol
        elif e < 0:
            r = m - tol

        iter += 1

    return -1


def fit_linear_estimator(ts, N_past_days=50):
    ts['date'] = pd.to_datetime(ts['date'])
    ts.sort_values(by=['date'])
    day_0 = ts.iloc[0].date
    print(ts.head())
    print(type(ts.date.tolist()[0]))
    ts['num_days_passed'] = (ts['date'] - day_0).dt.days

    last_day = ts.iloc[-1].num_days_passed
    train_ts = ts[ts.num_days_passed > last_day - N_past_days]

    lnr_fn = lambda x, m, c: m * x + c
    (m, c), pcov = optimize.curve_fit(lnr_fn, train_ts.num_days_passed, train_ts.levitt_score, p0=(-1, 1))

    ts['linear_fit'] = lnr_fn(ts.num_days_passed, m, c)
    # print(m, c)

    total_num_days = find_soln(lnr_fn, m, c)
    # print(total_num_days)
    num_days_estimated = round(total_num_days) - last_day if total_num_days >= 0 else None
    # print(num_days_estimated)

    result = dict()
    result['df'] = ts
    if num_days_estimated:
        result['num_days_estimated'] = max(num_days_estimated, 0)
    return result
