# -*- coding: UTF-8 -*-

import requests, urllib
import argparse
import re
import sys, os
from bs4 import BeautifulSoup, Comment
from urlparse import urljoin




def getJScomments(jscode):
	# get all comments inside jscode, returns a list

	js_comments=[]
	reg_comm_1l="[^:|\'|\"]\/\/.*"		# one-line comment
	reg_comm_ml="\/\*.*?\*\/"			# multi-line comment


	#if jscode is JS file/URL (*.js) the jscode is str
	#if jscode comes from an HTML source, then this is bs4 type

	# one-line comment: //example
	if isJS: comments_1l = re.findall(reg_comm_1l,jscode)
	elif not isJS: comments_1l = re.findall(reg_comm_1l,jscode.text)

	for comment_1l in comments_1l:
		js_comments.append(comment_1l)

	# multi-line comments: /* example */
	if isJS: comments_ml = re.findall(reg_comm_ml,jscode, re.DOTALL)
	elif not isJS: comments_ml = re.findall(reg_comm_ml,jscode.text, re.DOTALL)

	for comment_ml in comments_ml:
		js_comments.append(comment_ml)

	return js_comments



def getContent(target, target_type):
	'''
	get the target content, according to its type (file, url)
	
	supported types:
		- "url"
		- "file"
	'''

	global isJS

	print "\n[+] TARGET = %s  (%s)\n" %(target, target_type)

	if target_type == "file" or target_type == "folder":
		with open(target,'rb') as input_file:
			#if target is a JS file (*.js) then just get the content
			if os.path.splitext(target)[1] == ".js":
				content = input_file.read()
				isJS=True
			
			#if not, assume this is HTML type, then parse it with BS
			else:
				content = BeautifulSoup(input_file, "html.parser")
				isJS=False

	
	#if target url is provided
	#BE CAREFUL: if the URL has GET parameters, then you MUST put it between quotes
	elif target_type == "url":
		try:
			if args.c: resp = requests.get(target, cookies=dictcookies)
			else: resp = requests.get(target)
		except: 
			print "Error when requesting the target."
			sys.exit()
		
		#check if this is a JS or HTML code by getting the content-type
		#if JS then just get the content because BS is broken at some point when parsing JS content
		content_type=resp.headers.get("content-type")
		if re.search("javascript", content_type):
			isJS=True
			content = resp.text.encode("utf-8")
		
		#if it's not a JS, we can parse it with BS
		else:
			content = BeautifulSoup(resp.text, "html.parser")
			isJS=False

	else:
		print "Error, unknown type."
		sys.exit()

	# print "*** DEBUG ***\n %s \n*** DEBUG ***" %(content)
	return content




def displayChoice(choice_title, choice_list):
	print "\n\n\n[+] %s (%i found)\n" %(choice_title, len(choice_list))
	global choice_nb
	choice_nb=0
	for choice_element in choice_list :
		print "\t[%02d] %s" %(choice_nb, choice_element)
		choice_nb+=1



def clear():
	os.system("cls")





''' 
PROGRAM STARTS HERE 
'''

target=""

# Args
parser = argparse.ArgumentParser(
	usage="comments.py ([-u <target url>] | [-f <intput file>] | [-d <input directory>]) [-c cookie=value]", 
	description="Get HTML and JavaScript comments from a file or a website.", 
	epilog="Example: comments.py -u http://<website> -o output.txt"
	)

parser.add_argument("-o", help="output file", type=str)
parser.add_argument("-c", help="cookie='value'", type=str, nargs='+')

# can't use -f and -u together
# group = parser.add_mutually_exclusive_group()
parser.add_argument("-f", help="input source file", type=str)
parser.add_argument("-u", help="target url", type=str)
parser.add_argument("-d", help="input directory", type=str)

args = parser.parse_args()



if args.c:
	# Requests module requires a dictionary
	dictcookies={}

	for nbCookies in range(0,len(args.c)):
		cookie=args.c[nbCookies]
		
		cname=re.search("(.*)=.*",cookie)
		cname=cname.group(1)
		cvalue=re.search(".*=(.*)",cookie)
		cvalue=cvalue.group(1)
		dictcookies[cname]=cvalue



# if target is a source file (.js, .html, .php, etc.)
if args.f:
	if os.path.isfile(args.f)==False:
		print "File does not exist!"
		sys.exit()
	target_type="file"
	target=args.f
	target_origin=args.f

