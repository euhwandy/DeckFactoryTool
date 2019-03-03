# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 08:04:38 2019
deckFactory.py - Main Driver of the deck factory including the GUI and calling into the other systems
@author: Benjamin
"""

import sheetMaker as sm
import tkinter as tk
from tkinter import filedialog
import tkinter.scrolledtext as tkst
import numpy as np
import DeckEditor as dedit
import glob
import os
import sys
import json
import shutil
import logging


config = {
        "saved":False,
        "workingDir":"",
        "deckListPath":"",
        "cardDumpPath":"",
        "printSheetsPath":"",
        "referenceImagesPath":"",
        "systemSlash":'/',
        "logLevel":"ERROR"
        }

client_id = '46a5b17af3f323c'

client_secret = '293b64d937f56991f261334f4c7e928fb258c304'
def loadConfig():
    '''
    checks for configuration file adjacent to the executable and runs from there
    '''
    global config
    currentPath = os.path.abspath(os.curdir)
    config["workingDir"] = currentPath
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
        currentStuffs = glob.glob(currentPath+"/*")
        currentPath += '/'
        config["systemSlash"] = '/'
    elif sys.platform == 'win32':
        currentStuffs = glob.glob(currentPath+"\*")
        currentPath += '\\'
        config["systemSlash"] = '\\'
    if currentPath+"config.json" in currentStuffs:
        config = json.load(open(currentPath+"config.json","r"))
    else:
        if currentPath+"DeckLists" in currentStuffs and config["deckListPath"] == '':
            config["deckListPath"] = currentPath+"DeckLists"
        elif config["deckListPath"] == '':
            #make a decklists folder there
            os.mkdir("DeckLists")
            config["deckListPath"] = currentPath+"DeckLists"
        
        if currentPath+"PrintSheets" in currentStuffs and config["printSheetsPath"] == '':
            config["printSheetsPath"] = currentPath+"PrintSheets"
        elif config["printSheetsPath"] == '':
            #make a PrintSheets folder there
            os.mkdir("PrintSheets")
            config["printSheetsPath"] = currentPath+"PrintSheets"
        
        if currentPath+"CardDump" in currentStuffs and config["cardDumpPath"] == '':
            config["cardDumpPath"] = currentPath+"CardDump"
        elif config["cardDumpPath"] == '':
            #make a CardDump folder there
            os.mkdir("CardDump")
            config["cardDumpPath"] = currentPath+"CardDump"
            
        if currentPath+"referenceImages" in currentStuffs and config["referenceImagesPath"] == '':
            config["referenceImagesPath"] = currentPath+"referenceImages"
        elif config["referenceImagesPath"] == '':
            #make a referenceImages folder there
            os.mkdir("referenceImages")
            config["referenceImagesPath"] = currentPath+"referenceImages"
            #also need to populate the reference images folder with appropriate things
            if currentPath+"deck_template.png" in currentStuffs:
                shutil.copy2(currentPath+"deck_template.png",
                             config["referenceImagesPath"]+config["systemSlash"]+"deck_template.png")
    # default to ERROR if its not set yet
    config["logLevel"] = config.get("logLevel", "ERROR")
    return config

def saveConfig():
    '''
    should save the current config as a json
    '''
    global config
    config["saved"] = True
    if(config["workingDir"]+config["systemSlash"]+"config.json" in glob.glob(config["workingDir"]+config["systemSlash"]+"*")):
        os.remove(config["workingDir"]+config["systemSlash"]+"config.json")
    with open('config.json','w') as file:
        json.dump(config,file)
    
def editConfigWindow():
    '''
    this is the edit config window
    '''
    global config
    configEditor = tk.Tk()
    configEditor.title("Edit Configuration")
    configEditor.minsize(375,375)
    def changeDeckListFolder():
        '''
        reassigns the decklist folder
        '''
        global config
        deckListPathSelection = filedialog.askdirectory(initialdir = config["workingDir"],
                                               title = "Select DeckLists Folder")
        config["deckListPath"] = deckListPathSelection
        
        saveConfig()
    def changePrintSheetFolder():
        '''
        reassigns the printSheets folder
        '''
        global config
        pathSelection = filedialog.askdirectory(initialdir = config["workingDir"],
                                               title = "Select PrintSheets Folder")
        config["printSheetsPath"] = pathSelection
        saveConfig()
    def changeReferenceImagesFolder():
        '''
        reassigns the referenceImages folder
        '''
        global config
        pathSelection = filedialog.askdirectory(initialdir = config["workingDir"],
                                               title = "Select referenceImages Folder")
        config["referenceImagesPath"] = pathSelection
        saveConfig()
    def changeCardDumpFolder():
        '''
        reassigns the printSheets folder
        '''
        global config
        pathSelection = filedialog.askdirectory(initialdir = config["workingDir"],
                                               title = "Select CardDump Folder")
        config["cardDumpPath"] = pathSelection
        saveConfig()
    def close():
        nonlocal configEditor
        configEditor.destroy()
        configEditor.quit()
    dListButton = tk.Button(configEditor,text="Select Decklists Folder",
                            command = changeDeckListFolder,
                            bg='blue',fg='white',
                            width=20,height=4)
    dListButton.place(x=20,y=20)
    
    printSheetsButton = tk.Button(configEditor,text="Select PrintSheets Folder",
                                  command = changePrintSheetFolder,
                                  bg='blue',fg='white',
                                  width=20,height=4)
    printSheetsButton.place(x=200,y=20)
    
    referenceImagesButton = tk.Button(configEditor,text="Select ReferenceImage\nFolder",
                                      command = changeReferenceImagesFolder,
                                      bg='blue',fg='white',
                                      width=20,height=4)
    referenceImagesButton.place(x=20,y=150)
    
    cardDumpButton = tk.Button(configEditor,text="Select CardDump Folder",
                               command = changeCardDumpFolder,
                               bg='blue',fg='white',
                               width=20,height=4)
    cardDumpButton.place(x=200,y=150)
    
    closeButton = tk.Button(configEditor,text="Close", command = close,
                             bg='red',fg='white',
                             width=20,height=4)
    closeButton.place(x=110,y=250)
    configEditor.lift()
    configEditor.mainloop()
    


    
def main():
    '''
    this is the main driver of the script set
    '''
    global config
    loadConfig()
    saveConfig()
    master = tk.Tk()
    master.minsize(800,700)
    master.title("Deck Factory 2.7")
    master.geometry("800x700")
    master.lift()
    deckListPaths = []
    def initLogging(logLevelParm):
        loglevel = logging.ERROR
        if (logLevelParm == "DEBUG") :
            loglevel = logging.DEBUG
        elif (logLevelParm == "INFO") :
            loglevel = logging.INFO
        elif (logLevelParm == "WARNING") :
            loglevel = logging.WARNING
        elif (logLevelParm == "CRITICAL") :
            loglevel = logging.CRITICAL
            
            
        
        logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='debug.log',
                    filemode='w')


        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
                # create logger called deckfactory
        logger = logging.getLogger('deckFactory')
        logger.error("Log level set to :" + logLevelParm)

        logger.addHandler(ch)
    def killWindow():
        master.destroy()
    def getDeckLists():
        nonlocal deckListPaths
        global config
        clearDList()
        deckListPaths = filedialog.askopenfilenames(initialdir = config["deckListPath"]+config["systemSlash"],
                                               title = "Select Decks for Formatting",
                                               filetypes = (("All Files","*.*"),
                                                            ("Manual Decklists","*.txt"),
                                                            ("Xmage Decks","*.dck")))
        for i in deckListPaths:
            temp = sm.stripName(i)
            logger.debug("adding: " + temp + " to decklist")
            dList.insert(tk.END,temp+'\n')
    def clearSelection():
        logger.debug("clear decklist paths")
        nonlocal deckListPaths
        deckListPaths = []
        clearDList()
    def buildSheets():
        logger.debug("entering buildSheets")
        nonlocal deckListPaths
        global config
        count = 0
        for i in deckListPaths:
            logger.debug("calling buildSheet: " + i)  
            failedCards,ambiguities,dictVersionOfDeck = sm.buildSheet(i,buildLogPrint)
            logger.debug("returned from buildSheet")

            strippedName = str(sm.stripName(i))
            justName = str(sm.justName(i))
            if(np.size(failedCards) >0 or np.size(ambiguities) > 0):
                #cards failed in this run some how
                buildLogPrint("The file "+strippedName+" ran into the following issues:")
                for j in failedCards:
                    if j.setCode == '' :
                        buildLogPrint(j.cardName+" was not found.")
                    else:
                        if j.cn == '' :
                            buildLogPrint(j.cardName+" from set "+j.setCode+" was not found.")
                        else:
                            buildLogPrint("Card #"+j.cn+" from set "+j.setCode+" was not found.")
                for j in ambiguities:
                    if j.setCode == '':
                        buildLogPrint(j.cardName+" was an ambiguous search.")
                    else:
                        if j.cn=='':
                            buildLogPrint(j.cardName+" from set "+j.setCode+" was an ambiguous search.")
                        else:
                            buildLogPrint("Card #"+j.cn+" from set "+j.setCode+" was an ambiguous search.")
                if np.size(ambiguities) > 0:
                    buildLogPrint("")
                    buildLogPrint("Ambiguities can be helped by specifying a set code or using the collector's number and set code rather than the name.")
                buildLogPrint("No print sheets were generated for "+strippedName)
            else:
                count += 1
                buildLogPrint("Print sheet(s) successfully generated for "+strippedName)
                #here is an example of dropping the deck manifest component into place
                if(config["deckListPath"]+config["systemSlash"]+justName+".json" in glob.glob(config["deckListPath"]+config["systemSlash"]+"*")):
                    os.remove(config["deckListPath"]+config["systemSlash"]+justName+".json")
                with open(config["deckListPath"]+config["systemSlash"]+justName+".json","w") as file:
                    dictVersionOfDeck["deck_name"] = justName
                    json.dump(dictVersionOfDeck,file)
                buildLogPrint("JSONIFIED version of "+justName+" saved")
                
            buildLogPrint("")
        if(count > 0):
            buildLogPrint("Print Sheets have been generated!\nThey can be found in " + config["printSheetsPath"]+"\n")
                    
    def clearDList():
        dList.delete('1.0',tk.END)
        dList.insert(tk.END,"Files set to build:\n")
    def clearBuildLog():
        buildLog.delete('1.0',tk.END)
    def buildLogPrint(string):
        buildLog.insert(tk.END,str(string)+"\n")
        master.update_idletasks()
    def editDeckWindow():
        dedit.editDeck()
        
    def editConfig():
        '''
        this is a button event that will spawn a seperate window for setting config paths
        '''
        editConfigWindow()
        
    #default the logLevel to ERROR if it doesn't exist in the config.json file yet.
    initLogging(config.get("logLevel", "ERROR"))    
    logger = logging.getLogger("deckFactory")      
    dList = tk.Text(master,height = 12, width = 40)
    dList.place(x=325,y=20)
    clearDList()
    buildLog = tkst.ScrolledText(master,height=25,width =95)
    buildLog.place(x=20,y=220)
    clearBuildLog()
    #button structure
    selectButton = tk.Button(master,text="Select Decklists", command = getDeckLists,
                             bg='blue',fg='white',
                             width=17,height=4)
    selectButton.place(x = 20, y = 20)
    
    buildButton = tk.Button(master, text = "Build Print Sheets", command = buildSheets,
                            bg='green',fg='white',
                            width=17,height=4)
    buildButton.place(x = 20, y = 100)
    editButton = tk.Button(master, text = "Edit/Create Deck", command = editDeckWindow,
                            bg='blue',fg='white',
                            width=17,height=4)
    editButton.place(x = 170, y = 20)
    
    changeConfigButton = tk.Button(master, text = "Change Folder Defaults", command = editConfig,
                            bg='blue',fg='white',
                            width=17,height=4)
    changeConfigButton.place(x = 170, y = 100)
    
    exitButton = tk.Button(master,text='Exit', command = killWindow,
                           bg='red',fg='white',
                           width=4,height=2)
    exitButton.place(x=740,y=645)
    
    clearSelectionButton = tk.Button(master,text="Clear Selection", command=clearSelection,
                                     bg='blue',fg='white')
    clearSelectionButton.place(x = 660, y = 100)
    
    clearBuildLogButton = tk.Button(master,text = "Clear Log", command = clearBuildLog,
                                    bg='blue',fg='white')
    clearBuildLogButton.place(x=20,y=645)

    
    #button.pack()
    master.mainloop()
    
    
if __name__ == '__main__':
    main()