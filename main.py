import os
import csv
import shutil
import pydub 
import moviepy.editor
from pydub import AudioSegment
import wave
import matplotlib.pyplot as plt
import numpy as np
import pyfiglet
import termcolor

#Recusively looks for all files in a given directory, and returns a list with a file path to them
def getFilesInFolder(k):
    ret = []
    for filename in os.listdir(k):
        f = os.path.join(k, filename)
        # checking if it is a file
        if os.path.isfile(f):
            ret+=[f]
        else:
            ret+=getFilesInFolder(f)
     
    return ret

#print start up message
print("="*55) 
f = pyfiglet.Figlet(font = "standard")
print(termcolor.colored(f.renderText("PYthagoras"),'light_magenta'))
print("UB acoustical audio analysis research".center(55))
print("="*55) 
dir_path = os.path.dirname(os.path.realpath(__file__))

#Controls some of the optional print statements
verbose = True

#Get a list of files paths to all audio files inside InputAudioData
try:
    nonDem = getFilesInFolder(dir_path+'/InputAudioData/Non_DementiaFiles')
except:
    print("Non dem Files not found")
    nonDem=[]

try:    
    Dem = getFilesInFolder(dir_path+'/InputAudioData/DementiaFiles')
except:
    print("Dem Files not found")
    Dem = []

#Create empty directorys for output data
if os.path.exists(dir_path+'/non_dem_output'):
    shutil.rmtree(dir_path+'/non_dem_output')
os.makedirs(dir_path+'/non_dem_output')
if os.path.exists(dir_path+'/dem_output'):
    shutil.rmtree(dir_path+'/dem_output')
os.makedirs(dir_path+'/dem_output')






#runs through all files, and generates data
loopData = [[nonDem,'non_dem_output','/InputAudioData/Non_DementiaFiles'],[Dem, 'dem_output','/InputAudioData/DementiaFiles']]

for loop in loopData:
    for audio in loop[0]:
        file_name = os.path.basename(audio)
        file = os.path.splitext(file_name)
        file_location = audio.removeprefix(dir_path+loop[2])
        file_type = file[1]
        wavFile = dir_path+'/'+loop[1]+'/'+file[0]+"/"+file[0]+".wav"
        os.makedirs(dir_path+'/'+loop[1]+'/'+file[0])
        f = open(dir_path+'/'+loop[1]+'/'+file[0]+"/filedata.txt", "a")
        csvGen = open(dir_path+'/'+loop[1]+'/'+file[0]+"/genData.csv", "a")
        csvWriter = csv.writer(csvGen)
        f.write("The file came from: "+ file_location)
        #convert the file to a .wav if needed, and then copy the .wav to be part of the output
        if(file_type == ".wav"):
            if(verbose): print("Native Wave File:" + dir_path+'/'+loop[1]+'/'+file[0]+"/"+file_name)
            shutil.copyfile(audio, dir_path+'/'+loop[1]+'/'+file[0]+"/"+file_name)
        elif(file_type == ".mp3"):
            if(verbose): print("Converting Mp3 File:" + dir_path+'/'+loop[1]+'/'+file[0]+"/"+file_name)
            sound = pydub.AudioSegment.from_mp3(audio)
            sound.export(wavFile, format="wav")
        elif(file_type == ".mp4"):
            if(verbose): print("Converting Mp4 File:" + dir_path+'/'+loop[1]+'/'+file[0]+"/"+file_name)
            video = moviepy.editor.VideoFileClip(audio, verbose=verbose ,)
            #Extract the Audio
            audio = video.audio
            #Export the Audio
            if(verbose):
                audio.write_audiofile(wavFile)
            else:
                audio.write_audiofile(wavFile,logger=None)
        elif(file_type == ".cha"):
            if(verbose): print("Converting .cha File:" + dir_path+'/'+loop[1]+'/'+file[0]+"/"+file_name)
            print(".cha handiling not yet implement")

        #to get initailized later
        n_channels=0
        #Check is file audio is steore or not, and if so convert it to 
        with AudioSegment.from_file(file=wavFile, format="wav") as conversion:
            n_channels = conversion.channels
            if(n_channels>1):
                sound = AudioSegment.from_wav("stereo.wav")
                sound = sound.set_channels(1)
                sound.export(wavFile, format="wav")

        #Open the wave file and start reading from it
        with wave.open(wavFile) as input:
            #Read basic informaiton from the wavefile
            
            f.write("_"*15)
            f.write("Number of channels  - "+ str(n_channels) )
            sample_width = input.getsampwidth()
            f.write("Sample Width - "+ str(sample_width))
            sample_freq = input.getframerate()
            f.write("Frame rate  - "+ str(sample_freq))
            n_samples = input.getnframes()
            f.write("Number of Frames  - "+ str(n_samples))
            t_audio = round(n_samples/sample_freq,3)
            f.write("lenght of Audio sample - " + str(t_audio) )
            f.write("Compression type  - "+ str(input.getcompname()) + " --- Orignal file type: "+ file[1])

            csvWriter.writerow([n_channels,sample_width,sample_freq,n_samples,t_audio])
            
            signal_wave = input.readframes(n_samples)
            signal_array = np.frombuffer(signal_wave, dtype=np.int16)
            times = np.linspace(0, n_samples/sample_freq, num=n_samples)

            plt.figure(figsize=(15, 5))
            plt.plot(times, signal_array)
            plt.title('Signal Amplitude')
            plt.ylabel('Signal Value')
            plt.xlabel('Time (s)')
            plt.xlim(0, t_audio)
            plt.savefig("test.png")

            plt.figure(figsize=(15, 5))
            spectrum, freqs, t, im = plt.specgram(signal_array, Fs=sample_freq)
            plt.title('Frequency Spectrum')
            plt.ylabel('Frequency (Hz)')
            plt.xlabel('Time (s)')
            plt.xlim(0, t_audio)
            plt.colorbar(label ="dBFS")

            print(spectrum)

        f.close()


    