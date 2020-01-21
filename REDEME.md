## 对项目的一些总结

#### 1.配置前后端分离的Django项目，使其允许跨域请求

```python
创建django项目Django-admin startproject xxx
进入pycharm 在setting.py中配置
1.INSTALLED_APPS 中添加 ’corsheaders‘
2.MIDDLEWARE中添加corsheaders.middleware.CorsMiddleware
3.在代码空白处设置CORS_ORIGIN_ALLOW_ALL=True，允许所有跨域
4.在代码空白出设置CORS_ALLOW_METHODS = (
				'DELETE',
				'GET',
				'OPTIONS',
				'PATCH',
				'POST',
				'PUT',
				)# 允许跨域方法
5.在打吗空白出设置CORS_ALLOW_HEADERS = (
				'accept-encoding',
				'authorization',
				'content-type',
				'dnt',
				'origin',
				'user-agent',
				'x-csrftoken',
				'x-requested-with',）# 跨域允许的headers类型
```

####  2.对数据库的配置

```python
进入MySQL创建数据库
Create database xxx default utf8;
再进入settings.py 设置数据库配置
将'ENGINE': 'django.db.backends.sqlite3',修改成
’django.db.backends.mysql’
添加如下参数：
'NAME': ‘创建的库名称’,
'USER':'登陆用户名',
'PASSWORD':'密码',
'HOST':'IP号',
'PORT':'端口号'
再__init__.py中添加
import pymysql
pymysql.install_as_MySQLdb()
```

##### # 注意：

```python
1.Django3.0开始在设置LANGUAGE_CODE前需要设置：

from django.utils.translation import gettext_lazy as _

LANGUAGES = [

  ('zh-Hans', _('Chinese')),

]

\2. 在django3.0开始由于mysql版本和django和python版本的问题需要在python安装目录下进入Lib\site-packages

\django\db\backends\mysql将base.py中

if version < (1, 3, 13): 

 Raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)注释掉
```

3.测试跨域是否成功

```python
在主url.py中添加测试路由path(r'^test/$',views.test_api) 且导入from . import views
再在项目目录中新建views.py文件做测试
在views.py中测试能否返回响应值为{‘code’：200}的json响应

from django.http import JsonResponse
def test_api(request):
return JsonResponse({'code':200})
尝试运行flask，python3 xxx.py得到127.0.0.1:5000 
在前端页面login.html&.Ajax{中修改url=127.0.0.1：8000/test
}	
使登陆127.0.1:5000/login后发起请求时查看network中响应是否有返回的json数据{‘code’：200}，如果有说明跨域成功，已经可以从访问5000端口的服务器跨域得到8000端口的json数据，前后端分离开始。
```

#### 4.创建app项目

```python
Python3 manage.py startapp xxx 创建一个app项目
在settiing.py 中INSTALLED_APPS 添加创建的app
在xxx模块中进入models.py 进行对模型的设置
 Eg:
class  xxx(models.Model):
id = models.CharField(max_length=11,verbose_name=”xx”,primary_key=True)
class Meta:
 db_table = 'xxx'  # 修改数据库中表的名字

在模型设置好后进行数据库的迁移
Python3 manage.py makemigrations
Python3 manage.py migrate
(在数据库中检查是否迁移成功)
在主url.py中设置分布式路由
在from django.urls import path,re_path后添加include
在urlpatterns = []中添加分布式路由re_path(r’v1/xxx’,include(‘xxx.urls’)
#  在xxx后没有留后杠 满足restful
进入应用app中创建urls.py
From django.conf.urls import url
From .import views
urlpatterns=[
    url(r'^$',views.xxx) # 127.0.0.1:8000/v1/xxx
]

进入项目app中的视图函数，创建于分布式路由对应的方法
```

#### 5.一些杂七杂八的想法和理解

```python
Def xxx(request):
对服务器来说，为客户端从服务器获取数据 request.method为get方法
客户端向服务器上传数据request.method为POST方法
客户端向服务器跟新数据request.method为PUT方法
在完成后跨域向其发送json对应的数据
   测试是否能收到get请求，进入浏览器输入127.0.0.1:8000/v1/xxx查看是否收到json数据：
 if request.method == 'GET':
        # 获取用户数据
         return JsonResponse({'code': 200})
    elif request.method == 'POST':
        # 创建用户
        pass
    elif request.method == 'PUT':
        # 跟新用户
        pass
    else:
        raise

    return JsonResponse({'code': 200})

在request.method==’post’
中获取客户端传入的数据，Request.POST()只能拿表单提交数据
```

####  6.一些杂七杂八的想法和理解2

