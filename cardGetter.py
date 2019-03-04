# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 18:33:22 2017
cardGetter.py - contains functions used in getting card images and storing them

@author: Benjamin
"""

import urllib as ul
from urllib import request
#import requests as req
#import re
import os
import glob
import json
config = {}# this is set by 
class AmbiguityError(Exception):
    pass

class Card: 
    '''
    start using this structure as it will help with the 
    '''
    def __init__(self):
        self.cardName = ''
        self.cn = ''
        self.setCode = ''
        self.ambiguous = False
        self.notFindable = False
        self.copies = 1
        self.pileNumber = 0
        self.loadedFromJson = False
        self.cardData = '' #this will be populated by the json profile of the card from Scryfall
        
    def convertToTTSCard(self):
        '''
        this function takes all the appropriate information and converts it to a generic dictionary template for a card
        '''
        cardDict = {}
        cardDict["Name"] = 'Card'
        cardDict['Nickname'] = self.cardName
        cardDict['Description'] = self.cardData["type_line"]+"\n\n"+self.cardData["oracle_text"]
        cardDict["Transform"] = {"posX":0,"posY":0,"posZ":0,"rotX":0,"rotY":180,"rotZ":180,"scaleX":1,"scaleY":1,"scaleZ":1}
        
        return cardDict

def copyCard(cardFrom,cardTo):
    '''
    takes the values of cardfrom and copies them into cardto
    '''
    cardTo.cardName = cardFrom.cardName
    cardTo.cn = cardFrom.cn
    cardTo.setCode = cardFrom.setCode
    cardTo.ambiguous = cardFrom.ambiguous
    cardTo.notFindable = cardFrom.notFindable
    cardTo.copies = cardFrom.copies
    cardTo.pileNumber = cardFrom.pileNumber
    cardTo.cardData = cardFrom.cardData
    cardTo.loadedFromJson = cardFrom.loadedFromJson
    
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
            'q','r','s','t','u','v','w','x','y','z']
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def percentEncode(string):
    '''
    %encode the string
    '''
    temp = string.replace('!','%21')
    temp = temp.replace('#','%23')
    temp = temp.replace('$','%24')
    temp = temp.replace('&','%26')
    temp = temp.replace("'",'%27')
    temp = temp.replace('(','%28')
    temp = temp.replace(')','%29')
    temp = temp.replace('*','%2A')
    temp = temp.replace('+','%2B')
    temp = temp.replace(',','%2C')
    temp = temp.replace('/','%2F')
    temp = temp.replace(':','%3A')
    temp = temp.replace(';','%3B')
    temp = temp.replace('=','%3D')
    temp = temp.replace('?','%3F')
    temp = temp.replace('@','%40')
    temp = temp.replace('[','%5B')
    temp = temp.replace(']','%5D')
    
    return temp
def getUrl(cardName,setName):
    '''
    search a particular set version of a card and return the url to the 
    image of said card
    '''
    #use |number if using a collector's number
    colNum = False
    if(cardName[0]=='|'):
        colNum = True
    refString = "https://api.scryfall.com/cards/search?q="
    #percent Encoding the name string
    temp = percentEncode(cardName)
    if(setName != ''):
        if(colNum):
            temp = ''
        temp+="+e%3A"+setName
        if(colNum):
            temp+= "+cn%3A"+cardName[1:].replace(" ","")
    temp = temp.replace(' ', '+')
    #print(refString+temp)
    return refString+temp

def saveName(cardManifest,face,imType,config):
    '''
    this overload takes a card manifest json to work more effectively
    '''
    extension = '.jpg'
    if imType == 'png':
        extension = '.png'
    destination = config["cardDumpPath"]+config["systemSlash"]
    if 'card_faces' in cardManifest and not "image_uris" in cardManifest:
        temp = percentEncode(cardManifest['card_faces'][face]['name'] + cardManifest['set'] + cardManifest['collector_number']).replace(' ','_')
    else:
        temp = percentEncode(cardManifest['name'] + cardManifest['set'] + cardManifest['collector_number']).replace(' ','_')
    return destination+temp+extension

def getCardIm(cardManifest,face,imType,config):
    '''
    this function gets a card and stores the image for it locally as a .jpg
    '''
    if( "card_faces" in cardManifest and not "image_uris" in cardManifest):
        request.urlretrieve(cardManifest["card_faces"][face]["image_uris"][imType],saveName(cardManifest,face,imType,config))
    else:
        request.urlretrieve(cardManifest["image_uris"][imType],saveName(cardManifest,face,imType,config))

def searchCardByName(cardName,setName):
    '''
    this function pings the scryfall API the same way that getCardIm does, but instead of jumping into the images, it returns the JSON of the search
    '''
    url = getUrl(cardName,setName)
    dataTxt = request.urlopen(url).read()
    data = json.loads(dataTxt)
    return data

def searchCardByCN(cn,setName):
    return searchCardByName("|"+cn,setName)

def searchByParameters(args):
    '''
    search by a set of arguments for the scryfall search system
    '''
    url = "https://api.scryfall.com/cards/search?q="+percentEncode(args).replace(' ','+')
    data = []
    try:
        dataTxt = request.urlopen(url).read()
        data= json.loads(dataTxt)
        if("has_more" in data):
            if(data["has_more"] == True):
                tempDataTxt = request.urlopen(data["next_page"]).read()
                while True:
                    tempData = json.loads(tempDataTxt)
                    for i in tempData["data"]:
                        data["data"].append(i)
                    if ("has_more" in tempData):
                        if(tempData["has_more"] == True):
                            tempDataTxt = request.urlopen(tempData["next_page"]).read()
                        else:
                            break
    except ul.error.HTTPError:
        #failure occurred.
        data = {'code': '404'}
        pass
    return data

def getCardManifest(uri):
    '''
    given an extra uri, retrieve that extra's json
    '''
    dataTxt = request.urlopen(uri).read()
    data = json.loads(dataTxt)
    if("has_more" in data):
            if(data["has_more"] == True):
                tempDataTxt = request.urlopen(data["next_page"]).read()
                while True:
                    tempData = json.loads(tempDataTxt)
                    for i in tempData["data"]:
                        data["data"].append(i)
                    if ("has_more" in tempData):
                        if(tempData["has_more"] == True):
                            tempDataTxt = request.urlopen(tempData["next_page"]).read()
                        else:
                            break
    return data

def CleanUpCardDir(config):
    '''
    deletes all of the images in the Card Dump folder
    '''
    folder = config["cardDumpPath"]+config["systemSlash"]+'*'
    r = glob.glob(folder)
    for i in r:
        os.remove(i)

def main():
    '''
    this is a test case to figure out why things blowup.
    '''
    krenkoStr = "https://api.scryfall.com/cards/search?q=krenko+mob+boss"
    krenkoManifest = getCardManifest(krenkoStr)
    forestManifest = searchByParameters("forest")
    
    print(krenkoManifest)
    print(":::::::::")
    print(forestManifest)
    
if __name__ == '__main__':
    main()