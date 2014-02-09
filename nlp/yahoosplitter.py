# -*- coding: utf-8 -*-
from urllib import urlopen, quote_plus
from bs4 import BeautifulSoup
global query
appid = 'get_own_app_id_from_yahoo'
pageurl = 'http://jlp.yahooapis.jp/MAService/V1/parse'

# 形態素解析した結果をリストで返す
def split (sentence, app_id=appid, results='ma', filter='1|2|3|4|5|9|10'):
  ret=[]
  sentence=quote_plus(sentence.encode('utf-8')) # 文章をURLエンコード
  query="%s?appid=%s&results=%s&uniq_filter=%s&sentence=%s" % (pageurl,appid,results,filter,sentence)
  soup=BeautifulSoup(urlopen(query))
  try: return [l.surface.string for l in soup.ma_result.word_list]
  except: return[]