```python
根据项目文档查看从前端跨域传入的数据格式
使用request.body接收json数据，接收到的数据为字节串，需要使用json.load转为Python数据类型，在提取数据
如果python数据类型是字典，使用dict.get()方式获取值，而不用dict[‘’]取值
根据项目文档返回从服务器跨域返回给前端的数据格式包括响应码
如果从前端传入服务器的数据时，如传入字段不全时，在models.py中不要将为没传入的数据字段添加null=true  因为null也为一条数据，可以使用default

在数据传入后存入数据库  数据库名.objects.create(字段名=xxx,)
如果项目文档中需要返回服务器繁忙响应，尝试使用try添加数据入数据库，except
Exception 只要发生，就返回服务器繁忙响应
```

#### 7.密码的处理

```python
密码的加密处理
import hashlib
m = hashlib.md5()
        m.update(password.encode()) # password 为需要加密的密码
m.hexdigest()

```

####  8.token的处理

```python
在对token（令牌）操作时，可以使用官方jwt来产生token
encode(payload, key, algorithm)
payload为字典中带有公有声明，和私有声明
key为自定义的加密key
algorithm为使用的加密算法


import jwt
payload = {'username':'ybh'}
key = "123456"
token = jwt.encode(payload=payload,key=key,algorithm='HS256')
print(token)
#eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InliaCJ9.1ZQNvfi-eND6uUTPXwMYxjntwv-bjMjq0p_XrSU1WEQ'

# decode解开token
s = jwt.decode(jwt=token,key=key,algorithms=['HS256'])
print(s)
# 返回的是payload字典
# 注意：
若encode得时候 payload中添加了exp字段; 则exp字段得值需为 当前时间戳+此token得有效期时间， 例如希望token 300秒后过期 {'exp': time.time() + 300}; 在执行decode时，若检查到exp字段，且token过期，则抛出jwt.ExpiredSignatureError
```

#### 9.杂七杂八3

```python
注意数据库查询 xxx.objects.filter()返回的是一个列表对象
在发起get请求时，url格式为xxx?参数名=值1&参数名=值2
在url中需要添加查询字符串，配置url时需要设置捕获组为（?P<捕获组名>正则）
捕获组名相当于传参，可以在视图函数中接收此参数，再使用
其中正则用来匹配参数名 在视图函数中使用request.GET.get('捕获组名','默认值')来获得url中对应参数名的值

在进行数据返回时，imagefield 数据需要强制类型转换为str类型
# hasattr(对象，属性) 函数用于判断对象是否包含对应的属性。如果对象有该属性返回 True，否则返回 False 
# getattr(对象，属性)如果该对象中有此属性，直接获取此属性对应的value

# 获取请求头内数据时，使用request.META.get(请求头内需要提取的key name)
来获取value

DateTimeField(auto_now_add=True)里使用auto_now_add 表示自动创建创建数据时的时间
DateTimeField(auto_now=True) 表示自动创建修改数据时的时间

在setting.py中 将USE_TZ = False 使时间准确
字典方法setdefault()
d = {}
d.setdefault(‘1’,[])
>>d    {“1”:[]}
d[‘1’].append(2)
>>d    {‘1’:[2]}
>> d .setdefault (‘1’,[])
>> d   {‘1’:[2]}

没有改掉里面value的值
```

#### 10.装饰器的套路理解

```python
def login_check(func):
    def wrapper(*args,**kwargs):
        
        新功能区

        return func(*args,**kwargs)

return wrapper
如果需要给函数上的装饰器传参eg: @check_token(‘PUT’,’GET’)
需要在装饰器函数外再套一层装饰器
def first_login_check(*args):
def login_check(func):
    	def wrapper(*args,**kwargs):
        
        新功能区

        	return func(*args,**kwargs)

return wrapper
Return login_check

为了使装饰器中处理过的值返还给视图函数，可以对web开发整个过程存在的request的对象增加属性 request.xxx = xxx 这样可以使经过装饰器后，request一直保留此属性，再视图函数中便可以提取出这一需要的属性对象


```

####  11.multipart/form-data

```
从前端向服务器传图片，mysql中只保存上传图片的相对路径
需要在setting里配置MEDIA_URL和MEDIA_ROOT
MEDIA_URL =’/media/’ 为前端传入的url地址中包含/media/，服务器便知道只是一次媒体资源的操作
服务器中的媒体资源放在MEDIA_ROOT的目录
MEDIA_ROOT = os.path.join(BASE_DIR,”media/’)
然后在主urls.py中添加媒体资源路由
from django.conf.urls.static import static
from django.conf import settings
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
# static告知服务器哪里去找到媒体资源
由于图片上传的请求方式为multipart/form-data
获取时，使用request,FILES.get(‘xxxx’)
```

####  12.跨站点请求攻击防御

```python
XSS就是脚本注入 （跨站点脚本攻击) 可以将本地的cookie alert出来
再将cookie 返还给攻击者 

如何防止XSS脚本注入：  
1.转义 import html
Html.escape(xxxx)
```

