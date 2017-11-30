import pandas as pd
import numpy as np
import os
import shutil
import math
from itertools import chain
from urllib.request import Request, urlopen
import json


def clean_data():

	# data originally had 154 columns, did manual review to see which were necessary for this project
	useful_columns = ['EmploymentStatus', 'FormalEducation', 'MajorUndergrad', 'DeveloperType', 'CareerSatisfaction', 'JobSatisfaction', 'Salary', 'ExpectedSalary',]
	categorical_columns = ['EmploymentStatus', 'FormalEducation', 'MajorUndergrad', 'DeveloperType']
	# read in data with pandas
	so_data = pd.read_csv(os.getcwd() + '/stack-overflow-developer-survey-2017/survey_results_public.csv', skipinitialspace=True, usecols=useful_columns)
	# print('dtypes initially:\n{}\n\n'.format(so_data.dtypes))

	for column in categorical_columns:

		# convert all string columns to lower case
		if so_data[column].dtype == 'object':
			so_data[column] = so_data[column].replace(np.nan, '', regex=True)
			so_data[column] = so_data[column].str.lower()

		# clean up employment statuses
		if column == 'EmploymentStatus':
			so_data[column] = so_data[column].str.split(' ').str[0]
			so_data.loc[so_data.EmploymentStatus == 'i'] = 'independent'

		# condense degree types to be applicable
		elif column == 'FormalEducation':
			so_data.loc[so_data.FormalEducation == 'some college/university study without earning a bachelor\'s degree', 'FormalEducation'] = 'some college w/ no degree'
			so_data.loc[(so_data.FormalEducation != 'bachelor\'s degree') & (so_data.FormalEducation != 'master\'s degree') & (so_data.FormalEducation != 'doctoral degree') & (so_data.FormalEducation != 'some college w/ no degree'), 'FormalEducation'] = 'none'

		# change developer types into a set for quick lookup
		elif column == 'DeveloperType':
			so_data[column] = so_data[column].str.split('; ').apply(lambda x: set(x))

	return so_data

def set_backend_data_vars(data):

	# get list of all degree fields for dropdown
	degree_fields = list(data.MajorUndergrad.unique())
	degree_fields.remove('')

	# get all employment statuses
	employment_statuses = data.EmploymentStatus.value_counts()

	# get different types of degrees
	degree_types = list(data.FormalEducation.unique())

	# condense developer types list
	all_dev_types = []

	for dev_type in data['DeveloperType']:
		all_dev_types.append(dev_type)

	all_dev_types = set([item for sublist in all_dev_types for item in sublist])
	all_dev_types.remove('')
	all_dev_types.remove('developer with a statistics or mathematics background')
	all_dev_types.remove('other')
	all_dev_types.remove('independent')
	all_dev_types.add('software engineer')

	# initialize all variables to be quickly accessed
	variable_dict = {}
	variable_dict['degree_fields'] = degree_fields

	employment_status_counts = {}
	for i in range(len(employment_statuses)):
		employment_status_counts[employment_statuses.keys()[i]] = employment_statuses[i]

	variable_dict['employment_statuses'] = employment_status_counts

	variable_dict['degree_types'] = degree_types

	variable_dict['developer_types'] = all_dev_types

	return variable_dict

def create_stat_dictionary(data, current_col, degree_field):
	# set dictionary to house stats
	stats = {}

	# make new df with all rows that have desired degree_field
	degree_field_df = pd.DataFrame(data.loc[data['MajorUndergrad'] == degree_field][current_col])

	for value in degree_field_df[current_col].unique():
		stats[value] = degree_field_df.loc[degree_field_df[current_col] == value].count()[0]

	stats['total'] = degree_field_df.shape[0]

	return stats

def get_employment_stats(data, degree_field):
	return create_stat_dictionary(data, 'EmploymentStatus', degree_field)

def get_satisfaction_index(data, degree_field):
	satisfaction_dict = create_stat_dictionary(data, 'JobSatisfaction', degree_field)

	# calculate avg satisfaction
	cumulative_satisfaction = 0
	for key, value in satisfaction_dict.items():
		if type(key) == float and not math.isnan(key):
			cumulative_satisfaction += key*value

	satisfaction_dict['avg_satisfaction'] = cumulative_satisfaction/satisfaction_dict['total']

	return satisfaction_dict

def get_degree_type_stats(data, degree_field):
	return create_stat_dictionary(data, 'FormalEducation', degree_field)

def get_glassdoor_api_json(job_type):
	# Partner ID:	232698
	# Key:	d8TIuJMhACu
	base = 'http://api.glassdoor.com/api/api.htm?'
	v = 'v=1'
	response_format = '&format=json'
	tp = '&t.p=232698'
	tk = '&t.k=d8TIuJMhACu'
	user_ip = '&userip=88.192.249.8'
	user_agent = '&useragent=Mozilla/%2F4.0'
	action = '&action=jobs-stats'
	cities = '&returnCities=True'
	q = '&q='+job_type

	url = base+v+response_format+tp+tk+user_ip+user_agent+action+q+cities
	# print(url)
	#'http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=232698&t.k=d8TIuJMhACu&userip=88.192.249.8&useragent=Mozilla/%2F4.0&action=jobs-stats&q=engineer&returnCities=True'
	request = Request(url)
	request.add_header('User-Agent', 'Mozilla/%2F4.0')
	response = urlopen(request)
	json_return = json.loads(response.read())
	return json_return

def process_glassdoor_response(job_type):
	data = get_glassdoor_api_json(job_type)

	num_jobs_available = 0
	for city in data['response']['cities']:
		num_jobs_available += city['numJobs']

	return num_jobs_available

# run everything
so_data = clean_data()
backend_data = set_backend_data_vars(so_data)
get_satisfaction_index(so_data, 'computer science or software engineering')
