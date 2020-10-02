# Devoir 3 IFT6285
# Lucas Hornung
# Quentin Wolak
import csv
import re
import time

import numpy as np
import Levenshtein._levenshtein as lv
from minineedle import NeedlemanWunsch
from soundex import Soundex
from LCS import LCS
import jaro
#https://stackoverflow.com/questions/29054661/how-to-get-the-max-n-elements/29054704
import heapq


#------------------------- INITIALISATION -------------------------#

def readTextFile(path):
    text = open(path, "r")
    return text.read()

# Read a text file and transform it into an array with 1 word per cell
def sentenceToWordsArray(text):
    wordArray = re.findall(r'\w+', text.lower())
    #print(wordArray)

# Initiate a dictionary containing words for key and their frequence for value
def initiateDict(lexiquePath):
    lexique = open(lexiquePath, "r", encoding="utf8")

    lineArray = [] # Array containing line of the lexique

    for line in lexique:
        lineArray.append(line)

    freqDict = {}  # Frequency dictionnary

    for elem in lineArray:
        words = re.findall(r'[-a-zA-Z0-9_]+', elem)
        freqDict[words[1]] = int(words[0])

    return freqDict

# Dictionnary with format {word: frequence} type {String: int}
freqDict = initiateDict("./voc-1bwc.txt")

#------------------------- COMMON FUNCTIONS -------------------------#

# From https://norvig.com/spell-correct.html
def P(word, N=sum(freqDict.values())):
    #Modified here because if word is not present, il crashes
    if word in freqDict:
        return freqDict[word] / N
    else:
        return 0

#Modified P in order to take into account distances with scores (Ex: Jaro-Winkler)
def P_score(word, N=sum(freqDict.values())):
    # Word[0] is the candidate
    # Word[1] is the score
    if word[0] in freqDict:
        return (freqDict[word[0]] / N) * word[1]
    else:
        return 0

# From https://norvig.com/spell-correct.html
def correction(word, type):
    "Most probable spelling correction for word."
    corrections = []
    candidatesSet = candidates(word, type)

    if len(candidatesSet) > 0 and len(np.shape(candidatesSet)) == 2:
        #Takes the 3 best candidates (optimised)
        corrections = heapq.nlargest(3, candidatesSet, key=P_score)
        """
        for i in range(min(3, len(candidatesSet))):
            corrections.append(max(candidatesSet, key=P_score))
            # print(candidatesSet)
            candidatesSet.remove(corrections[i])
        """
    else:
        # Takes the 3 best candidates (optimised)
        corrections = heapq.nlargest(3, candidatesSet, key=P)
        """
        for i in range(min(3,len(candidatesSet))):
            corrections.append(max(candidatesSet, key=P))
            #print(candidatesSet)
            candidatesSet.remove(corrections[i])
        """

    return corrections

# From https://norvig.com/spell-correct.html
def candidates(word, type="hamming", topSimilarity=True):
    "Generate possible spelling corrections for word."
    if type == "hamming":
        return (known([word]) or known(hammingOneChange(word)) or known(hammingTwoChanges(word)) or [word]) #This is not hamming???
    elif type == "soundex":
        return (known([word]) or soundex(word) or [word])
    elif type == "LCS":
        return (known([word]) or lcs(word) or [word])
    elif type == "Jaro-Winkler":
        return (known([word]) or jaro_w(word, topSimilarity) or [word])
    elif type == "NeedleMan-Wunsch":
        return (known([word]) or needleman_w(word) or [word])
    elif type == "levenshtein":
        return (known([word]) or levenshteinClosest(word) or [word])
    else:
        return 0

# From https://norvig.com/spell-correct.html
# The argument words is an array containing strings and this function check whether a string exist in the dict or not
def known(words):
    "The subset of `words` that appear in the dictionary of freqDict."
    return set(w for w in words if w in freqDict)


#------------------------- HAMMING -------------------------#

# From https://norvig.com/spell-correct.html
# Create a set of every possible words with just one letter difference
def hammingOneChange(word):
    word = word.lower()
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    return replaces

# From https://norvig.com/spell-correct.html
# Create a set of every possible words with two letters difference
def hammingTwoChanges(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in hammingOneChange(word) for e2 in hammingOneChange(e1))

def hamming(word):
    result = correction(word, "hamming")
    print("Mot à corriger: " + word)
    return result


#------------------------- NEEDLEMAN WUNSCH -------------------------#

def needleman_wunsch(word_x, word_y):

    T = np.zeros((len(word_x), len(word_y)))

    return 0


#------------------------- LEVENSHTEIN -------------------------#

# Imported from https://github.com/ztane/python-Levenshtein/
# Documentation can be find https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html

# Calculate a list of the closest words using Levenshtein operations
# Try to build an array firstly with 1 operation, if not found then 2, then 3...
# If the number of operation is as many as there are characters in the word, then we return the word
def levenshteinClosest(word):
    operations = 1
    searching = True
    candidateArray = []
    while(operations < len(word)/2 and searching):
        for w in freqDict:
            if lv.distance(word, w) == operations:
                candidateArray.append(w)

        if len(candidateArray) == 0:
            operations += 1
        else:
            searching = False

    if searching == True:
        candidateArray.append(word)

    return candidateArray


def levenshtein(word):
    result = correction(word, "levenshtein")
    print("Mot à corriger: " + word)
    return result


print(lv.distance("Voiture", "Moteur"))

