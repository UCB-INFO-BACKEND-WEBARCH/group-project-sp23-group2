# Group 2 Proposal


## Team name & your members
* Rui Li
* Angela Liu
* Han Yang
* Shiyu Yin

## Idea Summary
We propose to develop an API that utilizes the Social Vulnerability to Environmental Hazards paper by Cutter et al.(https://onlinelibrary.wiley.com/doi/10.1111/1540-6237.8402002) as inspiration. Our goal is to provide a comprehensive report to users who inquire about a specific county's social vulnerability index (SVI). Our API will consist of three essential components:

1. Firstly, the API will receive a user's input query (County, State, and email) and utilize the Census API to retrieve a list of variables (demographics and income) for the requested County and State. Our API will use the ACS1 tables to collect data from the past ten years.
2. Secondly, our API will calculate the SVI score for the specific county and compare it to the State's average SVI score. We will generate a graphical representation of the comparison using GGplot or Matplotlib and store it on the server.
3. Lastly, our API will use an async task queue(MAYBE, let me know if you guys want to do this or not, we can skip) to send an email to the user who requested the information. The email will include a graph generated from the previous step and will be sent using SendGrid.

In conclusion, our API will provide users with an automated report that assesses a given county's SVI score, compares it to the State's average score for the past ten years, and delivers the report via email.

## What API you plan to use
1. Census API: https://www.census.gov/data/developers/data-sets/acs-1year.html
2. SendGrid API: https://github.com/sendgrid/sendgrid-python
