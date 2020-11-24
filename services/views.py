import json
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from services.functions.CosineResult import CosineResult
from services.functions.ConvertToVector import ConvertToVector
from django.views.decorators.csrf import csrf_exempt
import openpyxl
from services.models import Title, Data, Question


def index(request):
    if request.method == 'GET':
        dataObj = Data.objects.all()
        contents = list()

        for obj in dataObj:
            data = list()
            data.append(obj.article)
            data.append(Title.objects.get(pk=obj.title_id).title)
            data.append(obj.content)
            contents.append(data)
        response = JsonResponse({'data': contents})
        response.status_code = 200
        return response
    else:
        return render(request, '405error.html')


@csrf_exempt
def add_feedback(request):
    if request.method == 'POST':
        if request.body:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            try:
                token = body['token']
                question = body['question']
                id = body['id']
                if token and question and id:
                    isHave = Question.objects.filter(content=question).exists()
                    if not isHave:
                        Question.objects.create(content=question, knowledge_data_id=id)
                        response = JsonResponse({'message': 'Амжилттай хадгалагдлаа'})
                        response.status_code = 201
                        return response
                    else:
                        response = JsonResponse({'message': 'Бүртгэгдсэн байна'})
                        response.status_code = 200
                        return response
                else:
                    response = JsonResponse({'message': 'Өгөгдөл оруулна уу'})
                    response.status_code = 400
                    return response
            except Exception as e:
                response = JsonResponse({'message': 'Хүсэлт буруу байна'})
                response.status_code = 401
                return response
    else:
        return render(request, '405error.html')


@csrf_exempt
def search(request):
    if request.method == 'POST':
        if request.body:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            try:
                token = body['token']
                question = body['question']
                if token and question:
                    stop_word = ['нь', 'энэ', 'бол', 'дэх']
                    user_input = question

                    dataObj = Data.objects.all()
                    fullContents = list()
                    contents = list()

                    for obj in dataObj:
                        data = {
                            'id': obj.id,
                            'article': obj.article,
                            'title': Title.objects.get(pk=obj.title_id).title,
                            'content': obj.content,
                        }
                        fullContents.append(data)
                        contents.append(obj.content)

                    convertToVector = ConvertToVector(stop_word)

                    contents.append(user_input)
                    total_vec = convertToVector.convert_tfidf_vector(contents)

                    res = []
                    max_cos = 0

                    user_vec = total_vec[len(total_vec) - 1]

                    for i in range(len(total_vec) - 1):
                        cosine_number = convertToVector.cosine_similarity(user_vec, total_vec[i])
                        if cosine_number >= max_cos and cosine_number > 0:
                            max_cos = cosine_number
                            if len(res) == 0:
                                res.append(CosineResult(i, cosine_number))
                            else:
                                res.append(CosineResult(i, cosine_number))
                    if len(res) == 0:
                        response = JsonResponse({'message': 'Таны асуултанд тохирох хариулт олдсонгүй :('})
                        response.status_code = 204
                        return response
                    else:
                        answers = list()
                        res.sort(key=lambda c: c.cosine_number, reverse=True)
                        for obj in res:
                            answer = list()
                            answer.append(fullContents[obj.index]['id'])
                            answer.append(fullContents[obj.index]['article'])
                            answer.append(fullContents[obj.index]['title'])
                            answer.append(fullContents[obj.index]['content'])
                            answers.append(answer)

                        response = JsonResponse({'data': answers[0:5]})
                        response.status_code = 200
                        return response
                else:
                    response = JsonResponse({'message': 'Өгөгдөл оруулна уу'})
                    response.status_code = 400
                    return response
            except Exception as e:
                response = JsonResponse({'message': 'Хүсэлт буруу байна'})
                response.status_code = 401
                return response
    else:
        return render(request, '405error.html')


def excel_import(request):
    if request.method == 'POST':
        file = request.FILES['excel']

        wb = openpyxl.load_workbook(file)
        worksheet = wb["Sheet1"]
        excel_data = list()
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            excel_data.append(row_data)

        saved_title = list()
        last_title_id = 0
        last_content_id = 0
        for data in excel_data:
            if len(saved_title) == 0:
                saved_title.append(data[1])
                title = Title.objects.create(title=data[1])
                last_title_id = title.id
                newData = Data.objects.create(article=data[0], title_id=last_title_id, content=data[2])
                last_content_id = newData.id
            else:
                saved = False
                for title in saved_title:
                    if title == data[1]:
                        saved = True
                if saved != True:
                    saved_title.append(data[1])
                    title = Title.objects.create(title=data[1])
                    last_title_id = title.id
                    splitted_artice = data[0].split('.')
                    if len(splitted_artice) > 3:
                        Data.objects.create(article=data[0], title_id=last_title_id, content=data[2],
                                            data_id=last_content_id)
                    else:
                        newData = Data.objects.create(article=data[0], title_id=last_title_id, content=data[2])
                        last_content_id = newData.id
                        print(last_content_id)
                else:
                    splitted_artice = data[0].split('.')
                    if len(splitted_artice) > 3:
                        Data.objects.create(article=data[0], title_id=last_title_id, content=data[2],
                                            data_id=last_content_id)
                    else:
                        newData = Data.objects.create(article=data[0], title_id=last_title_id, content=data[2])
                        last_content_id = newData.id

        messages.success(request, 'Амжилттай хадгаллаа')
        return render(request, 'fileupload.html')
    elif request.method == 'GET':
        return render(request, 'fileupload.html')
    else:
        response = JsonResponse()
        response.status_code = 405
        return response
