import json,os,requests,sys,re
if len(sys.argv) < 2:
	print("Usage : earth.py <dir> \ndir: full-path-of-directory-to-store-images ; Ex : /Users/localuser/pic/")
	exit(1)
directory=sys.argv[1].strip()
os.chdir(directory)
f=open("img.json")
d=json.loads(f.read())
d=map(str,d["id"])
regex = re.compile("[^a-zA-Z0-9]")
for i in d:
	try:
		os.system("wget -q https://earthview.withgoogle.com/download/" + i + ".jpg")
		r=requests.get("https://www.gstatic.com/prettyearth/assets/data/"+i+".json")
		j=r.json()
		s=""
		country = j["geocode"]["country"]
		try:
			loc = j["geocode"]["locality"]
			loc += i
		except KeyError:
			try:
				loc= j["geocode"]["administrative_area_level_1"]
				loc += i
			except KeyError:
				loc=i
		s=country + loc
		s=s.encode("utf-8")
		s=regex.sub("-",s);
		os.system("mv "+directory +i+".jpg "+ directory + s+".jpg")
		if sys.argv[2] == "-v":
			print(s)	
	except KeyboardInterrupt:
		exit(0)
	


