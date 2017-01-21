# ---------- IMPORTS ----------
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import sys
import time
import csv

# ---------- GLOBALS ----------

def toXpath(tag, attribute, contains):
	return "//{}[contains({}, '{}')]".format(tag, attribute, contains)

PAGE_LOAD_TRIES = 15

STARTIME_DROPDOWN_XPATH = "//select[@id='SSR_CLSRCH_WRK_SSR_START_TIME_OPR$7']/option[text()='is exactly']"
STARTTIME_INPUTBOX_XPATH = toXpath("input", "@id", "SSR_CLSRCH_WRK_MEETING_TIME_START$7")
NO_RESULTS_WARNING_XPATH = toXpath("span", "@id", "DERIVED_CLSMSG_ERROR_TEXT")
COURSE_DIVS_XPATH = toXpath("div", "@id", "win0divSSR_CLSRSLT_WRK_GROUPBOX2$")
SECTION_TABLEROW_XPATH = toXpath("tr", "@id", "trSSR_CLSRCH_MTG1$")

browser = webdriver.Firefox()

# ---------- HELPERS ----------

def get_elem(tag, attribute, contains):
	return get_elem_by_xpath(toXpath(tag, attribute, contains))

def get_subelem(elem, tag, attribute, contains):
	return get_elem_by_xpath('.'+toXpath(tag, attribute, contains), element=elem)

def get_subelem_by_xpath(elem, xpath):
	return get_elem_by_xpath(xpath, element=elem)

def get_elem_by_xpath(xpath, element=browser):
	print("looking for "+xpath)
	for errorCount in range(0, PAGE_LOAD_TRIES-1):
		try:
			return element.find_element_by_xpath(xpath)
		except:
			print("looking for " + xpath)
			time.sleep(1)

	return element.find_element_by_xpath(xpath)

def get_elems(tag, attribute, contains):
	return get_elems_by_xpath(toXpath(tag, attribute, contains))

def get_subelems(elem, tag, attribute, contains):
	return get_elems_by_xpath('.'+toXpath(tag, attribute, contains), element=elem)

def get_subelems_by_xpath(elem, xpath):
	return get_elems_by_xpath(xpath, element=elem)

def get_elems_by_xpath(xpath, element=browser):
	print("looking for "+xpath)
	for errorCount in range(0, PAGE_LOAD_TRIES):
		elements = element.find_elements_by_xpath(xpath)

		if len(elements) > 0:
			return elements
		else:
			print("looking for "+xpath)
			time.sleep(1)
	raise NoSuchElementException(xpath)

def switch_frame():
	errorCount = 0
	while True:
		try:
			browser.switch_to.frame("ptifrmtgtframe")
			break
		except Exception:
			print("error switching frames")
			errorCount += 1
			if errorCount >= PAGE_LOAD_TRIES:
				raise Exception
			else:
				time.sleep(1)


# ---------- MAIN ----------

# browser.implicitly_wait(15)

browser.get('https://my.queensu.ca/')

browser.find_element_by_id('username').send_keys(sys.argv[0])

passwordElem = browser.find_element_by_id('password')
passwordElem.send_keys(sys.argv[1])
passwordElem.submit()

# big red SOLUS button
SOLUS = get_elem("a", "text()", "SOLUS")
SOLUS.click()
time.sleep(1)
try:
	SOLUS.click()
except:
	pass

# focus iframe containing Solus' content
switch_frame()

# give time for 'Search' hyperlink to appear on page
time.sleep(2.5)

# click Search
get_elem("a", "text()", "Search").click()

# Expand additional search criteria
get_elem("a", "@id", "DERIVED_CLSRCH_SSR_EXPAND_COLLAPS$149$$1").click()


