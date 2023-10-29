import numpy as np
import statistics as st
import webbrowser
from tkinter import *
import pywintypes
import win32api
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os, re, shutil, openpyxl, warnings
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import pwinput
import pywinauto
import win32com.client as win32
from win32com.client import Dispatch
import termcolor
import shutil
import sys
import io
import json
from selenium.webdriver.chrome.service import Service

os.system('color')

LOGGER.setLevel(logging.WARNING)
logging.getLogger('device_event_log_impl').setLevel(logging.ERROR)

warnings.filterwarnings("ignore", category=DeprecationWarning)

current_directory = os.getcwd()

# Set the download directory
download_dir = current_directory + '\EtudiantNote'
rapport_dir = current_directory + '\Rapport'


# Set Chrome options
chrome_options = webdriver.ChromeOptions()

# Set preferences for file download
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

# Add preferences to Chrome options

chrome_options.add_experimental_option("prefs", prefs)

class Statistique:

    def calcul_stats(self,colControl,filename, academie, enseignant, providence, matiere, niveau, classe, session, institution, controleNumber):
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
        notes = []
        nbr_eleve = 0

        column = colControl
        for i in range(18, ws.max_row + 1):
            if(ws[column + str(i)].value == None):
                break
            nbr_eleve = nbr_eleve+1
            notes.append(ws[column + str(i)].value)

        wb_st = openpyxl.load_workbook("RapportControleFr.xlsx")
        ws_st = wb_st.active

        ws_st['D2'].value = academie
        ws_st['A2'].value = enseignant
        ws_st['A4'].value = session
        ws_st['D3'].value = providence
        ws_st['D4'].value = institution
        ws_st['D7'].value = niveau
        ws_st['A3'].value = matiere
        ws_st['A7'].value = classe

        sans_moyenne = []
        avec_moyenne = []

        for note in notes:
            if note >= 10:
                avec_moyenne.append(note)
            else:
                sans_moyenne.append(note)

        ws_st['D13'].value = len(sans_moyenne)
        ws_st['E13'].value = len(avec_moyenne)
        ws_st['C13'].value = max(notes)
        ws_st['B13'].value = min(notes)
        ws_st['A19'].value = (len(sans_moyenne) * 100) / len(notes)
        ws_st['D19'].value = (len(avec_moyenne) * 100) / len(notes)
        ws_st['A13'].value = sum(notes) / len(notes)

        inf_5 = 0
        inf_10 = 0
        inf_15 = 0
        inf_20 = 0

        for note in notes:
            if 0 <= note < 5:
                inf_5 += 1
            elif 5 <= note < 10:
                inf_10 += 1
            elif 10 <= note < 15:
                inf_15 += 1
            else:
                inf_20 += 1

        ws_st['D16'].value = inf_5
        ws_st['C16'].value = inf_10
        ws_st['B16'].value = inf_15
        ws_st['A16'].value = inf_20
            
        wb_st.save("RapportControleFr.xlsx")
        time.sleep(4)
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        path = os.path.abspath('RapportControleFr.xlsx')
        workbook = excel.Workbooks.Open(path)
        worksheet = workbook.Worksheets('Feuil1')
        pdf_file = os.path.join(rapport_dir + '\\' + f'Rapport du {classe} Session {session} Controle Numero {controleNumber}.pdf')
        worksheet.ExportAsFixedFormat(0, pdf_file)
        workbook.Close(False)
        excel.Quit()
        
        os.startfile(rapport_dir + '\\' + f'Rapport du {classe} Session {session} Controle Numero {controleNumber}.pdf')
        # webbrowser.open('RapportControleFr.xlsx')
    
    def getFilesFromMassar(self,form_data, whichSession, download="yes"):

        try:
            # Convert the form data string back to a dictionary
            data = json.loads(form_data)

            # Access the values of the input fields using the keys
            email = data.get('email', '')
            password = data.get('password', '')

            response = "Form data processed successfully"
        except json.JSONDecodeError:
            response = "Error: Invalid form data format"
        
        if os.listdir(download_dir) and download == "yes":
            return "Done"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        # driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
        driver.get("https://massar.men.gov.ma/Account")
        wait = WebDriverWait(driver, 10)
        emailInput = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="UserName"]')))
        emailInput.send_keys(email)
        passwordInput = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Password"]')))
        passwordInput.send_keys(password)
        try:
            loginButton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSubmit"]')))
            loginButton.click()
        except:
            return "Verifier Votre Email ou Password est incorrecte"
        time.sleep(2)
        NumberOfClasses = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/section[2]/div[2]/div/div[2]/div[1]/div/div/h2/span')
        time.sleep(1)
        driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/nav/ul/li[1]/a').click()
        time.sleep(1)
        academie = driver.find_element(By.XPATH, '//*[@id="mCSB_2_container"]/div[1]/div/form/div[1]/div/div[1]/div/label').text
        providence = driver.find_element(By.XPATH, '//*[@id="mCSB_2_container"]/div[1]/div/form/div[1]/div/div[2]/div/label').text
        ecole = driver.find_element(By.XPATH, '//*[@id="mCSB_2_container"]/div[1]/div/form/div[1]/div/div[4]/div/label').text
        clickInside = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sidebar-menu"]/li[3]/a')))
        clickInside.click()
        clickInside = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mCSB_4_container"]/div/ul/li[3]/a')))
        clickInside.click()
        if download == 'yes':
            selectInput = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Cycle"]/option')))
            selectInput.click()
            if whichSession == 1:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="IdSession"]/option[1]'))).click()
            elif whichSession == 2:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="IdSession"]/option[2]'))).click()
            else:
                print('Choix errone')
                exit()
            selectWhatClass = driver.find_element(By.XPATH, '//*[@id="Niveau"]')
            options = selectWhatClass.find_elements(By.TAG_NAME, "option")
            clickInside = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnExport"]')))
            for option in options:
                option.click()
                classes = driver.find_element(By.XPATH, '//*[@id="Classe"]')
                classeOptions = classes.find_elements(By.TAG_NAME, 'option')
                for classe in classeOptions:
                    classe.click()
                    time.sleep(0.75)
                    clickInside.click()
                    time.sleep(1.5)
                    while True:
                        downloaded_files = os.listdir(download_dir)
                        if downloaded_files[-1].endswith("xlsx"):
                            pattern = r"export_notesCC_(\w+-\d+)_"
                            match = re.search(pattern, downloaded_files[-1])
                            last_downloaded_file = downloaded_files[-1]
                            # print(last_downloaded_file)
                            if match:
                                # print(match.group(1))
                                os.mkdir(download_dir + '\\' + match.group(1))
                                shutil.move(download_dir + '\\' + last_downloaded_file, download_dir + '\\' + match.group(1))
                            break
                        else:
                            continue
        return driver

    def allClasses(self):
        classes_uncleaned = []
        for classe in os.listdir(download_dir):
            classes_uncleaned.append(classe)
        classes = cleaned_list = [item for item in classes_uncleaned if item is not None]
        return json.dumps(classes)
    
    def getStudentsFromClasse(self,classeChoisi):
        students = []
        fileInside = os.listdir(download_dir + '\\' + classeChoisi)
        workbook = openpyxl.load_workbook(download_dir + '\\' + classeChoisi + '\\' + fileInside[-1])
        worksheet = workbook.active
        for colNumber in range(18, worksheet.max_row):
            students.append(worksheet['D' + str(colNumber)].value)
        
        return students


    def getAllStudents(self, classe):
        students = []
        fileInside = os.listdir(download_dir + '\\' + classe)
        workbook = openpyxl.load_workbook(download_dir + '\\' + classe + '\\' + fileInside[-1])
        worksheet = workbook.active
        for colNumber in range(18, worksheet.max_row):
            student = {
                "massar": worksheet['C' + str(colNumber)].value,
                "fullname": worksheet['D' + str(colNumber)].value,
                "controle1": worksheet['G' + str(colNumber)].value,
                "controle2": worksheet['I' + str(colNumber)].value,
                "controle3": worksheet['K' + str(colNumber)].value,
                "col1": 'G' + str(colNumber),
                "col2": 'I' + str(colNumber),
                "col3": 'K' + str(colNumber)
            }
            students.append(student)
        
        return students
    
    def changeNoteOfStudent(self, note, column, classe):
        fileInside = os.listdir(download_dir + '\\' + classe)
        workbook = openpyxl.load_workbook(download_dir + '\\' + classe + '\\' + fileInside[-1])
        worksheet = workbook.active

        worksheet[column] = int(note)

        workbook.save(download_dir + '\\' + classe + '\\' + fileInside[-1])
    
    def generateRapport(self, controleNumber, classe):
        fileInside = os.listdir(download_dir + '\\' + classe)
        workbook = openpyxl.load_workbook(download_dir + '\\' + classe + '\\' + fileInside[-1])
        worksheet = workbook.active

        enseignant = worksheet['O9'].value
        institution = worksheet['O7'].value
        matiere = worksheet['O11'].value
        niveau = worksheet['D9'].value
        classe = worksheet['I9'].value
        academie = worksheet['D7'].value
        session = worksheet['D11'].value
        providence = worksheet['I7'].value

        cols = ['G', 'I', 'K']
        colControl = ''
        if int(controleNumber) == 1:
            colControl = str(cols[0])
        elif int(controleNumber) == 2:
            colControl = str(cols[1])
        elif int(controleNumber) == 3:
            colControl = str(cols[2])
        print(colControl)
        filename = download_dir + '\\' + classe + '\\' + fileInside[-1]
        self.calcul_stats(colControl,filename, academie, enseignant, providence, matiere, niveau, classe, session, institution, controleNumber)
    
    def addToMassarNotes(self, classe, session, loginInfo):
        
        driver = self.getFilesFromMassar(loginInfo, int(session), 'no')
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="IdSessionEns"]'))).click()
        if int(session) == 1:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="IdSessionEns"]/option[1]'))).click()
        elif int(session) == 2:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="IdSessionEns"]/option[2]'))).click()


        driver.find_element(By.XPATH, '//*[@id="btnAdd"]').click()
        time.sleep(3)
        
        # retrieve a list of all currently open windows
        windows = pywinauto.Desktop(backend="win32").windows()

        # find the file dialog window
        file_dialog = None
        for window in windows:
            # print(f"Text: {window.window_text()} || Classe Name: {window.window_text()}")
            if window.window_text() == "Open" and window.class_name() == "#32770":
                file_dialog = window
                break
        fileInside = os.listdir(download_dir + '\\' + classe)
        # if the file dialog window was found
        if file_dialog is not None:
            # set the path of the file in the file dialog window
            file_path = download_dir + '\\' + classe + '\\' + fileInside[-1]
            file_dialog.set_focus()
            file_dialog.type_keys(file_path)
            file_dialog.type_keys("{ENTER}")
        else:
            # print an error message if the file dialog window was not found
            print("File dialog window not found.")
        
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="btnImport"]').click()

        time.sleep(2)
    
    def deleteAllFiles(self):
        for root, dirs, files in os.walk(download_dir, topdown=False):
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                shutil.rmtree(folder_path)


st=Statistique()