import sys
sys.path.append('.')
from yunabn_token import *

classlist=test.getclasslist()
students=test.getstulist(classlist[35]["uid"])
events=test.getevents(classlist[35]["roomUid"])
uidlist=[]
for stu in students:
    # stu=test.serchstubyuid(uid,students)
    try:
        if sys.argv[1]:
            event=events[int(sys.argv[1])]
        else:
            event=events[1]
    except:
        event=events[1]
    # print(sys.argv[1])
    faketime=test.randomtime(event)
    datenow=time.strftime('%Y-%m-%d', time.localtime())
    timenow=time.strftime('%H:%M:%S', time.localtime())
    print(test.attend(stu["name"],stu["uid"],stu["sid"],event,datenow,faketime,classlist[35]["uid"],classlist[35]["roomUid"]))
    print(f"{stu["name"]}已签到，时间：{datenow} {faketime}")