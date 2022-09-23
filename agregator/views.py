from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models.deletion import ProtectedError
import pandas as pd
from datetime import datetime
from asgiref.sync import async_to_sync
from .parcer import Parser,Audit_it
from django.core.files.storage import FileSystemStorage
from .models import Files,BaseParsingResult,BaseWord
from rest_framework.decorators import api_view
from rest_framework.response import Response
from celery.result import AsyncResult
from celery import Celery
from urllib.parse import unquote
import redis
import os
from .task import create_task
from celery import Celery

from my_site.celery import app as celery_app
agg_site=['site1','site2','site3','site4','site5','site6','site7','site8','site9']
def get_celery_queue_len(queue_name):
    with celery_app.pool.acquire(block=True) as conn:
        return conn.default_channel.client.llen(queue_name)



@api_view(['GET', 'POST'])
def task(request):
    #return Response({"message": 'Нет', "data": request.data})
    #print(get_celery_queue_len('celery'))
    print()
    if request.method == 'POST':
        print(request.POST)
        try:
            date_from = request.POST['date1']
        except:
            date_from=''
        try:
            date_to = request.POST['date2']
        except:
            date_to=''
        try:
            site_pars = ''.join([request.POST[x] for x in agg_site if x in request.POST])
        except:
            site_pars=''
        print('file_ml_restart' not in request.POST)
        if 'file_ml_restart' not in request.POST and 'file_word' not in request.FILES and request.POST['file_word_sep'] == '' and ( 'file_ml_reestr' not in request.FILES and 'file_ml_state' not in request.FILES) and 'file_word_restart' not in request.POST and 'file_ml_state_restart' not in request.POST and 'file_ml_reestr_restart'  not in request.POST :
            messages.success(request, 'Загрузите файл ключевых слов!')
            return render(request, 'agg/aggregator.html',{'date_from':date_from,'date_do':date_to,'sites':site_pars})

        elif request.POST['date1'] == '' or request.POST['date2'] == '':
            messages.success(request, 'Выберите диапазон дат!')
            return render(request, 'agg/aggregator.html',{'date_from':date_from,'date_do':date_to,'sites':site_pars})
        elif 'site1' not in request.POST and 'site2' not in request.POST and 'site3' not in request.POST and 'site4' not in request.POST and 'site5' not in request.POST and 'site6' not in request.POST and 'site7' not in request.POST and 'site8' not in request.POST and 'site9' not in request.POST:
            messages.success(request, 'Выберите сайт для парсинга!')
            return render(request, 'agg/aggregator.html',{'date_from':date_from,'date_do':date_to,'sites':site_pars})
        else:
            date_from = request.POST['date1']
            date_to = request.POST['date2']
            site_pars = [request.POST[x] for x in agg_site if x in request.POST]
            if request.POST['file_word_sep'] != '':
                word = request.POST['file_word_sep'].split(',')
                file = pd.DataFrame(word)
                try:
                    os.makedirs('media/'+'user_{0}'.format(request.user))
                except:
                    pass
                path = 'media/'+'user_{0}/слова_{1}.xlsx'.format(request.user, datetime.now().strftime('%m_%d_%Y_%H_%M_%S'))
                print(path)
                file.to_excel(path,index=False,header=None)
                file = [path.replace('media/','')]
                type_word = 'Ручные'
            elif 'file_word' in request.FILES or 'file_word_restart' in request.POST:
                try:
                    file = request.FILES['file_word']
                    file_model = Files()
                    file_model.user = request.user
                    file_model.upload = file
                    file_model.save()
                    file = [str(file_model.upload.name)]
                except MultiValueDictKeyError:
                    print(str(request.POST['file_word_restart']))
                    file = [unquote(str(request.POST['file_word_restart'])).replace('/media/','')]
                type_word = 'Ручные'
            elif 'file_ml_restart' in request.POST:
                type_word = 'Модель'
                file = [unquote(str(request.POST['file_ml_restart'])).replace('/media/', '')]
            elif ('file_ml_reestr' in request.FILES and 'file_ml_state' in request.FILES) or ('file_ml_reestr_restart' in request.POST and 'file_ml_state_restart' in request.POST):
                try:
                    file_reestr = request.FILES['file_ml_reestr']
                    file_model = Files()
                    file_model.user = request.user
                    file_model.upload = file_reestr
                    file_model.save()
                    file_reestr=str(file_model.upload.name)
                    file_state = request.FILES['file_ml_state']
                    file_model = Files()
                    file_model.user = request.user
                    file_model.upload = file_state
                    file_model.save()
                    file_state = str(file_model.upload.name)
                    type_word = 'Модель'
                    file = [file_reestr, file_state]
                except MultiValueDictKeyError:
                    file = [unquote(str(request.POST['file_ml_state_restart'])).replace('/media/', ''),unquote(str(request.POST['file_ml_reestr_restart'])).replace('/media/', '')]

            else:
                messages.success(request, 'Загрузите файл ключевых слов!')
                return render(request, 'agg/aggregator.html')

            task = create_task.delay(file, type_word, request.user.username, date_from,
                                     date_to, site_pars)
            result = f'Ваш запрос запущен!\n' \
                     f' Вы в очереди под номером:{str(get_celery_queue_len("celery")+1)}\n' \
                     f' Результаты смотрите в истории запросов в личном кабинете!'
            messages.success(request,result)
            return redirect('agregator')
    elif request.method == 'POST' and request.POST['file_word']:
        print(request.POST['file_word'])
    #     if "type" in request.data:
    #         category_name = request.data["type"]
    #         task = create_task.delay(category_name) # create celery task
    #         return Response({"message": "Create task", "task_id": task.id, "data": request.data})
    #     else:
    #         return Response({"message": "Error, not found 'type' in POST request"})
    # if request.method == 'GET': # get task status
    #     if "task_id" in request.data:
    #         task_id = request.data["task_id"]
    #         task_result = AsyncResult(task_id)
    #         result = {
    #             "task_id": task_id,
    #             "task_status": task_result.status,
    #             "task_result": task_result.result
    #         }
    #         return Response(result)
    #     else
    return Response({"message": 'Нет',"data": request.data})


