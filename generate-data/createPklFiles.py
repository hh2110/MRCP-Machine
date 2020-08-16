from HelperFunctions import saveNumpyArrayInformationOfPDF
import fitz

textCSS = {'questionNumberColour': 12867601, 'answerCommentColour': 28608,
           'textColour': 0, 'questionColour': 16711680,
           'textFont': 'ABCDEE+Calibri', 'questionFont': 'ABCDEE+Calibri,Italic',
           'fontSize': 11.04}

requiredFontSize = [textCSS['fontSize']]
requiredFont = [textCSS['textFont'], textCSS['questionFont']]
requiredColour = [textCSS['textColour'], textCSS['questionColour'],
                  textCSS['questionNumberColour'], textCSS['answerCommentColour']]

pageNumbers = {
    1: {'start': 34, 'end': 996},
    2: {'start': 14, 'end': 2139},
    # 3: {'start': , 'end': },
    4: {'start': 14, 'end': 2582},
    5: {'start': 14, 'end': 1097},
    6: {'start': 12, 'end': 1181}
}


for i in [1, 2, 4, 5, 6]:
    pdfFile = '../data/'+str(i)+'-questions.pdf'
    doc = fitz.open(pdfFile)
    saveNumpyArrayInformationOfPDF(
        doc, '{}.pkl'.format(str(i)),
        requiredFontSize, requiredFont, requiredColour,
        pageNumbers[i]
    )
