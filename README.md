WEBCOMMENTS
===========

This script gets HTML and JavaScript comments in a web source code. Input can be either a URL, a file (.js or a .html, .php, etc.) or a folder.
See "examples" section for more details.



SUMMARY:
-------
[Description][1]
[Requirements][2]
[Help][3]
[TODO][4]
[To Improve][5]
[Issues][6]
[Examples][7]



REQUIREMENTS:
------------
- [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/)
- [request](http://docs.python-requests.org/en/master/)



HELP:
----
####usage:
webcomments.py -c cookie1=value1 cookie2=value2 [-f <input file>] [-u <url>] [-d <folder>]

###arguments:
  -h, --help 	show this help message and exit
  -f 			input source file
  -d 			input directory
  -u 			target url

  -c 			cookies
  -lu 			list URLs
  -o 			output file (todo)



TODO:
----
* When source code is provided:
	-f what about external JS loaded?

* When source file is provided:
	How to make the difference between a call to a local files (/include/js/blah.js) and a call to a url (http://blah.com/yeah.js) ?

* CSS comments ?


TO IMPROVE:
----------
* clear screen (os.system("cls")) obviously doesn't work on Linux
* regex (all)
* at this point, can't use -f AND -u together
* -d displays absolute path
* -f displays external JS (from other domains), while -d displays local files (JS, html, php, etc.), no external files


ISSUES:
------
- if script tag is not closed, then jscode is empty
- when -u <url> if the URL has GET parameters, then you **must** use quotes. example: 
	comments.py -u "http://website.com?param1=1&param2=2"
	If you don't, you may have an error such as: 'blah' is not recognized as an internal or external command, ...
		Seems to work now...
- when -f <file>, the "target_type" is then defined with the value "file". There will be an issue if you try to request an external JS with its URL, for instance:
	1. run this script with a local file (php, html) as a target
	2. try to access an external JS such as: http://blah.com/myjs.js
	3. return to the original target

	In short: if file: stay with file, if url: stay with url


EXAMPLES:
--------
~~~
webcomments.py -f <file.php>
webcomments.py -f <file.html>
webcomments.py -f <file.js>

webcomments.py -u http://<url.com>
webcomments.py -u "http://url.com?param1=1&param2=2"
webcomments.py -u https://<url.com>
webcomments.py -u http://<url.js>
webcomments.py -u http://<url.com> -c cookie1=value1 cookie2=value2

webcomments.py -d ./test/
webcomments.py -d C:/Users/blah/Documents/
~~~

More to come.


[1]:https://github.com/Logeirs/WebComments#description
[2]:https://github.com/Logeirs/WebComments#requirements
[3]:https://github.com/Logeirs/WebComments#todo
[4]:https://github.com/Logeirs/WebComments#to-improve
[5]:https://github.com/Logeirs/WebComments#issues
[6]:https://github.com/Logeirs/WebComments#examples