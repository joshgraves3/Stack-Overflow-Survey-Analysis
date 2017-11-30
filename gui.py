# kivy imports
from kivy.core.window import Window
Window.maximize()
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.factory import Factory

# logic imports
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

# backend import
import read_backend as backend


class Screen1(Screen):

	def __init__(self, **kwargs):
		super(Screen1, self).__init__(**kwargs)

		# set up popup for graphs
		self.popup_layout = BoxLayout(orientation='vertical')
		self.graph_area = BoxLayout(id='graph_layout', size_hint=(1, .8))
		self.close_btn = Button(id='close_button', size_hint=(1, .2), text='Close', on_release=self.close_popup)
		self.popup_layout.add_widget(self.graph_area)
		self.popup_layout.add_widget(self.close_btn)
		self.popup = Popup(id='graph_popup', content=self.popup_layout, size_hint=(.7, .7), title='Graph')

		# instantiate degree field spinner
		self.degree_field_spinner = self.ids.degree_field_spinner
		self.degree_field_spinner.bind(text=self.select_degree_field)
		self.degree_field_spinner.values = backend.backend_data['degree_fields']

		# instantiate employment block
		self.employment_title_label = self.ids.employment_title_label
		self.total_employed_label = self.ids.total_employed_label
		self.total_unemployed_label = self.ids.total_unemployed_label
		self.percent_employed_label = self.ids.percent_employed_label
		self.employment_graph_btn = self.ids.employment_graph_btn

		# instantiate statisfaction block
		self.satisfaction_title_label = self.ids.satisfaction_title_label
		self.satisfaction_label = self.ids.satisfaction_label

		# instantiate degree types block
		self.degree_types_title_label = self.ids.degree_types_title_label
		self.no_degree_label = self.ids.no_degree_label
		self.associates_label = self.ids.associates_label
		self.bachelors_label = self.ids.bachelors_label
		self.masters_label = self.ids.masters_label
		self.phd_label = self.ids.phd_label
		self.degree_types_graph_btn = self.ids.degree_types_graph_btn

		# instantiate glassdoor block
		self.glassdoor_title_label = self.ids.glassdoor_title_label
		self.job_types_spinner = self.ids.job_types_spinner
		self.job_types_spinner.bind(text=self.select_job_type)
		self.job_types_spinner.values = backend.backend_data['developer_types']
		self.go_btn = self.ids.go_btn
		self.jobs_available_label = self.ids.jobs_available_label

		# instantiate necessary class variables
		self.selected_degree_field = ''
		self.selected_job_type = ''
		self.employment_stats = None
		self.satisfaction_stats = None
		self.degree_types_stats = None

	def select_degree_field(self, spinner, text, *args):

		# set selected degree field
		self.selected_degree_field = text

		# get cleaned data
		data = backend.so_data

		# populate employment grid
		self.employment_stats = OrderedDict(sorted(backend.get_employment_stats(data, self.selected_degree_field).items()))
		self.total_employed_label.text = 'Total employed: {}'.format(self.employment_stats['employed'] + self.employment_stats['independent'])
		self.total_unemployed_label.text = 'Total unemployed: {}'.format(self.employment_stats['not'])
		self.percent_employed_label.text = 'Percent employed: {}%'.format( round((self.employment_stats['employed'] + self.employment_stats['independent'])/self.employment_stats['total'], 4)*100 )

		# populate job satisfaction grid
		self.satisfaction_stats = backend.get_satisfaction_index(data, self.selected_degree_field)
		self.satisfaction_label.text = 'Average job satisfaction: {}/10'.format( round(self.satisfaction_stats['avg_satisfaction'],2) )

		# populate degree types grid
		self.degree_types_stats = OrderedDict(sorted(backend.get_degree_type_stats(data, self.selected_degree_field).items()))
		self.bachelors_label.text = 'Bachelor\'s Degree: {}'.format(self.degree_types_stats["bachelor's degree"])
		self.masters_label.text = 'Master\'s Degree: {}'.format(self.degree_types_stats["master's degree"])
		self.phd_label.text = 'Ph.D: {}'.format(self.degree_types_stats["doctoral degree"])
		self.associates_label.text = 'Associate\'s Degree: {}'.format(self.degree_types_stats['some college w/ no degree'])
		self.no_degree_label.text = 'No Degree: {}'.format(self.degree_types_stats['none'])

	def select_job_type(self, spinner, text, *args):

		# set selected job type to feed to API
		self.selected_job_type = self.clean_job_type(text)

	def clean_job_type(self, job):

		# replace space with dash for API
		clean_job = job.replace(' ','-')

		# split multiple entries and take first
		if '/' in clean_job:
			clean_job = clean_job.split('/')[0]

		return clean_job

	def plot_employment(self):

 		# set graph
		graph = self.create_plot(self.employment_stats, 'Employment Status', 'Employment Status Aggregates')

		# put graph to popup and display
		self.graph_area.add_widget(FigureCanvasKivyAgg(graph))
		self.popup.open()

	def plot_degree_types(self):

		# set graph
		graph = self.create_plot(self.degree_types_stats, 'Degree Type', 'Degree Type Aggregates')

		# add graph to popup and display
		self.graph_area.add_widget(FigureCanvasKivyAgg(plt.gcf()))
		self.popup.open()

	def create_plot(self, dict, x_label, title):

		# create histograms and return gcf to be put in popup
		x_vals = np.arange(0, len(dict))
		x_pos = np.arange(len(x_vals))
		plt.bar(x_vals, height=dict.values())
		plt.xticks(x_pos, dict.keys())
		plt.xlabel(x_label)
		plt.title(title)

		return plt.gcf()

	def close_popup(self, *args):

		# clear everything in the popup for potential new plot
		self.graph_area.clear_widgets()
		plt.gcf().clear()
		self.popup.dismiss()

	def process_glassdoor_api(self, *args):

		# check to make sure user has selected something
		if self.selected_job_type == '':
			return

		jobs_available = backend.process_glassdoor_response(self.selected_job_type)

		self.jobs_available_label.text = 'Number of Jobs Available for Selected Job: {}'.format(jobs_available)


class OccupationApp(App):
	def build(self):
		Builder.load_file(os.getcwd() + '/initial_screen.kv')
		inital_screen = Screen1()
		sm = ScreenManager()
		sm.add_widget(inital_screen)
		return sm

if __name__ == '__main__':
	OccupationApp().run()
