


class Card{

    constructor(){
        this.cardName         = '';
        this.cn               = '';
        this.setCode          = '';
        this.ambiguous        = false;
        this.notFindable      = false;
        this.copies           = 1;
        this.pileNumber       = 0;
        this.loadedFromJson   = false;
        this.selectedFace     = 0;    // Front face by default
        this.deckIndex        = 100;
        this.cardData         = '';   // json profile of the card from Scrfall
    }

    convertToTTSCard(){
        // Takes appropriate information and converts 
        // it to a json containing card data
        cardJSON = {};
        cardJSON['Name'] = 'Card';

        if(!this.cardData.includes('card_faces')){
            cardJSON['Nickname'] = this.cardData['name'];
            cardJSON['Description'] = this.cardData['type_line'] + '\n\n' + 
                                      this.cardData['oracle_text'].replace('\\n'
                                      , '\n\n');
            
            if(this.cardData.includes('power')){
                cardDict['Description'] += '\n\n' + this.cardData['power'] +
                                           '/' + self.cardData['toughness'];
            }
        }
        else{
            let card_face = this.cardData['card_faces'][this.selectedFace];
            cardJSON['Nickname'] = card_face['name'];
            cardJSON['Description'] = card_face['type_line'] + '\n\n' +
                                      card_face['oracle_text'].replace('\\n' 
                                      , '\n\n');

            if(card_face.includes('power')){
                cardDict['Description'] += '\n\n' + card_face['power'] +
                                           '/' + card_face['tougheness'];
            }
                                      
        }
        cardDict['Transform'] = {'posX':0,   'posY':0,   'pozZ':0,
                                 'rotX':0,   'rotY':180, 'rotZ':180,
                                 'scaleX':1, 'scaleY':1, 'scaleZ':1};
        
        return cardDict;
    }

    debugPrint(){
        console.log("____________________________")
        console.log("cardName:".padEnd(20,' '),        this.cardName)
        console.log("cn:".padEnd(20,' '),              this.cn)
        console.log('setCode:'.padEnd(20,' '),         this.setCode)
        console.log('ambiguous:'.padEnd(20,' '),       this.ambiguous)
        console.log('notFindable:'.padEnd(20,' '),     this.notFindable)
        console.log('copies:'.padEnd(20,' '),          this.copies)
        console.log('pileNumber:'.padEnd(20,' '),      this.pileNumber)
        console.log('loadedFromJson:'.padEnd(20,' '),  this.loadedFromJson)
        console.log('selectedFace:'.padEnd(20,' '),    this.selectedFace)
        console.log('deckIndex:'.padEnd(20,' '),       this.deckIndex)
        console.log('cardData:'.padEnd(20,' '),        this.cardData)
        console.log("____________________________\n")
    }
}

function copyCard(cardFrom, cardTo){
    cardTo.cardName         = cardFrom.cardName;
    cardTo.cn               = cardFrom.setCode;
    cardTo.setCode          = cardFrom.ambiguous;
    cardTo.ambiguous        = cardFrom.notFindable;
    cardTo.notFindable      = cardFrom.notFindable;
    cardTo.copies           = cardFrom.copies;
    cardTo.pileNumber       = cardFrom.pileNumber;
    cardTo.cardData         = cardFrom.cardData;
    cardTo.loadedFromJson   = cardFrom.loadedFromJson;
}

let alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
                'q','r','s','t','u','v','w','x','y','z'];

//function RepresentsInt(s){
// (just do isInteger() method)


