import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
import sys
from opensimplex import OpenSimplex
import random
import pyaudio
import struct

class Mesh:
	def __init__(self):
		self.app = QtGui.QApplication(sys.argv)
		self.view = gl.GLViewWidget()
		self.view.show()
		self.view.setWindowTitle('Audioflexica Codeology Spring 2018')
		self.noise = OpenSimplex()
		self.offSet = 0

		# Audio
		self.RATE = 16000 #44100
		self.CHUNK = 1024
		self.audioData = None
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK)

		# List of vertexes and faces, including a constant z value
		self.vertexesList, self.facesList = self.thirtyTwoGrid()
		self.vertexes = np.array(self.vertexesList)
		self.faces = np.array(self.facesList)

		# Lists of face colors and vertex colors
		faceColorList = self.makeFaceColor()
		self.faceColor = np.array(faceColorList)
		vertexColorList = self.makeVertexColor()
		self.vertexColor = np.array(vertexColorList)
		
		# List of vertexes, including a variable z value, intialized to an empty list
		self.movingVertexes = np.array([])

		# Create the GLMeshItem
		self.mesh = gl.GLMeshItem(vertexes=self.movingVertexes, faces=self.faces, drawEdges=True, vertexColors=self.vertexColor)
		self.mesh.setGLOptions("additive")
		self.view.addItem(self.mesh)

	def run(self):
		if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
			QtGui.QApplication.instance().exec_()

	def update(self):
		# Read audio data from stream
		self.audioData = self.stream.read(self.CHUNK, exception_on_overflow=False)
		structTuple = struct.unpack("2048B", self.audioData)
		audio = []
		for i in range(1024):
			curr = structTuple[i * 2]
			audio.append(curr)

		# Update self.movingVertexes to list of vertices centered at 0, with a varying z value
		vertexesList = []
		for x in range(-16, 16):
			for y in range(-16, 16):
				i = (x + 16) * 10 + (y + 16)
				#* self.noise.noise2d(x=x+self.offSet, y=y+self.offSet)
				z = audio[i] * 0.007
				curr = [x, y, z]
				vertexesList.append([x, y, z])
		self.offSet = self.offSet - 0.1
		self.movingVertexes = np.array(vertexesList)

		# Update the mesh data
		gl.GLMeshItem.setMeshData(self.mesh, vertexes=self.movingVertexes, faces=self.faces, vertexColors=self.vertexColor)

	def animation(self):
		timer = QtCore.QTimer()
		timer.timeout.connect(self.update)
		timer.start(10)
		self.run()
		self.update()

	def thirtyTwoGrid(self):
		# Make list of vertices centered at 0
		vertexesList = []
		for x in range(-16, 16):
			for y in range(-16, 16):
				z = self.noise.noise2d(x=x, y=y)
				curr = [x, y, z]
				vertexesList.append(curr)

		# Make list of faces in pairs - two triangles create a square
		facesList = []
		for x in range(31):
			for y in range(31):
				p1 = (32 * x) + y
				p2 = (32 * x) + (y + 1)
				p3 = (32 * (x + 1)) + y
				facesList.append([p1, p2, p3])
				x2 = x + 1
				y2 = y + 1
				p1 = (32 * x2) + y2
				p2 = (32 * x2) + (y2 - 1)
				p3 = (32 * (x2 - 1)) + y2
				facesList.append([p1, p2, p3])
		return vertexesList, facesList

	def makeFaceColor(self):
		# Return a list of list of rgba values for each of the faces
		# There are 31*31*2 faces in total.
		c = []
		for i in range(31 * 31 * 2):
			c.append([1, 0, 0, 1])
		return c

	def makeVertexColor(self):
		# Return a list of list of rgba values for each of the vertices.
		# There are 32*32 vertices in total.
		c = []
		for i in range(32 * 32):
			blue = random.uniform(0.65, 1)
			green = random.uniform(max(0.4, 0.6), 1)
			red = random.uniform(max(0.1, 0.25), 0.1)
			c.append([red, green, blue, 1])
		return c

if __name__ == '__main__':
	mesh1 = Mesh()
	#mesh1.run()
	mesh1.animation()

