import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.login_check import login_check
from topic.models import Topic


@login_check('POST')
def messages(request, topic_id):
    if request.method != 'POST':
        result = {'code': 401, 'error': 'please use post'}
        return JsonResponse(result)
    # 发表留言/回复

    user = request.user  # 获取用户
    req = request.body
    req_dic = json.loads(req)
    content = req_dic.get('content')
    if not content:
        return JsonResponse({'code': 600, 'error': 'no content'})

    parent_id = req_dic.get('parent_id', 0)
    try:
        topic = Topic.objects.get(id=topic_id)
    except:
        result = {'code': 403, 'error': "no topic"}
        return JsonResponse(result)

    # 校验topic是否为私有topic
    if topic.limit == 'private':
        # 检查身份
        if user.username != topic.author.username:
            result = {'code': 404, 'error': 'get out'}
            return JsonResponse(result)

    # 创建数据
    Message.objects.create(content=content,
                           publisher=user,
                           topic=topic,
                           parent_message=parent_id)
    return JsonResponse({'code': 200, 'data': {}})
