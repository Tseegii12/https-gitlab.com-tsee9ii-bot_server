import json
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from services.functions.CosineResult import CosineResult
from services.functions.ConvertToVector import ConvertToVector
from django.views.decorators.csrf import csrf_exempt
import openpyxl
from services.models import Title, Data


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
        response = JsonResponse()
        response.status_code = 405
        return response


@csrf_exempt
def search(request):
    if request.method == 'POST':
        if request.body:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            question = body['question']
            stop_word = ['нь', 'энэ', 'бол', 'дэх']
            user_input = question

            dataObj = Data.objects.all()
            contents = list()

            for obj in dataObj:
                contents.append(obj.content)

            convertToVector = ConvertToVector(stop_word)

            # contents_vec = convertToVector.convert_tfidf_vector(contents)

            contents.append(user_input)
            user_input_vec_c = convertToVector.convert_count_vector(contents)

            res = []
            max_cos = 0

            for i in range(len(user_input_vec_c) - 1):
                cosine_number = convertToVector.cosine_similarity(user_input_vec_c[len(user_input_vec_c) - 1], user_input_vec_c[i])
                if cosine_number >= max_cos:
                    max_cos = cosine_number
                    if len(res) == 0:
                        res.append(CosineResult(i, cosine_number))
                    else:
                        for obj in res:
                            if obj.cosine_number < cosine_number:
                                obj.index = i
                                obj.cosine_number = cosine_number
                            else:
                                res.append(CosineResult(i, cosine_number))

            print('max_cos: ', max_cos)
            if len(res) == 0:
                response = JsonResponse({'message': 'Таны асуултанд тохирох хариулт олдсонгүй :('})
                response.status_code = 204
                return response
            else:
                answers = list()
                for obj in res:
                    answer = list()
                    data_obj = Data.objects.get(content=contents[obj.index])
                    title = Title.objects.get(pk=data_obj.title_id).title
                    answer.append(data_obj.article)
                    answer.append(title)
                    answer.append(data_obj.content)
                    answers.append(answer)

                response = JsonResponse({'data': answers})
                response.status_code = 200
                return response
        else:
            response = JsonResponse({'message': 'Өгөгдөл оруулна уу'})
            response.status_code = 400
            return response
    else:
        response = JsonResponse()
        response.status_code = 405
        return response


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
        last_pk = 0
        for data in excel_data:
            if len(saved_title) == 0:
                title = Title.objects.create(title=data[1])
                last_pk = title.id
                new_data = Data.objects.create(article=data[0], title_id=last_pk, content=data[2])

            else:
                saved = False
                for title in saved_title:
                    if title == data[1]:
                        saved = True
                if saved != True:
                    saved_title.append(data[1])
                    title = Title.objects.create(title=data[1])
                    last_pk = title.id
                    new_data = Data.objects.create(article=data[0], title_id=last_pk, content=data[2])
                else:
                    new_data = Data.objects.create(article=data[0], title_id=last_pk, content=data[2])

        messages.success(request, 'Амжилттай хадгаллаа')
        return render(request, 'fileupload.html')
    elif request.method == 'GET':
        return render(request, 'fileupload.html')
    else:
        response = JsonResponse()
        response.status_code = 405
        return response
