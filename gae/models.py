# -*- coding: utf-8 -*-

from google.appengine.ext import db


class User(db.Model):
    u"""ユーザ情報
    key_name… user_id"""
    # TwitterUserID
    user_id = db.IntegerProperty()
    # デマ数
    dema_count = db.IntegerProperty()
    # デマ率（発言数におけるデマ率）
    dema_ratio = db.IntegerProperty()
    # 登録日時
    created_at = db.DateTimeProperty(auto_now_add=True)
    # 更新日時
    updated_at = db.DateTimeProperty(auto_now=True)
    
    #v1用(deprecated)
    # 生成(初回アクセス)日時
    date = db.DateTimeProperty(auto_now_add=True)
    # ユーザ確認トークン(ランダムキー)
    token = db.StringProperty()
    # トークンの長さ
    #TOKEN_LENGTH = 20

class Reporter(db.Model):
    u"""デマ通報者
    key_name… Userのkey_nameと同一"""
    # 登録日時
    created_at = db.DateTimeProperty(auto_now_add=True)
    # 更新日時
    updated_at = db.DateTimeProperty(auto_now=True)
    # Userエンティティ
    user = db.ReferenceProperty(User)

class Tweet(db.Model):
    u"""ツイート情報
    key_name… tweet_id"""
    # 作成日時
    created_at = db.DateTimeProperty(auto_now_add=True)
    # 更新日時
    updated_at = db.DateTimeProperty(auto_now=True)
    # ツイート日時
    tweeted_at = db.DateTimeProperty()
    # ツイートID(key_nameと同一)
    tweet_id = db.IntegerProperty()
    # 発言者Userエンティティ
    user = db.ReferenceProperty(User)
    # 本文
    tweet = db.StringProperty()
    # デマ報告数
    dema_count = db.IntegerProperty(default=0)
    # 非デマ報告数
    non_dema_count = db.IntegerProperty(default=0)
    # スコア
    dema_score = db.FloatProperty(default=0.0)
    
    #v1用(deprecated)
    # ツイートID
    tweetid = db.StringProperty()
    # レポート件数
    count = db.IntegerProperty()
    # ツイート日時
    createdat = db.DateTimeProperty()
    # 発言者のスクリーンネーム
    screen_name = db.StringProperty()
    # 発言者のユーザ名
    user_name = db.StringProperty()

    def get_jst(self):
        from datetime import timedelta
        return self.tweeted_at + timedelta(hours=9)

    def set_dema_cnt(self, dema_count_delta, non_dema_count_delta):
        self.dema_count += dema_count_delta
        self.non_dema_count += non_dema_count_delta
        self.calc_dema_score()
    def calc_dema_score(self):
        bunbo = float(self.dema_count + self.non_dema_count)
        if  bunbo == 0.0:
            self.dema_score = bunbo
        else:
            self.dema_score = self.dema_count / bunbo

class Report(db.Model):
    u"""レポート(デマ通報)"""
    # 登録日時
    created_at = db.DateTimeProperty(auto_now_add=True)
    # 更新日時
    updated_at = db.DateTimeProperty(auto_now=True)
    # Reporterエンティティ
    reporter = db.ReferenceProperty(User)  # 後々Reporterに差し替える
    # Tweetエンティティ
    tweet = db.ReferenceProperty(Tweet)
    # デマフラグ
    dema_flag = db.IntegerProperty()

    #v1用(deprecated)
    # レポート日時
    date = db.DateTimeProperty(auto_now_add=True)
    # ユーザトークン
    token = db.StringProperty()
    # ツイートID
    tweetid = db.StringProperty()