# Create your views here.
def agg(request):
    if request.user.is_authenticated == True:
        return render(request, 'agg/aggregator.html')
    else:
        return redirect('home')
def account(request):
    if request.user.is_authenticated == True:
        return render(request, 'agg/account.html')
    else:
        return redirect('home')

def history(request):
    if request.user.is_authenticated == True:
        hist_s = BaseWord.objects.filter(user=request.user.username)
        return render(request, 'agg/history.html',{'hist_s':hist_s})
    else:
        return redirect('home')

def files(request):
    # POST - обязательный метод
    if request.method == 'POST' and request.FILES:
        # получаем загруженный файл
        file = request.FILES['file_word']
        date_from = request.POST['date1']
        date_to = request.POST['date2']
        #file_model = Files()
        #file_model.user=request.user
        #file_model.upload = file
        #file_model.save()
        # df = pd.read_excel(file,header=None)
        # words = df[0].unique().tolist()
        # print(df)
        # parser = Parser.Parser()
        # news = parser.get_news([Audit_it.Audit_it()], date_from,date_to)
        # news = parser._check_keywords(news,words)
        # df = pd.DataFrame(news, columns=['Source', 'Header', 'Article', 'Url', 'Check_word'])
        # df = parser._filter_headers(df)
        # df.to_excel('media/user_{0}/result.xlsx'.format(request.user.username))
    #messages.success(request, supper_sum.delay(5,7))

    return redirect('home')
