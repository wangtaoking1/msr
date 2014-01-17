#-*- coding: utf-8 -*-

from threading import Thread
from queue import Queue
from urllib import request
import re, os

class Downloader:
    def __init__(self, songsList):
        self._songs = songsList
        self._Q = Queue()
        self._done = self._getDone()
    
    def download(self, number=None, threadNum=5):
        if not number:
            number = len(self._songs)
        #start threadNum Threads
        for i in range(threadNum):
            t = Thread(target=self._working)
            t.setDaemon(True)
            t.start()
        
        #add number songs to Q
        base = len(self._done)
        bigend = base + number
        if bigend > len(self._songs): bigend = len(self._songs)
        for i in range(base, bigend):
            self._Q.put(self._songs[i])
        
        self._Q.join()
    
    def _working(self):
        while True:
            song = self._Q.get()
            
            res = re.search(r"id=(\d*)", song)
            name = res.group(1) + ".mp3"
            if name in self._done:
                continue
            print(name, "downloading...")
            response = request.urlopen(song)
            fp = open("music" + os.sep + name, "wb")
            fp.write(response.read())
            fp.close()
            print(name, "done.")
            self._done.append(name)
            self._Q.task_done()
    
    def _getDone(self):
        done = os.listdir(path=r'./music/')
        print(len(done))
        return done
    
