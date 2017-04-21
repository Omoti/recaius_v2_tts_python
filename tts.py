# coding:utf-8
import requests
import json
import wave
import time
import os
import pyaudio
import configparser


def get_token():
    url = "https://api.recaius.jp/auth/v2/"
    func = "tokens"
    data = {
        'speech_synthesis' : {
            'service_id' : str(ini_file.get("recaius-tts", "id")),
            'password' : str(ini_file.get("recaius-tts", "password")),
        }
    }

    headers = {"Content-type": "application/json"}

    res = requests.post(
        url + func,
        data = json.dumps(data),
        headers = headers
    )

    if res.status_code != 201:
        print(res)
        print(res.text)
        raise

    return res.json()["token"]


def delete_token(token):
    url = "https://api.recaius.jp/auth/v2/"
    func = "tokens"
    headers = {
        "X-Token" : token
    }
    res = requests.delete(
        url + func,
        headers = headers
    )
    if res.status_code != 204:
        print(res)
        print(res.text)
        raise


def tts():
    url = "https://api.recaius.jp/tts/v2/"
    func = "plaintext2speechwave"
    headers = {
        "X-Token": token,
        "Content-type": "application/json"
    }

    data = {
        'user_name': str(ini_file.get("recaius-tts", "id") + "01"),
        'plain_text': str(ini_file.get("recaius-tts", "speech_text")),
        'lang': str(ini_file.get("recaius-tts", "lang")),
        'speaker_id': str(ini_file.get("recaius-tts", "speaker_id")),
        'codec': 'audio/x-linear'
    }

    # temporary audio data file
    audio_data_path = 'output.wav'

    # save response wav file.
    with open(audio_data_path, 'wb') as handle:
        res = requests.post(
            url + func,
            data=json.dumps(data),
            headers=headers
        )
        if res.status_code != 200:
            print(res)
            print(res.text)
            raise
        handle.write(res.content)

    # open wav file.
    wav = wave.open(audio_data_path, "rb")
    # create PyAudio instanse
    p = pyaudio.PyAudio()

    # define callback for playing audio
    def play_callback(in_data, frame_count, time_info, status):
        data = wav.readframes(frame_count)
        return (data, pyaudio.paContinue)

    # open stream.
    stream = p.open(format=p.get_format_from_width(wav.getsampwidth()),
                    channels=wav.getnchannels(),
                    rate=wav.getframerate(),
                    output=True,
                    stream_callback=play_callback)

    # play start.
    stream.start_stream()

    # waiting while playing audio.
    while stream.is_active():
        time.sleep(0.1)

    # When playback ends , stop and release the stream.
    stream.stop_stream()
    stream.close()
    wav.close()

    # close PyAudio
    p.terminate()

    # delete wav file
    os.remove(audio_data_path)


ini_file = configparser.ConfigParser()
ini_file.read("./config.ini")

token = get_token()

tts()

delete_token(token)
