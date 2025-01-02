#!/usr/bin/env python3
"""
Merges the output of sabayomikun24 and Katikati Counter.
"""
import sys
import os
from os.path import expanduser
import datetime
import linecache
import shutil
import re
try:
    import openpyxl
except ModuleNotFoundError:
    print('openpyxl is not installed.')
    print('pip install openpyxl')
    sys.exit()
if sys.version_info.major == 2:
    import Tkinter
    import tkMessageBox
    import tkFileDialog
    TKROOT = Tkinter.Tk()
elif sys.version_info.major == 3:
    import tkinter
    from tkinter import messagebox as tkMessageBox
    from tkinter import filedialog as tkFileDialog
    TKROOT = tkinter.Tk()
TKROOT.withdraw()

#MODEを指定
INTERACTMODE = True
for agvs in sys.argv:
    if agvs == '-b':
        INTERACTMODE = False

#AutoCountedFileのPATHを指定
if INTERACTMODE:
    if os.name == 'nt':
        IDIR = expanduser("~") + '/Desktop'
    else:
        IDIR = os.environ['HOME'] + '/Desktop'
    FTYP1 = [('From sabayomikun24', '*.csv')]
    if not tkMessageBox.askokcancel('katisaba24', 'Select automatic count csv file.\n(The output file of sabayomikun24)'):
        sys.exit()
    CSVPATH1 = tkFileDialog.askopenfilename(filetypes=FTYP1, initialdir=IDIR)
    if CSVPATH1 == '':
        sys.exit()
    if not os.path.exists(CSVPATH1):
        tkMessageBox.showinfo('katisaba24', 'Missing input file.')
        sys.exit()
    if not os.path.isfile(CSVPATH1):
        tkMessageBox.showinfo('katisaba24', 'Missing input file.')
        sys.exit()
else:
    if '-a' in sys.argv:
        if len(sys.argv) > sys.argv.index('-a') + 1:
            CSVPATH1 = sys.argv[sys.argv.index('-a') + 1]
            if not os.path.exists(CSVPATH1):
                print('Missing input file.')
                sys.exit()
            if not os.path.isfile(CSVPATH1):
                print('Missing input file.')
                sys.exit()
    else:
        print('Input file is not defined.')
        print('Use -a option.')
        sys.exit()

#AutoCountedFileの形式を検証
CSVFILE1 = open(CSVPATH1, mode='r')
CSVTEXT1 = CSVFILE1.readlines()
CSVFILE1.close()
BASENAME1 = os.path.basename(CSVPATH1)
DIRNAME1 = os.path.dirname(CSVPATH1)
ROOTNAME1, EXT1 = os.path.splitext(BASENAME1)
CONTELINE1_arr = []
LINESVERT = 1
while LINESVERT < 13:
    INDEXLINE1 = linecache.getline(CSVPATH1, LINESVERT).replace('\n', '').split(',')
    if not INDEXLINE1[2].isdigit():
        if not uf == 'ND':
            if INTERACTMODE:
                tkMessageBox.showinfo('katisaba24', 'Input file format does not match.\nIs this the output file of sabayomikun24?')
            else:
                print('Input file format does not match.\nIs this the output file of sabayomikun24?')
            sys.exit()
    if len(INDEXLINE1) != 3:
        if INTERACTMODE:
            tkMessageBox.showinfo('katisaba24', 'Input file format does not match.\nIs this the output file of sabayomikun24?')
        else:
            print('Input file format does not match.\nIs this the output file of sabayomikun24?')
        sys.exit()
    LINESVERT += 1
    CONTELINE1_arr.append(INDEXLINE1)
CONTELINE1_arr = sorted(CONTELINE1_arr)
if len(CONTELINE1_arr) != 24:
    if INTERACTMODE:
        tkMessageBox.showinfo('katisaba24', 'Inpt file format does not match.\nIs this the output file of sabayomikun24?')
    else:
        print('Input file format does not match.\nIs this the output file of sabayomikun24?')
    sys.exit()
if re.search('_auto.csv$', ROOTNAME1):
    if INTERACTMODE:
        tkMessageBox.showinfo('katisaba24', 'Inpt file name does not match.\nIs this the output file of sabayomikun24?')
    else:
        print('Input file format does not match.\nIs this the output file of sabayomikun24?')
    sys.exit()

#ManualCountedFileのPATHを指定
if INTERACTMODE:
    FTYP2 = [('From Katikati Counter', '*.csv')]
    if not tkMessageBox.askokcancel('katisaba24', 'Select manual count csv file.\n(The output file of Katikati Counter)'):
        sys.exit()
    CSVPATH2 = tkFileDialog.askopenfilename(filetypes=FTYP2, initialdir=IDIR)
    if CSVPATH2 == '':
        sys.exit()
    if not os.path.exists(CSVPATH2):
        tkMessageBox.showinfo('katisaba24', 'Missing input file.')
        sys.exit()
    if not os.path.isfile(CSVPATH2):
        tkMessageBox.showinfo('katisaba24', 'Missing input file.')
        sys.exit()
