# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import errno
import os
import sys
import cv2
from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, SourceUser, TemplateSendMessage, ConfirmTemplate, MessageAction, PostbackAction, ImageSendMessage, PostbackEvent)

# DB関連機能の読み込み
from DB.db import *
import urllib.parse

# 温湿度計機能の読み込み
from nekonisi_dht11.app import *

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_admin_user_id = os.getenv('LINE_ADMIN_USER_ID', None)

if channel_secret is None or channel_access_token is None or line_admin_user_id is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN, LINE_ADMIN_USER_ID as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    #1 Some Request
    # 認証機能
    if isinstance(event.source, SourceUser):
        #2 check users
        user_id = event.source.user_id
        # 3 result
        user = session.query(User).filter(User.user_id == user_id).first()
        session.close()
    else:
        pass
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="[Error]プロフィール情報が取得できませんでした。"))
    
    if user is None:
        # User is not authenticated
        # 4 Message
        confirm_template = ConfirmTemplate(text='あなたは未認証のユーザです。管理者に認証リクエストを送信しますか？', actions=[
            PostbackAction(
                label='はい',
                data='action=auth&user_id=' + user_id
            ),
            PostbackAction(
                label='いいえ',
                data='action=bye&user_id=' + user_id
            ),
        ])
        template_message = TemplateSendMessage(
            alt_text='認証確認', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    else:
        # User is Authenticated
        # Do Action
        pass

    text = event.message.text

    if text == '写真撮影する':
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text="写真を撮るよ！はいチーズ！")
        )
        url = take_photo()
        if url:
            url = request.url_root + '/static/photo.png'
            app.logger.info("url=" + url)
            line_bot_api.push_message(
                event.source.user_id,
                ImageSendMessage(url, url)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='写真撮影に失敗しちゃいました！')
            )
        # センサーのオブジェクトをインスタンス化
        dht11 = Dht11(4, 10)
        result = dht11.getTempeatureAndHumidity()
        if result:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='温度: ' + str(result[0]) + ' 湿度: ' + str(result[1]))
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='気温と温度の取得は失敗しちゃいました！')
            )
    else:
        line_bot_api.push_message(
            line_admin_user_id,
            TextSendMessage(text=text)
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    # postbackのデータ解析
    qs_d = urllib.parse.parse_qs(event.postback.data)
    action = qs_d['action'][0]
    user_id = qs_d['user_id'][0]
    if action == 'auth':
        line_bot_api.push_message(
            user_id, TextSendMessage(text='管理者宛に認証リクエストを申請しました。ちょっと待ってね'))
        # User is not authenticated
        # 7 Message
        confirm_template = ConfirmTemplate(text=line_bot_api.get_profile(user_id).display_name + 'から認証リクエストきたけど認証しちゃう？', actions=[
            PostbackAction(
                label='はい',
                data='action=auth_yes&user_id=' + user_id
            ),
            PostbackAction(
                label='いいえ',
                data='action=auth_no&user_id=' + user_id
            ),
        ])
        template_message = TemplateSendMessage(
            alt_text='認証確認', template=confirm_template)
        line_bot_api.push_message(line_admin_user_id, template_message)
    elif action == 'bye':
        # 6 Message
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='bye!'))
    elif action == 'auth_no':
        # [Admin's Answer is "No"]
        line_bot_api.push_message(user_id, TextSendMessage(text="ごめん。あかんってさ"))
    elif action == 'auth_yes':
        # [Admin's Answer is "Yes"]
        user = User(name=line_bot_api.get_profile(user_id).display_name, user_id=user_id)
        session.add(user) # insert処理
        try:
            session.commit()    # commit
        except:
            session.rollback()
            raise
        finally:
            session.close()
        line_bot_api.push_message(user_id, TextSendMessage(text="よかったね。承認されたみたいよ。"))


def take_photo():
    # 写真撮影
    cap = cv2.VideoCapture(0)
    res, frame = cap.read()
    if res:
        cv2.imwrite('./static/photo.png', frame)
    return res

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(
        'fullchain.pem', 'privkey.pem'
    )
    app.run(ssl_context=ssl_context, debug=options.debug, port=options.port, host="0.0.0.0")