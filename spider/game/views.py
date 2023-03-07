import json
import grpc

from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .proto import game_pb2,game_pb2_grpc


def index(request):
    return HttpResponse("Hello, world. You're at the game index.")



@csrf_exempt
def game_list(request):
    try:
        data = request.body.decode("utf-8")
        req = json.loads(data)
        page = 0
        page_size = 0
        keyword = ""
        if "page" in req:
            page = int(req["page"])
        if "page_size" in req:
            page_size = int(req["page_size"])
        if "key_word" in req:
            keyword = req["key_word"]
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
        data = request.body.decode("utf-8")
        req = json.loads(data)
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


