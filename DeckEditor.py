# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 17:54:13 2019
deckEditor.py - building a deck list editing interface

@author: Benjamin
"""

import cardGetter as cg
import sheetMaker as sm
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.scrolledtext as tkst
from PIL import Image, ImageTk
import glob
import os
import numpy as np
import deckFactory as df

config= {}
def generateListEntry(selectedManifest):
    '''
    given a card's json, generate and return the string list entry for it
    '''
    '''
    out = ''
    if(cg.RepresentsInt(selectedManifest["collector_number"]) or cg.RepresentsInt(selectedManifest["collector_number"][:-1]) ):
        out = ("|"+str(selectedManifest["collector_number"])+" ! "+
                        selectedManifest["set"].upper()+ " & " +
                        selectedManifest["name"] + " " + selectedManifest["set_name"]+
                        " #"+selectedManifest['collector_number']+"\n")
    else:
        out = (selectedManifest["name"]+" ! "+
                        selectedManifest["set"].upper()+ " & " +
                        selectedManifest["name"] + " " + selectedManifest["set_name"]+
                        " #"+selectedManifest['collector_number']+"\n")
                    
    return out
    '''
    
    out = str(selectedManifest["collector_number"]) + " | "
    out += selectedManifest["set"].upper() + " | "
    out += selectedManifest["name"] + " | "
    out += selectedManifest["copies"] + " | " 
    out += selectedManifest["pileNumber"]+" | "
    out += selectedManifest["uri"]+"\n"
    return out
def searchCardDialogTree(searchManifest):
    savedCardInfo = ''
    returnString = ''
    if(searchManifest['total_cards'] > 1):
        #search was ambiguous
        savedCardIndex = -1
        toomanyCards = tk.Tk()
        toomanyCards.title("Please Select Card to proceed with")
        toomanyCards.minsize(width = 300, height = 100)
        toomanyCards.lift()
        cardOptions = []
        for i in searchManifest["data"]:
            cardOptions.append(i["name"])
        combo = ttk.Combobox(toomanyCards, justify = 'center',
                             state = 'readonly',values=cardOptions)
        combo.current(0)
        combo.pack()
        def comboSelectnClose():
            nonlocal savedCardIndex
            savedCardIndex = combo.current()
            nonlocal toomanyCards
            toomanyCards.destroy()
            toomanyCards.quit()
            nonlocal savedCardInfo
            savedCardInfo = searchManifest["data"][savedCardIndex]

        selectButton = tk.Button(toomanyCards,text="Select",command = comboSelectnClose)
        selectButton.pack()
        closeButton = tk.Button(toomanyCards,text="Close",command = toomanyCards.destroy)
        closeButton.pack()
        toomanyCards.mainloop()
    else: #we have 1 card!
        savedCardInfo = searchManifest["data"][0]
    # now we have saved data for card manipulation
    if(not savedCardInfo == ''):
        variationManifest = cg.getCardManifest(savedCardInfo["prints_search_uri"])
        variationCardList = variationManifest["data"]
        variationImList = []
        variationSetNameList = []
        #variationCurrentInventory = []
        counter = 2
        for i in variationCardList:
            variationImList.append(cg.saveName(i,0,'normal',config))
            if(np.size(variationSetNameList) > 0):
                if(variationSetNameList[-1] == i["set_name"] + " " + str(counter-1) or variationSetNameList[-1] == i["set_name"]):
                    variationSetNameList.append(i["set_name"]+" "+str(counter))
                    counter+=1
                else:
                    variationSetNameList.append(i["set_name"])
                    counter = 2
            else:
                variationSetNameList.append(i["set_name"])
            #cg.getCardIm(i,0,"normal")
        #populate the first one
        cg.getCardIm(variationCardList[0],0,'normal',config)
        
        pickVar = tk.Tk()
        pickVar.title("Select Printing, Number of Copies, and Pile")
        pickVar.minsize(width = 500, height = 750)
        pickVar.lift()
        varOptions = ttk.Combobox(pickVar,
                                  values = variationSetNameList,
                                  state='readonly',justify='center',
                                  width = 30)
        #build the image view portlet to display the card option at hand

        varOptions.current(0)
        varOptions.place(x=20,y=50)
        copiesLabel = tk.Label(pickVar,text="Number of Copies")
        copiesLabel.place(x=20,y=0)
        copiesEntry = tk.ttk.Entry(pickVar,width=10)
        copiesEntry.place(x=20,y=20)
        copiesEntry.insert(0,"1")
        
        pilesLabel = tk.Label(pickVar,text="Pile Number")
        pilesLabel.place(x=200,y=0)
        pilesEntry = tk.ttk.Entry(pickVar,width=10)
        pilesEntry.place(x=200,y=20)
        pilesEntry.insert(0,"0")
        
        initImage = Image.open(variationImList[0])
        #cardImage = ImageTk.PhotoImage(initImage)
        #cardImage = pl.ImageTk.PhotoImage(initImage)
        cardImage = ImageTk.PhotoImage(master=pickVar,image=initImage)
        cardPreview = tk.Canvas(pickVar,width=488,height=680)
        cardPreview.place(x=6,y=70)
        cardPreview.create_image(0,0,anchor=tk.NW,image=cardImage,tags='bg_img')
        
        def on_select(event=None):
            '''
            this should update the image below the combobox
            '''
            nonlocal initImage
            nonlocal cardImage
            nonlocal cardPreview
            nonlocal pickVar
            nonlocal varOptions
            global config
            targ = varOptions.current()
            folder = config["cardDumpPath"]+config["systemSlash"]+'*'
            cardDumpInv = glob.glob(folder)
            if( not variationImList[targ] in cardDumpInv):
                cg.getCardIm(variationCardList[targ],0,'normal',config)
            initImage = Image.open(variationImList[targ])
            cardImage = ImageTk.PhotoImage(master=pickVar,image=initImage)
            cardPreview.create_image(0,0,anchor=tk.NW,image=cardImage,tags='bg_img')
            cardPreview.update()
        varOptions.bind('<<ComboboxSelected>>',on_select)
        def selectCard():
            '''
            this returns the appropriate card image information
            '''
            nonlocal returnString
            nonlocal copiesEntry
            nonlocal pilesEntry
            selectedManifest = variationCardList[varOptions.current()]
            selectedManifest["copies"] = copiesEntry.get()
            selectedManifest["pileNumber"] = pilesEntry.get()
            returnString = generateListEntry(selectedManifest)
            pickVar.destroy()
            pickVar.quit()
        selectButton = tk.Button(pickVar,text="Confirm Selection",command = selectCard)
        selectButton.place(x = 340, y = 40)
        pickVar.mainloop()
        #at the end of this process, clean up your messy card options
    return returnString

def cardBackDialogTree():
    '''
    this function allows the user to navigate through the tree of things
    and select an image to use as a cardback
    '''
    global config
    config = df.loadConfig()
    
    outPath = filedialog.askopenfilename(initialdir=config["referenceImagesPath"],title="Select an image for your Card Backs" )
    return outPath

def cardHiddenFaceDialogTree():
    '''
    this function allows the user to navigate through the tree of things
    and select an image to use as a cardback
    '''
    global config
    config = df.loadConfig()
    
    outPath = filedialog.askopenfilename(initialdir=config["referenceImagesPath"],title="Select an image for your Card Hidden Faces" )
    return outPath

def editDeck():
    '''
    primary deck editing window
    '''
    
    global config
    config = df.loadConfig()
    master= tk.Tk()
    master.minsize(850,865)
    master.title("Deck Factory: List Editor")
    master.geometry("700x700")
    master.lift()
    
    #define text windows here
    listLabel = tk.Label(master,text = "Deck List Name:")
    listLabel.place(x=20,y=20)
    listTitle = tk.Entry(master, width = 54)
    listTitle.place(x=130,y = 20)
    listWindow = tkst.ScrolledText(master,width = 70, height = 48)
    listWindow.place(x=20,y=40)
    
    #define button functions here

    def printToListWindow(string):
        nonlocal listWindow
        listWindow.insert(tk.END,str(string))
        listWindow.update_idletasks()
    def setTitle(string):
        listTitle.delete(0,tk.END)
        listTitle.insert(0,string)
    def saveDeckList():
        filename = listTitle.get()#selection eliminates the \n
        targFile = config["deckListPath"]+config["systemSlash"]+cg.percentEncode(filename).replace(" ","_")+".csv"
        if(targFile in glob.glob(config["deckListPath"]+config["systemSlash"]+'*')):
            os.remove(targFile)
        with open(config["deckListPath"]+config["systemSlash"]+cg.percentEncode(filename).replace(" ","_")+".csv","w") as file:
            file.write(listWindow.get('1.0',tk.END))
        #master.destroy()
    def loadDeckList():
        deckFile = filedialog.askopenfilename(initialdir = config["deckListPath"],
                                               title = "Select Decks to load",
                                               filetypes = (("All Files","*.*"),
                                                           ("Manual Decklists","*.txt")
                                                            ))
        listWindow.delete("1.0",tk.END)
        if deckFile[-4:] == '.dck' :
            #importing an xmage deck
            importDeckList(deckFile)
        elif(not deckFile == ''):
            strippedName = sm.stripName(deckFile)[:-4]
            
            listWindow.delete('1.0',tk.END)
            listTitle.delete(0)
            listTitle.insert(tk.END,strippedName)
            with open(deckFile,'r') as file:
                lines = file.readlines()
                for i in lines:
                    printToListWindow(i)
                    
    def searchCard():
        searchArgs = searchParams.get()
        searchManifest = cg.searchByParameters(searchArgs)
        if "code" in searchManifest:
            #card wasn't found, search was incorrect
            warning = tk.Tk()
            warning.title("Warning: No Results")
            warning.minsize(width = 100, height = 100)
            warning.lift()
            warningLabel = tk.Label(warning,text="Your search brought back no results.\n Please check your search parameters")
            warningLabel.pack()
            
            closeButton = tk.Button(warning,text="Close",command = warning.destroy)
            closeButton.pack()
            warning.mainloop()
        else:#we have a search
            returnString = searchCardDialogTree(searchManifest)
                #at the end of this process, clean up your messy card options
            printToListWindow(returnString)
            searchParams.delete(0,tk.END)
    def searchCardEntry(event):
        searchCard()
    printToListWindow("#Collector # | SET | NAME | # COPIES | PILE # | SCRYFALL URI\n")
    searchParams = tk.Entry(master,width = 30)
    searchParams.place(x=620,y = 80)
    searchParams.bind('<Return>',searchCardEntry)
    
    
    def importDeckList(targDeck):
        '''
        the purpose of this is to import an xmage deck into the new format,
        that way we can make all those decks not have gone to waste
        '''
        global config
        cardMat = sm.readInFile(targDeck)
        printList = [] #this will be a list of strings designed for printing in the decklist
        importWindow = tk.Tk()
        importWindow.title("Importing Xmage Deck")
        importLabel = tk.Label(importWindow,text="Import Xmage deck: Warning, this may take a few moments to complete.")
        importLabel.pack()
        def importMatters():
            nonlocal cardMat
            nonlocal printList
            nonlocal importWindow
            importWindow.destroy()
            for i in cardMat:
                if(i.cardName == '' and i.cn == '' and i.setCode == ''):
                        1+1 #do nothing
                else:
                    tempData = []
                    flag1 = False
                    flag2 = False
                    try:
                        tempData = cg.searchCardByCN(i.cn,i.setCode)
                    except cg.ul.error.HTTPError:
                        flag1 = True #didn't find it 
                    if("code" in tempData):
                        flag1 = True
                    elif("data" in tempData and not tempData["data"][0]["name"] == i.cardName):
                        flag1 = True
                    if (flag1):
                        try:
                            tempData = cg.searchCardByName(i.cardName,i.setCode)
                        except cg.ul.error.HTTPError:
                            flag2 = True #didn't find it the second way
                            
                    if(flag1 and flag2):#we have a card that neither #+set or name+set works, try just name
                        try:
                            tempData = cg.searchByParameters(i.cardName)
                        except cg.ul.error.HTTPError as e:
                            print("YOU DONE GOOFED,and this shouldn't happen")
                            raise e
                        
                    if(tempData["total_cards"] == 1):
                        #special case, just use the card as listed:
                        i.cardData = tempData["data"][0]
                        printList.append(generateListEntry(i.cardData))
                    else:
                        if(i.cardName == '' and i.cn == '' and i.setCode == ''):
                            1+1 #do nothing
                        else:
                            warning = tk.Tk()
                            warning.title(i.cardName+ " was not found clearly")
                            warning.minsize(width = 100, height = 100)
                            warning.lift()
                            def warningOver():
                                warning.destroy()
                                warning.quit()
                            warningLabel = tk.Label(warning,text=i.cardName+ " was not found clearly, please select the correct card and version.")
                            warningLabel.pack()
                            closeButton = tk.Button(warning,text="Close",command = warningOver)
                            closeButton.pack()
                            warning.mainloop()
                            temp = searchCardDialogTree(tempData)
                            printList.append(temp)
            for i in printList:
                printToListWindow(i)
            deckName = sm.stripName(targDeck)[:-4]
            setTitle(deckName)
            importWindow.quit()
        startButton = tk.Button(importWindow,text="Start",command = importMatters)
        startButton.pack()
        importWindow.mainloop()
    #define buttons here
    exitButton = tk.Button(master,text='Exit', command = master.destroy,
                           bg='red',fg='white',
                           width=13,height=2)
    exitButton.place(x=620,y=650)
    addCardButton = tk.Button(master,text='Add a Card', command = searchCard,
                           bg='blue',fg='white',
                           width=13,height=2)
    addCardButton.place(x=620,y=100)
    loadListButton = tk.Button(master,text='Load Deck List', command = loadDeckList,
                           bg='blue',fg='white',
                           width=13,height=2)
    loadListButton.place(x=620,y=150)
    saveListButton = tk.Button(master,text='Save Deck List', command = saveDeckList,
                           bg='green',fg='white',
                           width=13,height=2)
    saveListButton.place(x=620,y=200)
    
    master.mainloop()

def cardAddDialog():
    '''
    this is the card adding dialog
    '''
    global config
    returnString = ''
    pane = tk.Tk()
    pane.minsize(width=400,height=150)
    pane.title("Add a Card")
    pane.geometry("400x300")
    pane.lift()
    
    instructions = tk.Label(pane,text="Please enter your search parameters")
    instructions.place(x=20,y=80)
    
    
    def killPane():
        nonlocal pane
        pane.destroy()
        pane.quit()
    
    def searchCard():
        searchArgs = searchParams.get()
        searchManifest = cg.searchByParameters(searchArgs)
        nonlocal returnString
        if "code" in searchManifest:
            #card wasn't found, search was incorrect
            warning = tk.Tk()
            warning.title("Warning: No Results")
            warning.minsize(width = 100, height = 100)
            warning.lift()
            warningLabel = tk.Label(warning,text="Your search brought back no results.\n Please check your search parameters")
            warningLabel.pack()
            
            closeButton = tk.Button(warning,text="Close",command = warning.destroy)
            closeButton.pack()
            warning.mainloop()
        else:#we have a search
            returnString = searchCardDialogTree(searchManifest)
                #at the end of this process, clean up your messy card options
            killPane()
    def searchCardEntry(event):
        searchCard()
    searchParams = tk.Entry(pane,width = 50)
    searchParams.place(x=20,y = 100)
    searchParams.bind('<Return>',searchCardEntry)
    cancelButton = tk.Button(pane,text='Cancel', command = killPane,
                           width=13,height=2)
    cancelButton.place(x=250,y=160)
    
    searchButton = tk.Button(pane,text='Search', command = searchCard,
                           bg='green',fg='white',
                           width=13,height=2)
    searchButton.place(x=20,y=160)
    pane.mainloop()
    cg.CleanUpCardDir(config)
    return returnString

def main():
    '''
    for now this is the main function, however we will build a seperate method
    for the external calling into this
    '''
    editDeck()
    
    

if __name__ == '__main__':
    main()