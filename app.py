# mybot/app.py

import os

from kbbi import KBBI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import random
import string
import time
import _thread

from decouple import config
from flask import (
    Flask, request, abort
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
app = Flask(__name__)
# get LINE_CHANNEL_ACCESS_TOKEN from your environment variable
Fritbot = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))

# get LINE_CHANNEL_SECRET from your environment variable
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

about_txt = ("Fritbot\n"
             "Namaku Frit. Aku bakal ngejawab pertanyaan tentang Fasilkom UI," 
             " tempat dimana pembuatku berkuliah yang ada di database ku.\n"
             "Aku juga memiliki beberapa fitur, yakni: \n"
             '  -Pengingat\n "/reminder (aktifitasmu) dalam (waktu) (menit atau jam)"\n\n'
             '  -Mengartikan kata menurut KBBI\n\
                 "/makna (kata yang anda ingin artikan)"\n\n'
             '  -Mengartikan sekaligus contoh penggunaan\n\
                 "/contoh (kata yang anda inginkan)\n\n'
             '  -Bantuan /tulung\n'
             ' Pesan pembuat: Fritbot ini tidak sempurna, ada kemungkinan jawaban dari bot\
               tidak nyambung karena bot ini menggunakan metode cosine similarity.'
            )

GREETING_INPUTS = ("halo", "hi", "salam", "hai", "oy","bot",'ay','hei')
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hai disana",'*dadah pake tangan virtual*','*senyum*', "halo", "aku senang kau berbicara denganku",'naon']
Confused_responses =['umm, itu privasi. saya gabisa jawab.',"maksudmu?",'maaf?', 'maksudnya?', 'tolong gunakan bahasa indonesia yang baik dan benar', 
                     'kamu pake bahasa indonesia kan? kok aku gak ngerti kamu ngomong apa.', "maaf, aku gangerti kamu ngomong apa", 'apa?',
                     'hah?', 'kursus bahasa indonesia gih.','bisa ngetik lebih baik tidak?']

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    textlul=event.message.text
    user_input=textlul.lower().split()
    def balas(pesan):
        Fritbot.reply_message(
            event.reply_token,
            TextSendMessage(text=pesan))        

    def reminder(acara, angka, waktu, timer):
        while timer>0:
            time.sleep(1)
            timer-=1
        balas('Hey, ini udah {} {}.\n Sudah waktunya untuk {}'.format(angka, waktu, acara))       

    if '/' in user_input:
        if user_input[0]=='/reminder':
            #/reminder (aktivitasmu) dalam (waktu) (menit atau jam)
            try:
                if 'menit'==user_input[-1]:
                    timer=float(user_input[-2])*60
                elif 'jam'==user_input[-1]:
                    timer=float(user_input[-2])*3600
            except ValueError:
                balas('Eeeh, bingung akutu, input waktunya kan angka bukan huruf.\nUlang lagi!!')
                
            acara=user_input[1:-3]
            angka=user_input[-2]
            waktu=user_input[-1]

            balas('Okeh, bakal aku ingetin buat {} dalam {} {}'.format(acara, angka, waktu))
            _thread.start_new_thread(reminder,(acara, angka, waktu,timer)) #ini module biar timernya jalan terpisah sama program

        elif user_input[0]=='/makna':
            kata=KBBI(user_input[1:])
            balas(kata)
        elif user_input[0]=='/contoh':
            kata=KBBI(user_input[1:])
            temp=kata.arti_contoh
            for i in range(len(temp)):
                temp[i]+='\n'
            balas(''.join(temp))
        elif user_input[0]=='/help':
            balas(about_txt)
        else:
            balas("Perintahnya salah!")

    else:
        balas(textlul)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)