# if target is a url
# BE CAREFUL: if the URL has GET parameters, then you MUST put it between quotes	
elif args.u:
	target_type="url"
	target=urllib.unquote_plus(args.u)	#unquote_plus: Replace %xx by their single-character equivalent
	target_origin=urllib.unquote_plus(args.u) #args.u



# if target is a directory
elif args.d:
	#take the first file
	#need to select only the web files! (html, php, etc.)

	for root, dirs, files in os.walk(args.d):
		if files:
			for f in files:
				target_type="folder"
				target=os.path.join(root, f)
				target_origin=target
				break
			break
	if not target:
		print "No target found."
		sys.exit()


	
else:
	print "Need a target!"
	sys.exit()


while True:	
	js_ext_all=[]			# JS from a file or url (not included within the web page with <script> tag)
	js_comments_all=[]
	isJS=''
	files_all=[]
	clear()

	# Get target's content
	try: 
		content = getContent(target,target_type)
	except: 
		print "Error while getting the content."
		sys.exit()


	#if the target file is not a JS file:
	#get external JS, HTML comments and all JS codes
	if not isJS: 

		# get all HTML comments
		html_comments = content.findAll(text=lambda text:isinstance(text, Comment))
		print "\n[+] HTML COMMENTS (%i found)\n" %(len(html_comments))
		for html_com in html_comments:
			try:
				print "\t[-]%s\n" %(html_com)
			except:
				print "\t[-] !Error! (very special characters?)\n"

		# to get all JS comments:
		# get all je JS code, then for each one of them get all comments and add the returned list (from getJScomments) to the final list (js_comments_all)
		js_all = content.find_all('script')
		for js in js_all:
			# check if there is an 'src' attribute in order to know if there is a call to an external JS file:
			if js.has_attr("src"):js_ext_all.append(js.get('src'))
			js_comments_all += getJScomments(js)


	#if the target is a JS file, then just get the comments fom the JS code
	elif isJS:
		js_comments_all += getJScomments(content)

	else:
		print "Erorr: don't know how to handle this target."
		sys.exit()





	# remove occurences and keep it as a list
	js_comments_all = list(set(js_comments_all))
	print "\n\n\n[+] JS COMMENTS (%i found)\n" %(len(js_comments_all))

	for js_com in js_comments_all:
		try:
			print "\t[-] %s\n" %(js_com)
		except:
			print "\t[-] !Error! (very special characters?)\n"







	if args.d:
		for root, dirs, files in os.walk(args.d):
			for f in files:
				files_all.append(os.path.abspath(os.path.join(root, f)))

		choice_list=files_all
		choice_title="FILES"

	else:
		js_ext_all.append(target_origin)	# add the original target
		js_ext_all=list(set(js_ext_all))	# remove ext JS occurences and keeps it as a list (because a 'set' type is not indexable), set = remove occurences
		js_ext_all.sort()					# sort the list
		js_ext_all.insert(0,js_ext_all.pop(js_ext_all.index(target_origin)))		#bring the original target to the first position
		
		choice_list=js_ext_all
		choice_title="EXTERNAL JS"


	displayChoice(choice_title, choice_list)	#display


		# if no ext JS
		# if len(js_ext_all) == 0: sys.exit()

	choice=''
	while True:
		choice = raw_input("\nYour choice? ('q' to exit): ")
		if choice.isdigit():
			choice=int(choice)
			if choice < choice_nb:

				# concatenate url if the ext JS is in the same domain
				# targe_type stays 'url'
				if target_type == "url": target=urljoin(target_origin,choice_list[choice])

				elif target_type == "file" or target_type == "folder": 
					#if choice=0, it means the new target is the origin target (=args.f)
					if choice==0: 
						target=target_origin
						break

					# last element in os.path.join() should not start with '/' because they will be considered as "absolute path" and everything before them is discarded
					choice_value=list(choice_list[choice])
					if choice_value[0]=='/':
						choice_value[0]=''
					
					choice_value=str(''.join(choice_value))
					# if file as input, need to join the 2 paths: path of origin target + value
					if target_type == "file": target=os.path.join(os.path.dirname(os.path.realpath(target_origin)),choice_value)
					else: target=choice_value

				#choice is ok, we can exit the while loop (choice.isdigit)
				#reinit values
				js_comments_all = []
				break

			else:
				print "Index out of range."
				choice = ''	# need to convert it back to a string because isdigit() in the while loop requires a string

		elif choice == 'q': sys.exit()

		else: 
			print "Error: Type a number or 'q' to exit."


'''
# write to output file
if args.o:
	# with open (args.o, 'wb') as f:
	print args.o
'''






