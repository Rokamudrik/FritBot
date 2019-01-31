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
    str_input = event.message.text
    lst_input = str_input.lower().split()
    
    def balas(pesan):
        Fritbot.reply_message(
            event.reply_token,
            TextSendMessage(text=pesan))        

    def main_resp(msg):
        def LemNormalize(text):
            remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
            #fungsi ini meremove punct yang ada di dict dan menghilangkan huruf kapital
            return [token for token in nltk.word_tokenize(text.lower().translate(remove_punct_dict))]

        frit_response=''
        sent_tokens.append(user_response) #Ini ngeappend input user ke list yang dibuat dari chatbot.txt
        if 'apa itu fasilkom' in user_response or 'fasilkom adalah' in user_response or 'fasilkom' in user_response:
            frit_response = frit_response+sent_tokens[0]
            balas(frit_response)
        elif 'paralel untuk d3' in user_response or 'ekstensi' in user_response:
            frit_response = frit_response+sent_tokens[8]
            balas(frit_response)

        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
        tfidf = TfidfVec.fit_transform(sent_tokens)
        # TF IDF ini gunanya buat bikn statistik numerikal suatu kata untuk memberi 
        # gambaran seberapa seringnya kemunculan/berat kata itu dalam dokumen.
        # menghitungnya menggunakan rumus khusus
        
        vals = cosine_similarity(tfidf[-1], tfidf) 
        # Ini buat mencocokan antara kata input dari user(yang baru dimasukin ke list
        # (biar 'kata'nya juga ada bobot(dalam vektor))) dengan isi list
        # nanti hasil perintah ini berupa list yang isinya kecocokan setiap item list 
        # terhadap input user dalam besaran sudut, semakin mendekati 1 maka semakin mirip katanya.
        idx=vals.argsort()[0][-2]
        flat = vals.flatten() #di flatten karena hasilnya list dalem list
        flat.sort()
        req_tfidf = flat[-2] #lalu diambil index -2 karena setelah di sort hasil yg paling mirip ada di index itu(mendekati 1)
        
        if(req_tfidf==0): #Jika gaada yg mirip maka responnya gini
            frit_response+="{}".format(random.choice(Confused_responses))
            balas(frit_response)
        elif req_tfidf<=0.5:
            balas('Maaf, bisa tolong lebih diperdetil pertanyaannya?')
        else:
            frit_response += sent_tokens[idx]
            balas(frit_response)

    def greeting(sentence):
        """kalo input usernya menyapa, maka bakal disapa balik"""
        for word in sentence.split():
            if word.lower() in GREETING_INPUTS:
                return random.choice(GREETING_RESPONSES)

    def reminder(acara, angka, waktu, timer):
        while timer>0:
            time.sleep(1)
            timer-=1
        balas('Hey, ini udah {} {}.\n Sudah waktunya untuk {}'.format(angka, waktu, acara))       

    f = open('chatbot.txt', 'r', errors='ignore')
    raw = f.read()
    raw = raw.lower()
    sent_tokens = nltk.sent_tokenize(raw)

    if '/' in str_input:
        if lst_input[0]=='/reminder':
            #/reminder (aktivitasmu) dalam (waktu) (menit atau jam)
            try:
                if 'menit'==lst_input[-1]:
                    timer=float(lst_input[-2])*60
                elif 'jam'==lst_input[-1]:
                    timer=float(lst_input[-2])*3600
                else:
                    balas('tolong masukin menit atau jam ya!')
            except ValueError:
                balas('Eeeh, bingung akutu, input waktunya kan angka bukan huruf.\nUlang lagi!!')
                
            acara=lst_input[1:-3]
            angka=lst_input[-2]
            waktu=lst_input[-1]

            _thread.start_new_thread(reminder,(' '.join(acara), angka, waktu,timer)) #ini module biar timernya jalan terpisah sama program

        elif lst_input[0]=='/makna':
            kata=KBBI(' '.join(lst_input[1:]))
            balas(kata)
        elif lst_input[0]=='/contoh':
            kata=KBBI(' '.join(lst_input[1:]))
            temp=kata.arti_contoh
            for i in range(len(temp)):
                temp[i]+='\n'
            balas(''.join(temp))
        elif lst_input[0]=='/help':
            balas(about_txt)
        else:
            balas("Perintahnya salah!")

    else:
        if 'bye' in str_input:
            balas('Bye! sampai nanti.')
        elif ('terima kasih' or 'terimakasih' or 'thanks' or 'thankyou' in str_input)==False:
            balas('Sama sama...')
        elif len(str_input)<=1:
            balas(random.choice(Confused_responses))
        elif greeting(str_input) != None:
            balas(greeting(str_input))
        else:
            main_resp(str_input)
            sent_tokens.remove(str_input)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)