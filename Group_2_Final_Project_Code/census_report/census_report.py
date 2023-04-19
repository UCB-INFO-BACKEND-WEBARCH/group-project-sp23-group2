from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from worker import send_census_report, celery_app
# from celery.result import AsyncResult
import json
import requests

app = Flask(__name__)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/request_history"
db.init_app(app)


class Census_request_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    county = db.Column(db.String(40))
    state = db.Column(db.String(20))
    email = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'county': self.county,
            'state': self.state,
            'email': self.email,
        }


    
def validate_county_state_pair(state_name, county_name):
    base_url = 'https://nominatim.openstreetmap.org/search'

    params = {
        'q': f'{county_name} County, {state_name}, USA',
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if not data:
            return False
        result = data[0]['address']
        if result.get('county', '').lower() == f'{county_name} County'.lower() and result.get('state', '').lower() == state_name.lower():
            return True
        return False
    else:
        print('Error:', response.status_code, flush=True)
        return None



@app.route("/report", methods=['POST'])
# call async task send_sensus_report in worker.py and store the request input into history db
def report():
    try:
        input = request.get_json().get('input')
        county = input['county']
        state = input['state']
        email = input['email']
    except:
        return "Invalid input", 400
    
    if validate_county_state_pair(state, county):
        new_request_history = Census_request_history(county=county, state=state, email=email)
        db.session.add(new_request_history)
        db.session.commit()
        print('Request history added successfully', flush=True)

        asyncTask = send_census_report.delay(county, state, email)
        taskID = asyncTask.id
        return json.dumps({
            'message': 'We will process your request and email you the results when ready.',
            'taskID': taskID
        })
    else:
        return "Invalid county or state, please verify your input", 400


@app.route("/result/<id>", methods=['GET'])
# return result and save SVI from worker db to history db
def result(id):
    result = AsyncResult(id, app=celery_app)
    return jsonify(result)


@app.route("/history", methods=['GET'])
def history():
    census_data_history = Census_request_history.query.all()
    return jsonify([census_data.to_dict() for census_data in census_data_history])


# python -m flask --app census_report run --host=0.0.0.0 --port=5050

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True, port=5050)
