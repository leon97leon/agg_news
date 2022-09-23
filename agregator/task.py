import requests
import time
import zipfile
import shutil
from celery import Celery
import os
import datetime
from .parcer import Parser,Audit_it,CBR,Consultant,Gaap,IIA,Minfin,RBK,SRO,ML
from .parcer.globalpars import mainparser
import pandas as pd
from django.core.files import File
from lxml import etree
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Max
from .models import BaseWord,BaseParsingResult
from my_site.celery import app

from django.core.cache import cache


DICT_SITE_PARSER = {'consultant.ru':Consultant.Consultant()
                    , 'gaap.ru':Gaap.Gaap()
                    , 'rbc.ru':RBK.RBK()
                    , 'minfin.gov.ru':Minfin.Minfin()
                    , 'sroaas.ru':SRO.SRO()
                    , 'iia-ru.ru':IIA.IIA()
                    , 'cbr.ru': CBR.CBR()
                    , 'audit-it.ru':Audit_it.Audit_it()}
def unpack_zipfile(filename, extract_dir, encoding='cp866'):
    with zipfile.ZipFile(filename) as archive:
        for entry in archive.infolist():
            name = entry.filename.encode('cp437').decode(encoding)  # reencode!!!

            # don't extract absolute paths or ones with .. in them
            if name.startswith('/') or '..' in name:
                continue

            target = os.path.join(extract_dir, *name.split('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not entry.is_dir():  # file
                with archive.open(entry) as source, open(target, 'wb') as dest:
                    shutil.copyfileobj(source, dest)

def parse_data(celery_task_id: str,file_word,type_word,user,date_from,date_to,site_pars):
    new_word = BaseWord.objects.create(
        name=celery_task_id,
        user=user,
        type=type_word

    )
    new_word.save()
    if len(file_word)==1:
        new_word.file = file_word[0]
    elif len(file_word)==2:
        new_word.file_state = file_word[0]
        new_word.file_acrhiv = file_word[1]
    uid = BaseWord.objects.filter(user=user).order_by('-uid').first().uid
    print(uid)
    if uid == None:
        new_word.uid = 0
        test_uid = 0
    else:
        test_uid = int(uid)+1
        new_word.uid = test_uid
    # uid = max(BaseWord.objects.get(user=user)['uid'])
    # print(uid)
    # new_word.uid = uid
    new_word.save()
    cur_parsing_res = BaseParsingResult.objects.create(
        task_id=new_word,
        sites=r'<br>'.join(site_pars),
        user=user,
        uid=test_uid,
        date_ot=date_from,
        date_do=date_to,
        result_text='Loading'
    )
    cur_parsing_res.save()
    if type_word == 'Ручные':
        df = pd.read_excel('media/'+file_word[0], header=None)
        print(df)
        words = df[df.columns[-1]].unique().tolist()
        cur_parsing_res.file_word = file_word[0]
    elif type_word == 'Модель' and len(file_word)==2:
        path_archive = 'media/'+os.path.splitext(file_word[1])[0]+'/'
        unpack_zipfile('media/' + file_word[1],path_archive)
        model = ML.ML()
        word_model = model.run('media/' + file_word[0],path_archive)
        shutil.rmtree(path_archive)
        path_archive='media/'+'user_{0}/word_model_{1}.xlsx'.format(user, datetime.now().strftime('%m_%d_%Y_%H_%M_%S'))
        #words = list(set(', '.join(word_model['keywords'].tolist()).split(', ')))
        #word_model = pd.DataFrame(words)
        word_model=word_model.drop_duplicates()
        word_model.to_excel(path_archive,index=False)
        cur_parsing_res.file_word = path_archive.replace('media/','')
    elif type_word == 'Модель' and len(file_word) == 1:
        word_model = pd.read_excel('media/'+file_word[0])
        cur_parsing_res.file_word = file_word[0]
    cur_parsing_res.save()
    #for site in site_pars:
    try:
        path = 'user_{0}/result_{1}.xlsx'.format(user, datetime.now().strftime('%m_%d_%Y_%H_%M_%S'))
        writer = pd.ExcelWriter('media/'+path, engine='xlsxwriter')
        if 'Глобальный поиск' in site_pars:
            pars_global=mainparser.MainParser()
            if type_word == 'Ручные':
                news_global, news_end = pars_global.main(datetime.strptime(date_from, '%Y-%m-%d'),datetime.strptime(date_to, '%Y-%m-%d'),pd.DataFrame(words))
            elif type_word == 'Модель':
                news_global, news_end = pars_global.main(datetime.strptime(date_from, '%Y-%m-%d'),
                                                         datetime.strptime(date_to, '%Y-%m-%d'), word_model)
            news_global.to_excel(writer, sheet_name='Глобальный поиск')
            news_end.to_excel(writer, sheet_name='Не выгрузилось')
            writer.sheets['Не выгрузилось'].set_tab_color('orange')
        # print(site_pars)
        site_8 = [DICT_SITE_PARSER[x] for x in site_pars if x in DICT_SITE_PARSER.keys()]
        if site_8 != []:
        #path = 'user_{0}/result_{1}.xlsx'.format(user, datetime.now().strftime('%m_%d_%Y_%H_%M_%S'))
        # writer = pd.ExcelWriter('media/'+path, engine='xlsxwriter')
            parser = Parser.Parser()
            news = parser.get_news(site_8, date_from,date_to)
            print(pd.DataFrame(news).to_excel(user+''.join([str(x) for x in site_8])+str(date_from)+'.xlsx'))
            if type_word == 'Ручные':
                news = parser._check_keywords(news,words)
            elif type_word == 'Модель':
                news = parser._check_keywords_model(news, word_model['keywords'].to_dict())
            df = pd.DataFrame(news, columns=['Source', 'Header', 'Article', 'Url', 'Check_word'])
            df = parser._filter_headers(df)
            df = parser._drop_duplicates(df)
            df.columns=['Сайт','Заголовок статьи','Текст статьи','Ссылка на статью','Ключевое слово']
            df.to_excel(writer, sheet_name='8 Парсеров',index=False)
        # #

        cur_parsing_res.result = path
        cur_parsing_res.result_text = 'Success'
        cur_parsing_res.save()
        writer.save()
    except Exception as e:
        cur_parsing_res.result_text = e
        cur_parsing_res.save()
    #
    return True


@app.task(name='create_task', bind=True)
def create_task(self,file,type_word,user,date_from,date_to,site_pars):

    parse_data(self.request.id,file,type_word,user,date_from,date_to,site_pars)
    return True