"""
Adreanna LaPorte
ISE 150, Spring 2019
alaporte@usc.edu
hw 7
"""
import random


def loadWords(wordFileName):

    """
    loads the words form the file
    :param wordFileName: file to load words from
    :return: a list of the words
    """

    wordFile = open("words.txt", "r")

    if wordFileName == "words.txt":
        wordList = []

        for line in wordFile:
            line = line.strip()
            wordList.append(line)

        return wordList

    wordFile.close()


def loadArt(artFileName):

    """
    loads the art from the file
    :param artFileName: file to load art from
    :param artIndex: a list of the art
    :return:
    """

    artFile = open("art.txt", "r")
    artList = []

    if artFileName == "art.txt":

        for line in artFile:
            line = line.strip()
            line = line.replace('\\n', '\n')
            line = line.replace('\\\\', '\\')
            artList.append(line)

        return artList
    artFile.close()


def addWord(addWords, wordList):

    """
    addWords to add to wordList if it doesn't already exist
    :param addWords: the word we are adding
    :param wordList: the list we are adding to
    :return: success value (if it was added)
    """

    # addWords = input("Enter a word to add to the word list: ")
    if addWords not in wordList:
        wordList.append(addWords.lower())
        wordList.sort()
        # print("Added the word \"" + addWords.lower() + "\"")
        return True
    else:
        # print("The word \"" + addWords.lower() + "\" is already in the list!")
        return False


def storeWords(wordFileName, wordList):

    """
    save the words in a list in wordList to the file
    hint : you need to iterate through the wordList
    :param wordFileName: file to save words to
    :param wordList: the words to save
    :return: none
    """

    wFile = open(wordFileName, "w")
    for line in wordList:
        wFile.write(line + "\n")

    wFile.close()
    print("Storing words...")


def pickWord(wordList):

    """
    get a random element from from the list
    :param wordList: the list of things
    :return: randomly selected element
    """

    index = random.randrange(len(wordList))
    word = wordList[index]
    print(word)
    return word


def genEmpties(word):

    """
    this should not take userGuess??
    creates list of underscores with len equal to len(word)
    :param word: string
    :return: list of underscores
    """
    underScoreList = []

    for x in range(len(word)):
        underScoreList.append("_")

    return underScoreList


def setToString(lettersGuessSet):

    """
    1. convert set to list
    2. sort list
    3. make list into pretty string
    :param lettersGuessSet: set of letters already guessed
    :return: pretty string
    """

    lettersList = list(lettersGuessSet)

    lettersList.sort()

    lettersString = " ".join(lettersList)

    return lettersString


def gameOver(underScoreList):

    """
    list of each letter in the words where underscores represent letters not yet guessed
    :param underScoreString:
    :return:
    """
    if "_" in underScoreList:
        return False
    else:
        return True


def checkGuess(word, underScoreList, userGuess):

    """

    :param userGuess: letters user is guessing
    :param word: random word they are trying to guess
    :param underScoreList: list of underscores
    :return:
    """
    replaceTheLetter = False
    indexesToReplace = []
    counter = 0
    for x in range(len(word)):
        if word[x] == userGuess:
            indexesToReplace.append(x)
            counter += 1

    for index in indexesToReplace:
        underScoreList[index] = userGuess
        replaceTheLetter = True

    if counter == 0:
        print(f"Didn't find any \"{userGuess}\"")
    else:
        print(f"Found {str(counter)} \"{userGuess}\"")

    return replaceTheLetter

# checkGuess('p', 'apple', ['_', '_', '_', '_', '_'])


def main():

    wordFileName = input("Word file name: ")

    artFileName = input("Art file name: ")

    wordListVariable = loadWords(wordFileName)

    userInput = "blah"

    while userInput:

        userInput = input("\nPick an option...\n"
                              "1) Play Hangman\n"
                              "2) Add to word list\n"
                              "?) Quit \n "
                              "> ")
        # if the user wants to play hangman we go here

        if userInput == "1":
            print("Let's Play HANGMAN!\n")

            # calling functions and assigning to variables before beginning game loop

            randomWord = pickWord(wordListVariable)

            artFileVariable = loadArt(artFileName)

            underScoreDisplay = genEmpties(randomWord)

            endGame = gameOver(underScoreDisplay)

            wrongGuessCounter = 0

            guessedLettersSet = set()

            # beginning game loop

            while wrongGuessCounter < (len(artFileName)-1) and gameOver(underScoreDisplay) == False:

                print(artFileVariable[wrongGuessCounter])
                # displaying art ^

                guessedLetters = setToString(guessedLettersSet)

                print("You've already guessed these letters: \n " + guessedLetters)
                # displaying letters guessed ^

                stringUnderScoreDisplay = " ".join(underScoreDisplay)
                # making list into string ^

                print("Your word is \" {} \" ".format(stringUnderScoreDisplay))
                # displaying underscores and letters guessed combination as a string

                userGuess = input("Letter please: ").lower()
                # calling function that replaces underscores and letters

                if userGuess in guessedLettersSet:
                    print("You've already guessed \"{}\"".format(userGuess))
                    wrongGuessCounter += 1
                    continue

                guessedLettersSet.add(userGuess)

                if not checkGuess(randomWord, underScoreDisplay, userGuess):
                    wrongGuessCounter += 1

                # if letter not already guessed, adding it to guessed letter display
                # if userGuess is not a letter in the alphabet

                # this is what i used to index the art list

                if userGuess == "":
                    print("Returning to main menu...")
                    break
                # breaks out of loop if the user hits enter

                if len(userGuess) > 1:
                    print("You can only guess 1 letter!")
                    continue
                # goes back to beginning of game loop if the user enters more than one character

            print("Game over!!")
            if wrongGuessCounter >= (len(artFileName)-1):
                print(f"You lose! \n The word was \"{randomWord}\"")
                # if we are out of index range for art list this will tell you that you lost

            if gameOver(underScoreDisplay) == True:
                print(f"You win! \n You discovered the word \"{randomWord}\"")
                # if there are no more underscores in the letter/underscore list then game is over

        # second option to add words

        elif userInput == "2":
            addWords = input("Enter a word to add to the word list: ")

            if addWord(addWords, wordListVariable) == True:
                print("Added the word \"" + addWords.lower() + "\"")
            else:
                print("The word \"" + addWords.lower() + "\" is already in the list!")

        else:
            storeWordsVariable = storeWords(wordFileName, wordListVariable)
            break

    print("Goodbye!")


main()
