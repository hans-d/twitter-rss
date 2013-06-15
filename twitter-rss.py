#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### TODO ###
  #check connection
#generate and append to rss
#multiple feeds
#atom?

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import arrow

class TwitterToRss:

	def __init__(self):
		self.tweets = []
		self.title = ''

	def initBeautifulSoup(self):
		url = "https://twitter.com/framasoft"

		content = urllib2.urlopen(url)
		if urllib2.urlopen(url).getcode() == 200:

			print 'Connection successful!'
			soup = BeautifulSoup(content)
			
			self.title = soup.title.string
			self.tweets = []

			for content in soup.findAll("div", "content"):

				for info, tweet in zip(content.findAll("small", "time"), content.findAll("p", "js-tweet-text tweet-text")):

					self.tweets.append([info, tweet])

		else:
			print 'Error, site returned:', urllib2.urlopen(url).getcode()

	def printTweets(self):
		for tweet in self.tweets:
			print tweet

	def cleanTwit(self):

		to_delete = [
		# clean text
		' class="js-tweet-text tweet-text"', 
		' class="twitter-atreply pretty-link"',
		' class="invisible"',
		' class="js-display-url"',
		' class="twitter-hashtag pretty-link js-nav"',
		' class="twitter-timeline-link"',
		' class="tco-ellipsis"',
		' class="invisible"',
		' data-query-source="hashtag_click"',
		' rel="nofollow"',
		' target="_blank"',
		' data-expanded-url=".*?"', 
		' title=".*?"',
		' data-query-source="hashtag_click"',
		' dir="ltr"',
		'<span><span>&nbsp;</span>.*</span>',
		'<span>http://</span>',
		'<span></span>',
		' data-pre-embedded="true"']


		to_replace = [{'<s>@</s>' : '@'},
		{'href="/' : 'href="http://twitter.com/'}]

		for i, tweet in enumerate(self.tweets):
			for item in to_delete:
				self.tweets[i][1] = re.sub(item, '', str(self.tweets[i][1]))
			for item in to_replace:
				for old, new in item.items():
					self.tweets[i][1] = re.sub(old, new, str(self.tweets[i][1]))

		return self.tweets

	def cleanInfo(self):
		
		for i, tweet in enumerate(self.tweets):

			soup = BeautifulSoup(str(self.tweets[i][0]))
			for href in soup.findAll('a'):
				
				link = re.sub(r'\(u\'href\', u\'(.*)\'\)', r'\1', str(href.attrs[0]))

				tmp = soup.find('span')
				date = re.sub(r'\(u\'data-time\', u\'(.*)\'\)', r'\1', str(tmp.attrs[1]))

				plop = str(self.tweets[i][1])
				
				self.tweets[i][0] = [link, date, plop]

	def cleanTweet(self):

		to_delete = ['<p>', '</p>', r'<a href=".*?">', '<s>', '</s>', r'http://twitter.com/search\?q=.*?&amp;src=hash',
		'<span>', '</span>', '</a>', '<b>', '</b>']

		for i, clean_twit in enumerate(self.tweets):
			for item in to_delete:

				self.tweets[i][0][2] = re.sub(item, '', str(self.tweets[i][0][2]))

	def cleanTimestamp(self):

		for i, tweet in enumerate(self.tweets):
			timestamp = arrow.Arrow.fromtimestamp(float(self.tweets[i][0][1]))
			date = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')
			self.tweets[i][0][1] = date

	def generateHtml(self):
		with open('myfile.html', 'w') as html:
			html.write('<meta http-equiv="Content-type" content="text/html; charset=UTF-8"/>\n\n')
			for tweet in self.tweets:

				html.write(str(tweet[1])+'\n\n')

		html.close()

	def backupTweet(self):

		with open('tweet.xml', 'r') as original:

			first_tweet = []
			first_tweet.append(original.readline())

			first_tweet = first_tweet[0].split('\'')[1]

			update = True

			for i, tweet in enumerate(self.tweets):
				if first_tweet in self.tweets[i][0][0]:
					update = False
					data = original.read()
			original.close()

			if update:
				with open('tweet.xml', 'w') as modified:

					print 'Update in progress'

					for tweet in self.tweets:
						modified.write(str(tweet)+'\n\n')
					modified.write(str(data))
				modified.close()
			else:
				print 'Already updated, nothing to do'

	def generateRss(self):

		filename = re.sub(r'.*\((.*?)\).*', r'\1', self.title)
		with open(filename+'.xml', 'w') as html:

			html.write('''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
	<channel>
		<title>'''+self.title+'''</title>
		<link>https://twitter.com/framasoft rel="self"</link>
		<description>twitter-rss of framasoft</description>
		<language>fr</language>

		''')

			for i, item in enumerate(self.tweets):

				date = str(self.tweets[i][0][1])
				link = str(self.tweets[i][0][0])
				twit = str(self.tweets[i][1])
				title = str(self.tweets[i][0][2])

				html.write(
				'''
				<item>
				<title>'''+title+'''</title>
				<guid>https://twitter.com'''+link+'''</guid>
				<link>https://twitter.com'''+link+'''</link>
				<pubDate>'''+date+'''</pubDate>
				<description><![CDATA['''
				+twit+
				''']]></description>
				</item>
				''')
				

			html.write('''
	</channel>
</rss>''')
		html.close()

		with open(filename+'.html', 'w') as html:
			print 'twitter.com',link
			html.write('''<!DOCTYPE html>

<html lang="fr">
<head>

	<meta charset="utf-8">
	<title>Framasoft-Twitter</title>

</head>
<body>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />''')

			for i, item in enumerate(self.tweets):

				date = str(self.tweets[i][0][1])
				link = str(self.tweets[i][0][0])
				twit = str(self.tweets[i][1])
				title = str(self.tweets[i][0][2])

				html.write(
				'''
<blockquote class="twitter-tweet"><p>'''+title+'''</p>&mdash; Alexis Kauffmann (@framaka) <a href="https://twitter.com'''+link+'''">'''+date+'''</a></blockquote>
''')

			html.write('''

<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>

</body>

</html>''')
			html.close()




tweet = TwitterToRss()
tweet.initBeautifulSoup()

tweet.generateHtml()


tweet.cleanTwit()
tweet.cleanInfo()
tweet.cleanTimestamp()
tweet.cleanTweet()
tweet.generateRss()

tweet.backupTweet()
