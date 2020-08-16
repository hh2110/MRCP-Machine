from HelperFunctions import (
    setRegionPerHtmlItem, saveNumpyArrayInformationOfPDF,
    createQuestionsList, cleanUpQuestionList
)
import json
import sys
import re

textCSS = {'questionNumberColour': 12867601, 'answerCommentColour': 28608,
           'textColour': 0, 'questionColour': 16711680,
           'textFont': 'ABCDEE+Calibri', 'questionFont': 'ABCDEE+Calibri,Italic',
           'fontSize': 11.04}

requiredFontSize = [textCSS['fontSize']]
requiredFont = [textCSS['textFont'], textCSS['questionFont']]
requiredColour = [textCSS['textColour'], textCSS['questionColour'],
                  textCSS['questionNumberColour'], textCSS['answerCommentColour']]

for fileNumber in [1, 2, 4, 5, 6]:
    # constants
    regions = {
        'questionNumber': False,
        'questionDescription': False,
        'question': False,
        'option': False,
        'answer': False,
        'explanation': False
    }
    newQuestion = {'questionNumber': '',
                   'questionDescription': '',
                   'question': '',
                   'options': '',
                   'answer': ''}
    emptyQuestionList = []

    with open("../data/{}.pkl".format(str(fileNumber)), "r") as read_file:
        documentInformationFile = json.load(read_file)

    # get list of questions
    newRegionsDocumentInformationFile = setRegionPerHtmlItem(
        documentInformationFile, regions, textCSS
    )

    questionList = createQuestionsList(
        emptyQuestionList, newQuestion, newRegionsDocumentInformationFile
    )

    [cleanQuestionList, numberRemoved] = cleanUpQuestionList(questionList)

    print('{}/{} questions were removed for file {}.'.format(
        numberRemoved, len(questionList), str(fileNumber))
    )

    with open('../data/cleanQuestionList-{}.json'.format(str(fileNumber)), 'w') as fout:
        json.dump(cleanQuestionList, fout)


# 147/19889 questions ignored