function percentEncode(string){
    let ret = string.replace('!','%21')
    ret = ret.replace('#','%23')
    ret = ret.replace('$','%24')
    ret = ret.replace('&','%26')
    ret = ret.replace("'",'%27')
    ret = ret.replace('(','%28')
    ret = ret.replace(')','%29')
    ret = ret.replace('*','%2A')
    ret = ret.replace('+','%2B')
    ret = ret.replace(',','%2C')
    ret = ret.replace('/','%2F')
    ret = ret.replace(':','%3A')
    ret = ret.replace(';','%3B')
    ret = ret.replace('=','%3D')
    ret = ret.replace('?','%3F')
    ret = ret.replace('@','%40')
    ret = ret.replace('[','%5B')
    ret = ret.replace(']','%5D')

    return ret
}


export function getUrl(cardName, setName){
    // Search a particular set version of a card and return the url to the image
    // of said card

    //use |number if using a collector's number
    let colNum = false;
    if(cardName[0]=='|'){
        colNum = true;
    }
    let refString = 'https://api.scryfall.com/cards/search?q='
    // percent Encoding the name string
    let temp = percentEncode(cardName);
    if(setName != ''){
        if(colNum){
            temp = '';
        }
        temp += "+e%3A" + setName
        if(colNum){
            temp += "+cn%3A" + cardName.slice(1).replace(" ","");
        }
    }
    temp = temp.replace(' ', '+');
    return refString + temp;
}


/* NOTE: Since sheet generation can be entirely done in an HTML canvas, there is
no need to save images locally and so this function is likely not needed (same
goes for getCardIm() ). Regardless, I have adapted it in JS here just in case */

// function saveName(cardManifest, face, imType, config){

//     extension = '.jpg';
//     if(imType == 'png'){
//         extension = '.png';
//     }
//     destination = config['cardDumpPath'] + 
//                   config['systemSlash']

//     if(cardManifest.includes('card_faces') && 
//        !cardManifest.includes('image_uris')){
//         temp = percentEncode(cardManifest['card_faces'][face]['name'] + 
//                              cardManifest['set'] +
//                              cardManifest['collector_number']).replace(' ','_');
//     }
//     else{
//         temp = percentEncode(cardManifest['name'] + cardManifest['set'] +
//                              cardManifest['collector_number']).replace(' ','_');
//     }
//     return destination + temp + extension;
// }


export function searchCardByName(cardName, setName){
    /* Sends a fetch request to the scryfall API and returns a promise 
    to the JSON card object */

    let url = getUrl(cardName, setName);
    return fetch(url).then(response => response.json());
}



export function searchCardByCN(cn, setName){
    return searchCardByName('|'+cn,setName);
}



function searchByParameters(args){
    /* Search through scryfall search system using a set of arguments.
    
    Returns a promise to an array filled with card json objects that are
    contained across various webpages on the scryfall API. */
    let url = "https://api.scryfall.com/cards/search?q=" + 
               percentEncode(args).replace(' ','+')

    return fetch(url).then(response => {
        if(response.status >= 200 && response.status < 300){
            return response.json().then(sf_json => {
                let data = sf_json['data'];
                return appendCardPages(data, sf_json, 0);
            });
        }
        else{
            return Promise.resolve({'code':'404'});
        }
    });
}


// TODO: Check with Ben to make sure this function works as intended. 
function getCardManifest(uri){
    /* Given an extra URI, retrieve that extra's json 

    Returns a promise to an array filled with card json objects that are
    contained across various webpages on the scryfall API. */

    return fetch(uri).then(response => {
        return response.json().then(sf_json => {
            let data = sf_json['data'];
            return appendCardPages(data, sf_json, 0);
        });
    });
}



function appendCardPages(data, sf_json, f){
    /* Recursive function which traverses pages of the scryfall API, appending
    cards on each page to an array "data". 

    Recursively returns a promise to data.*/
    return new Promise(resolve => {
        if(f != 0){
            data = data.concat(sf_json['data']);
        }
        if(sf_json['has_more'] == true){
            resolve(fetch(sf_json['next_page'])
                          .then(response => response.json())
                          .then(sf_json => appendCardPages(data, sf_json, 1)));
        }else{
            resolve(data);
        }
    });   
}


// CleanUpCardDir

