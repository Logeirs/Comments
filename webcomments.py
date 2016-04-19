# -*- coding: UTF-8 -*-

'''
TODO:
-----
	* Spidering URLs (in progress)

	* POST requests and arguments
		
	* When source code is provided:
		-f what about external JS loaded?

	* When source file is provided:
		How to make the difference between a call to a local files (/include/js/blah.js) and a call to a url (http://blah.com/yeah.js) ?

	* CSS comments ?


TO IMPROVE:
-----------
	* clear screen (os.system("cls")) obviously doesn't work on Linux
	* regex (all)
	* at this point, can't use -f AND -u together
	* -d displays absolute path
	* -f displays external JS (from other domains), while -d displays local files (JS, html, php, etc.), no external files


ISSUES:
-------
	- REGEX doesn't work when JS is minimized
	- if script tag is not closed, then jscode is empty
	- when -u <url> if the URL has GET parameters, then you MUST use quotes. example: 
		comments.py -u "http://website.com?param1=1&param2=2"
		If you don't, you may have an error such as: 'blah' is not recognized as an internal or external command, ...
			Seems to work now...
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

comments.py -u http://<url.com> -c Cookie1=value1 Cookie2=value2

comments.py -d ./test/
comments.py -d C:/Users/blah/Documents/

More to come.
'''

#http://docs.python-requests.org/en/latest/user/quickstart/
import urllib
import argparse
import re
import sys, os
from bs4 import BeautifulSoup, Comment
from urlparse import urljoin

import contentmod



def getURLs(content):
	cont = content[0]
	urls= cont.findAll('a',href=True)
	urls=list(set(urls))
	for url in urls:
		print '\t'+url['href']



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
web_ext=[".asp", ".aspx", ".asx", ".html", ".htm", ".js", ".php"]		# valid extensions used to keep only the files (when -d) we want to parse
urls=[]
u=[]
dictcookies={}

# Args
parser = argparse.ArgumentParser(
	usage="comments.py ([-u <target url>] | [-f <intput file>] | [-d <input directory>]) [-c cookie=value]", 
	description="Get HTML and JavaScript comments from a file or a website.", 
	epilog="Example: comments.py -u http://<website> -c cookie=value -o output.txt"
	)

parser.add_argument("-o", help="output file", type=str)
parser.add_argument("-c", help="cookie='value'", type=str, nargs='+')

# can't use -f and -u together
# group = parser.add_mutually_exclusive_group()
parser.add_argument("-f", help="input source file", type=str)
parser.add_argument("-u", help="target url", type=str)
parser.add_argument("-d", help="input directory", type=str)
parser.add_argument("-lu", help="grab href tags", action="store_true")

args = parser.parse_args()

if args.c:
	# Requests module requires a dictionary

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
	#need to select only the web files! (html, php, etc.)

	for root, dirs, files in os.walk(args.d):
		if files:
			for f in files:
				target_type="folder"

				# get file extension
				f_name, f_ext = os.path.splitext(f)
				# if this is a web file
				if f_ext in web_ext: 
					target=os.path.join(root, f)
					target_origin=target

				if target!='': break	#take the first file
			if target!='': break
	if not target:
		print "No target found."
		sys.exit()


	
else:
	print "Need a target!"
	sys.exit()


while True:	
	# vars below need to be reset (that's why they're here)
	js_ext_all=[]			# JS from a file or url (not included within the web page with <script> tag)
	js_comments_all=[]		# list of all the JavaScript comments
	content=[None,None]		# [content, isJSFile]
	files_all=[]			# list of all files contained in the directory (related to -d arg)
	# clear()

	# Get target's content
	try: 
		content = contentmod.getContent(target,target_type,dictcookies)
	except: 
		print "Error while getting the content."
		sys.exit()


	#get external JS, HTML comments and all JS codes
	
	#if the target file is not a JS file:
	if not content[1]: 

		# get all HTML comments
		html_comments = content[0].findAll(text=lambda text:isinstance(text, Comment))
		print "\n[+] HTML COMMENTS (%i found)\n" %(len(html_comments))
		for html_com in html_comments:
			try:
				print "\t[-]%s\n" %(html_com)
			except:	
				print "\t[-] !Error! (very special characters?)\n"

		# to get all JS comments:
		# get all the JS code, then for each one of them get all comments and add the returned list (from getJScomments) to the final list (js_comments_all)
		js_all = content[0].find_all('script')
		for js in js_all:
			# check if there is an 'src' attribute in order to know if there is a call to an external JS file:
			if js.has_attr("src"):js_ext_all.append(js.get('src'))
			js_comments_all += contentmod.getJScomments(js, False)


	#if the target is a JS file, then just get the comments fom the JS code
	elif content[1]:
		js_comments_all += contentmod.getJScomments(content[0], True)

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




	# URLs (href)
	if args.lu:
		print "\n\n\n[+] URLs (i found)\n" #%(len(js_comments_all))
		getURLs(content)




	if args.d:
		for root, dirs, files in os.walk(args.d):
			for f in files:
				# get file extension
				f_name, f_ext = os.path.splitext(f)
				# if this is a web file, add it to the list
				if f_ext in web_ext: files_all.append(os.path.abspath(os.path.join(root, f)))

		choice_list=files_all
		choice_title="FILES"

	else:
		js_ext_all.append(target_origin)	# add the original target
		js_ext_all=list(set(js_ext_all))	# remove ext JS occurences and keeps it as a list (because a 'set' type is not indexable), set = remove occurences
		js_ext_all.sort()					# sort the list
		js_ext_all.insert(0,js_ext_all.pop(js_ext_all.index(target_origin)))		#bring the original target to the first position
		
		choice_list=js_ext_all
		choice_title="EXTERNAL JS"

		# if no ext JS
		if len(js_ext_all) == 0: sys.exit()

	displayChoice(choice_title, choice_list)	#display


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






