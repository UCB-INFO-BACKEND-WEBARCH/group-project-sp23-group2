# Learnings.md

## Team name & your members
* Rui Li
* Angela Liu
* Han Yang
* Shiyu Yin

## What was your original goal and how much of it were you able to achieve?
Our original goal for this project was to develop a county-level Social Vulnerability Index (SVI) API that sends both the index as well as a corresponding graph via email upon user inquiry. We planned to rely on the US Census API to obtain a series of socioeconomic and demographic data, and then calculate the SVI index based on the method outlined in paper [*Social Vulnerability to Environmental Hazards*](https://onlinelibrary.wiley.com/doi/10.1111/1540-6237.8402002).
### What we achieved as planned
* Receive user input with a county name, a state name, and an email address
* Retrieve data required from the US Census API
* Calculate a county-level SVI for the inquired county and a state average SVI for the state where the inquired county is located
* Send both indices in a json format using SendGrid API to the email address users inputted
* Store the request input data (county name, state name, and email address) into census_request_history database and check the request history through an endpoint
### What we achieved as extras
* Validate the county and state names using the Nominatim API provided by OpenStreetMap (OSM)
### Limitations / What we were unable to achieve
* Generate a graph for the indices and send it via email
* The Census API does not provide data for every county

## A description of what your project does and the functionality that it provides
* Users send a json POST request body to endpoint "/report" in the following format:
```
{
    "county": "alameda",
    "state": "california",
    "email": "han_yang@berkeley.edu"
}
```
* OpenStreetMap API validates the county and state names
* If valid, an async task will be initiated. Users receive a json response as the following:
```
{
    'message': 'We will process your request and email you the results when ready.',
    'taskID': taskID
}
```
* The async task first sends a request to the US Census API to obtain relevant data.
* If successful, the API starts calculate SVIs for the county and the state
* If successful, the API then sends an email to the email address users inputted, with a json body in the following format:
```
{
    "county": "Alameda County",
    "county_index": 3.74,
    "state": "California",
    "state_avg_index": 4.05
}
```
* If county or state name is invalid, users receive "Invalid county or state, please verify your input"
* If no data is found, users receive "County not in State or this dataset"
* If SVI calculation cannot proceed, users receive "Data is not in the expected format"
* If emails cannot be sent, users receive "Something is not right. Email not sent."

## What did you learn from the project? 
* We learned how to construct a backend development pipeline while working with containers
* We learned how to diagram the development work flow and divide up the work between multiple people and stages.
* We learned how to work with external APIs, async task queues, inspect the 'job' with flower, and how to containerize apps and host a sql database with Docker container. 
