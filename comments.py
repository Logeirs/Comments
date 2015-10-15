# -*- coding: UTF-8 -*-

'''
TODO:
-----
	* Spidering
	* manage session/cookies (detect when redirect towards login page)
		-> see requests (requests.get)
	
	* When source code is provided:
		-d input dir
		-f what about external JS loaded?

	* When source file is provided:
		How to make the difference between a call to a local files (/include/js/blah.js) and a call to a url (http://blah.com/yeah.js) ?

	* CSS comments ?


TO IMPROVE:
-----------
	* clear screen (os.system("cls")) obviously doesn't work on Linux
	* regex (all)
	* at this point, can't use -f AND -u together


ISSUES:
-------
	- REGEX doesn't work when JS is minimized
	- if script tag is not closed, then jscode is empty
	- when -u <url> if the URL has GET parameters, then you MUST use quotes. example: 
		comments.py -u "http://website.com?param1=1&param2=2"
		If you don't, you may have an error such as: 'blah' is not recognized as an internal or external command, ...
	- when -f <file>, the "target_type" is then defined with the value "file". There will be an issue if you try to request an external JS with its URL, for instance:
		1. run this script with a local file (php, html) as a target
		2. try to access an external JS such as: http://blah.com/myjs.js
		3. return to the original target

		In short: if file: stay with file, if url: stay with url


EXAMPLES:
---------
comments.py -f <file.php>
comments.py -f <file.html>
comments.py -f <file.js>

comments.py -u http://<url.com>
comments.py -u "http://url.com?param1=1&param2=2"
comments.py -u https://<url.com>
comments.py -u http://<url.js>

More to come.
'''

#http://docs.python-requests.org/en/latest/user/quickstart/
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

	if target_type == "file":
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
		try: resp = requests.get(target)
		except: 
			print "Error when requesting the target"
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
		print "Error, type unknown"
		sys.exit()

	# print "*** DEBUG ***\n %s \n*** DEBUG ***" %(content)
	return content




def getExtJS(js_ext_all):
	print "\n\n\n[+] EXTERNAL JS (%i found)\n" %(len(js_ext_all))
	global nbJS
	nbJS=0
	for js_ext in js_ext_all :
		print "\t[%02d] %s" %(nbJS, js_ext)
		nbJS+=1



def clear():
	os.system("cls")


''' 
PROGRAM STARTS HERE 
'''

# Args
parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser(
	usage="comments.py [-o <output file>]", 
	description="Get HTML and JavaScript comments from a file or a website.", 
	epilog="Example: comments.py -u http://<website> -o output.txt"
	)

# parser.add_argument("-o", help="output file", type=str)
parser.add_argument("-f", help="input source file", type=str)
parser.add_argument("-u", help="target url", type=str)
args = parser.parse_args()


# if target is a source file (.js, .html, .php, etc.)
if args.f: 
	target_type="file"
	target=args.f
	target_origin=args.f

# if target is a url
# BE CAREFUL: if the URL has GET parameters, then you MUST put it between quotes	
elif args.u:
	target_type="url"
	target=urllib.unquote_plus(args.u)	#unquote_plus: Replace %xx by their single-character equivalent
	target_origin=args.u

else:
	print "Need a target!"
	sys.exit()


while True:	
	js_ext_all=[]
	js_comments_all=[]
	isJS=''
	clear()

	# Get target's content
	content = getContent(target,target_type)

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
		print "Erorr: don't know how to handle this target"
		sys.exit()





	# remove occurences and keeps it as a list
	js_comments_all = list(set(js_comments_all))
	print "\n\n\n[+] JS COMMENTS (%i found)\n" %(len(js_comments_all))

	for js_com in js_comments_all:
		try:
			print "\t[-] %s\n" %(js_com)
		except:
			print "\t[-] !Error! (very special characters?)\n"

	
	js_ext_all.append(target_origin)	# add the original target
	js_ext_all=list(set(js_ext_all))	# remove ext JS occurences and keeps it as a list (because a 'set' type is not indexable)
	js_ext_all.sort()					# sort the list
	js_ext_all.insert(0,js_ext_all.pop(js_ext_all.index(target_origin)))		#bring the original target to the first position

	getExtJS(js_ext_all)	#display, set = remove occurences


	# if no ext JS
	# if len(js_ext_all) == 0: sys.exit()

	choice=''
	while (choice.isdigit != False) or (choice != 'q'):
		choice = raw_input("\nChoose an external JS ('q' to exit): ")
		if choice.isdigit():
			choice=int(choice)
			if choice < nbJS:
				# clear()

				#reinit values
				js_comments_all = []

				# concatenate url if the ext JS is in the same domain
				# targe_type stays 'url'
				if target_type == "url": target=urljoin(target_origin,js_ext_all[choice])

				elif target_type == "file": 
					#if choice=0, it means the target is the origin target (=args.f)
					if choice==0: 
						target=target_origin
						break

					# latter element in os.path.join() should not start with '/'
					js_ext_choice=list(js_ext_all[choice])
					if js_ext_choice[0]=='/':
						js_ext_choice[0]=''
						js_ext_choice=str(''.join(js_ext_choice))

					# join the 2 paths: path of origin target + js
					target=os.path.join(os.path.dirname(os.path.realpath(target_origin)),js_ext_choice)

				#choice is ok, we can exit the infinite loop
				break

			else:
				print "Index out of range"
				choice = ''	# need to convert it back to a string because isdigit() in the while loop requires a string

		elif choice == 'q': sys.exit()

		else: 
			print "Error: Type a number or 'q' to exit"


'''
# write to output file
if args.o:
	# with open (args.o, 'wb') as f:
	print args.o
'''