else: 
    if '-m' in sys.argv:
        if len(sys.argv) > sys.argv.index('-m') + 1:
            CSVPATH2 = sys.argv[sys.argv.index('-m') + 1]
            if not os.path.exists(CSVPATH2):
                print('Missing input file.')
                sys.exit()
            if not os.path.isfile(CSVPATH2):
                print('Missing input file.')
                sys.exit()
    else:
        print('Input file is not defined.')
        print('Use -m option.')
        sys.exit()
    
#ManualCountedFileの形式を検証
CSVFILE2 = open(CSVPATH2, mode='r')
CSVTEXT2 = CSVFILE2.readlines()
INDEXLINE2 = linecache.getline(CSVPATH2, 1).replace('\n', '').split(',')
CONTELINE2 = CSVTEXT2[1:]
CSVFILE2.close()
if 'Red' not in INDEXLINE2 or 'Green' not in INDEXLINE2 or 'Blue' not in INDEXLINE2:
    if INTERACTMODE:
        tkMessageBox.showinfo('katisaba24', 'Index line is modified, or this is not\nthe output file of Katikati Counter.')
    else:
        print('Index line is modified, or this is not\nthe output file of Katikati Counter.')
    sys.exit()
REDINDEX = INDEXLINE2.index('Red')
GREENINDEX = INDEXLINE2.index('Green')
BLUEINDEX = INDEXLINE2.index('Blue')
if not 0 < REDINDEX < 4 or not 0 < GREENINDEX < 4 or not 0 < BLUEINDEX < 4:
    if INTERACTMODE:
        tkMessageBox.showinfo('katisaba24', 'Index line is modified, or this is not\nthe output file of Katikati Counter.')
    else:
        print('Index line is modified, or this is not\nthe output file of Katikati Counter.')
    sys.exit()
CONTELINE2_arr = []
for lines in CONTELINE2:
    line = lines.replace('\n', '').split(',')
    if re.search("[1-4][A-C]$", line[0]):
        CONTELINE2_arr.append(line)
if len(CONTELINE2_arr) != 24:
    if INTERACTMODE:
        tkMessageBox.showinfo('katisaba24', 'This is not the correct output file of\nKatikati Counter, or you included\nnon-graphic files.')
    else:
        print('This is not the correct output file of\nKatikati Counter, or you included\nnon-graphic files.')
    sys.exit()
CONTELINE2 = sorted(CONTELINE2_arr)
for lines in CONTELINE2:
    if not line[1].isdigit() or not line[2].isdigit() or not line[3].isdigit():
        if INTERACTMODE:
            tkMessageBox.showinfo('katisaba24', 'This is not the output file of\nKatikati Counter.')
        else:
            print('This is not the output file of\nKatikati Counter.')
        sys.exit()
TKROOT.update()

#データ統合
outputarr = [['data', 'well', 'number', 'auto', 'appended', 'removed', 'marked']]
rangearry = list(range(24))
for num in rangearry:
    results = int(CONTELINE1_arr[num][2]) + int(CONTELINE2_arr[num][REDINDEX]) - int(CONTELINE2_arr[num][BLUEINDEX])
    linesarr = [CONTELINE1_arr[num][0], CONTELINE1_arr[num][1], int(results), CONTELINE1_arr[num][2], CONTELINE2_arr[num][REDINDEX], CONTELINE2_arr[num][BLUEINDEX], CONTELINE2_arr[num][GREENINDEX]]
    outputarr.append(linesarr)
ROOTNAME3 = re.sub('_auto', '_corrected', ROOTNAME1)
WB = openpyxl.Workbook()
WS = WB.active
seettitle = re.sub('_auto', '', str(ROOTNAME1))
WS.title = str(seettitle)
for row in outputarr:
    WS.append(row)
if os.path.exists(DIRNAME1 + '/' + ROOTNAME3 + '.xlsx'):
    DATETIME = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
    shutil.move(DIRNAME1 + '/' + ROOTNAME3 + '.xlsx', DIRNAME1 + '/' + ROOTNAME3 + '_old_' + DATETIME + '.xlsx')
sheet = WB[str(seettitle)]
rangearryxl = list(range(2, 26))
for k in rangearryxl:
    if not sheet['E' + str(k)].value == str(0):
        sheet['E' + str(k)].font = openpyxl.styles.fonts.Font(color='FF0000')
    if not sheet['F' + str(k)].value == str(0):
        sheet['F' + str(k)].font = openpyxl.styles.fonts.Font(color='0000FF')
    if not sheet['G' + str(k)].value == str(0):
        sheet['G' + str(k)].font = openpyxl.styles.fonts.Font(color='00FF00')
    if not str(sheet['C' + str(k)].value) == str(sheet['D' + str(k)].value):
        sheet['D' + str(k)].font = openpyxl.styles.fonts.Font(color='CCCCCC')
WB.save(DIRNAME1 + '/' + ROOTNAME3 + '.xlsx')
if INTERACTMODE:
    tkMessageBox.showinfo('katisaba24', 'Task finished.')
