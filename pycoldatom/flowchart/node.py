import pyqtgraph.flowchart as pgfc

class Node(pgfc.Node):
	def saveState(self):
		"""Return a dictionary representing the current state of this node
		(excluding input / output values). This is used for saving/reloading
		flowcharts. The default implementation returns this Node's position,
		bypass state, and information about each of its terminals. 
		
		Subclasses may want to extend this method, adding extra keys to the returned
		dict."""
		pos = self.graphicsItem().pos()
		state = {'pos': (pos.x(), pos.y()), 'bypass': self.isBypassed()}
		termsEditable = self._allowAddInput | self._allowAddOutput
		for term in list(self._inputs.values()) + list(self._outputs.values()):
			termsEditable |= term._renamable | term._removable | term._multiable
		if termsEditable:
			state['terminals'] = self.saveTerminals()
		return state