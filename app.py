# # Meet YAVA: your friend

import nltk
import warnings
import random
import string # to process standard python strings
import time
import _thread
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from win10toast import ToastNotifier

warnings.filterwarnings("ignore")

f=open('chatbot.txt','r',errors = 'ignore')
raw=f.read()
raw=raw.lower()# converts to lowercase

sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 

GREETING_INPUTS = ("halo", "hi", "salam", "hai", "oy","bot",'ay','hei')
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hai disana",'*dadah pake tangan virtual*','*senyum*', "halo", "aku senang kau berbicara denganku",'naon']
Confused_responses =['umm, itu privasi. saya gabisa jawab.',"maksudmu?",'maaf?', 'maksudnya?', 'tolong gunakan bahasa indonesia yang baik dan benar', 
                     'kau manusia, kok aku gak ngerti kau ngomong apa.', "maaf, aku gangerti kamu ngomong apa", 'apa?',
                     'hah', 'kursus bahasa indonesia gih.','bisa ngetik lebih baik tidak?']

def LemNormalize(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    #fungsi ini meremove punct yang ada di dict dan menghilangkan huruf kapital
    return [token for token in nltk.word_tokenize(text.lower().translate(remove_punct_dict))]

#Menjawab salam dari user
def greeting(sentence):
    """kalo input usernya menyapa, maka bakal disapa balik"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

# Generating response
def response(user_response): 
    Yava_response=''
    sent_tokens.append(user_response) #Ini ngeappend input user ke list yang dibuat dari chatbot.txt
    if 'apa itu fasilkom' in user_response or 'fasilkom adalah' in user_response or 'fasilkom' in user_response:
        Yava_response = Yava_response+sent_tokens[0]
        return Yava_response
    elif 'paralel untuk d3' in user_response or 'ekstensi' in user_response:
        Yava_response = Yava_response+sent_tokens[8]
        return Yava_response

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
        Yava_response=Yava_response+"{}".format(random.choice(Confused_responses))
        return Yava_response
    else:
        Yava_response = Yava_response+sent_tokens[idx]
        return Yava_response

def reminder(event, angka, waktu, timer):
    while timer>0:
        time.sleep(1) #ini fungsi yang bisa membuat disable program selama 1 detik
        timer-=1 #simulasi timer untuk detik
    toaster = ToastNotifier()  
    toaster.show_toast("Pengingat", "hei, ini udah {}.\nagenda kamu itu {}".format(angka+' '+waktu, ' '.join(event)), icon_path=None, duration=5)
    while toaster.notification_active(): time.sleep(0.1)

def main(user_response): #ini program utama yang menghandle chat dari user
    if(user_response!='bye'):
        if(user_response=='thanks' or user_response=='thank you' ):
            global flag
            flag=False
            print("YAVA: Sama sama..")
        else:
            if len(user_response)==0:
                print('YAVA:  {}'.format(random.choice(Confused_responses)))
            elif(greeting(user_response)!=None):
                print("YAVA: "+greeting(user_response))
            else:
                print("YAVA:", ''+response(user_response))
                sent_tokens.remove(user_response) #setelah selesai digunakan, input user akan dihapus dari list dan list siap digunakan kembali
    else:
        flag=False


print("YAVA: Namaku Yava. Aku bakal ngejawab pertanyaan tentang Fasilkom UI, tempat dimana pembuatku berkuliah yang ada di database ku.")
print('YAVA: Bot ini memiliki beberapa fitur\n\
      Fitur pengingat, "ingetin saya untuk (aktifitasmu) dalam (waktu) (menit atau jam)"\n\
      Kalau mau keluar, ketik bye!')
print('      Pesan pembuat: Yavabot ini tidak sempurna, ada kemungkinan jawaban dari bot tidak nyambung karena bot ini menggunakan metode cosine similarity.')

flag=True
while(flag==True):
    user_response = input('>>> ')
    user_response=user_response.lower()

    if 'ingetin saya untuk' in user_response:
        perintah=user_response.split()
        try:    
            if 'menit'==perintah[-1]:
                timer=int(perintah[-2])*60
            elif 'jam'==perintah[-1]:
                timer=int(perintah[-2])*3600
        except ValueError:
            print("YAVA: kau tahu, kau gabisa input angka desimal karena aku bilang begitu.")
            print("YAVA: input bilangan bulat, bukan desimal 'manoosia cerdas'.")
            continue
        acara=perintah[3:-3]
        angka=perintah[-2]
        jenis_waktu=perintah[-1]
    
        print("YAVA: oke, bakal diingetin buat {} dalam {} {}".format(' '.join(acara), angka, jenis_waktu))  
        _thread.start_new_thread(reminder,(acara, angka, jenis_waktu,timer)) #ini module biar timernya jalan terpisah sama program
    else:    
        main(user_response)

print("YAVA: Bye! sampai ketemu nanti.") 

# Code taken from https://github.com/parulnith/Building-a-Simple-Chatbot-in-Python-using-NLTK/blob/master/chatbot.py
# Modification has taken place, so this code is original
# Created by Muhammad Mudrik for TP4 Task
# Task to fullfill DDP1 Final Mini Project