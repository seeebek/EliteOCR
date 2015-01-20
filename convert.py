import json
import codecs

with open ("list.txt", "r") as myfile:
    data=myfile.read()
    
with open ("commodities.json", "r") as jsonfile:
    jsondata=jsonfile.read()

com = json.loads(data)

full = json.loads(jsondata)

for i in com["x"]:
    full[i[0]]["deu"] = i[1]

#print full

file = codecs.open("commodities.json", 'w', "utf-8")
file.write(json.dumps(full, indent=2, separators=(',', ': '), ensure_ascii=False))
file.close()
