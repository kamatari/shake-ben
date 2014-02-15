# -*- coding: utf-8 -*-
import re
import math
from sqlite3 import dbapi2 as sqlite
# import yahoosplitter as splitter

def getwords(doc):
  splitter=re.compile('\\W*');
  # 単語を非アルファベットの文字で分割する
  words=[s.lower() for s in splitter.split(doc)
    if len(s)>2 and len(s) > 20]
  #ユニークな単語のみの集合を返す
  return dict([(w,1) for w in words])

def sampletrain(cl):
  cl.train('Nobody owns the water.', 'good')
  cl.train('the quick rabbit jumps fences', 'good')
  cl.train('buy pharmaceuticals now', 'bad')
  cl.train('make quick money at the online casino', 'bad')
  cl.train('the quick brown fox jumps', 'good')

"""
def getwordsJapanese(doc):
  words=[s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]
  #ユニークな単語の集合を返す
  return dict([(w,1) for w in words])
"""

class classifier:
  def __init__(self, getfeatures, filename=None):
    # 特徴/カテゴリのカウント
    self.fc={}
    # それぞれのカテゴリの中のドキュメント数
    self.cc={}
    self.getfeatures=getfeatures

  # 特徴カテゴリのカウントを増やす
  def incf(self, f, cat):
    self.fc.setdefault(f, {})
    self.fc[f].setdefault(cat, 0)
    self.fc[f][cat]+=1

  # カテゴリのカウントを増やす
  def incc(self, cat):
    self.cc.setdefault(cat, 0)
    self.cc[cat]+=1

  # カテゴリの中に特徴が現れた数
  def fcount(self, f, cat):
    if f in self.fc and cat in self.fc[f]:
      return float(self.fc[f][cat])
    return 0.0

  # あるカテゴリ中のアイテムたちの数
  def catcount(self, cat):
    if cat in self.cc:
      return float(self.cc[cat])
    return 0

  # アイテム達の総数
  def totalcount(self):
    return sum(self.cc.values())

  # すべてのカテゴリのたちのリスト
  def categories(self):
    return self.cc.keys()

  def train(self, item, cat):
    features=self.getfeatures(item)
    # このカテゴリの中の特徴たちのカウントを増やす
    for f in features:
      self.incf(f,cat)
    # このカテゴリのカウントを増やす
    self.incc(cat)

  def fprob(self, f, cat):
    if self.catcount(cat)==0: return 0
    # このカテゴリ中にこの特徴が出現する回数を、このカテゴリ中のアイテムの総数で割る
    return self.fcount(f, cat)/self.catcount(cat)

  def weightedprob(self, f, cat, prf, weight=1, ap=0.5):
    # 現在の確率を計算する
    basicprob=prf(f, cat)

    #この特徴が全てのカテゴリ中に出現する数を数える
    totals = sum([self.fcount(f,c) for c in self.categories()])

    # 重み付けした平均を計算
    bp=((weight*ap)+(totals*basicprob))/(weight+totals)
    return bp

class naivebayes(classifier):
  def __init__(self, getfeatures):
    classifier.__init__(self, getfeatures)
    self.thresholds={}

  def setthreshold(self, cat, t):
    self.thresholds[cat] = t

  def getthreshold(self, cat):
    if cat not in self.thresholds: return 1.0
    return self.thresholds[cat]

  def docprob(self, item, cat):
    features = self.getfeatures(item)
    # すべての特徴の確率を掛け合わせる
    p=1
    for f in features: p*=self.weightedprob(f, cat, self.fprob)
    return p

  def prob(self, item, cat):
    catprob=self.catcount(cat)/self.totalcount()
    docprob=self.docprob(item, cat)
    return docprob*catprob

  def classify(self, item, default=None):
    probs={}
    # もっとも確率の高いカテゴリを探す
    max = 0.0
    for cat in self.categories():
      probs[cat]=self.prob(item, cat)
      if probs[cat]>max:
        max=probs[cat]
        best=cat

    # 確率がしきい値 *2番目にベストなものを超えているか確認する
    for cat in probs:
      if cat==best: continue
      if probs[cat]*self.getthreshold(best)>probs[best]: return default
    return best

class fisherclassifier(classifier):
  def __init__(self, getfeatures):
    classifier.__init__(self,getfeatures)
    self.minimums={}

  def setdb(self, dbfile):
    self.con=sqlite.connect(dbfile)
    self.con.execute('create table if not exists fc(feature, category, count)')
    self.con.execute('create table if not exists cc(category, count)')

  def setminimum(self, cat, min):
    self.minimums[cat] = min

  def getminimum(self, cat):
    if cat not in self.minimums: return 0
    return self.minimums[cat]

  def classify(self, item, default=None):
    # もっともよい結果を探してループする
    best  = default
    max   = 0.0
    for c in self.categories():
      p = self.fisherprob(item, c)
      # 下限値を超えていることを確認する
      if p>self.getminimum(c) and p>max:
        best  = c
        max   = p
    return best

  def cprob(self, f, cat):
    # このカテゴリの中でのこの特徴の頻度
    clf=self.fprob(f, cat)
    if clf==0: return 0
    # すべてのカテゴリ中でのこの特徴の頻度
    freqsum=sum([self.fprob(f,c) for c in self.categories()])
    # 確率はこのカテゴリでの頻度を全体の頻度で割ったもの
    p=clf/(freqsum)
    return p

  def fisherprob(self, item, cat):
    # すべての確率を掛け合わせる
    p=1
    features=self.getfeatures(item)
    for f in features:
      p*=(self.weightedprob(f, cat, self.cprob))
    # 自然対数をとり-2を掛け合わせる
    fscore = -2*math.log(p)
    # 関数 chi2の逆数を利用して確率を得る
    return self.invchi2(fscore, len(features)*2)

  def invchi2(self, chi, df):
    m = chi / 2.0
    sum = term = math.exp(-m)
    for i in range(1, df/2):
      term *= m/i
      sum += term
    return min(sum, 1.0)
