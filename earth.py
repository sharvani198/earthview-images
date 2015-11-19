from time import time
from os import chdir, mkdir
from json import loads
from requests import get
from base64 import decodestring
from multiprocessing import Pool, Process, Manager
import threading as th

JSON_FILE_NAME = "img.json"


def read_img_json():
    imgJson = open(JSON_FILE_NAME)
    imgIds = loads(imgJson.read())
    imgIds = map(str, imgIds.get("id"))
    return imgIds


def create_img_directory():
    mkdir("images")
    chdir("images")


def create_img(imgNum, count):

    responseJson = get("https://www.gstatic.com/prettyearth/assets/data/"+imgNum+".json").json()

    #get a suitable name for image
    geocode = responseJson.get("geocode", imgNum)
    country = geocode.get("country", imgNum)
    locality = geocode.get("locality", imgNum)
    area = geocode.get("administrative_area_level_1", imgNum)
    fileName = country + "-" + locality + "-" + area
    fileName = fileName.encode("utf-8")
    fileName = fileName.replace(" ", "-")
    fileName = fileName + ".jpg"

    #create an image by decoding then encoding response data
    imgData = responseJson.get("dataUri", "").split("base64,")[1]
    imgFile = open(fileName, "w")
    imgFile.write(decodestring(imgData))
    imgFile.close()
    count.put(imgNum)


def create_threads(ids, count):
    threads = []
    for i in ids:
        t = th.Thread(target=create_img, args=(i, count))
        t.start()
        threads.append(t)
    t.join()


def split(arr, size):
    arrs = []
    while len(arr) > size:
        piece = arr[:size]
        arrs.append(piece)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


#Not used as cross process sync is hard
def create_process_pool():
    ids = read_img_json()
    create_img_directory()
    pool = Pool()
    id_set = split(ids, 100)
    result = [pool.apply_async(create_threads, args=(i,)) for i in id_set]
    if result:
        pool.close()
        pool.join()


def worker(q):
    ids = read_img_json()
    create_img_directory()
    id_set = split(ids, 50)
    for i in id_set:
        create_threads(i, q)


def create_worker(q):
    p = Process(target=worker, args=(q,))
    p.start()
    p.join()
    q.put(0)


def progress(count):
    print("Downloading")
    count = 0
    while 1:
        c = q.get()
        if c == 0:
            print(count)
            break
        count += 1
        print("*"),
        if count % 50 == 0:
            print(str(count) + " \n")


def create_listener(q):
    p = Process(target=progress, args=(q,))
    p.start()
    #p.join()


if __name__ == '__main__':
    startTime = time()
    q = Manager().Queue()

    create_listener(q)
    create_worker(q)

    finishTime = time()
    print(" Took " + str(finishTime - startTime) + "sec")
