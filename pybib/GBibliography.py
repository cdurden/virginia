import Bibliography;
import BibEntry;
import BibTeX;
import string;

from Tkinter import *
from Tkconstants import *

#
# extend the Bibliography class to present a GUI interface
class GBibliography(Bibliography.Bibliography):
	def __init__(self, bib, root):
		self.bib = bib;

		self.root = root;

		# configure the grid layout manager
		root.columnconfigure(0, weight=1);
		root.columnconfigure(1, weight=2);
		root.columnconfigure(2, weight=2);
		#self.root.title(bib.getFilename());
		
		# create the widgets
		self.scrollbar = scrollbar = Scrollbar(root);

		# called with 2 floats
		self.lb1 = lb1 = Listbox(root,
				width=10,
				background="light blue",
				exportselection=0,
				selectmode=EXTENDED,
				yscrollcommand=self.scrollbar_set);
		self.lb2 = lb2 = Listbox(root,
				width=40,
				background="light blue",
				exportselection=0,
				selectmode=EXTENDED,
				yscrollcommand=self.scrollbar_set);
		self.lb3 = lb3 = Listbox(root,
				width=40,
				background="light blue",
				exportselection=0,
				selectmode=EXTENDED,
				yscrollcommand=self.scrollbar_set);

		lb1.grid(column=0, row=0, sticky=W+E);
		lb2.grid(column=1, row=0, sticky=W+E);
		lb3.grid(column=2, row=0, sticky=W+E);
		scrollbar.grid(column=3, row=0, sticky=N+S);

		# build the three list boxes
		for be in bib:
			lb1.insert(END, be.getKey());
			lb2.insert(END, be.getAuthors());
			lb3.insert(END, be.getTitle());

		scrollbar.config(command=self.scrollall);
		root.bind_class("Listbox", "<Button-1>", self.select);
		root.bind_class("Listbox", "<MouseWheel>", self.blah);
		lb1.bind("<MouseWheel-0>", self.blah);
		lb1.bind("<MouseWheel-1>", self.blah);
		lb1.bind("<MouseWheel-2>", self.blah);

	def blah(self):
		print "blah";

	def scrollbar_set(self, a1, a2):
		print "in scrollbar_set", a1, a2
		self.scrollbar.set(a1, a2);
		#self.scrollall(a1, a2);


	def select(self, event):
		sel = self.lb1.nearest(event.y);
		self.lb1.select_clear(sel);
		self.lb1.select_set(sel);
		self.lb2.select_clear(sel);
		self.lb2.select_set(sel);
		self.lb3.select_clear(sel);
		self.lb3.select_set(sel);

	# scrollbar adjusts all the listboxes
	def scrollall(self, *args):
		print "scrollall", args
		apply( self.lb1.yview, args);
		apply( self.lb2.yview, args);
		apply( self.lb3.yview, args);

	def bind(self, event, func):
		print "in bind"
		self.root.bind_class("Listbox", event, func);
