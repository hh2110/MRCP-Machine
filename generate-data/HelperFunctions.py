import re
import json


def loadDictPerPage(pageNumber, doc):
    return doc.loadPage(pageNumber).getText('dict')


def saveHtmlPerPage(pageNumber, doc):
    html = doc.loadPage(pageNumber).getText('html')
    Html_file = open("{}.html".format(str(pageNumber)), "w")
    Html_file.write(html)
    Html_file.close()


def saveNumpyArrayInformationOfPDF(
    doc, fileName, requiredFontSize, requiredFont, requiredColour, pageNumbers
):
    s = []
    for pageNumber in range(pageNumbers['start'], pageNumbers['end']):
        currentDict = loadDictPerPage(pageNumber, doc)
        for block in currentDict['blocks']:
            try:
                for line in block['lines']:
                    for span in line['spans']:
                        if span['color'] in requiredColour \
                                and span['font'] in requiredFont \
                                and round(span['size'], 2) in requiredFontSize:
                            s.append(
                                {
                                    'text': span['text'].strip(),
                                    'colour': span['color'],
                                    'font': span['font'],
                                    'size': span['size']
                                }
                            )
            except:
                continue

    with open(fileName, 'w') as fout:
        json.dump(s, fout)


def resetRegion(regions, relevantRegion=None):
    # function to make all regions false and set the relevant region to tru
    regions = dict.fromkeys(regions, False)
    if relevantRegion:
        regions[relevantRegion] = True

    return regions


def setRegionPerHtmlItem(
        documentInformationFile, regions, textCSS
):
    # function to set the region of each item in the html list of items
    # by 2 methods:
    # 1-looking at the specific font/text(regex)/colour of a html item
    # 2-for those regions that cannot be identified by #1, then we
    # look at what came before the region
    questionNumberRegex = re.compile(r'Q: \d*')
    answerCommentsRegex = re.compile(r'Answer & Comments')
    regions = resetRegion(regions)
    for info in documentInformationFile:
        questionNumberSearch = questionNumberRegex.search(info['text'])
        answerCommentsSearch = answerCommentsRegex.search(info['text'])

        info['region'] = None

        # method #2 - looking at what came before
        if regions['questionDescription']:
            if info['colour'] == textCSS['questionNumberColour']:
                info['region'] = 'questionNumber'
            else:
                info['region'] = 'questionDescription'
        elif regions['question']:
            info['region'] = 'options'
        elif regions['answer']:
            info['region'] = 'answer'

        # method #1 - looking at colour, font, text(regex)
        if questionNumberSearch and info['colour'] == textCSS['questionNumberColour']:
            info['region'] = 'questionNumber'
            regions = resetRegion(regions, 'questionDescription')
        elif info['colour'] == textCSS['questionColour'] and info['font'] == textCSS['questionFont']:
            info['region'] = 'question'
            regions = resetRegion(regions, 'question')
        elif answerCommentsSearch and info['colour'] == textCSS['answerCommentColour']:
            info['region'] = 'answer'
            regions = resetRegion(regions, 'answer')

        # ignoring certain words (in header and footer)
        for stopWord in ['zohry', 'Questions', 'Sohag', '01118']:
            if stopWord in info['text']:
                info['region'] = None

        info['text'] = re.sub(' +', ' ', info['text'])

    return documentInformationFile


def createQuestionsList(
    emptyQuestionList, newQuestionDict, newRegionsDocumentInformationFile
):
    # function to store separate parts of a quesiton in a q list
    for item in newRegionsDocumentInformationFile:
        if item['region'] == 'questionNumber' and item['text'] != '' and item['text'][0] == '[':
            emptyQuestionList.append(newQuestionDict)
            newQuestionDict = {'questionNumber': '',
                               'questionDescription': '',
                               'question': '',
                               'options': '',
                               'answer': ''}

        for key in ['questionNumber', 'questionDescription',
                    'question', 'options', 'answer']:
            if item['region'] == key:
                newQuestionDict[key] += ' ' + item['text']

    return emptyQuestionList


def getQuestionNumber(text):
    # function to split questionNumberText and get only the number
    numberSearch = re.match(r'(.*):(\d*)(.*)]', text)
    if numberSearch:
        return int(numberSearch.group(3).strip())
    else:
        return None


def getQuestionOrigin(text):
    numberSearch = re.match(r'(.*)](.*)-(.*)$', text)
    if numberSearch:
        return numberSearch.group(2).strip()
    else:
        return None


def getQuestionTopic(text):
    numberSearch = re.match(r'(.*)](.*)-(.*)$', text)
    if numberSearch:
        return numberSearch.group(3).strip()
    else:
        return None


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def splitOptions(optionText):
    optionSearch = re.match(
        r'^(.*)1-(.*)2-(.*)3-(.*)4-(.*)5-(.*)$', optionText)
    if optionSearch:
        return {
            1: optionSearch.group(2).strip(),
            2: optionSearch.group(3).strip(),
            3: optionSearch.group(4).strip(),
            4: optionSearch.group(5).strip(),
            5: optionSearch.group(6).strip()
        }
    else:
        return None


def splitAnswer(answerText):
    # answerSearch = re.match(
    #     r'^(.*)Comments(.*)(\d-)(.*)', answerText[0:40].replace(' ', '')
    # )
    answerSearch = findFirstNumber(answerText)
    if answerSearch:
        number = answerSearch
        return {'number': number, 'description': answerText}
    else:
        return None


def findFirstNumber(inputString):
    for i in inputString:
        if isInt(i):
            return int(i)
        else:
            continue
    return None


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def splitQuestion(question):
    # split question number item up into number, origin and topic
    qNumber = getQuestionNumber(question['questionNumber'])
    qOrigin = getQuestionOrigin(question['questionNumber'])
    qTopic = getQuestionTopic(question['questionNumber'])
    # reset question-number,origin,topic
    question['qNumber'] = qNumber
    question['qOrigin'] = qOrigin
    question['qTopic'] = qTopic
    del question['questionNumber']
    return question


def cleanUpQuestionList(questionList):
    # function to clean up list of questions
    numberRemoved = 0
    newQList = []
    for question in questionList:
        # first split question details into number, topic, origin
        question = splitQuestion(question)

        # split up the options into a separate dictionary and only replace current
        # value in question if options is not None
        options = splitOptions(question['options'])
        if options:
            question['options'] = options

        # split answer into answer and number, text and explanation
        answer = splitAnswer(question['answer'])
        if answer:
            question['answerNumber'] = answer['number']
            question['answerDescription'] = answer['description']
            # del question['answer']

        # strip the qdescipriton, and question
        for key in ['questionDescription', 'question']:
            question[key] = question[key].strip()

        if question['qTopic'] == '':
            numberRemoved += 1
        else:
            newQList.append(question)

    return [questionList, numberRemoved]
