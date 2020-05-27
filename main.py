#!/usr/bin/env python3

import argparse
import os  
import datetime
# from crawler import Crawler
import urllib.request
from urllib.parse import urlsplit, urlunsplit, urljoin, urlparse
import re

class Crawler:

	def __init__(self, url, exclude=None, no_verbose=False):
	
		self.url = self.normalize(url)
		self.host = urlparse(self.url).netloc
		self.exclude = exclude
		self.no_verbose = no_verbose
		self.found_links = []
		self.visited_links = [self.url]

	def start(self):
		self.crawl(self.url)

		return self.found_links


	def crawl(self, url):
		if not self.no_verbose:
			print("Parsing " + url)

		response = urllib.request.urlopen(url)
		page = str(response.read())
		pattern = '<a [^>]*href=[\'|"](.*?)[\'"].*?>'

		found_links = re.findall(pattern, page)
		links = []

		for link in found_links:
			is_url = self.is_url(link)

			if is_url:
				is_internal = self.is_internal(link)

				if is_internal:
					self.add_url(link, links, self.exclude)
					self.add_url(link, self.found_links, self.exclude)

		for link in links:
			if link not in self.visited_links:
				link = self.normalize(link)

				self.visited_links.append(link)
				self.crawl(urljoin(self.url, link))

	def add_url(self, link, link_list, exclude_pattern=None):
		link = self.normalize(link)

		if link:		
			not_in_list = link not in link_list

			excluded = False

			if exclude_pattern:
				excluded = re.search(exclude_pattern, link)

			if not_in_list and not excluded:
				link_list.append(link)
			

	def normalize(self, url):
		scheme, netloc, path, qs, anchor = urlsplit(url)
		return urlunsplit((scheme, netloc, path, qs, anchor))

	def is_internal(self, url):
		host = urlparse(url).netloc
		return host == self.host or host == ''	

	def is_url(self, url):
		scheme, netloc, path, qs, anchor = urlsplit(url)
		
		if url != '' and scheme in ['http', 'https', '']:
			return True 
		else:
			return False

#link for the site to be generated
url = "https://fast.com"

# initializeing crawler
crawler = Crawler(url);
# fetch links
links = crawler.start()

# adding last modified link <lastmod>2020-02-29T11:49:22+00:00</lastmod>
lastMod = "\t\t\t<lastmod>"+str(datetime.date.today())+"T11:49:22+00:00</lastmod>"

#createBackup
todaysDate = datetime.datetime.now().day
os.rename('sitemap.xml','backup'+str(todaysDate)+'sitemap.xml') 

#write into file 
outputFile = "./sitemap.xml"
with open(outputFile, "w") as file: 
	file.write('<?xml version="1.0" encoding="UTF-8"?>\n\t<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

	for link in links:
		print(link)
		eqCount = link.count('=')
		qmCount = link.count('?')
		if eqCount and qmCount :
			continue
		counter = link.count('/')
		p = ""
		if link == '/' and counter == 1:
			p = "\t\t\t<priority>1.00</priority>\n"
		elif counter <= 2:
			p = "\t\t\t<priority>0.80</priority>\n"
		elif counter <=4:
			p = "\t\t\t<priority>0.60</priority>\n"
		else:
			p = "\t\t\t<priority>0.50</priority>\n"			
		file.write("\n\t\t<url>\n\t\t\t<loc>{0}{1}</loc>\n{3}\n{2}\t\t</url>".format(url, link, p, lastMod))

	file.write('\n\t</urlset>')


