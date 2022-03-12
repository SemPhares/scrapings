def extractTextPdf(pathPDF,nameFileText):
    """
        use this function to extract text in pdf and save  this text in nameFileText
        @param pathPDF: is the path to the pdf file
        @param nameFileText: the path as well as the name or the file will be downloaded       
    """    
    metaData = dict()

    try:
        text_file = open(nameFileText+".txt", "w")
        pdfRead = pdfplumber.open(pathPDF)

        for i in range(len(pdfRead.pages)):
            texteContain = pdfRead.pages[i].extract_text()
            text_file.write(texteContain)
        
        try:
            metaData["creationDate"] = pdfRead.metadata["CreationDate"]
        except:
            pass
        try:
            metaData["keywords"] = pdfRead.metadata["Keywords"]
        except:
            # print('ok')
            pass
        try:
            metaData["autors"] = pdfRead.metadata["Author"]
        except:
            pass
        try:
            metaData["subjectDoc"] = pdfRead.metadata["Subject"]
        except:
            pass
        try:
            metaData["title"] = pdfRead.metadata["Title"]
        except:
            pass
        try:
            metaData["pathPdfFile"] = pathPDF
        except:
            pass

        try:
            metaData["pathTextExtractor"] = nameFileText
        except:
            pass

        text_file.close()

    except:

        print("Error Save Text Pdf")
        return "ERROR"

    return nameFileText+".txt",metaData