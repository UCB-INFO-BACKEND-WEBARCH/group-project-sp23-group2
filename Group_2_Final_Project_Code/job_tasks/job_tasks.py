from flask import Flask, jsonify, request
import requests
import pandas as pd
import numpy as np
import os
from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging


broker_url = os.environ.get("CELERY_BROKER_URL"),
res_backend = os.environ.get("CELERY_RESULT_BACKEND")

celery_app = Celery(name='job_tasks',
                    broker=broker_url,
                    result_backend=res_backend)


#Computing Vunlerability Index based on available census variables
def calc_index(county,state,data):
        #Load state data into dataframe (nested list -> df)
        try:
                #Rename columns
                cols = ['county','m_ratio','depend_ratio','tot_25','below_hs_25','hs_25','tot_pov','pov','m_sp','f_sp','tot_fam','n_vehicle_pct','rent_pct','mobile_hm_pct','white_pct','state_code','county_code']
                data_df = pd.DataFrame(data[1:],columns = cols)
                
                #Check if not county in state ?> return error msg
                county_state = county+", "+state
                print(county_state)
                if county_state in data_df['county'].unique():
                        
                        #Clean df, compute columns
                        #1.Fill Nans with state average; cast columns data type to numeric
                        data_df[cols[1:-2]] = data_df[cols[1:-2]].apply(pd.to_numeric, errors = 'coerce')
                        data_df.iloc[:,1:-2] = data_df.iloc[:,1:-2].mask(data_df.iloc[:,1:-2]<0, np.nan)
                        data_df.loc[:,cols[1:-2]] = data_df[cols[1:-2]].fillna(data_df[cols[1:-2]].mean())

                        #2.Convert m_ratio to f_ratio
                        cols_drop = []
                        data_df['f_ratio'] = round(100/data_df['m_ratio'],4)
                        cols_drop.append('m_ratio')

                        #3.Calculate low_edu_pct
                        data_df['low_edu_pct'] = round((data_df['below_hs_25']+data_df['hs_25'])/data_df['tot_25'],4)
                        cols_drop.extend(['tot_25','below_hs_25','hs_25'])
                        
                        #4.Calculate pov_pct
                        data_df['pov_pct'] = round(data_df['pov']/data_df['tot_pov'],4)
                        cols_drop.extend(['tot_pov','pov'])

                        #5.Calculate sp_pct
                        data_df['sp_pct'] = round((data_df['m_sp']+data_df['f_sp'])/data_df['tot_fam'],4)
                        cols_drop.extend(['m_sp','f_sp','tot_fam'])

                        #6.Calculate minority_pct
                        data_df['minority_pct'] = 1 - data_df['white_pct']
                        cols_drop.extend(['white_pct','state_code','county_code'])
                        data_df.drop(columns= cols_drop,inplace=True)
                        
                        #7.Compute index and state average index with max-min normalization
                        def max_min(col):
                                return(col-col.min())/(col.max()-col.min())
                        data_df.loc[:,data_df.columns[1:]] = data_df[data_df.columns[1:]].apply(max_min)
                        data_df['vul_ind'] = data_df.iloc[:,1:].sum(axis = 1)

                        state_avg = round(data_df['vul_ind'].mean(),2)
                        county_ind = round(data_df.loc[data_df['county'] == county_state,'vul_ind'],2).values[0]
                        #Return output as json:
                        #Format: {"county":"str","county_index":float,"state":"str","state_avg_index":float}
                        #Example: {"county":"Los Angeles County", "county_index":4.40, "state":"California", "state_avg_index": 4.05}
                        output = {'county':county,'county_index':county_ind,"state":state, 'state_avg_index':state_avg}
                        return jsonify(output)
                else:
                        return "County not in State or this dataset", 403
        except:
                return "Data is not in the expected format"
        
        
@celery_app.task
def send_census_report(county, state, email):
    
    #Reformat string for census api
    county = county.lower().lstrip().rstrip()
    state = state.lower().lstrip().rstrip().capitalize()
    
    county = [word.capitalize() for word in county.split(" ")]
    county = " ".join(county)
    county += " County"

    #Define variable names that will be used to call census api 
    vars = ['NAME',
            "S0101_C01_033E",
            "S0101_C01_034E",
            "S0701_C01_033E",
            "S0701_C01_034E",
            "S0701_C01_035E",
            "S1701_C02_001E",
            "S1701_C01_001E",
            "S1101_C03_005E",
            "S1101_C04_005E",
            "S1101_C01_005E",
            "S0802_C01_094E",
            "S1101_C01_019E",
            "S1101_C01_017E",
            "S0601_C01_014E"]
    vars = ",".join(vars)
    
    #Mapping state to state codes in census
    state_codes = {'Alabama': '01',
        'Puerto Rico': '72',
        'Arizona': '04',
        'Arkansas': '05',
        'California': '06',
        'Colorado': '08',
        'Connecticut': '09',
        'Delaware': '10',
        'District of Columbia': '11',
        'Florida': '12',
        'Georgia': '13',
        'Hawaii': '15',
        'Idaho': '16',
        'Illinois': '17',
        'Indiana': '18',
        'Iowa': '19',
        'Kansas': '20',
        'Kentucky': '21',
        'Louisiana': '22',
        'Maine': '23',
        'Maryland': '24',
        'Massachusetts': '25',
        'Michigan': '26',
        'Minnesota': '27',
        'Mississippi': '28',
        'Missouri': '29',
        'Montana': '30',
        'Nebraska': '31',
        'Nevada': '32',
        'New Hampshire': '33',
        'New Jersey': '34',
        'New Mexico': '35',
        'New York': '36',
        'North Carolina': '37',
        'North Dakota': '38',
        'Ohio': '39',
        'Oklahoma': '40',
        'Oregon': '41',
        'Pennsylvania': '42',
        'Rhode Island': '44',
        'South Carolina': '45',
        'South Dakota': '46',
        'Tennessee': '47',
        'Texas': '48',
        'Utah': '49',
        'Vermont': '50',
        'Virginia': '51',
        'Washington': '53',
        'West Virginia': '54',
        'Wisconsin': '55',
        'Wyoming': '56',
        'Alaska': '02'}
    
    #Validate state (try-except can be removed if the validation works well in census_report.py!!!)
    try:
            state_num = state_codes[state]
    except:
            return "Invalid State name, please verify your input", 403
    
    
    #Census api url
    #Documentation - Subject Tables: https://www.census.gov/data/developers/data-sets/acs-1year.2021.html#list-tab-1471773036
    census_api = "https://api.census.gov/data/2021/acs/acs1/subject"

    #Api key - free key so I'm just gonna put it here
    api_key =  "5088592d798320729bc69a3c56b6451189c893f7"
    
    #Config api call
    api_call = "%(census_api)s?get=%(var_list)s&for=county:*&in=state:%(state_num)s&key=%(api_key)s" % {"census_api":census_api,"var_list":vars,"state_num":state_num,"api_key":api_key}
    
    #Now we call the api
    try: 
        r = requests.get(api_call)
        r_data = r.json()
        
        result = calc_index(county,state,r_data)
        message = Mail(
                from_email="han_yang@berkeley.edu",
                to_emails=email,
                subject="Your SVI report",
                html_content=result)
        try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                sg.send(message)
        except Exception as e:
                logging.error(e)
    except:
        return "not right"