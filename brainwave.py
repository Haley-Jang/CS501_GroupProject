'''
Author: Zhiyu Yang
Last modified: 09/13/2018

This moudle is for translating brainwave to midi music

	- tested for txt coded brainwave signals.
	- works but quite messy output
	- new update with svd denoising (15%)
'''


#########loading data function needed
import numpy as np
from midiutil.MidiFile import MIDIFile
from numpy.linalg import svd  #try to use svd to denoise the data before transformation
#--------

def brainwave_to_melody(_filename, _nChannal, _sampleRate):

	filename = _filename
	nChannal = _nChannal
	SampleRate = _sampleRate

	data = np.loadtxt(filename,delimiter = ",")

	[a,b] = data.shape
	for i in range (0,a):
		data[i,:] = data[i,:] - np.mean(data[i,:])  #this step is self-defined by Zhiyu, lift the basedline to get more positive data points and increase the variaty of music; normalize before denoising

	[u,s,v] = svd(data,full_matrices=False)
	s = np.array(list(map(lambda x:0 if x <= np.percentile(s,15) else x,list(s))))  #remove last 10% as noise
	s = np.diag(s)
	data = np.matmul(np.matmul(u,s),v)

	data = data[nChannal,:]

	#data = data - np.mean(data)

	#------------

	length = len(data)
	sign = np.sign(data)
	pot = np.flatnonzero(sign) #need verification
	NoteOn = []

	#----------------------------
	for i in range(0,length):
		if sign[i] >= 0:
			NoteOn.append(1)
		else:
			NoteOn.append(0)

	Time = [0] #need verification. The assignment of Time[] in the original .m starts from Time[1], hence a random value is given to Time[0]

	#----------------------------
	for i in range(1,length):
		if ((NoteOn[i-1] == 0) and (NoteOn[i] == 1)):
			Time.append(1)
		else:
			Time.append(0)

	#----------------------------
	Timefb = np.flatnonzero(np.array(Time))
	Timefb1=Timefb[:-1];
	Timefb2=Timefb[1:];
	nTime = Timefb2 - Timefb1

	duration = np.divide(nTime,SampleRate,dtype = "float")
	freq = np.divide(SampleRate,nTime,dtype = "float") #need to be elementwise operation, varification needed
	#works

	#----------------------------
	nAl = []
	nMark = []
	for i in range(0,len(nTime)):
		elem = max(data[Timefb[i]:(Timefb[i+1]+1)]) - min(data[Timefb[i]:(Timefb[i+1]+1)])
		nAl.append(elem)
	#	nAl[i] = nAl[i]*0.5
		nMark.append(max(data[Timefb[i]:(Timefb[i+1]+1)]))

	#-----------------------------
	#nX = []
	pit = []
	for i in range(0,len(nTime)):
		if ((nAl[i] > 1) and (nAl[i] < 200)):
			if freq[i] > 10:
				alpha = 1.50
				elem = 96 - round(40/alpha * np.log10(nAl[i]))
			else:
				alpha = 0.48
				elem = 109 - round((40/alpha * np.log10(nAl[i]))/190 * 84)
			pit.append(elem)
		elif (nAl[i] <= 1):
			pit.append(96)
		elif (nAl[i] >= 200):
			pit.append(24)

	pit = list(map(int,pit))
	#	nX0 = []
	#	for j in range(0,nTime[i]):
	#		nX0.append(pit[i]) ##nX0 is an array
	#	nX.extend(nX0) ## need varification, need to be flat array

	#tmp = list(np.zeros(Timefb[0]-1))
	#tmp.extend(nX)
	#tmp.extend(np.zeros(length-Timefb[-1]+1))
	#nX = tmp

	#----------------------------
	Ap = []
	for i in range(0,len(nTime)):
		w = data[Timefb1[i]:(Timefb2[i]+1)]
		Ap.append(np.mean(np.power(w,2)))

	ApD = [1]
	ApD.extend(np.diff(Ap))
	ApD1 = np.multiply(np.log10(np.absolute(ApD)),np.sign(ApD),dtype = "float")
	Vol = list(map(lambda x: x+64,np.multiply(ApD1,16)))

	for i in range(0,len(nTime)):
		if Vol[i] > 127:
			Vol[i] = 127
		elif Vol[i] < 1:
			Vol[i] = 1

	Vol = list(map(int,Vol))

	#-----------------------------
	#nMat = np.zeros(len(nTime),7)
	tStart = [0]
	for i in range(0,len(nTime)):
		tStart.append(tStart[i]+duration[i])

	tempo = 120
	Tb = np.multiply(tStart,tempo/60,dtype = "float")
	Db = np.multiply(duration,tempo/60,dtype = "float")
	#nMat[:,0] = Tb[:-2];
	#nMat[:,1] = Db;
	#nMat[:,2] = 1;
	#nMat[:,3] = pit;
	#nMat[:,4] = Vol;
	#nMat[:,5] = tStart[:-2];
	#nMat[:,6] = duration;
	#all info recorded but not necessary

	out_midi = MIDIFile(1)
	track = 0
	channel = 0
	time = 0
	out_midi.addTrackName(track, time, "brainwave track")
	out_midi.addTempo(track, time, tempo)

	for i in range(0,len(nTime)):
		out_midi.addNote(track, channel, pit[i], tStart[i], duration[i], Vol[i])

	filename = "Brainwave_channal"+str(nChannal+1)+"_SR"+str(SampleRate)+".mid"
	with open(filename, 'wb') as file:
		out_midi.writeFile(file)

	out_midi.close()

	return filename
