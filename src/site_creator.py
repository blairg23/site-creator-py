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
import hashlib
import json
from PIL import Image
import sys

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
		self.data_directory = os.path.join(self.app_directory, 'data')
		self.static_directory = os.path.join(self.app_directory, 'static')
		self.image_directory = os.path.join(self.static_directory, 'img')

		self.input_template_directory = os.path.join(self.in_directory, 'html_pages')
		self.output_template_directory = os.path.join(self.app_directory, 'templates')

		self.input_static_directory = os.path.join(self.in_directory, 'static_files')
		self.output_static_directory = os.path.join(self.app_directory, 'static')

		self.pages = None


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
				print '[CREATED] virtual environment {venv_name}...'.format(venv_name=venv_name)
		except Exception as e:
			print e


	def create_flask_directory(self, out_directory=None, sitename='default', debug_mode='False'):
		'''
		Creates all the basic elements for a Flask project.
		'''

		if os.path.exists(self.app_directory):
			shutil.rmtree(self.app_directory)
			print '[DELETED] {app_directory}...'.format(app_directory=self.app_directory)

		try:
			site_directories = [
						self.app_directory,
						self.data_directory,
						self.static_directory,
						os.path.join(self.static_directory, 'css'),
						self.image_directory,
						os.path.join(self.static_directory, 'js'),
					]
			if out_directory == None:
				raise IOError('[ERROR] No output directory defined.')
			else:
				for site_directory in site_directories:
					os.makedirs(site_directory)
					print '[CREATED] {site_directory} successfully...'.format(site_directory=site_directory)

			run_file_name = os.path.join(out_directory, 'run.py')
			with open(run_file_name, 'w+') as outfile:
				content = '#!flask/bin/python\n'
				content += 'from app import app as application\n'				
				content += '\n'
				content += 'if __name__ == "__main__":\n'
				content += '\tapplication.run(host="0.0.0.0", debug={debug_mode})\n'.format(debug_mode=debug_mode)
				outfile.write(content)

			init_file_name = os.path.join(self.app_directory, '__init__.py')
			with open(init_file_name, 'w+') as outfile:
				content = 'from flask import Flask\n'
				content += '\n'
				content += 'app = Flask(__name__)\n'
				content += 'from app import views\n'
				outfile.write(content)
		except Exception as e:
			print e


	def create_base_page(self, page={}):
		'''
		Creates a base.html page to act as the general template for the site.
		'''
		pass


	def move_pages(self, input_directory=None, output_directory=None):
		'''
		Moves previously created pages to the appropriate output directory.
		'''
		if os.path.exists(output_directory):
			shutil.rmtree(output_directory)
			print '[DELETED] {output_directory}...'.format(output_directory=output_directory)

		shutil.copytree(input_directory, output_directory)
		print '[COPYING] contents of {input_directory} to {output_directory}...'.format(
																							input_directory=input_directory,
																							output_directory=output_directory
																						)


	def import_data(self, in_site_directory=None):
		'''
		Imports the data necessary to build the site, given some directory of the
		virtual directory structure and content. Populates a "page" dictionary with
		the information and returns a list of these "page" dictionaries.
		'''
		def clean_url(url_to_clean):
			'''Clean up a filepath to become a web URL.'''
			return url_to_clean.lower().replace(in_site_directory, '').replace(' ', '_').replace(',', '').replace('-', '_').replace('\\', '/')

		def parse_content_file(content_file_path):
			'''Parse a .txt file containing content for the specific page'''
			parsed_content_file = {}
			with open(content_file_path) as infile:
				lines = infile.readlines()

			heading_index = None
			try:
				heading_index = lines.index('# Heading\n')
			except:
				heading_index = None
			try:
				title_index = lines.index('# Title\n')
			except:
				# If no title tag exists, use the heading tag for the title:
				title_index = heading_index
			try:
				description_index = lines.index('# Description\n')
			except:
				description_index = None

			try:
				if not title_index == None:
					if title_index == heading_index:
						title = ''.join(lines[heading_index+1:description_index])
					else:
						title = ''.join(lines[title_index+1:heading_index])
					title = title.replace('\n', '')

					heading = ''.join(lines[heading_index+1:description_index])
					heading = heading.replace('\n', '')

					if not description_index == None:
						description = ''.join(lines[description_index+1:])
						description = description.replace('\n', '<br />')

					if self.verbose:
						print 'title:', title
						print 'heading:', heading
						print 'description:', description

					parsed_content_file['title'] = title
					parsed_content_file['heading'] = heading
					parsed_content_file['description'] = description

				else:
					raise Exception('[ERROR] Need to provide a # Heading tag in {content_file}.'.format(content_file=content_file_path))
			except Exception as e:
				print e

			print '[PARSED] {content_file}...'.format(content_file=content_file_path)			
			return parsed_content_file

		def get_images_in_directory(directory):
			'''Returns all the image names found in the given directory.'''
			image_extensions = ['.jpg', '.JPG', '.jpeg', '.png', '.PNG', '.gif']
			files = os.listdir(directory)
			return [image for image in files if any(extension in image for extension in image_extensions)]

		def hash_image_name(image):
			'''Returns the hashed image name with extension for a given image name.'''
			image_name, image_extension = os.path.splitext(image)
			h = hashlib.new('md5')
			h.update(image_name)
			hashed_image_name = h.hexdigest()
			hashed_image_name += image_extension

			return hashed_image_name

		pages = {}
		
		try:
			if in_site_directory == None:
				raise IOError('[ERROR] No input directory defined.')
			else:				
				for root, subdirectories, files in os.walk(in_site_directory):
					page = {}
					page_content = {}
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
						# Get content from .txt file in directory:						
						content_file_list = [file for file in files if '.txt' in file]
						
						# If there is a content file:
						if not len(content_file_list) == 0:
							content_file = content_file_list[0]
							content_file_path = os.path.join(root, content_file)
							content = parse_content_file(content_file_path)
							page_content['title'] = content['title']
							page_content['jumbotron'] = content['heading']
							page_content['content'] = content['description']
						else:
							page_content['title'] = current_folder
							page_content['jumbotron'] = current_folder + '.'
							page_content['content'] = ''

						url = cleaned_root
						page_content['url'] = url
						page_content['images'] = []
						images = get_images_in_directory(root)

						# Copy images and hash image names:
						for image in images:
							src = os.path.join(root, image)

							# Hash the image name before copying:
							hashed_image_name = hash_image_name(image)							
							dest = os.path.join(self.image_directory, hashed_image_name)

							# Finally, copy to the new directory:
							if self.verbose:
								print 'image source:', src
								print 'image dest:', dest

							if not os.path.exists(dest):
								shutil.copy2(src, dest)

							relative_hashed_image_path = '/static/img/' + hashed_image_name

							page_content['images'].append(relative_hashed_image_path)

						links = []
						link_images = []
						if not len(subdirectories) == 0:
							for subdirectory in subdirectories:
								link = {}
								link_image = {}

								url_subdirectory = os.path.join(url, subdirectory)								
								cleaned_url_subdirectory = clean_url(url_subdirectory)
								full_subdirectory_path = os.path.join(root, subdirectory)

								if self.verbose:
									print 'url_subdirectory:', url_subdirectory
									print 'cleaned_url_subdirectory:', cleaned_url_subdirectory
									print 'full_subdirectory_path:', full_subdirectory_path
									print 'current working directory:', os.getcwd()
	
								link['display_name'] = subdirectory
								link['url'] = cleaned_url_subdirectory
								link_images = get_images_in_directory(full_subdirectory_path)
								hashed_link_images = []
								for link_image in link_images:
									src = os.path.join(os.getcwd(), full_subdirectory_path, link_image)
									
									with Image.open(src) as im:
										width, height = im.size
									
									# Set minimum width of an image:
									if width >= 350:
										# Hash the image name before copying:
										hashed_link_image_name = hash_image_name(link_image)
										relative_hashed_link_image_name = '/static/img/' + hashed_link_image_name
										hashed_link_images.append(relative_hashed_link_image_name)

										dest = os.path.join(self.image_directory, hashed_link_image_name)

										if not os.path.exists(dest):
											shutil.copy2(src, dest)

								link['images'] = hashed_link_images
								if len(images) > 0:
									print 'hashed_link_images:',hashed_link_images								
								links.append(link)
						page_content['links'] = links
						pages[url] = page_content
					else:
						# Currently not using this:
						tabs = []
						for subdirectory in subdirectories:
							tabs.append(subdirectory)
					
		except Exception as e:			
			print e		
		return pages


	def export_data(self, pages={}):
		'''
		Export the pages data to a JSON file.
		'''
		if pages == {}:
			pages = self.pages

		pages_file_name = os.path.join(self.data_directory, 'pages.json')
		with open(pages_file_name, 'w+') as outfile:
			json.dump(pages, outfile)


	def create_view_pages(self, app_directory=None, pages={}):
		'''
		Creates Flask functions that act as individual routes or pages.
		'''
		if pages == {}:
			pages = self.pages

		print '[CREATING] URL routes...'
		try:
			if app_directory == None:
				raise IOError('[ERROR] No application directory defined.')
			else:
				content = 'from flask import render_template\n'
				content += 'from app import app\n'
				content += '\n'
				content += 'import json\n'
				content += '\n'

				for page_key, page_value in pages.iteritems():					
					current_page = pages[page_key]
			
					url = current_page['url']
					# Remove any empty strings after splitting the URL:
					url_split = filter(None, url.split('/'))

					if len(url_split) > 1:
						function_name = url_split[-2] + '_' + url_split[-1]
						template_name = url_split[-2] + '_' + url_split[-1] + '.html'	
					else:						
						function_name = url_split[-1]
						template_name = url_split[-1] + '.html'	

					# Overwrite stuff for the index page:
					if page_key == '/home':
						function_name = 'index'
						template_name = 'index.html'
						content += '@app.route(\'/\')\n'
						content += '@app.route(\'/index\')\n'
					
					content += '@app.route(\'{url}\')\n'.format(url=url)
					content += 'def {function_name}():\n'.format(function_name=function_name)
					content += '\twith open(\'app/data/pages.json\', \'r\') as infile:\n'
					content += '\t\tdata = json.load(infile)\n'
					content += '\tpage = data[\'{url}\']\n'.format(url=url)
					content += '\treturn render_template(\'{template_name}\', page=page)\n'.format(template_name=template_name)
					content += '\n'

					print '[CREATED] URL route for {url}...'.format(url=page_key)

				views_file_name = os.path.join(app_directory, 'views.py')
				with open(views_file_name, 'w+') as outfile:
					outfile.write(content)
		except Exception as e:
			print e


	def create_template_pages(self, pages={}, overwrite=False):
		'''
		Create template pages from the list of pages.
		Can overwrite previously written pages or ignore them.
		'''
		if pages == {}:
			pages = self.pages

		print '[CREATING] template pages...'
		for page_key in pages.keys():
			page_split = filter(None, page_key.split('/'))			
			base_route_name = 'base'
			if len(page_split) > 1:
				base_route_name = page_split[0] + '.html'
				template_name = page_split[-2] + '_' + page_split[-1] + '.html'	
			else:
				template_name = page_split[-1] + '.html'

			# Special case for the index page:
			if page_key == '/home':
				template_name = 'index.html'

			template_full_path = os.path.join(self.output_template_directory, template_name)

			if os.path.exists(template_full_path):
				if overwrite:
					content = '{% extends \"' + base_route_name + '\" %}'
					with open(template_full_path, 'w') as outfile:
						outfile.write(content)
					print '[OVERWROTE] {template_name}...'.format(template_name=template_name)
			else:
				content = '{% extends \"' + base_route_name + '\" %}'
				with open(template_full_path, 'w') as outfile:
					outfile.write(content)
				print '[CREATED] {template_name}...'.format(template_name=template_name)

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

		input_static_directory = self.input_static_directory
		output_static_directory = self.output_static_directory
		
		if not os.path.exists(self.venv_directory):
			self.create_virtual_environment(out_directory=out_directory)

		self.create_flask_directory(out_directory=out_directory, sitename=sitename)

		self.move_pages(
						input_directory=input_template_directory,
						output_directory=output_template_directory
					)

		self.move_pages(
						input_directory=input_static_directory,
						output_directory=output_static_directory
					)
		
		self.pages = self.import_data(in_site_directory=self.in_site_directory)

		self.export_data()

		self.create_view_pages(app_directory=app_directory)

		self.create_template_pages()


if __name__ == '__main__':
	import_folder = os.path.join('data', 'import')
	export_folder = os.path.join('data', 'export')
	sitename = 'fabricon'
	site_creator = FlaskSiteCreator(
									sitename=sitename,
									import_folder=import_folder,
									export_folder=export_folder,
									verbose=False
								)	

	site_creator.run()


# TODO:
# 1. Write html to add content description (shortened) to product thumbnails.
# 2. Write tests for functions.