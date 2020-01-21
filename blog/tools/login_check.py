import jwt
from django.http import JsonResponse

from user.models import UserProfile

key = '1234567'


def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # methods = ['POST', 'GET', 'PUT']
            token = request.META.get('HTTP_AUTHORIZATION')
            print(token)
            if request.method not in methods:
                return func(request, *args, **kwargs)
            if not token:
                result = {'code': 107, 'error': 'please give me token'}

                return JsonResponse(result)
            # print(111111111111111)
            try:
                res = jwt.decode(jwt=token, key=key, algorithms='HS256')

            except jwt.ExpiredSignatureError:
                # token 过期
                result = {"code": 108, 'error': '请登录'}
                return JsonResponse(result)
            except Exception as e:
                result = {'code': 109, 'error': "请登录"}
                return JsonResponse(result)
            username = res['username']
            try:
                user = UserProfile.objects.get(username=username)
            except:
                user = None
            if not user:
                result = {'code': 110, 'error': '没有user'}
                return JsonResponse(result)
            # print(user.username)
            # 利用request，将user赋给request为属性
            request.user = user

            return func(request, *args, **kwargs)

        return wrapper

    return _login_check


def get_user_by_request(request):
    """
    通过request 尝试获取user
    :param request:
    :return: UserProfile OBJ OR None

    """
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None

    try:
        res = jwt.decode(token, key,algorithms='HS256')
    except:
        return None

    username = res['username']
    print(username)
    try:
        user = UserProfile.objects.get(username=username)
        return user
    except:
        return None
