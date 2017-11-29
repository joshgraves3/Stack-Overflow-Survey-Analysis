# kivy imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.factory import Factory

# logic imports
import os
import matplotlib.pyplot as plt
import numpy as np

# backend import
import read_backend as backend


class InitialScreen(Screen):

	def __init__(self, **kwargs):
		super(InitialScreen, self).__init__(**kwargs)

		# instantiate graph popup
		self.graph_popup = Factory.GraphPopup()
		self.graph_popup_graph = self.graph_popup.ids.graph_layout

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

	def select_degree_field(self, spinner, text, *args):

		# TODO: error checking of spinner
		self.selected_degree_field = text
		print(self.selected_degree_field)

		# TODO: use backend to populate everything based on degree field chosen

	def select_job_type(self, spinner, text, *args):
		self.selected_job_type = text
		print(self.selected_job_type)

	def show_plot(self):
		self.graph_popup.open()

		x = [0,1,2,3]
		x_pos = np.arange(len(x))
		plt.bar(x, height=[10, 20, 50, 2])
		plt.xticks(x_pos, ['Bachelor\'s', 'Master\'s', 'PhD', 'Other'])
		plt.xlabel('Degree Type')
		plt.ylabel('Number of People Holding Degree')

		self.graph_popup_graph.add_widget(FigureCanvasKivyAgg(plt.gcf()))

	def create_plot(self, x, y, x_label, y_label):
		print('create plot')

	def process_glassdoor_api(self, *args):
		# TODO: process glassdoor API
		# TODO: error checking for input of spinner
		self.jobs_available_label.text = 'Number of Jobs Available: 12,345'

		
class OccupationApp(App):
	def build(self):
		Builder.load_file(os.getcwd() + '/initial_screen.kv')
		inital_screen = InitialScreen()
		sm = ScreenManager()
		sm.add_widget(inital_screen)
		return sm

if __name__ == '__main__':
	OccupationApp().run()
