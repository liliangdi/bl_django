import hashlib
import json
import time

from django.http import JsonResponse
from django.shortcuts import render
from user.models import UserProfile

# Create your views here.


def tokens(request):
    # 创建token == 登陆
    if not request.method == 'POST':
        result = {'code': 201, 'error': 'please use POST'}
        return JsonResponse(result)
    # 获取前端传来的数据
    # 获取数据-检验密码-生成token

    req_str = request.body
    if not req_str:
        result = {'code': 102, 'error': "给我json"}
        return JsonResponse(result)
    req_dic = json.loads(req_str)
    username = req_dic.get('username')
    password = req_dic.get('password')

    if not username:
        result = {'code': 202, 'error': '请输入用户名'}
        return JsonResponse(result)
    if not password:
        result = {'code': 203, 'error': '请输入密码'}
        return JsonResponse(result)

    db_user = UserProfile.objects.filter(username=username)
    if not db_user:
        result = {'code': 208, 'error': '用户名或密码不正确'}
        return JsonResponse(result)
    user = db_user[0]

    m = hashlib.md5()
    m.update(password.encode())
    hash_password = m.hexdigest()
    if hash_password != user.password:
        result = {'code': 209, 'error': '用户名或密码不正确'}
        return JsonResponse(result)

    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
    return JsonResponse(result)



def make_token(username, expire=3600 * 24):
    # 官方jwt
    import jwt
    key = '1234567'
    now = time.time()
    payload = {'username': username, 'exp': int(now + expire)}
    return jwt.encode(payload, key, algorithm='HS256')
