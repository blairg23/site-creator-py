# -*- coding: utf-8 -*-
'''
Name: site_creator.py
Author: Blair Gemmer
Version: 20160910

Description: 

Creates a template for a web application, based on the contents 
of the "import/<project_name>" directory, where <project_name> is
the name of the current project.

'''
import os
import subprocess
import shutil

class FlaskSiteCreator():
	def __init__(self, sitename='default', import_folder=None, export_folder=None, verbose=False):
		self.sitename = sitename
		self.import_folder = import_folder
		self.export_folder = export_folder
		self.verbose = verbose

		self.in_directory = os.path.join(self.import_folder, self.sitename)
		self.in_site_directory = os.path.join(self.in_directory, self.sitename+'-website')
		self.out_directory = os.path.join(self.export_folder, self.sitename)

		self.venv_directory = os.path.join(self.out_directory, 'venv')
		self.app_directory = os.path.join(self.out_directory, 'app')

		self.input_template_directory = os.path.join(self.in_directory, 'html_pages')
		self.output_template_directory = os.path.join(self.app_directory, 'templates')

		self.pages = self.import_data(in_site_directory=self.in_site_directory)


	def import_data(self, in_site_directory=None):
		'''
		Imports the data necessary to build the site, given some directory of the
		virtual directory structure and content. Populates a "page" dictionary with
		the information and returns a list of these "page" dictionaries.
		'''
		def clean_url(url_to_clean):
			'''Clean up a filepath to become a web URL.'''
			return url_to_clean.lower().replace(in_site_directory, '').replace(' ', '_').replace(',', '').replace('\\', '/')

		pages = []
		try:
			if in_site_directory == None:
				raise IOError('[ERROR] No input directory defined.')
			else:				
				for root, subdirectories, files in os.walk(in_site_directory):
					page = {}
					cleaned_root = clean_url(root)
					current_folder = root.split(os.path.sep)[-1]
					if self.verbose:
						print 'root:', root
						print 'cleaned root:', cleaned_root
						print 'subdirectories:', subdirectories
						print 'files:', files
						print '\n'
					# If we're not at the root directory:
					if not root == in_site_directory:
						url = cleaned_root						
						page['url'] = url
						page['title'] = current_folder
						page['jumbotron'] = current_folder + '.'
						links = []
						if not len(subdirectories) == 0:
							for subdirectory in subdirectories:
								link = {}
								cleaned_subdirectory = clean_url(subdirectory)
								link['display_name'] = subdirectory
								link['url'] = os.path.join(url, cleaned_subdirectory)
								links.append(link)
						page['links'] = links
						pages.append(page)
					else:
						# Currently not using this:
						tabs = []
						for subdirectory in subdirectories:
							tabs.append(subdirectory)
					
		except Exception as e:
			print e

		return pages



	def create_virtual_environment(self, out_directory=None, venv_name='venv'):
		'''
		Creates the Python virtual environment to develop with.
		'''
		try:
			if out_directory == None:
				raise IOError('[ERROR] No output directory defined.')
			else:
				venv_directory = os.path.join(out_directory, venv_name)
				command = ['virtualenv '+ venv_directory]
				subprocess.call([command])
		except Exception as e:
			print e


	def create_flask_directory(self, out_directory=None, sitename='default'):
		'''
		Creates all the basic elements for a Flask project.
		'''
		try:
			app_path = self.app_directory
			site_directories = [
						app_path,
						os.path.join(app_path, 'data'),
						os.path.join(app_path, 'static'),
						os.path.join(app_path, 'static', 'css'),
						os.path.join(app_path, 'static', 'img'),
						os.path.join(app_path, 'static', 'js'),						
					]
			if out_directory == None:
				raise IOError('[ERROR] No output directory defined.')
			else:
				for site_directory in site_directories:
					os.makedirs(site_directory)
					print '[CREATED] {site_directory} successfully...'.format(site_directory=site_directory)
		except Exception as e:
			print e


	def create_base_page(self, page={}):
		'''
		Creates a base.html page to act as the general template for the site.
		'''
		pass


	def move_template_pages(self, input_template_directory=None, output_template_directory=None):
		'''
		Moves previously created template pages to the appropriate output directory.
		'''
		shutil.copytree(input_template_directory, output_template_directory)
		print '[COPYING] contents of {input_template_directory} to {output_template_directory}...'.format(
																										input_template_directory=input_template_directory,
																										output_template_directory=output_template_directory
																									)	


	def create_view_pages(self, app_directory=None, pages=[]):
		'''
		Creates Flask functions that act as individual routes or pages.
		'''
		if pages == []:
			pages = self.pages

		try:
			if app_directory == None:
				raise IOError('[ERROR] No application directory defined.')
			else:
				pass				
		except Exception as e:
			print e

	def run(self):
		sitename = self.sitename
		import_folder = self.import_folder
		export_folder = self.export_folder

		in_directory = self.in_directory
		out_directory = self.out_directory

		venv_directory = self.venv_directory
		app_directory = self.app_directory

		input_template_directory = self.input_template_directory
		output_template_directory = self.output_template_directory

		if not os.path.exists(venv_directory):
			self.create_virtual_environment
		
		if os.path.exists(app_directory):
			shutil.rmtree(app_directory)
			print '[DELETED] {app_directory}...'.format(app_directory=app_directory)
		if os.path.exists(output_template_directory):
			shutil.rmtree(output_template_directory)
			print '[DELETED] {output_template_directory}...'.format(output_template_directory=output_template_directory)

		self.create_flask_directory(out_directory=out_directory, sitename=sitename)

		self.move_template_pages(
									input_template_directory=input_template_directory,
									output_template_directory=output_template_directory
								)
		
		self.create_view_pages(app_directory=app_directory)


if __name__ == '__main__':
	import_folder = os.path.join('data', 'import')
	export_folder = os.path.join('data', 'export')
	sitename = 'testing'
	site_creator = FlaskSiteCreator(
									sitename=sitename,
									import_folder=import_folder,
									export_folder=export_folder,
									verbose=False
								)	

	site_creator.run()


# TODO:
# 1. Import pics, hash them, and push to export folder
# 2. Write views.py functions (append to current, default ones?)
# 3. Write tests for functions