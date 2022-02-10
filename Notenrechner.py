# importing all the required modules
import argparse
import sys
import PyPDF2


def argparser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help=".pdf file von deinem Notenspiegel", required=True)
    parser.add_argument("--hauptstudium", action='store_true', default=False, help="Aktivieren um Hauptstudiumsschnitt zu berechnen.")
    parser.add_argument("--grundstudium", action='store_true', default=False, help="Aktivieren um Grundstudiumsschnitt zu berechnen.")
    parser.add_argument("--zusatz", nargs="+", help="Für Zusatzfächer, die nicht zum Schnitt dazu zählen")
    return parser.parse_args(args)


def createNotenList(l, n):
    notenList = list()
    n = max(1, n)
    SubjectObject = (l[i:i + n] for i in range(0, len(l), n))
    for subject in SubjectObject:
        notenList.append(subject)
    return notenList


def readPDF(pdfFile):
    # creating an object
    file = open(pdfFile, 'rb')

    # creating a pdf reader object
    fileReader = PyPDF2.PdfFileReader(file)

    pageObj = fileReader.getPage(0)
    text = pageObj.extractText()
    words = text.split('\n')
    return words


def calculateGrade (markedZusatzFach, gradeList, gradeSum, cpSum):
    for fach in gradeList:
        if fach[0] in markedZusatzFach:
            continue

        CreditPoints = float(fach[1])
        Grade = float(fach[2])
        cpSum = cpSum + CreditPoints
        gradeSum = gradeSum + CreditPoints * Grade

    avg = gradeSum / cpSum
    return avg, cpSum


def getSubjects(words, checkPoint):
    subjectList = list ()
    cnt = 0
    for word in words:
        cnt += 1
        # 17 is the number where the first subject begins
        # 22 maschinenbau
        if cnt == 17:
            checkPoint = True
        if word == '* anerkannt, nicht an der Hochschule Esslingen erbracht':
            break
        if checkPoint:
            subjectList.append(word)
    return subjectList

def removeLabs(orderedSubjectList, zusatzFach):
    gradeList = list()
    markedZusatzFach = list()
    for elem in orderedSubjectList:
        # skip zusatz fach
        if zusatzFach:
            for zusatzFach_ in zusatzFach:
                if zusatzFach_ in elem[0]:
                    markedZusatzFach.append(elem[0])
                    continue

        # skip labs
        if 'Labor' in elem[0] or elem[2] == 'be':
            continue
        else:
            gradeList.append(elem)

    return gradeList, markedZusatzFach


def main():
    args = argparser(sys.argv[1:])
    pdfFile = args.file
    zusatzFach = args.zusatz

    words = readPDF(pdfFile)

    checkPoint = False

    subjectList = getSubjects(words, checkPoint)
    orderedSubjectList = createNotenList(subjectList, 3)

    gradeList, markedZusatzFach = removeLabs(orderedSubjectList, zusatzFach)

    # filter out grades from hauptstudium
    markerHauptstudium = 0
    gradeListHauptStudium = list()

    for elem in gradeList:
        if markerHauptstudium:
            gradeListHauptStudium.append(elem)
            continue
        if 'Betriebswirtschaftslehre' in elem[0]:
            markerHauptstudium = 1

    gradeListGrundStudium = list ()
    markerGrundstudium = 0;

    for elem in gradeList:
        if not markerGrundstudium:
            gradeListGrundStudium.append(elem)
        if 'Betriebswirtschaftslehre' in elem[0]:
            markerGrundstudium = 1


    # replace ',' in order to calculate later on
    for elem in gradeList:
        elem[2] = elem[2].replace(",", ".")

    gradeSum, cpSum, gradeSumHP, cpSumHP, gradeSumG, cpSumG = 0, 0, 0, 0, 0, 0

    #Prognose Section
    '''
    gradeList.append(['statistik', 4, 3])
    gradeList.append(['mathe2', 4, 3])
    gradeList.append(['et2', 4, 3])
    '''

    avg, cpSum = calculateGrade(markedZusatzFach, gradeList, gradeSum, cpSum)
    if args.hauptstudium:
        avgHP, cpSumHP = calculateGrade(markedZusatzFach, gradeListHauptStudium, gradeSumHP, cpSumHP)
    if args.grundstudium:
        avgG, cpSumG = calculateGrade(markedZusatzFach, gradeListGrundStudium, gradeSumG, cpSumG)

    if not args.grundstudium and not args.hauptstudium:

        print("{:<35} {:<25} {:<5}".format('Fach', 'CP', 'Note'))
        print("------------------------------------------------------------------------------")
        for fach in gradeList:
            subject, creditPoints, grade = fach
            if subject in markedZusatzFach:
                continue
            print("{:<35} {:<25} {:<5}".format(subject, creditPoints, float(grade)))
        print("------------------------------------------------------------------------------")
        print("{:<35} {:<25} {:<5}".format("Durchschnitt-Gesamt:", int(cpSum), round(avg, 3)))



    if args.hauptstudium:
        print()
        print()
        print("{:<35} {:<25} {:<5}".format('Fach', 'CP', 'Note'))
        print("------------------------------------------------------------------------------")
        for fach in gradeListHauptStudium:
            subject, creditPoints, grade = fach
            if subject in markedZusatzFach:
                continue
            print("{:<35} {:<25} {:<5}".format(subject, creditPoints, float(grade)))
        print("------------------------------------------------------------------------------")
        print("{:<35} {:<25} {:<5}".format("Durchschnitt-Hauptstudium:", int(cpSumHP), round(avgHP, 3)))

    if args.grundstudium:
        print()
        print()
        print("{:<35} {:<25} {:<5}".format('Fach', 'CP', 'Note'))
        print("------------------------------------------------------------------------------")
        for fach in gradeListGrundStudium:
            subject, creditPoints, grade = fach
            if subject in markedZusatzFach:
                continue
            print("{:<35} {:<25} {:<5}".format(subject, creditPoints, float(grade)))
        print("------------------------------------------------------------------------------")
        print("{:<35} {:<25} {:<5}".format("Durchschnitt-GrundStudium:", int(cpSumG), round(avgG, 3)))

    if args.zusatz:
        print("\nMarkierte Zusatzfächer, welche nicht gewertet wurden:")
        for markedZusatzFach_ in markedZusatzFach:
            print("  {}".format(markedZusatzFach_))


if __name__ == "__main__":
    main()
