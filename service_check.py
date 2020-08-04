import json, sys
import subprocess
from os import  getcwd

try:
    with open(getcwd() +"./servicelist.json", "r") as fp:
        data = fp.read()

    srvc_d = json.loads(fp)
    srvc_list = srvc_d['service_list']
    
except Exception as ep:
    print "Error:== Reading config file and loading service list failed."
    print str(ep)
    sys.exit(1)

#srvc_d loaded successfully.
for el in srv_list:
    if isinstance(el, dict) :
        p = subprocess.Popen("netstat -panltu|awk '{print $4, $NF}' |grep %s |grep %s"%(el['name'],el['port']) , shell=True,
                     stdout= subprocess.PIPE ,stderr= subprocess.PIPE )
        o,e = p.communicate()
        ret = p.returncode
        if ret == 0 and el['name'] in str(o) :
            print "%s is running on %s port."%(el['name'], el['port'])
        elif e :
            print "unable to find process %s, error in checking service"%el['name']
        p.close()
    else:
        print "invalid format in service list, checking next element"
