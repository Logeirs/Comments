import requests
import re
import sys, os
from bs4 import BeautifulSoup, Comment






def getJScomments(jscode, isFile):
	# get all comments inside jscode, returns a list

	js_comments=[]
	reg_comm_1l="[^:|\'|\"]\/\/.*"		# one-line comment regex (used in getJScomments())
	reg_comm_ml="\/\*.*?\*\/"			# multi-line comment regex


	#if jscode is a JS file/URL (*.js) the jscode is str
	#if jscode comes from an HTML source (embedded JS), then this is bs4 type

	# one-line comment: //example
	# if 
	if isFile: comments_1l = re.findall(reg_comm_1l,jscode)
	elif not isFile: comments_1l = re.findall(reg_comm_1l,jscode.text)

	for comment_1l in comments_1l:
		js_comments.append(comment_1l)

	# multi-line comments: /* example */
	if isFile: comments_ml = re.findall(reg_comm_ml,jscode, re.DOTALL)
	elif not isFile: comments_ml = re.findall(reg_comm_ml,jscode.text, re.DOTALL)

	for comment_ml in comments_ml:
		js_comments.append(comment_ml)

	return js_comments




def getContent(target, target_type, dictcookies):
	'''
	get the target content, according to its type (file, url)
	
	supported types:
		- "url"
		- "file"
	'''

	content=[None,None]		# [content, isJSFile]

	print "\n[+] TARGET = %s  (%s)\n" %(target, target_type)

	if target_type == "file" or target_type == "folder":
		with open(target,'rb') as input_file:
			#if target is a JS file (*.js) then just get the content
			if os.path.splitext(target)[1] == ".js":
				content[0] = input_file.read()
				content[1]=True		#JS file
			
			#if not, assume this is HTML type, then parse it with BS
			else:
				content[0] = BeautifulSoup(input_file, "html.parser")
				content[1]=False	#JS code in a web page

	
	#if target url is provided
	#BE CAREFUL: if the URL has GET parameters, then you MUST put it between quotes
	elif target_type == "url":
		try:
			resp = requests.get(target, cookies=dictcookies)
		except: 
			print "Error when requesting the target."
			sys.exit()
		
		#check if this is a JS or HTML code by getting the content-type
		#if JS then simply get the content (BS is broken at some point when parsing JS content)
		content_type=resp.headers.get("content-type")
		if re.search("javascript", content_type):
			content[1]=True		#JS file
			content[0] = resp.text.encode("utf-8")
		
		#if it's not a JS, we can parse it with BS
		else:
			content[0] = BeautifulSoup(resp.text, "html.parser")
			content[1]=False	#JS code in a web page

	else:
		print "Error, unknown type."
		sys.exit()

	return content