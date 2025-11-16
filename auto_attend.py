from yunban import *

test=yunban("", "")
classlist=test.getclasslist()
students=test.getstulist(classlist[35]["uid"])
events=test.getevents(classlist[35]["roomUid"])
stu=test.serchstubyname("",students)
faketime=test.randomtime(events[2])
datenow=time.strftime('%Y-%m-%d', time.localtime())
print(test.attend(stu["name"],stu["uid"],stu["sid"],events[1],datenow,faketime,classlist[35]["uid"],classlist[35]["roomUid"]))
print("Attended")