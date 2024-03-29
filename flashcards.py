from typing import List
import requests
import unidecode

'''
-------------
UTILS
-------------
'''


def getPartOfSpeechPrefix(wordLabel):
    abbrevs = {
        "adjective": "adj",
        "feminine noun": "n",
        "masculine noun": "n",
        "noun": "n",
        "adverb": "adv",
        "verb": "v",
        "intransitive verb": "iv",
        "transitive verb": "tv",
        "conjunction": "conj",
        "preposition": "prep",
        "interjection": "int",
        "masculine or feminine noun": "n",
        "invariable singular or plural masculine noun": "pl.m. n"
    }
    return abbrevs.get(wordLabel, wordLabel)


def cleanseAccents(word: str):
    pairs = [('á', 'a'),  ('é', 'e'), ('í', 'i'),
             ('ó', 'o'), ('ú', 'u'), ('ü', 'u'), ('ñ', 'n')]
    for (accented, clean) in pairs:
        word = word.replace(accented, clean)
    return word


def formatUrl(word, apiKey):
    return f'https://www.dictionaryapi.com/api/v3/references/spanish/json/{word}?key={apiKey}'


def formatOutput(spanishText, englishText, partOfSpeech):
    if (len(partOfSpeech) > 0):
        return f'"{spanishText}";"({partOfSpeech})\n{englishText}"\n'
    return f'"{spanishText}";"{englishText}"\n'


'''
-------------------
DICTIONARY MANAGER 
-------------------
'''


'''
-------------------
API INFO
-------------------
Sample request URL (try it in a browser!): 
https://www.dictionaryapi.com/api/v3/references/spanish/json/hola?key=3deabaf6-7c11-4b4a-b260-881c414eb911

(Limited to 1000 requests per day, be CAREFUL!)

API Response Format is:
  - list of results (one for each sense of the word)
  - each result is a dict
  - result['shortdef'] is a list of defs for that sense of the word
  - each def in shortdef is either "eng1, eng2" or "sp_word : eng_word"
      e.g.
          'shortdef': [
            "evil, wrong",
            "desgracia : misfortune"
          ]
'''
apiKey = "3deabaf6-7c11-4b4a-b260-881c414eb911"
#apiKey = "0e78a8cf-97ce-44c0-8a10-8ee923b2f495"


def getDataForWord(word: str):
    '''
    Make request to dictionary API & return all valid results
    '''
    print("...Making request for word", word)
    results = requests.get(formatUrl(word, apiKey)).json()

    # Check for plurals, or words not in Merriam Webster
    if (len(results) == 0 or not isinstance(results[0], dict)) or ' ' in word:
        # if word[-1] == 's' and len(results) > 0 and (results[0] == word[:-1] or results[0] == word[:-2]):
        #   print("--------Skipping plural---------")
        #   return ([], True)
        # else:
        return []

    validResults = [x for x in results if isValidDictionaryResult(x, word)]
    return validResults


def isValidDictionaryResult(result: dict, word: str):
    '''
    Check whether a result from the spanish dictionary is actually relevant to the given word
    '''
    try:
        metadata = result['meta']
        lang = metadata.get('lang', "")   # language of word
        id = metadata.get('id', "").split(":")[0]   # the base form of the word
    except (TypeError, KeyError) as e:
        print(e)
        return False
    return (lang == "es" and cleanseAccents(id) == cleanseAccents(word))


def getEnglishDefinition(dictResult):
    '''
    Creates a full English definition out of the list of En/Sp definitions provided
    '''
    def engOnly(x): return ":" not in x    # Filter out spanish synonyms
    shortDefs = dictResult['shortdef']   # the array of short definitions
    engDefs = list(filter(engOnly, shortDefs))
    # return ", ".join(engDefs)
    return engDefs[0] if len(engDefs) > 0 else ""


'''
------------
LABELER
------------
'''


def labelNoun(word: str, wordLabel: str, dictResult):
    # Check part of speech label
    if wordLabel == 'feminine noun':
        return "la " + word
    elif wordLabel == 'masculine noun':
        return "el " + word
    elif wordLabel == 'noun':
        # both gender case
        try:
            mascForm = word  # If it weren't it would have been filtered out
            femForm = dictResult['ahws'][0]['hw']
            print("Found feminine noun form", femForm)
            return "el " + mascForm + "\n" + "la " + femForm
        except:
            print("No feminine form found")
            return "un\\una " + mascForm
    # If not a noun, return it unchanged
    return word


def labelAdjective(word, wordLabel, dictResult):
    if wordLabel == 'adjective':
        try:
            mascForm = word
            femForm = dictResult['ahws'][0]['hw']
            print("Found feminine adj form", femForm)
            return mascForm + "\n" + femForm
        except:
            print("No feminine form found")
            return mascForm
    return word


def labelWord(word: str, wordLabel, dictResult):
    if 'noun' in wordLabel:
        return labelNoun(word, wordLabel, dictResult)
    if wordLabel == 'adjective':
        return labelAdjective(word, wordLabel, dictResult)
    return word


'''
------------
MAIN
------------
'''


class VocabEntry:
    def __init__(self, spText, enText, partOfSpeech):
        self.spText = spText
        self.enText = enText
        self.partOfSpeech = partOfSpeech


def processWord(word: str) -> List[VocabEntry]:
    '''
    Takes a word, and makes a list of VocabEntry objects to be output to the spreadsheet
    '''
    if (len(word) < 1):
        return []

    validResults = getDataForWord(word)
    print("Num results", len(validResults))

    # If no valid results in the dictionary, make an empty entry
    if len(validResults) == 0:
        return [VocabEntry(word, "", "")]

    # Make multiple entries
    vocabEntries = []
    for dictResult in validResults:
        wordLabel = dictResult.get('fl', "unknown label")

        # Label the words and get a definition with part of speech
        partOfSpeech = getPartOfSpeechPrefix(wordLabel)  # eg. "<adj>"
        labeledWord = labelWord(
            word, wordLabel, dictResult)  # eg. "el mesero \ la mesera"
        definition = getEnglishDefinition(
            dictResult)  # eg. "waiter, server"

        vocabEntries.append(VocabEntry(labeledWord, definition, partOfSpeech))

    return vocabEntries


def processList(rawWordList):
    outputString = ""
    vocabEntries = []

    for word in rawWordList:
        vocabEntries += processWord(word.strip())

    for entry in vocabEntries:
        if (len(entry.enText) == 0):
            entry.enText = input(f"\nCouldn't find a definition for:\n     {entry.spText}\nPress enter to skip this word, or type a quick definition:\n")
        if (len(entry.enText) == 0):
            continue    # if the user skips the word, don't add it
        outputString += formatOutput(
            entry.spText, entry.enText, entry.partOfSpeech) + "\n"
    return outputString


testList = input("Paste a semicolon-separated word list here:").split(";")

# testList = ["maraca", "cabeza"]

result = processList(testList)
print(result)

outputFile = open("flashcards-output.txt", "w+")
outputFile.truncate(0)
outputFile.write(result)
