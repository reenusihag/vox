from __future__ import unicode_literals
import time
import ctypes
from google import google
import boto3
import speech_recognition as sr
import os
from playsound import playsound

from fbchat import Client
from fbchat.models import *
import requests
import webbrowser
import random


speech = sr.Recognizer()

greeting_dict = {'hello': 'hello', 'hi': 'hi'}
open_launch_dict = {'open': 'open', 'launch': 'launch'}
google_searches_dict = {'what': 'what', 'why': 'why', 'who': 'who', 'which': 'which'}
social_media_dict = {'facebook': 'https://www.facebook.com', 'youtube': 'https://www.youtube.com', 'google': 'https://www.google.com'}

mp3_thanktyou_list = ['mp3/friday/thankyou_1.mp3', 'mp3/friday/thankyou_2.mp3']
mp3_google_search = ['mp3/vox/google_search_1.mp3', 'mp3/vox/google_search_2.mp3']
mp3_greeting_list = ['mp3/vox/greeting_accept.mp3', 'mp3/vox/greeting_accept_2.mp3']
mp3_open_launch_list = ['mp3/vox/open_1.mp3', 'mp3/vox/open_3.mp3', 'mp3/vox/open_2.mp3']
mp3_listening_problem_list = ['mp3/vox/listening_problem_1.mp3', 'mp3/vox/listening_problem_2.mp3']
mp3_struggling_list = ['mp3/vox/struggling_1.mp3']


error_occurrence = 0
counter = 0

polly = boto3.Session( aws_access_key_id='enter your id here', aws_secret_access_key='enter your key here', region_name='ap-south-1').client('polly')

def play_sound_from_polly(result):
    global counter
    mp3_name = "output{}.mp3".format(counter)
    obj = polly.synthesize_speech(Text=result, OutputFormat='mp3', VoiceId='Joanna')
    play_sound(mp3_google_search)
    with open(mp3_name, 'wb') as file:
        file.write(obj['AudioStream'].read())
        file.close()

    playsound(mp3_name)
    os.remove(mp3_name)
    counter+= 1


def google_search_result(query):
    search_result = google.search(query)

    for result in search_result:
        print(result.description.replace('...', '').rsplit('.', 3)[0])
        if result.description != '':
            play_sound_from_polly(result.description.replace('...', '').rsplit('.', 3)[0])
            break

def is_valid_google_search(phrase):
    if (google_searches_dict.get(phrase.split(' ')[0]) == phrase.split(' ')[0]):
        return True

def play_sound(mp3_list):
    mp3 = random.choice(mp3_list)
    playsound(mp3)

def read_voice_cmd():
    voice_text = ''

    print('Listening...')

    global  error_occurrence


    try:
        with sr.Microphone() as source:
            audio = speech.listen(source=source, timeout=10, phrase_time_limit=5)
            voice_text = speech.recognize_google(audio)
    except sr.UnknownValueError:
        if error_occurrence == 0:
            play_sound(mp3_listening_problem_list)
            error_occurrence += 1
        elif error_occurrence == 1:
            play_sound(mp3_struggling_list)
            error_occurrence += 1

    except sr.RequestError as e:
        print('Network error.')
    except sr.WaitTimeoutError:
        if error_occurrence == 0:
            play_sound(mp3_listening_problem_list)
            error_occurrence += 1
        elif error_occurrence == 1:
            play_sound(mp3_struggling_list)
            error_occurrence += 1

    return voice_text

def is_valid_note(greet_dict, voice_note):
    for key, value in greet_dict.iteritems():
        try:
            if value == voice_note.split(' ')[0]:
                return True
                break
            elif key == voice_note.split(' ')[1]:
                return True
                break
        except IndexError:
            pass

    return False




if __name__=='__main__':

    playsound('mp3/vox/greeting.mp3')

    while True:

        voice_note = read_voice_cmd().lower()
        print('cmd:{}'.format(voice_note))

        if is_valid_note(greeting_dict, voice_note):
            print('In greeting.....')
            play_sound(mp3_greeting_list)
            continue

        elif is_valid_note(open_launch_dict, voice_note):
            print('print in open...')
            play_sound(mp3_open_launch_list)

            if (is_valid_note(social_media_dict, voice_note)):
                key = voice_note.split(' ')[1]
                webbrowser.open(social_media_dict.get(key))
            else:
                os.system('explorer C:\\"{}"'.format(voice_note.replace('open ', '').replace('launch', '')))
            continue

        elif is_valid_google_search(voice_note):
            print('i google search....')
            playsound('mp3/vox/search_1.mp3')
            google_search_result(voice_note)
            continue
        elif 'send message on facebook' in voice_note:
            client = Client('enter here user name', 'enter facebook password here')
            no_of_friends = 1;
            for i in xrange(no_of_friends):
                name = str(raw_input("Name: "))
                friends = client.searchForUsers(name, 5)  # return a list of names
                friend = friends[0]
                print(friend.uid)

                msg = str(raw_input("Message: "))
                sent = client.send(Message(text=msg), thread_id=friend.uid, thread_type=ThreadType.USER)
                if sent:
                    print("Message sent successfully!")
            client.logout()
            continue

        elif 'send message on whatsapp' in voice_note:
            from twilio.rest import Client
            a_sid ='ACce9b6e03e93f5fed9a8aa937b222c6e6'
            a_token ='enter twilio token here'

            client = Client(a_sid, a_token)

            message = client.messages.create(body='hello',from_='whatsapp:+14155238886',
                                        to = 'whatsapp:+919355242300')

            print(message.sid);
            continue

        elif 'find weather' in voice_note:

            play_sound_from_polly('Sir for which city?')
            voice_note = read_voice_cmd().lower()

            print voice_note

            base_url = "http://api.openweathermap.org/data/2.5/weather?"

            city_name = voice_note

            complete_url = base_url + "appid=" + "6c67dd2fd1ea20a77be253dcbb923496" + "&q=" + city_name

            response = requests.get(complete_url)

            x = response.json()

            if x["cod"] != "404":

                y = x["main"]

                current_temperature = y["temp"]

                current_pressure = y["pressure"]

                current_humidiy = y["humidity"]

                z = x["weather"]

                weather_description = z[0]["description"]

                play_sound_from_polly(" Temperature (in kelvin unit) = " +
                      str(current_temperature) +
                      "\n atmospheric pressure (in hPa unit) = " +
                      str(current_pressure) +
                      "\n humidity (in percentage) = " +
                      str(current_humidiy) +
                      "\n description = " +
                      str(weather_description))

            else:
                play_sound_from_polly(" City Not Found ")
            continue

        elif 'latest news' in voice_note:

            contents = requests.get("https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=ace7c1fca4544f4f8b0bd6a31888e7d5").json()

            articles = contents['articles']
            count = 0
            for article in articles:
                play_sound_from_polly(article['title'] + article['content'])
                count += 1
                time.sleep(1)
                if (count == 3):
                    break

            continue

        elif 'lock' in voice_note:
            play_sound_from_polly('Sure sir')
            for value in ['pc', 'system', 'windows']:
                ctypes.windll.user32.LockWorkStation()
            play_sound_from_polly('Your system is locked.')
            continue

        elif 'thank you' in voice_note:
            play_sound_from_polly('You are welcome Sir');
            continue

        elif 'what\'s up' in voice_note:
            play_sound_from_polly('Just doing my thing')
            continue
        elif voice_note != '':
            play_sound_from_polly('command not found')
            continue

        elif 'bye' in voice_note:
            playsound('mp3/vox/bye.mp3')
            exit()