def download(request, pk,type):
    '''Счетчик клика по ссылке скачать прайс лист.'''
    # try:
    #     price = get_object_or_404(PriceList, is_active=True)
    # except MultipleObjectsReturned:
    #     return HttpResponse('Вы выбрали более одного файла')
    if type == 'result':
        price = BaseParsingResult.objects.get(pk=pk)
        return redirect(price.result.url)
    elif type == 'word_result':
        price = BaseParsingResult.objects.get(pk=pk)
        return redirect(price.file_word.url)
    elif type == 'word':
        price = BaseWord.objects.get(pk=pk)
        if price.type == 'Ручные':
            return redirect(price.file.url)
    elif type == 'word_reestr':
        url = BaseWord.objects.get(pk=pk)
        return redirect(url.file_state.url)
    elif type == 'word_achive':
        url = BaseWord.objects.get(pk=pk)
        return redirect(url.file_acrhiv.url)

def restart(request):
    # try:
    #     price = get_object_or_404(PriceList, is_active=True)
    # except MultipleObjectsReturned:
    #     return HttpResponse('Вы выбрали более одного файла')
    id = request.GET.get('id',None)
    if request.GET.get('typ',None) == 'парсинг':
        hist_s = BaseWord.objects.filter(user=request.user.username,uid=id)
        date_from = str(hist_s[0].links.all()[0].date_ot)
        date_do = str(hist_s[0].links.all()[0].date_do)
        sites = str(hist_s[0].links.all()[0].sites)
        if hist_s[0].type == 'Ручные':
            file_word = hist_s[0].file.url
            return render(request, 'agg/aggregator.html',
                          {'date_from': date_from, 'date_do': date_do, 'file_word': file_word, 'sites': sites})
        elif hist_s[0].type == 'Модель':
            file_word_model = hist_s[0].links.all()[0].file_word.url
            return render(request, 'agg/aggregator.html',
                          {'date_from': date_from, 'date_do': date_do, 'file_word_model': file_word_model, 'sites': sites})
        #return redirect('agregator')

    elif request.GET.get('typ',None) == 'слово':
        hist_s = BaseWord.objects.filter(user=request.user.username, uid=id)
        if hist_s[0].type == 'Ручные':
            file_word = hist_s[0].file.url
            return render(request, 'agg/aggregator.html',
                          {'file_word':file_word})
        elif hist_s[0].type == 'Модель':
            file_state = hist_s[0].file_state.url
            file_archive = hist_s[0].file_acrhiv.url
            return render(request, 'agg/aggregator.html',
                          {'file_state': file_state,'file_archive':file_archive})
    return redirect('history_keys')

def delete(request, pk):
    '''Счетчик клика по ссылке скачать прайс лист.'''
    # try:
    #     price = get_object_or_404(PriceList, is_active=True)
    # except MultipleObjectsReturned:
    #     return HttpResponse('Вы выбрали более одного файла')
    object = BaseParsingResult.objects.get(pk=pk)
    try:
        os.remove('.'+object.result.url)
    except (ValueError,FileNotFoundError):
        pass
    try:
        os.remove('.'+object.file_word.url)
    except (ValueError,FileNotFoundError):
        pass
    object.delete()
    return redirect('history')
def history_keys(request):
    if request.user.is_authenticated == True:
        hist = BaseWord.objects.filter(user=request.user.username)
        return render(request, 'agg/history_keys.html',{'hist_s':hist})
    else:
        return redirect('home')

def delete_keys(request, pk):
    '''Счетчик клика по ссылке скачать прайс лист.'''
    # try:
    #     price = get_object_or_404(PriceList, is_active=True)
    # except MultipleObjectsReturned:
    #     return HttpResponse('Вы выбрали более одного файла')
    try:
        object = BaseWord.objects.get(pk=pk)
        #os.remove('.'+object.file.url)
        try:
            os.remove('.' + object.file.url)
        except (ValueError, FileNotFoundError):
            pass
        try:
            os.remove('.' + object.file_state.url)
        except (ValueError, FileNotFoundError):
            pass
        try:
            os.remove('.' + object.file_acrhiv.url)
        except (ValueError, FileNotFoundError):
            pass
        object.delete()
    except ProtectedError:
        messages.success(request, f'Для удаления ключевых слов, необходимо удалить результаты {str(object.uid)} парсинга!')
    return redirect('history_keys')