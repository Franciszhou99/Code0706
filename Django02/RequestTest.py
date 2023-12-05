import requests

# 发送请求
x = requests.get('https://www.runoob.com/')

#print(x.text,x.content)

# 返回 http 的状态码
print(x.status_code,x.reason)
print(x.headers)  # 获取响应头
print(x.apparent_encoding,x.encoding,x.cookies,x.elapsed,x.history,x.is_permanent_redirect,x.is_redirect,x.url)

cookies = x.cookies
for cookie in cookies:
    print(cookie.name, cookie.value)

request = x.request
# 访问请求对象的属性
print('请求方法:', request.method)
print('目标 URL:', request.url)
print('请求头:', request.headers)
print('请求体:', request.body)

if x.status_code == 200:
    try:
        data = x.json()
        print(data)
    except requests.exceptions.JSONDecodeError as e:
        print(f'JSON 解析错误: {e}')
else:
    print('请求失败')

# 发送请求
x = requests.get('https://www.runoob.com/try/ajax/json_demo.json')
# 返回 json 数据
print(x.json())


# 发送请求
x = requests.request('get', 'https://www.runoob.com/')
# 返回网页内容
print(x.status_code)

kw = {'s': 'python 教程'}

# 设置请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

# params 接收一个字典或者字符串的查询参数，字典类型自动转换为url编码，不需要urlencode()
response = requests.get("https://www.runoob.com/", params=kw, headers=headers)

# 查看响应状态码
print(response.status_code)
# 查看响应头部字符编码
print(response.encoding)
# 查看完整url地址
print(response.url)
# 查看响应内容，response.text 返回的是Unicode格式的数据
#print(response.text)

x = requests.post('https://www.runoob.com/try/ajax/demo_post.php')
print(x.text)

# 表单参数，参数名为 fname 和 lname
myobj = {'fname': 'RUNOOB','lname': 'Boy'}
# 发送请求
x = requests.post('https://www.runoob.com/try/ajax/demo_post2.php', data = myobj)
# 返回网页内容
print(x.text)

headers = {'User-Agent': 'Mozilla/5.0'}  # 设置请求头
params = {'key1': 'value1', 'key2': 'value2'}  # 设置查询参数
data = {'username': 'example', 'password': '123456'}  # 设置请求体
x = requests.post('https://www.runoob.com', headers=headers, params=params, data=data)
#print(x.text)

# 定义请求的 URL
url = 'https://example.com/login'
# 定义要提交的数据，通常是一个字典
data = {
    'username': 'your_username',
    'password': 'your_password'
}
# 发送 POST 请求，并传递数据
response = requests.post(url, data=data)
# 处理服务器的响应
if response.status_code == 200:
    print('登录成功')
else:
    print('登录失败')