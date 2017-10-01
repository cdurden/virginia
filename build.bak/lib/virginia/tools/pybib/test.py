import sys;
import os;

def test(cmd):
	print "testing:", cmd
	stat = os.system(cmd);
	if stat != 0:
		print "*****************************************"
		print "failed at", cmd
		sys.exit(0);
	
	
test('./bibcat p.bib > zz');
test('./bibcat p.bib | ./bibcat > zz');
test('./bibcat --ignore p.bib p.bib | ./bibcat > zz');

test('./bibcat p.bib | ./bib2html --highlight Corke  > zz');
test('./bibcat p.bib | ./bibdvi');

test('./bibcat p.bib | ./bibkey --key bob1 --key bob2 --aux test.aux | ./bibcat > zz');
test('./bibcat p.bib | ./bibfilter --hasfield year --field author Corke --since 7/1988 --before 1/2006 | ./bibcat > zz');

test('./bibcat p.bib | ./biblint > zz');

test('./bibcat p.bib | ./biblist > zz');
test('./bibcat p.bib | ./biblist --brief > zz');

test('./bibgoogle p1.bib | ./bibcat > zz');

test('./bibmerge p.bib p50.bib | ./bibcat > zz');

test('./bibcat p.bib | ./bibnames | sort +1 -n > zz');

test('./bibcat p.bib | ./bibsort | ./bibcat > zz');
test('./bibcat p.bib | ./bibsort --reverse | ./bibcat > zz');

test('./bibcat p.bib | ./bibsummary  > zz');
