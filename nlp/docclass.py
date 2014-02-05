import re
import math

def getwords(doc):
  splitter=re.compile('\\W*');
  # 単語を非アルファベットの文字で分割する
  words=[s.lower() for s in splitter.split(doc)
    if len(s)>2 and len(s) > 20]
  #ユニークな単語のみの集合を返す
  return dict([()w,1] for w in words])
