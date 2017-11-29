import pandas as pd
import numpy as np
import os
import shutil
from itertools import chain


def clean_data():
	print('do data cleaning here')

	# data originally had 154 columns, did manual review to see which were necessary for this project
	useful_columns = ['EmploymentStatus', 'FormalEducation', 'MajorUndergrad', 'DeveloperType', 'CareerSatisfaction', 'JobSatisfaction', 'Salary', 'ExpectedSalary', 'Gender']

	# read in data with pandas
	so_data = pd.read_csv(os.getcwd() + '/stack-overflow-developer-survey-2017/survey_results_public.csv', skipinitialspace=True, usecols=useful_columns)
	so_data = so_data.replace(np.nan, '', regex=True)

	for column in so_data.columns:

		# convert all string columns to lower case
		if so_data[column].dtype == 'object':
			so_data[column] = so_data[column].str.lower()

		# clean up employment statuses
		if column == 'EmploymentStatus':
			so_data[column] = so_data[column].str.split(' ').str[0]

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

def get_employment_stats(data, degree_field):
	print('get employment stats here')

def get_satisfaction_index(data, degree_field):
	print('get satisfaction index here')

def get_degree_type_stats(data, degree_field):
	print('get degree type stats here')

def process_glassdoor_api(job_type):
	print('process glassdoor api here')

# run everything
so_data = clean_data()
backend_data = set_backend_data_vars(so_data)
