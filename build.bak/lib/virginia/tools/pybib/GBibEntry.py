import Bibliography;
import BibEntry;
import BibTeX;
import string;

from Tkinter import *
from Tkconstants import *

class GBibEntry(BibEntry.BibEntry):
	def __init__(self, top):
		self.top = top;

	def display(self, be):
		be.display();

		top = self.top;
		#top.title(be.getKey())

		row = 0;

		for f in BibEntry.required_fields[be.getType()]:
			l = Label(top, text=f, justify=RIGHT);
			l.grid(row=row, column=0, sticky=E);
			#Entry(top, text=be.getField(f)).grid(row=row, column=1);
			e = Entry(top, width=80, background="yellow")
			e.grid(row=row, column=1);

			if f in be:
				if f == 'Author':
					e.insert(INSERT, string.join( be.getField(f), " and "))
				else:
					e.insert(INSERT, be.getField(f))
			row = row+1;
		for f in BibEntry.opt_fields[be.getType()]:
			l = Label(top, text=f, justify=RIGHT);
			l.grid(row=row, column=0, sticky=E);
			#Entry(top, text=be.getField(f)).grid(row=row, column=1);
			e = Entry(top, width=80, background="white")
			e.grid(row=row, column=1);

			if f in be:
				e.insert(INSERT, be.getField(f))
				#e.insert(INSERT, "text")
			row = row+1;
