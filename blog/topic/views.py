import json

import jwt
from django.http import JsonResponse
from django.shortcuts import render

from message.models import Message
from tools.login_check import login_check, get_user_by_request
from user.models import UserProfile
from .models import Topic

KEY = '1234567'


# Create your views here.
@login_check('POST', 'DELETE')
def topics(request, author_id):
    if request.method == 'GET':
        # 获取用户数据
        # author_id 被访问的博客的博主用户名
        # visitor 访客
        authors = UserProfile.objects.filter(username=author_id)
        # print(author_id)
        if not authors:
            result = {'code': 308, 'error': '?no author'}
            return JsonResponse(result)
        # 取出结果中的博主
        author = authors[0]

        # visitor
        visitor = get_user_by_request(request)
        visitor_name = None
        if visitor:
            # 是登陆用户
            visitor_name = visitor.username
        t_id = request.GET.get('t_id')
        if t_id:
            # 当前是否为 博主访问自己的博客
            is_self = False
            # 获取详情页
            t_id = int(t_id)
            if author_id == visitor_name:
                is_self = True
                # 博主访问自己的博客详情页
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code': 312, 'error': 'no topic'}
                    return JsonResponse(result)
            else:
                # 访客访问博主博客详情页

                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    return JsonResponse({'code': 313, 'error': 'no topic!'})

            res = make_topic_res(author, author_topic, is_self)

            return JsonResponse(res)




        else:
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # / v1/topics/<author_id>?category=[tec|no-yec]
                if author_id == visitor_name:
                    # 博主访问自己
                    topics = Topic.objects.filter(author_id=author_id, category=category)

                else:
                    # 访客
                    topics = Topic.objects.filter(author_id=author_id, category=category, limit='public')

            else:
                if author_id == visitor_name:
                    # 博主
                    topics = Topic.objects.filter(author_id=author_id)

                else:
                    # 登陆访客
                    topics = Topic.objects.filter(author_id=author_id, limit='public')

            # 返回 author为 UserProfile对象 topics 为Topic对象
            res = make_topics_res(author, topics)
            return JsonResponse(res)


    elif request.method == 'DELETE':
        author = request.user
        token_author_id = author.username
        # url 传入的author_id 必须与token中的用户名相等
        if token_author_id != author_id:
            return JsonResponse({'code': 404, 'error': '用户不一致'})
        topic_id = request.GET.get('topic_id')
        try:
            topic = Topic.objects.get(id=topic_id)
        except:
            result = {'code': 405, 'error': 'you can not do it'}
            return JsonResponse(result)
        if topic.author.username != author_id:
            return JsonResponse({'code': 406, 'error': 'you can do yit'})
        topic.delete()
        res = {'code': 200}
        return JsonResponse(res)


    elif request.method == 'POST':
        # 创建用户博客数据
        # token = request.META.get('HTTP_AUTHORIZATION')
        # if not token:
        #     return JsonResponse({'code':403,'error':'用户未登陆'})
        req = request.body
        req_dic = json.loads(req)
        if not req_dic:
            return JsonResponse({'code': 401, 'error': '没有JSON数据'})
        title = req_dic.get('title')

        # xss 注入
        import html
        title = html.escape(title)
        if not title:
            return JsonResponse({'code': 402, 'error': '没有用户名'})
        category = req_dic.get('category')
        if category not in ['tec', 'no-tec']:
            return JsonResponse({'code': 403, 'error': 'category不正确'})
        content = req_dic.get('content')
        if not content:
            return JsonResponse({'code': 405, 'error': 'content 不正确'})
        content_text = req_dic.get('content_text')
        if not content_text:
            return JsonResponse({'code': 406, 'error': 'content_text 不正确'})
        introduce = content_text[:30]
        limit = req_dic.get('limit')
        if limit not in ['public', 'private']:
            return JsonResponse({'code': 407, 'error': 'gei wo  limit'})

        Topic.objects.create(
            title=title,
            category=category,
            limit=limit,
            content=content_text,
            introduce=introduce,
            author=request.user)
        user = request.user
        username = user.username
        return JsonResponse({'code': 200, 'username': username})


def make_topics_res(author, topics):
    res = {'code': 200, 'data': {}}
    data = {}
    data['nickname'] = author.nickname
    topic_list = []
    for topic in topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['author'] = author.nickname
        d['content'] = topic.content
        d['introduce'] = topic.introduce
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        # print(d['create_time'])
        topic_list.append(d)
    data['topics'] = topic_list
    res['data'] = data
    return res


def make_topic_res(author, author_topic, is_self):
    """
    拼接详情页 返回数据
    :param author: 从url中取出的author_id所对应的author对象(写这文章的作者)
    :param author_topic: 根据t_id查找到的topic对象
    :param is_self: 判断是否为博主访问
    :return:
    """

    if is_self:
        # 博主访问自己的博客
        # 取出id大于当前博客的第一个且author为当前作者
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        # 访客访问博主的
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()

    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title

    else:
        last_id = None
        last_title = None

    all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
    msg_list = []  # 所有留言
    reply_dict = {}  # 留言回复的映射
    msg_count = 0
    for msg in all_messages:
        msg_count += 1
        if msg.parent_message == 0:  # 当前是留言
            msg_list.append({'id': msg.id, 'content': msg.content,
                             'publisher': msg.publisher.nickname,
                             'publisher_avatar': str(msg.publisher.avatar),
                             'created_time': msg.created_time.strftime('%Y-%m-%d'), 'reply': []})
        else:
            # 当前是回复
            reply_dict.setdefault(msg.parent_message, [])
            reply_dict[msg.parent_message].append({'msg_id': msg.id,
                                                   'content': msg.content,
                                                   'publisher': msg.publisher.nickname,
                                                   'publisher_avatar': str(msg.publisher.avatar),
                                                   'created_time': msg.created_time.strftime('%Y-%m-%d')})
            # 合并msg_list 和reply_dict
    for _msg in msg_list:
        if _msg['id'] in reply_dict:  # 此条_msg下有回复
            _msg['reply'] = reply_dict[_msg['id']]  # 对应msg.parent_message

    res = {'code': 200, 'data': {}}
    res['data']['nickname'] = author.nickname
    res['data']['title'] = author_topic.title
    res['data']['category'] = author_topic.category
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['author'] = author.username
    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title

    # messages
    res['data']['messages'] = msg_list
    res['data']['messages_count'] = msg_count
    return res
