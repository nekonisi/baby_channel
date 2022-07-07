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


import datetime
import errno
import json
import os
import sys
import tempfile
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
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_admin_user_id = os.getenv('LINE_ADMIN_USER_ID', None)

if channel_secret is None or channel_access_token is None or line_admin_user_id is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
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
    text = event.message.text

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + str(profile.status_message)),
                    TextSendMessage(text='User id: ' + event.source.user_id),
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == '写真撮影する':
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text="写真を撮るよ！はいチーズ！")
        )
        url = take_photo()
        if url:
            url = request.url_root + '/static/photo.png'
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(url, url)
            )
            # 気温と湿度を返却
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='気温と湿度')
            )
        else:
            # 気温と湿度を返却
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='写真撮影に失敗しちゃいました！')
            )
    elif text == 'confirm':
        confirm = ConfirmTemplate(text='新規ユーザを認証しますか？', actions=[
            MessageAction(label='はい', postback='yes'),
            MessageAction(label='いいえ', text='no'),
        ])
        confirm_message = TemplateSendMessage(
            alt_text='新規ユーザの認証', template=confirm)
        print(confirm_message)
        # if confirm_message == 'yes':
        #     pass
        #     # 認証データに追加
        # else:
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(text="認証が却下されました。nekonisi（こうすけ）に連絡してください。")
        #     )


        line_bot_api.push_message(line_admin_user_id, confirm_message)
    else:
        emojis = [
            {
                "index": 0,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "191"
            },
        ]
        text_message = TextSendMessage(text='$', emojis=emojis)
        line_bot_api.reply_message(
            event.reply_token, [
                text_message
            ]
        )


def take_photo():
    # 写真撮影
    cap = cv2.VideoCapture(0)
    res, frame = cap.read()
    if res:
        cv2.imwrite('./static/photo.png', frame)
    return res


@handler.add(FollowEvent)
def handle_follow(event):
    app.logger.info("Got Follow event:" + event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='nekonisiに認証されるまで待ってね'))


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

    app.run(debug=options.debug, port=options.port, host="0.0.0.0")