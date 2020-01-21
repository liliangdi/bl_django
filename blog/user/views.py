import hashlib
import json
import time

from django.http import JsonResponse
from django.shortcuts import render

from tools.login_check import login_check
from . import models


# Create your views here.

@login_check('GET', 'PUT')
def users(request, username=None):
    if request.method == 'GET':
        # 获取用户数据
        if username:
            # 对象列表
            db_user = models.UserProfile.objects.filter(username=username)
            user = db_user[0]
            if not user:
                result = {'code': 209, 'error': '用户不存在'}
                return JsonResponse(result)
            # 检查是否有查询字符串
            # request.GET获取到查询字符串，是一个类字典对象
            # 字典对象.keys()获取到所有的key，返回列表形式
            if request.GET.keys():
                data = {}
                # 查询指定字段
                for key in request.GET.keys():
                    # hasattr判断对象中是否有这一属性
                    if hasattr(user, key):
                        # 获取到这一属性的值用getattr
                        value = getattr(user, key)
                        if key == 'avatar':
                            data[key] = str(value)
                        data[key] = value

                result = {'code': 200, 'data': data}
                return JsonResponse(result)

            else:
                # 全量查询

                nickname = user.nickname
                sign = user.sign
                avatar = user.avatar
                info = user.info
                result = {'code': 200, 'username': username,
                          'data': {'nickname': nickname, 'sign': sign, 'avatar': str(avatar), 'info': info}}
                return JsonResponse(result)

            # return JsonResponse({'code': 200,'error':'wo 来了'})
        else:
            return JsonResponse({'code': 200, 'error': 'asdasd'})
    elif request.method == 'POST':
        # 创建用户
        # 前端注册页面地址 127.0.0.1：5000/register

        print(request.body)
        req_dict = json.loads(request.body)
        if not bool(req_dict):
            return JsonResponse({'code': 202, 'error': '请求中无内容'})
        username = req_dict.get('username')
        if not username:
            return JsonResponse({'code': 203, 'error': "请输入用户名"})
        email = req_dict.get('email')
        if not email:
            return JsonResponse({'code': 204, 'error': '请输入邮箱'})
        password1 = req_dict.get('password_1')
        password2 = req_dict.get('password_2')
        if not password1 or not password2:
            return JsonResponse({'code': 205, 'error': "请输入密码"})
        if password1 != password2:
            return JsonResponse({'code': 206, 'error': '两次密码不一致'})
        old_user = models.UserProfile.objects.filter(username=username)
        if old_user:
            return JsonResponse({'code': 207, 'error': '用户已存在'})
        # 密码处理
        m = hashlib.md5()
        m.update(password1.encode())

        try:
            models.UserProfile.objects.create(username=username,
                                              nickname=username,
                                              email=email,
                                              password=m.hexdigest())
        except Exception as e:
            # 可能发生的问题为数据库down，用户名存在
            result = {'code': 208, 'error': '服务器忙'}
            return JsonResponse(result)

        # make token
        token = make_token(username)
        # 正常返回给前端
        return JsonResponse({'code': 200, 'username': username, 'data': {"token": token.decode()}})
    elif request.method == 'PUT':
        # 更新用户
        # 此头可获取前端传来的token，META可以拿去http协议原生头
        # META 也是类字典对象 可以使用类相关方法
        # http头有可能被django重命名
        user = request.user
        req = request.body
        if not req:
            return JsonResponse({'code': 209, 'error': '给我json'})
        req_dic = json.loads(req)
        if 'sign' not in req_dic:
            return JsonResponse({'code': 210, 'error': 'no sign'})
        if 'info' not in req_dic:
            return JsonResponse({'code': 210, 'error': 'no info'})
        if 'nickname' not in req_dic:
            return JsonResponse({'code': 211, 'error': 'no nickname'})
        sign = req_dic.get('sign', '')
        info = req_dic.get('info', '')
        nickname = req_dic.get('nickname', '')
        try:
            the_db_user = models.UserProfile.objects.get(username=user.username)
        except Exception as e:
            return JsonResponse({'code': 110, 'error': '服务器忙'})
        the_db_user.sign = sign
        the_db_user.info = info
        the_db_user.nickname = nickname
        the_db_user.save()

        return JsonResponse({'code': 200, 'error': "成功"})

    else:
        raise


def make_token(username, expire=3600 * 24):
    # 官方jwt
    import jwt
    key = '1234567'
    now = time.time()
    payload = {'username': username, 'exp': int(now + expire)}
    return jwt.encode(payload, key, algorithm='HS256')


@login_check('POST')
def user_avatar(request, username):
    # 上传用户头像

    if request.method != 'POST':
        return JsonResponse({'code': 212, 'error': 'i need post'})
    avatar = request.FILES.get('avatar')
    if not avatar:
        result = {"code": 213, 'error': 'i need avatar'}
        return JsonResponse(result)

    request.user.avatar = avatar
    request.user.save()
    result = {'code':200,'username':request.user.username}
    return JsonResponse(result)



    # return JsonResponse({'code': 200, 'error': 'wo shi avatar'})
