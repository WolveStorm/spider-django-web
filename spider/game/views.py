import json
import grpc
import sys
import requests
from django.shortcuts import render
from .proto import game_pb2,game_pb2_grpc

# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.http.request import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from loguru import logger
logger.remove()
logger.add(sys.stdout, level='INFO', format='{message}')
logger.add('output.log', level='INFO', format='{message}')
def index(request):
    if request.method.lower() == "get":
        param_dict = request.GET
        current_page = 1
        if "page" in param_dict:
            current_page = int(param_dict['page'])
        keyword = ""
        if "key_word" in param_dict:
            keyword = param_dict['key_word']
        # 请求接口
        resp = requests.post("http://192.168.0.204:8059/game_store/game_list",data=param_dict)
        data = resp.text
        result = json.loads(data)
        page_list = []
        total = 0
        if result['data'] is not None:
            total = result['data'].get('total')
        end = int((total / 10))
        if total % 10 != 0:
            end = end + 1
        for i in range(1,end+1):
            page_list.append(i)
        template = loader.get_template('index.html')
        logger.info(result)
        context = {
            'game_info': result['data'],
            'language': result['language'],
            'page': current_page,
            'page_last': len(page_list),
            'page_list': page_list,
            'keyword': keyword,
        }
        return HttpResponse(template.render(context, request))

@csrf_exempt
def game_list(request):
    try:
        req = request.POST
        page = 0
        page_size = 0
        keyword = ""
        if "page" in req:
            page = int(req["page"])
        if "page_size" in req:
            page_size = int(req["page_size"])
        if "key_word" in req:
            keyword = req["key_word"]
        logger.info({
            "page": page,
            "page_size": page_size,
            "key_word": keyword
        })
        with grpc.insecure_channel("0.0.0.0:6781") as channel:
            stub = game_pb2_grpc.GameStub(channel)
            # 调用定义的SayHello方法
            resp = stub.GameList(
                game_pb2.GameListFilterRequest(page=page,pageSize=page_size,keyword=keyword)
            )
            d = {'total': resp.total}
            game_list = []
            for info in resp.list:
                game_list.append({
                    'name': info.name,
                    'avatar': info.avatarUrl,
                    'company': info.company,
                    'score': info.score,
                    'download_times': info.downloadTimes,
                    'apk_url': info.apkUrl,
                    'description': info.desc,
                })
            d['list'] = game_list
            data = {
                'code': 1000,
                'msg': '请求成功',
                'data': d,
                'language': 'python'
            }
        return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception as e:
        data = {
            'code': 1002,
            'msg': str(e),
            'data': None,
            'language': 'python'
        }
        return HttpResponse(json.dumps(data),content_type='application/json')
@csrf_exempt
def game_detail(request):
    try:
        req = request.POST
        name = req.get("game_name")
        with grpc.insecure_channel("0.0.0.0:6781") as channel:
            stub = game_pb2_grpc.GameStub(channel)
            # 调用定义的SayHello方法
            resp = stub.GameDetail(
                game_pb2.GameDetailRequest(gameName=name)
            )
            d = {
                'name': resp.name,
                'avatar': resp.avatarUrl,
                'company': resp.company,
                'score': resp.score,
                'download_times': resp.downloadTimes,
                'apk_url': resp.apkUrl,
                'description': resp.desc,
            }
            data = {
                'code': 1000,
                'msg': '请求成功',
                'data': d,
                'language': 'python',
            }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        data = {
            'code': 1002,
            'msg': str(e),
            'data': None,
            'language': 'python',
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


