import requests, bs4, os


# makes a txt file with just the table we are interested in (N.B. file name must include .txt)
def writeToTxt(content, txtFileName):
	text_file = open(txtFileName, "w")
	n = text_file.write(content)
	text_file.close()
# makes an HTML file from page provided and names it htmlFileName (N.B. the file name must include .html)
def makeHTMLFile(pageURL, htmlFileName):
	# gets the page
	res = requests.get(pageURL)
	res.raise_for_status()
	# creates the html file in directory (not technically needed I think)
	htmlFile = open(htmlFileName, 'wb')
	for chunk in res.iter_content(100000):
        	htmlFile.write(chunk)
	htmlFile.close()
# used for filtering out unneeded lines
def lineFilter(line):
	return len(line) > 4
# returns a txt file of opponents from the site
def getOppos(tableTXTFile, outputFileName):
	opponentsList = []
	# array with all lines in, mostly '\n'
	allLines = open(tableTXTFile, 'r').readlines()
	# removes all lines that have fewer than 4 characters (everything except team names)
	for elem in filter(lineFilter, allLines):
		opponentsList.append(elem)
	# creates the final file with just the names of all teams in the league
	tempFile = open(outputFileName, "w")
	tempFile.writelines(opponentsList)
	# can delete the table.txt here
	os.remove(tableTXTFile)
	return tempFile


# @@@@@@@@@@@@@@@ PULLING 1S OPPOS @@@@@@@@@@@@@@@
onesHTML = 'temp.html'
# pulls the HTML from site and makes a file called 'temp.html'
makeHTMLFile('https://www.south-league.com/results/league/hants11', onesHTML)
# creates the soup
exampleFile = open(onesHTML)
exampleSoup = bs4.BeautifulSoup(exampleFile, "html.parser")
# array of all tables on the page (including all tags etc)
# table 0 = contact details, table 1 = the results table (the one we want), table 2 & 3 = recent results, table 4 = league above (I think?), table 5 = league below (CONTAINS THE 2s!!)
tablesArray = exampleSoup.find_all('table')
#creates a txt of the 1s table called "1sTable.txt"
writeToTxt(tablesArray[1].get_text(), "1sTable.txt")
# plucks out relevant lines and writes them to a file
getOppos("1sTable.txt", "1sopponents.txt")




# @@@@@@@@@@@@@@@ PULLING 2S OPPOS @@@@@@@@@@@@@@@
twosHTML = 'temp.html' 
# pulls the HTML from site and makes a file called 'temp.html'
makeHTMLFile('https://www.south-league.com/results/league/hants12/2019-2020', twosHTML)

# creates the soup
exampleFile = open(twosHTML)
exampleSoup = bs4.BeautifulSoup(exampleFile, "html.parser")
tablesArray = exampleSoup.find_all('table')

#creates a txt of the 1s table called "2sTable.txt"
writeToTxt(tablesArray[1].get_text(), "2sTable.txt")
# plucks out relevant lines and writes them to a file
getOppos("2sTable.txt", "2sopponents.txt")


# @@@@@@@@@@@@@@@ PULLING 3S OPPOS @@@@@@@@@@@@@@@
threesHTML = 'temp.html' 
# pulls the HTML from site and makes a file called 'temp.html'
makeHTMLFile('https://www.south-league.com/results/league/hants14/2019-2020', threesHTML)

# creates the soup
exampleFile = open(threesHTML)
exampleSoup = bs4.BeautifulSoup(exampleFile, "html.parser")
tablesArray = exampleSoup.find_all('table')

#creates a txt of the 1s table called "3sTable.txt"
writeToTxt(tablesArray[1].get_text(), "3sTable.txt")
# plucks out relevant lines and writes them to a file
getOppos("3sTable.txt", "3sopponents.txt")



# @@@@@@@@@@@@@@@ REDUNDANT @@@@@@@@@@@@@@@

# will do all tables if true
if(False):
	for tableNumber in range(0, 6):
		print('\n','\n','\n', "table  ", tableNumber, '\n')
		print(tablesArray[tableNumber].get_text())


# def get1sOppos(tableTXTFile, outputFileName):
# 	opponentsList = []
# 	# array with all lines in, mostly '\n'
# 	allLines = open(tableTXTFile, 'r').readlines()
# 	# picking out teams based on specific index of where they appear in the file. Could probably be done bt filtering out any line with less than 4 chars if this becomes an issue
# 	for i in range(0, 12):
# 		if(i == 0):
# 			opponentsList.append(allLines[25])
# 		elif(i == 11):
# 			opponentsList.append(allLines[216])
# 		else:
# 			opponentsList.append(allLines[(27 + i*17)])
# 	# removing the '\n' from each element (commented out as when writing the list to a file it all appears on 1 line so having th '\n' might be helpful)
# 	# for elem in opponentsList:
# 	# 	opponentsList[opponentsList.index(elem)] = elem[:-1]

# 	# creates the final file with just the names of all teams in the league
# 	tempFile = open(outputFileName, "w")
# 	tempFile.writelines(opponentsList)
# 	return tempFile