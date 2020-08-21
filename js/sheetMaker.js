import {Card} from './cardGetter.js'

const input = document.getElementById('input-file')


let alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
                'q','r','s','t','u','v','w','x','y','z']


function xMageFile(file){
    let cardMat = new Array();

    let lines           = file.split('\n');
    let xmagePileNum    = 0;

    for(let i = 0, il = lines.length; i < il; i++){
        console.log(lines[i]);
        if(lines[i].startsWith('LAYOUT MAIN:')) break;
        cardMat[i]          = new Card();

        // Grabbing everything except for the # of cards. 
        const targReg       = lines[i].match( /\[(\S)*\]((\s)*(\S)*)*/)[0];
        // Grabbing just the set name
        let setN            = lines[i].match( /\[(\S)*\:/)[0].slice(1, -1);

        // Account for XMage silliness
        let doubleFacedSets = ['rix','soi','dka','xln','isd','emn','ori','m19'];
        switch(setN.toLowerCase()){
            case('gur'):  //guru lands
                setN = 'pgru'; break;
            case('dd3dvd'): //duel decks: divine vs demonic
                setN = 'dvd'; break;
            case('dd3jvc'): //duel decks: jace vs chandra
                setN = 'jvc'; break;
            case('dd3evg'): //elves vs goblins
                setN = 'evg'; break;
            case('cp'): //champions and states
                setN = 'pcmp'; break;
            case('gpx'): //grand Prix Promos
                setN = 'pgpx'; break;
            default:
                setN = setN.toLowerCase();
        }

        cardMat[i].setCode  = setN;
        let cNum            = lines[i].match(/\:(\S)*\]/)[0].slice(1,-1);

        // Check if this is a double faced card
        if(alphabet.includes(cNum.slice(-1)) && doubleFacedSets.includes(setN)){
            cNum            = cNum.slice(0,-1);
        }
        let copies = lines[i].split(' ')[0];

        // Check if this is a sideboarded card
        if(copies == 'SB'){
            copies          = lines[i].split(' ')[1]
            xmagePileNum    = 1;
        }

        let cName = lines[i].match(/\]((\s)*(\S)*)*/)[0].slice(1,-1);

        cardMat[i].cardName     = cName
        cardMat[i].cn           = cNum;
        cardMat[i].copies       = parseInt(copies);
        cardMat[i].pileNumber   = xmagePileNum;
        
    }

    return cardMat
}



function readInFile(file, fileName){

    let fileType;
    let cardMat;
    console.log(fileName);
    if(fileName.endsWith('.dck') ){
        fileType = Xmage;
        cardMat  = xMageFile(file);
    }
    // TODO: Finish writing functions for reading in .json, .csv, .txt., etc.
    // else if(fileName.endsWith('.json') ){

    // }
    // else if(fileName.endsWith('.csv') ){

    // }

    return cardMat, fileType;
}




// function buildSheet(file, fileName, ){
    
// }










input.addEventListener('input', function(e){

    const reader = new FileReader();
    reader.readAsText(input.files[0])

    reader.addEventListener('load', function(e){
        let data = reader.result;
        readInFile(data, input.files[0].name)

    });
    
});
