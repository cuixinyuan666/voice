'''Sidekick
Copyright (C) 2021 UT-Battelle - Created by Sean Oesch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''
from vosk import Model, KaldiRecognizer
import os
import json
import audioop
import string
import math
import threading
from parsepackage import *
from ui import SidekickUI

if not os.path.exists("model_cn"):
    print ("请下载中文模型 from https://alphacephei.com/vosk/models 并解压为 'model_cn' 在当前文件夹中.")
    exit (1)

import pyaudio

parser = parser.Parser() 
ui = None
is_paused = False

def listToList(words):
    wordlist = '['
    for word in words:
        wordlist = wordlist + "\"" + word + "\"" + ","
    wordlist = wordlist.strip(",") + "]"
    return wordlist

def setRec(state,crec,trec,arec):
    if state == "text":
        return trec
    elif state == "command" or state == "mouse":
        return crec
    else:
        return arec 

def clearRec(crec,trec,arec):
    crec.Result()
    trec.Result()
    arec.Result()

def stateSwap(nextstate,crec,trec,arec):
    rec = setRec(nextstate,crec,trec,arec)
    res = json.loads(rec.Result())
    swap = False
    if res["text"] != "":
        if swap:
            parser.ingest(res["text"]) 

        if res["text"] == nextstate:
            swap = True
    
    clearRec(crec,trec,arec)

def ingest(currentstate,crec,trec,arec):
    rec = setRec(currentstate,crec,trec,arec)
    res = json.loads(rec.Result()) # this not only returns the most accurate result, but also flushes the list of words stored internally
    if res["text"] != "":
        for text in res["text"].split(" "):
            if text in ["text","alpha","command"] and text != currentstate:
                parser.ingest(text)
                stateSwap(text,crec,trec,arec)
                # Update UI state
                if ui:
                    ui.update_state(parser.state)
                    ui.add_log_message(f"切换到{parser.state}模式", "成功")
            else:
                # Check if the command is a pause/resume command
                if text == "暂停":
                    parser.pause = True
                    parser.state = "文本"
                    if ui:
                        ui.update_state(parser.state)
                        ui.add_log_message("Sidekick 已暂停", "成功")
                        ui.paused = True
                        ui.start_pause_button.configure(text="开始")
                        ui.status_label.configure(text="状态: 已暂停")
                elif text == "开始" and len(res["text"].split(" ")) >= 2 and res["text"].split(" ")[1] == "工作":
                    parser.pause = False
                    parser.state = "命令"
                    if ui:
                        ui.update_state(parser.state)
                        ui.add_log_message("Sidekick 已开始工作", "成功")
                        ui.paused = False
                        ui.start_pause_button.configure(text="暂停")
                        ui.status_label.configure(text="状态: 等待指令")
                else:
                    # Execute the command and get status
                    original_buffer = parser.command_buffer.copy()
                    parser.ingest(text)
                    # Determine if the command was successful
                    status = "成功" if parser.command_buffer != original_buffer else "失败"
                    # Update UI log
                    if ui:
                        ui.add_log_message(f"识别: {text}", status)
        
    clearRec(crec,trec,arec)

def audio_processing():
    # create wordlist for our command model so that commands will be more accurately detected
    commandwords = listToList(parser.nontextcommands)
    alphavals = listToList(parser.alphavalues)

    model = Model("model_cn")
    # the text recommender uses the standard model for transcription
    textrec = KaldiRecognizer(model, 16000)
    # use wordlist in our command recommender
    commandrec = KaldiRecognizer(model, 16000, commandwords)
    alpharec = KaldiRecognizer(model, 16000, alphavals)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("\nSidekick 为您服务。请保持安静，等待基于环境噪音设置阈值。")

    threshold_buffer = 1 # how many dB above ambient noise threshold will be set
    thresholdset = False # whether or not threshold has been set
    threshcount = 0 # count that determines when threshold is set
    ambientvals = [] # Ambient noise level in dB is used to calculate appropriate threshold at which to send audio to vosk
    wait = False # after threshold breached, need to process the next 5-10 audio samples through the model even if they don't breach threshold 
    waittime = 0 # when to toggle wait from True to False 
    while True:
        # read in audio data
        data = stream.read(4000,exception_on_overflow = False)

        # calculate decibels
        dB = 20 * math.log10(audioop.rms(data,2))

        # Update UI volume
        if ui and thresholdset:
            # Normalize volume to 0-1 range
            normalized_volume = min(1.0, (dB - threshold) / 20)
            ui.update_volume(normalized_volume)

        # we want to set threshold based on ambient noise prior to processing audio data
        if not thresholdset: 
            ambientvals.append(int(dB))
            threshcount += 1
            if threshcount >= 10:
                thresholdset = True
                print("您的 Sidekick 现在等待您的指令。")
                threshold = sum(ambientvals) / len(ambientvals) + threshold_buffer
                print("阈值现在设置为 " + str(round(threshold,2)) + " dB。")
                # Update UI status
                if ui:
                    ui.status_label.configure(text="状态: 等待指令")
        
        # send audio data to model for processing when threshold breached and shortly afterward
        elif (dB > threshold or wait == True) and not is_paused:

            waittime += 1
            if dB > threshold:
                waittime = 0
                wait = True

            if waittime >= 8: # in my testing max wait time before word sent to parser was 6 - added a bit of buffer 
                wait = False

            trec = textrec.AcceptWaveform(data)
            crec = commandrec.AcceptWaveform(data)
            arec = alpharec.AcceptWaveform(data)

            if len(data) == 0:
                break
            if parser.state == "text":
                if trec: # if this returns true model has determined best word candidate
                    ingest(parser.state,commandrec,textrec,alpharec) 
                else: # if false only a partial result returned - not useful for this application
                    pass
                    #print(rec.PartialResult()) - partial result is faster, but not accurate enough for use
            
            elif parser.state == "alpha":
                if arec: # if this returns true model has determined best word candidate
                    ingest(parser.state,commandrec,textrec,alpharec)                 
            else:
                if crec: # if this returns true model has determined best word candidate
                    ingest(parser.state,commandrec,textrec,alpharec)

def main():
    global ui
    
    # Create UI instance
    ui = SidekickUI()
    
    # Start audio processing thread
    audio_thread = threading.Thread(target=audio_processing)
    audio_thread.daemon = True
    audio_thread.start()
    
    # Run UI loop
    ui.run()

if __name__ == "__main__":
    main() 