# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 22:16:19 2015

@author: Diana
"""

#!/usr/bin/env python3.4

print("/nContent-Type: text/html\n\n")
print("")

import cgi

print('<html>')

print('<body>')
print('<form action=\'http://students.hi.gmu.edu/cgi-bin/dciricea/interactive2.cgi\'>')
print('<br>how many: <input type=text name=val></input><br>')
print('what color: <input type=text name=color></input><br>')
print('<input type=submit name=Submit/>')
print('</form>')
print('</body>')

form = cgi.FieldStorage()
val = form.getvalue("val", 1)
col = form.getvalue("color","black")

#print ('val is : ' + val +'<br>')
max = int(val)

for i in range(max):
   print('bla','<font color='+col+'>'+str(i)+'</font><br>')

print ('</html>')