# for search_day in ["MON", "TUES", "WED", "THURS", "FRI", "SAT", "SUN"]:
for search_day in ["TUES", "WED", "THURS", "FRI", "SAT", "SUN"]:
	# create csv named date+time
	file = open(search_day+".csv", 'a+')
	writer = csv.writer(file)
	writer.writerow(["class", "number", "section", "time", "room", "prof", "enrollment"])

	# search_times = ["8:00AM", "8:30AM", "9:00AM", "9:30AM", "10:00AM", "10:30AM", "11:00AM", "11:30AM", "12:00PM",
	# 				"12:30PM", "1:00PM", "1:30PM", "2:00PM", "2:30PM", "3:00PM", "3:30PM", "4:00PM", "4:30PM", "5:00PM",
	# 				"5:30PM", "6:00PM", "6:30PM", "7:00PM", "7:30PM", "8:00PM", "8:30PM", "9:00PM", "9:30PM"]

	search_times = ["8:00AM", "8:30AM", "9:00AM", "9:30AM", "10:00AM", "10:30AM", "11:00AM", "11:30AM", "12:00PM",
					"12:30PM", "1:00PM", "1:30PM", "2:00PM", "2:30PM", "3:00PM", "3:30PM", "4:00PM", "4:30PM", "5:00PM",
					"5:30PM", "6:00PM", "6:30PM", "7:00PM", "7:30PM", "8:00PM", "8:30PM", "9:00PM", "9:30PM"]
	time_index = 0
	while time_index < len(search_times):
		# uncheck 'Show Open Classes Only'
		get_elem("input", "@id", "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$5").click()

		# click Mon checkbox
		get_elem("input", "@id", "SSR_CLSRCH_WRK_"+search_day+"$8").click()

		# select 'is exactly' from 'Meeting start time' dropdown
		get_elem_by_xpath(STARTIME_DROPDOWN_XPATH).click()

		# Wait for Solus to inexplicably reload the time start box
		time.sleep(3)

		# enter '8:30', submit
		startTimeElem = get_elem_by_xpath(STARTTIME_INPUTBOX_XPATH)
		startTimeElem.click()
		startTimeElem.send_keys(search_times[time_index])
		startTimeElem.send_keys(Keys.ENTER)

		# each course has a //div[contains(@id, 'win0divSSR_CLSRSLT_WRK_GROUPBOX2$')]
		# containing the course name //div[contains(@id, 'win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$')]
		# and 1 or more sections //tr[contains(@id, 'trSSR_CLSRCH_MTG1$')]

		def get_courseDivs():
			for i in range(0, PAGE_LOAD_TRIES):
				# get list of webElements containing courses
				courseElems = browser.find_elements_by_xpath(COURSE_DIVS_XPATH)
				if len(courseElems) > 0:
					return courseElems
				else:
					print("looking for "+COURSE_DIVS_XPATH)
					try:
						# look for 'no results' warning (throws error if not found)
						browser.find_element_by_xpath(NO_RESULTS_WARNING_XPATH)
						return None
					except:
						#neither has loaded yet, try again
						print("looking for "+NO_RESULTS_WARNING_XPATH)
						time.sleep(1)
			#halt the program
			raise NoSuchElementException()

		courseDivs = get_courseDivs()
		while courseDivs is None:
			# no results, search for next time
			time_index += 1
			# break if time_index is past 9:30PM
			if (time_index >= len(search_times)):
				break

			# submit search
			startTimeElem = get_elem_by_xpath(STARTTIME_INPUTBOX_XPATH)
			startTimeElem.click()
			startTimeElem.clear()
			startTimeElem.send_keys(search_times[time_index])
			startTimeElem.send_keys(Keys.ENTER)

			#search for courseDivs for PAGE_LOAD_TRIES seconds
			try:
				courseDivs = get_elems_by_xpath(COURSE_DIVS_XPATH)
			except:
				pass

		# go to next day if time_index is past 9:30PM
		if (time_index >= len(search_times)):
			break

		print("len(courseElems) = {}".format(len(courseDivs)))


		# 1-based indexing >:(
		for i in range(1, len(courseDivs)+1):
			# get the ith course div
			courseDiv = get_elem_by_xpath("({})[{}]".format(COURSE_DIVS_XPATH, i))
			# get courseDiv's name
			name = get_subelem(courseDiv, "div", "@id", "win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$").text
			# get number of sections
			sections = get_subelems_by_xpath(courseDiv, '.'+SECTION_TABLEROW_XPATH)
			print("{}, sections = {}".format(name, len(sections)))

			section = sections[0]
			for j in range(1, len(sections)+1):
				number = get_subelem(section, "a", "@id", "MTG_CLASS_NBR$")
				row = [
					name,
					number.text,
					get_subelem(section, "a", "@id", "MTG_CLASSNAME$").text,
					get_subelem(section, "span", "@id", "MTG_DAYTIME$").text,
					get_subelem(section, "span", "@id", "MTG_ROOM$").text,
					get_subelem(section, "span", "@id", "MTG_INSTR$").text
				]

				# navigate to course info page
				number.click()
				# append enrollment number
				row.append(get_elem("span", "@id", "SSR_CLS_DTL_WRK_ENRL_TOT").text)

				# write to csv
				print(row)
				writer.writerow(row)

				# navigate back
				get_elem("a", "@id", "CLASS_SRCH_WRK2_SSR_PB_BACK").click()

				# if we aren't on the last iteration
				if j < len(sections):
					# re-fetch courseDiv and section since they went stale after we left
					courseDiv = get_elem_by_xpath("({})[{}]".format(COURSE_DIVS_XPATH, i))
					section = get_subelem_by_xpath(courseDiv, "(.{})[{}]".format(SECTION_TABLEROW_XPATH, j+1))

		# new search
		get_elem("a", "@id", "CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH").click()
		time_index += 1

	file.close()