#------------------------- SOUNDEX -------------------------#
def soundex(word):

    word = word.capitalize()
    sound_candidates = []
    soundexScore = Soundex().soundex
    for c in freqDict:
        if (soundexScore(word) == soundexScore(c.capitalize())):
            sound_candidates.append(c)

    words = []
    for i in range(min(len(sound_candidates), 3)):
        words.append(max(sound_candidates, key=P))
        sound_candidates.remove(words[i])
    return words
    #    s = sound.compare(word, c)
     #   if s == 1 or s == 0:

    #return sound_candidates

#------------------------- LCS -------------------------#
def lcs(word):

    lcs_candidates = []
    for c in freqDict:
        lcs = LCS(word, c)
        lcs_candidates.append((c, lcs.get_LCS()))

    return lcs_candidates

#------------------------- Needleman Wunsch -------------------------#
def needleman_w(word):

    nw_candidates = []
    for c in freqDict:
        nw = NeedlemanWunsch(word, c)
        nw.align()
        nw_candidates.append((c, nw.get_score()))

    return nw_candidates

#------------------------- Jaro_Wrinkler -------------------------#
# I think that for Jaro-W, we have two possible choice to choose the best words.
# The way it works now, is that we have a dict with words ranking from the highest similiarity to the lowest
# excluding zero.
# So we have the choice to:
# - Return the 3 top similarity or
# - Take like the 10% best words and then in this 10% we take the 3 words that appear the most in the corpus

def jaro_w(word, topSimilarity):

    nw_candidates = {}
    for c in freqDict:
        similiarity = jaro.jaro_winkler_metric(word, c)
        if similiarity > 0.5:
            nw_candidates[c] = similiarity

    if len(nw_candidates) == 0:
        return [word]

    else:

        sorted_candidates_word_freq = sorted(nw_candidates.items(), key=lambda x: x[1], reverse=True)
        sorted_candidate_word = []

        for i in range(len(sorted_candidates_word_freq)):
            sorted_candidate_word.append(sorted_candidates_word_freq[i][0])

        words = []

        if topSimilarity:
            return sorted_candidate_word[0:min(3, len(sorted_candidate_word)-1)] # Les 3 premiers mots
        else:
            # sorted_candidate_word = sorted_candidate_word[0:min(3, len(sorted_candidate_word)/10+1)]
            sorted_candidate_word = sorted_candidate_word[0:min(3, len(sorted_candidate_word)-1)]
            for i in range(min(len(sorted_candidate_word), 3)):
                words.append(max(sorted_candidate_word, key=P))
                sorted_candidate_word.remove(words[i])
            return words

def benchmark(test_path, distance="Jaro-Wrinkler"):
    tsv_file = open(test_path, encoding="utf8")
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    match_1_cases = 0
    match_cases = 0
    total_cases = 0

    for row in read_tsv:
        elements = row
        best_cases = correction(elements[0], distance)
        #best_case = best_cases[0]
        #if best_case == elements[-1]:
        #testVl = elements[-1]
        if elements[1] in best_cases:
            match_cases += 1
        if elements[1] == best_cases[0]:
            match_1_cases += 1

        total_cases += 1
        print(total_cases)

    tsv_file.close()
    return (match_cases/total_cases, match_1_cases/total_cases)

if __name__ == "__main__":
    #text = readTextFile("/Users/quentinwolak/PycharmProjects/devoir3/test.txt")

    #print(freqDict["aaa-rating"])

    #print(hammingOneChange("Concombre"))
    #print(len(hammingOneChange("concombre")))

    #print(P("the"))
    #print(freqDict)
    #proba = hamming('thys')
    #print("Mots les plus probables: ")
    #for elem in proba:
    #    print("- " + elem)

    #print(" ")
    proba = levenshtein('begolf')

    #print("Jaro-Winkler en prenant compte des fréquences de mot")
    #proba = jaro_w('backgrounging', True)
    print("Mots les plus probables: ")
    for elem in proba:
        print("- " + elem)

    print("Jaro-Winkler sans prendre compte des fréquences de mot")
    proba = jaro_w('beholf', False)
    print("Mots les plus probables: ")
    for elem in proba:
        print("- " + elem)


    #Lucas Hornung
    #test_lcs = LCS("reccodmission", "recognition")
    #print(test_lcs.get_LCS())
    #nw_test = NeedlemanWunsch("reccodmission", "recognition")
    #nw_test.align()
    #print(nw_test.get_score())
    #sound = Soundex()
    #print(sound.compare("reccodmission", "recognition"))s
    #print(jaro.jaro_winkler_metric("reccodmission", "recognition"))
    #print(benchmark("./devoir3-train.txt", "Jaro-Wrinkler"))

    #print(benchmark("./devoir3-train.txt", "soundex"))

    distances = ["hamming", "levenshtein", "Jaro-Winkler", "NeedleMan-Wunsch", "soundex", "LCS"]

    for distance in distances:
        print("Calculating " + distance + " distance benchmark" + "\n")
        start_time = time.time()
        bench_results = benchmark("./devoir3-train.txt", distance)
        elapsed_time = time.time() - start_time
        file1 = open("BenchMarkResults_" + distance + ".txt", "w+")
        file1.write(distance + " Distance \n")
        file1.write("On best candidate only: " + str(bench_results[1]) + "\n")
        file1.write("On 3 best candidates: " + str(bench_results[0]) + "\n")
        file1.write("Run time (In seconds): " + str(elapsed_time) + "\n")
        file1.close()
