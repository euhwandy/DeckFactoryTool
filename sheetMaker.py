# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 21:16:17 2017
sheetMaker.py - assembles the printing sheet(s) from the set of images for 
the decklist

@author: Benjamin
"""

import re
import PIL
import cardGetter as cg
from cardGetter import Card
import numpy as np
import deckFactory as df
import json
#import sys
#import glob
from time import sleep
import logging
dlDir = 'DeckLists/'
psDir = 'PrintSheets/'
config = {}#dictionary set by buildSheets via argument passed in from driver
def buildPrint(string):
    '''
    this is a default printing function, however this should be overloaded by a 
    functor passed in from the main deckFactory script
    '''
    print(string)
class InvalidListSelection(Exception):
    pass
class Manifest:
    cards = []
    extras = []
    printList = []
    ambiguities = []
    failedCards = []
    cardCount = 0
    printable = True
    def __init__(self):
        self.cards = []
        self.extras = []
        self.printList = []
        self.ambiguities = []
        self.failedCards = []
        self.cardCount = 0
        self.printable = True
    def convertToDict(self):
        '''
        here we write functionality that creates a big old json blob like dictionary
        so that it can be dumped into a json as the deck format
        '''
        outDict = {}
        if(self.printable):
            outDict["cards"] = []
            outDict["card_count"] = self.cardCount
            for i in self.cards:
                tempBlob = i.cardData
                tempBlob["numberOfCopies"] = i.copies
                tempBlob["pile"] = i.pileNumber
                outDict["cards"].append(tempBlob)
            
            for i in self.extras:
                tempBlob = i.cardData
                tempBlob["numberOfCopies"] = i.copies
                tempBlob["pile"] = i.pileNumber
                outDict["cards"].append(tempBlob)
        else:
            buildPrint("DeckManifest could not be converted to dictionary blob")
            outDict["errorCase"] = "NOT PRINTABLE"
        return outDict
        
def stripName(deckPath):
    '''
    takes a deck path and extracts just the file name
    '''
    global buildPrint
    global config
    config = df.loadConfig()
    i = -1
    while True:
        if deckPath[i] == '/':
            break
        i = i - 1
    fname = deckPath[i+1:]
    return fname

def justName(deckPath):
    '''
    takes the deck path and returns just the name sans file extension
    '''
    temp = stripName(deckPath)
    i = -1
    while True:
        if temp[i]=='.':
            break
        i = i-1
    fname = temp[:i]
    return fname
    
def saveSheet(sheet,deckName,sheetNum):
    '''
    sheet is an image object deckname is a string, sheetnum is the current sheet in the project
    '''
    global buildPrint
    global config
    config = df.loadConfig()
    sheet.save(config["printSheetsPath"]+config["systemSlash"]+deckName+str(sheetNum)+'.png','PNG')

def buildManifest(cardMat,deckManifest):
    '''
    searches through the card matrix object that has been built and returns a
    requisition list with all the card objects fully populated
    '''
    global buildPrint
    global config
    config = df.loadConfig()
    logger.debug("entering buildManifest")
    for i in cardMat:
        if( not i.loadedFromJson):#flag that it is for the json style load in
            cardData = ''
            if not i.cn == ''  and not i.setCode =='':
                try:
                    i.cardData= cg.searchCardByCN(i.cn,i.setCode)
                except:
                    buildPrint("Card Not findable")
                    i.notFindable = True
                    deckManifest.failedCards.append(i)
                    deckManifest.printable = False
                    logger.debug("Supplied CN: " + i.cn + "Setcode: " + i.setCode + " not found" )
            elif not i.cardName == '':
                try:
                    i.cardData = cg.searchCardByName(i.cardName,i.setCode)
                except:
                    buildPrint("Card Not findable")
                    i.notFindable = True
                    deckManifest.failedCards.append(Card())
                    cg.copyCard(i,deckManifest.failedCards[-1])
                    deckManifest.printable = False
                    logger.debug("card name: " + i.cardName + " not found")
            #print(cardData)
            if not i.cardData == '' and i.notFindable == False:
              logger.debug("cardData: " + str(i.cardData))
              if "code" in cardData:
                    buildPrint("Card Not findable")
                    i.notFindable = True
                    deckManifest.failedCards.append(Card())
                    cg.copyCard(i,deckManifest.failedCards[-1])
                    deckManifest.printable = False
              elif i.cardData["total_cards"] > 1 :
                    #ambiguity found
                    buildPrint("Card Found to be ambiguous, manifest will not produce print sheets")
                    i.ambiguous = True
                    deckManifest.ambiguities.append(Card())
                    cg.copyCard(i,deckManifest.ambiguities[-1])
                    deckManifest.printable = False
              else:#card found, not ambiguous, lets catalog it
                    #first check if double sided
                    i.cardData = i.cardData["data"][0]
                    deckManifest.cards.append(Card())
                    cg.copyCard(i,deckManifest.cards[-1])
                    deckManifest.cardCount = deckManifest.cardCount +1
                    logger.debug("card added to manifest")
                    #print("Card added to Manifest")
                    if "all_parts" in i.cardData:
                        for j in i.cardData["all_parts"]:
                            if j["component"] == 'token' or (j['component'] == 'combo_piece' and j['name'][-6:].lower() == 'emblem'):
                                duplicate = False
                                for k in deckManifest.extras:
                                    if k.cardData["id"] == j["id"]:
                                        #we found a duplicate, don't add it
                                        duplicate = True
                                        break
                                for k in deckManifest.cards:
                                    if k.cardData["id"] == j["id"]:
                                        #more duplicate finding, this way we cannot auto add something manually added
                                        duplicate = True
                                        break
                                if not duplicate:
                                    deckManifest.extras.append(cg.Card())
                                    deckManifest.extras[-1].cardData = cg.getCardManifest(j["uri"])
                                    deckManifest.extras[-1].cardName = deckManifest.extras[-1].cardData["name"]
                                    deckManifest.extras[-1].setCode = deckManifest.extras[-1].cardData["set"]
                                    deckManifest.extras[-1].cn = deckManifest.extras[-1].cardData["collector_number"]
                                    deckManifest.extras[-1].pileNumber = 1 #one is the default for tokens/extras
                                    deckManifest.cardCount = deckManifest.cardCount +1
                                    logger.debug("Extra added to Manifest")
                                #print("Extra added to Manifest")
                    if "card_faces" in i.cardData and not "image_uris" in i.cardData:
                        deckManifest.cardCount = deckManifest.cardCount +1
                        deckManifest.extras.append(cg.Card())
                        cg.copyCard(i,deckManifest.extras[-1])
                        deckManifest.extras[-1].pileNumber = 1 #one is the default for tokens/extras
                        logger.debug("Card back face added to manifest")
                        #deckManifest.cardCount = deckManifest.cardCount +1
        else:#we jsoning folks!
            if(i.pileNumber == 1):#this is an extra
                deckManifest.extras.append(cg.Card())
                cg.copyCard(i,deckManifest.extras[-1])
            else:
                deckManifest.cards.append(cg.Card())
                cg.copyCard(i,deckManifest.cards[-1])
            deckManifest.cardCount = deckManifest.cardCount +1
    '''
    TODO: 
        build a loop here to iterate through the manifest's main list and find
        if any meld cards have both halves here, if so, add the meld result to 
        the extras list.
    '''
    if deckManifest.printable:
        buildPrint("deckManifest Completed")
        logger.debug("deckManifest Completed")
    else:
        buildPrint("deckManifest could not be completed.")
        logger.debug("deckManifest could not be completed.")
        
        
def readInFile(listName):
    '''
    this is the first part of the buildSheet functionality, refactored away so it can be accessed
    for importing purposes as well
    '''
    global buildPrint
    global config
    config = df.loadConfig()
    dList = listName
    cardMat = []
    fileType = "txt"
    if dList[-4:] == '.dck':
        fileType = "Xmage"
    elif(dList[-5:]=='.json'):
        fileType = "Json"
    if not fileType == "Json":
        with open(dList) as file:
            for line in file:
                #print(line)
                #sys.stdout.flush()
                logger.debug("parsing line: " + line)
                cardMat.append(Card())
                if fileType == "Xmage":
                    if line[:11] == 'LAYOUT MAIN':
                        break#we have hit the formatting section
                    if line[:5] == 'NAME:':
                        buildPrint(line[5:])

                    else:
                        targReg = re.search('\[(\S)*\]((\s)*(\S)*)*',line).group(0)
                        setN = re.search('\[(\S)*\:',targReg).group()
                        setN = setN[1:-1]
                         #Xmage silliness corrected here to some extent (DARN YOU PROMOS)
                        if setN.lower() == 'gur':  #guru lands
                            setN = 'pgru'
                        elif setN.lower() == 'dd3dvd': #duel decks: divine vs demonic
                            setN = 'dvd'
                        elif setN.lower() == 'dd3jvc' : #duel decks: jace vs chandra
                            setN = 'jvc'
                        elif setN.lower() == 'dd3evg': #elves vs goblins
                            setN = 'evg'
                        elif setN.lower() == 'cp': #champions and states
                            setN = 'pcmp'
                        elif setN.lower() == 'gpx': #grand Prix Promos
                            setN = 'pgpx'
                        else:
                            setN = setN.lower()
                        cardMat[-1].setCode = setN
                        cNum = re.search('\:(\S)*\]',line).group()[1:-1]
                        cName = re.search('\]((\s)*(\S)*)*',line).group()[1:-1]
                        cardMat[-1].cardName = cName
                        cardMat[-1].cn = cNum
                else:#text file type
                    #filter out comments and empty lines
                    if not (line[0] == '#' or line.replace(" ","")=='\n'):
                        tc = -1
                        name1 = ''
                        setN = ''
                        for i in range(len(line)):
                            if(line[i] == '!' and i >= 2):
                                if(line[i-1]==' ' or line[i-1]=='\t'):
                                    name1 = line[:i]
                                    tc = i
                        #name1 = re.search('((\S)*(\s)*)*\s!',line).group()
                        if tc > -1:
                            for i in range(tc,len(line)):
                                if(line[i] == '&' and (line[i-1]==' ' or line[i-1]=='\t')):
                                    setN = line[tc+1:i]
                        #setN = re.search('!((\S)*(\s)*)*\s&',line)
                        
                        if setN:
                            setName1 = setN
                            setName = setName1[1:-1].replace(' ','')
                        else:
                            setName = ''
    
                        name = name1[:-1]
                        name = name.replace('\t','')
                        setName = setName.replace('\t','')
                        if(not name == ''):
                            if(name[0] == '|'):#its a card number
                                cardMat[-1].cn = name[1:]
                            else:
                                cardMat[-1].cardName=name
                        else:
                            #card failed to read in properly, flag as failed.
                            cardMat[-1].cardName = name
                            cardMat[-1].notFindable = True
                            buildPrint("a card's name could not be read from this line:")
                            buildPrint(line)
                            logger.debug("name not found in: " + line)
                        cardMat[-1].setCode = setName
                        
    else:#json deck format, load in based on card data.
        deckListContents = json.load(open(dList,"r"))
        for i in deckListContents["cards"]:
            cardMat.append(cg.Card())
            cardMat[-1].cardData = i
            cardMat[-1].cn = i["collector_number"]
            cardMat[-1].setCode = i["set"]
            if("card_faces" in i and not "image_uris" in i):#double faced but not split card
                if(not i["pile"] == 1):#not an extra
                    cardMat[-1].cardName = i["card_faces"][0]["name"]
                else:#is the back face beacause it is an extra
                    cardMat[-1].cardName = i["card_faces"][1]["name"]
            else:
                cardMat[-1].cardName = i["name"]
            cardMat[-1].copies = i["numberOfCopies"]
            cardMat[-1].pileNumber = i["pile"]
            cardMat[-1].loadedFromJson = True
    return cardMat,fileType


def buildSheet(listName,buildPrintFunctor):
    '''
    this is the main point of entry for this package
    '''
    global buildPrint
    global logger
    global config
    config = df.loadConfig()
    logger = logging.getLogger("sheetMaker")
    buildPrint = buildPrintFunctor
    failureState = False
    dList = listName
    deckManifest = Manifest()
    cardMat,deckFileType = readInFile(dList)
    buildPrint(stripName(dList)+" Read into initial state")
    buildManifest(cardMat,deckManifest)
    numCards = deckManifest.cardCount
    if numCards > 69:
        numSheets = int(np.floor(numCards/69)+1)
    else:
        numSheets = int(1)
    count = 1
    if deckManifest.printable:
        #test creation of json deck format
        for j in deckManifest.cards:
            cardFailed = False
            if("card_faces" in j.cardData and not "image_uris" in j.cardData):
                buildPrint("Finding "+ j.cardData["card_faces"][0]["name"])
                try:
                    cg.getCardIm(j.cardData,0,"large",config)
                except:
                    buildPrint("An error occurred in card image retrieval")
                    cardFailed = True
                if(not cardFailed):
                    buildPrint('Card '+ str(count)+ ' of '+ str(numCards) + ' retrieved')
                    count += 1
                    deckManifest.printList.append(cg.saveName(j.cardData,0,'large',config))
                else:
                    buildPrint('Card '+ str(count)+ ' of '+ str(numCards) + ' failed to retrieve')
                    count += 1
            else:
                buildPrint("Finding "+ j.cardData["name"])
                try:
                    cg.getCardIm(j.cardData,0,"large",config)#the 0 is a placeholder in this case as card_faces is not in the cardManifest
                except:
                    buildPrint("An error occurred in card image retrieval")
                    cardFailed = True
                if(not cardFailed):
                    buildPrint('Card '+ str(count)+ ' of '+ str(numCards)+ ' retrieved')
                    count += 1
                    deckManifest.printList.append(cg.saveName(j.cardData,0,'large',config))
                else:
                    buildPrint('Card '+str(count)+ ' of '+ str(numCards)+ ' failed to retrieve')
                    count += 1
        for j in deckManifest.extras:
            if("card_faces" in j.cardData and not "image_uris" in j.cardData):#double faced not split
                buildPrint("Finding "+ j.cardData["card_faces"][1]["name"])
                try:
                    cg.getCardIm(j.cardData,1,"large",config)
                except:
                    buildPrint("An error occurred in card image retrieval")
                    cardFailed = True
                if(not cardFailed):
                    buildPrint('Card '+ str(count)+ ' of '+ str(numCards)+ ' retrieved')
                    count += 1
                    deckManifest.printList.append(cg.saveName(j.cardData,1,'large',config))
                else:
                    buildPrint('Card '+str( count)+ ' of '+ str(numCards)+ ' failed to retrieve')
                    count += 1
            else:
                buildPrint("Retrieving "+ j.cardData["name"])
                try:
                    cg.getCardIm(j.cardData,0,"large",config)#the 0 is a placeholder in this case as card_faces is not in the cardManifest
                except:
                    buildPrint("An error occurred in card image retrieval")
                    cardFailed = True
                if(not cardFailed):
                    buildPrint('Card '+ str(count)+' of '+ str(numCards)+' retrieved')
                    count += 1
                    deckManifest.printList.append(cg.saveName(j.cardData,0,'large',config))
                else:
                    buildPrint('Card '+str(count)+' of '+str(numCards)+' failed to retrieve')
                    count += 1
        '''
        we have the card images now
        now to assemble the print sheet
        '''
        template = PIL.Image.open(config["referenceImagesPath"]+config["systemSlash"]+'deck_template.png')
        temp = template.copy()
        currentSheet = 1
        ci = 0 #card iterator (for going through the set of cards)
        dispName = justName(dList)
        if( np.size(deckManifest.printList) == deckManifest.cardCount):
            while ci < np.size(deckManifest.printList):
                    lci = np.mod(ci,69) #local card iterator
                    cardim=PIL.Image.open(deckManifest.printList[ci])
                    size = 332, 500#471 #this took some tinkering to get Scryfall's to work.
                    cardim.thumbnail(size,PIL.Image.ANTIALIAS)
                    #to determine the location of pasting.
                    coordx =332*np.mod(lci,10)
                    coordy =462*int(lci/10)
                    #box size is 10 + 312 + 10, 10+445+10
                    temp.paste(cardim,(coordx,coordy))
                    #colorBorders(temp,coordx,coordy,cardim)
                    #determine if we have finished a sheet
                    buildPrint('Card '+str(ci+1)+' of '+str(np.size(deckManifest.printList))+' complete')
                    if ci == np.size(deckManifest.printList)-1:
                        saveSheet(temp,dispName,currentSheet)
                        buildPrint('Sheet '+str(currentSheet)+' of '+str(numSheets)+' complete')
                        buildPrint('Print Sheets for '+str(dispName)+' complete.')
                        break
                    elif lci == 68:
                        saveSheet(temp, dispName,currentSheet)
                        temp = template.copy()
                        buildPrint('Sheet '+ str(currentSheet)+ ' of '+ str(numSheets)+ ' complete')
                        currentSheet += 1
                        ci+=1
                    else:
                        ci+=1
        else:
            #this should never happen.
            failureState = True
            buildPrint("One or more cards failed to download images. No sheets will be generated.")
    else:
        failureState = True
    if failureState:
        buildPrint("Not all cards were successfully retrieved, print sheets will not be assembled")
        if(np.size(deckManifest.failedCards)>0):
            buildPrint("The following cards could not be found: ")
            for i in deckManifest.failedCards:
                if(i.setCode == ''):
                    buildPrint(i.cardName+" with no specified set")
                else:
                    if(i.cn == ''):
                        buildPrint(i.cardName + ' from '+ i.setCode)
                    else:
                        buildPrint("card #"+str(i.cn)+' from '+str(i.setCode))
        if(np.size(deckManifest.ambiguities)>0):
            buildPrint("The following card searches were ambiguous and require more detail in specification:")
            for i in deckManifest.ambiguities:
                if(i.setCode == ''):
                    buildPrint(i.cardName +"with no specified set")
                else:
                    if(i.cn == ''):
                        buildPrint(i.cardName + ' from '+ i.setCode)
                    else:
                        buildPrint("card # "+i.cn + ' from ' + i.setCode)
            buildPrint("a couple of ways to increase specificity are to indicate a set code or pick by collector number within a given set")
    outFail = deckManifest.failedCards[:]
    outAmb = deckManifest.ambiguities[:]
    sleep(0.01)
    cg.CleanUpCardDir(config)
    sleep(0.01)
    tempOut = deckManifest.convertToDict()
    del deckManifest
    del cardMat
    #build the error reporting
    return outFail,outAmb,tempOut

