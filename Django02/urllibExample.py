from urllib.request import urlopen
#import urllib.request

#myURL = urllib.request.urlopen("https://www.runoob.com/")
#print(myURL.read(300))
#print(myURL.readline())

#lines = myURL.readlines()
#for line in lines:
#    print(line)

#print(myURL.getcode())   # 200

#try:
#    myURL2 = urllib.request.urlopen("https://www.runoob.com/no.html")
#except urllib.error.HTTPError as e:
#    if e.code == 404:
#        print(404)   # 404

myURL = urlopen("https://www.runoob.com/")
f = open("runoob_urllib_test.html", "wb")
content = myURL.read()  # 读取网页内容
f.write(content)
f.close()

import urllib.request

encode_url = urllib.request.quote("https://www.runoob.com/")  # 编码
print(encode_url)

unencode_url = urllib.request.unquote(encode_url)    # 解码
print(unencode_url)


from urllib.parse import urlparse
o = urlparse("https://www.runoob.com/?s=python+%E6%95%99%E7%A8%8B")
print(o)

import urllib.robotparser
rp = urllib.robotparser.RobotFileParser()
rp.set_url("http://www.musi-cal.com/robots.txt")
rp.read()
print(rp.can_fetch("*", "http://www.musi-cal.com/cgi-bin/search?city=San+Francisco"))
print(rp.can_fetch("*", "http://www.musi-cal.com/"))
print(rp.mtime(),rp.modified(),rp.crawl_delay("*"))
rrate = rp.request_rate("*")
if ( rrate):
   print(rrate.requests,rrate.seconds)
print(rp.site_maps())