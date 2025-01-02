#!/usr/bin/env python3
"""
Crops each well from 12-well plate images. And counts foci in the wells.
"""
import sys
import os
from os.path import expanduser
import shutil
import datetime
import tkinter
from tkinter import messagebox as tkMessageBox
from tkinter import filedialog as tkFileDialog
try:
    import numpy as np
except ModuleNotFoundError:
    print('numpy is not installed.\npip install numpy')
    sys.exit()
try:
    import cv2
except ModuleNotFoundError:
    print('opencv-python is not installed.\npip install opencv-python')
    sys.exit()
try:
    from PIL import ImageDraw, ImageFont, Image
except ModuleNotFoundError:
    print('Pillow is not installed.\npip install Pillow')
    sys.exit()
if os.name == 'nt':
    try:
        PICKFONT = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        tkMessageBox.showinfo('sabayomikun24', 'Font \"arial.ttf\" is not installed.')
        sys.exit()
else:
    try:
        PICKFONT = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        print('sabayomikun24', 'Font \"Arial.ttf\" is not installed.\napt install ttf-mscorefonts-installer')
        sys.exit()

#MODEを指定
INTERACTMODE = True
for agvs in sys.argv:
    if agvs == '-b':
        INTERACTMODE = False
CROPMODE = False
for agvs in sys.argv:
    if agvs == '-c':
        CROPMODE = True

if INTERACTMODE:
    #GUIからPATHを指定
    TKROOT = tkinter.Tk()
    TKROOT.withdraw()
    if os.name == 'nt':
        IDIR = expanduser("~") + '/Desktop'
    else:
        IDIR = os.environ['HOME'] + '/Desktop'
    if not tkMessageBox.askokcancel('sabayomikun24', 'Select input directory.'):
        sys.exit()
    INPUTPATH = tkFileDialog.askdirectory(initialdir = IDIR)
    if INPUTPATH == '':
        sys.exit()
    INPUTPATH = INPUTPATH + '/'
    if not tkMessageBox.askokcancel('sabayomikun24', 'Input directory is \n' + INPUTPATH + '\n\nSelect output Directory.'):
        sys.exit()
    OUTPUTPATH = tkFileDialog.askdirectory(initialdir = IDIR)
    if OUTPUTPATH == '':
        sys.exit()
    OUTPUTPATH = OUTPUTPATH + '/'
else:
    #CUIからPATHを指定
    if '-i' in sys.argv:
        if len(sys.argv) > sys.argv.index('-i') + 1:
            INPUTOPTION = sys.argv[sys.argv.index('-i') + 1]
            if os.path.exists(INPUTOPTION):
                INPUTPATH = str(INPUTOPTION) + '/'
            else:
                print('Input directory is defined by the option -i, but not found.')
                print(INPUTOPTION)
                sys.exit()
        else:
            print('Input directory is defined by the option -i, but no argument.')
            sys.exit()
    else:
        print('Input directory is not defined.')
        print('Use -i option.')
        sys.exit()
    if not os.path.isdir(INPUTPATH):
        print('Input directory is defined, but this is not a directory.')
        print(INPUTPATH)
        sys.exit()
    if '-o' in sys.argv:
        if len(sys.argv) > sys.argv.index('-o') + 1:
            OUTPUTOPTION = sys.argv[sys.argv.index('-o') + 1]
            if os.path.exists(OUTPUTOPTION):
                OUTPUTPATH = OUTPUTOPTION + '/'
            else:
                print('Output directory is defined by the option -o, but not found.')
                print(OUTPUTOPTION)
                sys.exit()
        else:
            print('Output directory is defined by the option -o, but no argument.')
            sys.exit()
    else:
        print('Output directory is not defined.')
        print('Use -o option.')
        sys.exit()
    if not os.path.isdir(OUTPUTPATH):
        print('Output directory is defined, but this is not directory.')
        print(OUTPUTPATH)
        sys.exit()

#ファイル名取得
DATETIME = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
filepathsarray = []
for imputfiles in os.listdir(INPUTPATH):
    filesset = []
    file_path = INPUTPATH + imputfiles
    basename = os.path.basename(file_path)
    rootname, ext = os.path.splitext(basename)
    if os.path.isdir(file_path) or os.path.islink(file_path):
        if os.path.exists(OUTPUTPATH + basename):
            if (str(file_path).replace('//', '/')).rstrip('/') != (str(OUTPUTPATH + basename).replace('//', '/')).rstrip('/'):
                shutil.move(OUTPUTPATH + basename, OUTPUTPATH + basename + '_old_' + DATETIME)
        if (str(file_path).replace('//', '/')).rstrip('/') not in (str(OUTPUTPATH).replace('//', '/')).rstrip('/'):
            shutil.move(file_path, OUTPUTPATH + basename)
        continue
    if basename.startswith('.'):
        continue
    imgtarget = Image.open(file_path)
    imagetype = imgtarget.format    
    if imagetype is None:
        continue
    if not ext:
        ext = '.' + imagetype.lower()
    if os.path.exists(OUTPUTPATH + str(rootname)):
        shutil.move(OUTPUTPATH + str(rootname), OUTPUTPATH + str(rootname) + '_old_' + DATETIME)
    os.makedirs(OUTPUTPATH + str(rootname))
    out_crop_picked_path = OUTPUTPATH + str(rootname) + '/'
    filesset = [file_path, out_crop_picked_path, str(rootname)]
    filepathsarray.append(filesset)

#各入力ファイルへの処理
if len(filepathsarray) == 0:
    if INTERACTMODE:
        tkMessageBox.showinfo('sabayomikun24', 'No image.')
    else:
        print('No image.')
    sys.exit()
for j in filepathsarray:
    inputfilepath = j[0]
    outputfilepath = j[1]
    datanametrunc = j[2]
    
    #PillowでImageを読み込む、余白追加
    importimg = Image.open(inputfilepath)
    widthorig, heightorig = importimg.size
    marginval = int(widthorig / 60)
    widthorig, heightorig = widthorig + marginval * 2, heightorig + marginval * 2
    backwhite = Image.new('RGBA', (widthorig, heightorig), 'white')
    backwhite.paste(importimg, (marginval, marginval))
    
    #OpenCVに変換、分割
    colorimg = np.array(backwhite, dtype = np.uint8)
    colorimg = cv2.flip(colorimg, 1)
    colorimg = cv2.cvtColor(colorimg, cv2.COLOR_RGB2BGR)
    heightpanel, widthpanel = int(heightorig / 4), int(widthorig / 6)
    minradiusval, maxradiusval = int(widthpanel * 0.39), int(widthpanel * 0.58)
    horizontalarr = [['1', [0, widthpanel + marginval]], ['2', [widthpanel - marginval, widthpanel * 2 + marginval]], ['3', [widthpanel * 2 - marginval, widthpanel * 3 + marginval]], ['4', [widthpanel * 3 - marginval, widthpanel * 4 + marginval]], ['5', [widthpanel * 4 - marginval, widthpanel * 5 + marginval]], ['6', [widthpanel * 5 - marginval, widthorig]]]
    verticalarr = [['A', [0, heightpanel + marginval]], ['B', [heightpanel - marginval, heightpanel * 2 + marginval]], ['C', [heightpanel * 3 - marginval, heightpanel * 4 + marginval]], ['D', [heightpanel * 4 - marginval, heightorig]]]
    clippingarr = []
    for f in horizontalarr:
        for g in verticalarr:
            elements = [f[0] + g[0], [g[1][0], g[1][1], f[1][0], f[1][1]]]
            clippingarr.append(elements)
    
    #各ウェルの処理
    for h in clippingarr:
        wellname = h[0]
        
        #Pillowで余白追加、OpenCVに戻す
        colorbigclip = colorimg[h[1][0]:h[1][1], h[1][2]:h[1][3]]
        colorbigclip = Image.fromarray(colorbigclip)
        widthclip, heightclip = colorbigclip.size
        widthclip, heightclip = widthclip + marginval * 2, heightclip + marginval * 2
        backclip = Image.new('RGBA', (widthclip, heightclip), 'white')
        backclip.paste(colorbigclip, (marginval, marginval))
        colorbigclip = np.array(backclip, dtype = np.uint8)
        
        #大円検出
        glaysbigclip = cv2.cvtColor(colorbigclip, cv2.COLOR_BGR2GRAY)
        glaysbigclip = cv2.GaussianBlur(glaysbigclip, (15, 15), 2)
        circles = cv2.HoughCircles(glaysbigclip, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = minradiusval, maxRadius = maxradiusval)
        if not type(circles) == np.ndarray:
            colorsmallclip = colorbigclip
            detectednum = 0
        else:
            circles = np.uint16(np.around(circles))
            
            #大円周辺にズーム
            origx, origy, radius = circles[0][0][0], circles[0][0][1], circles[0][0][2]
            x1 = origx - radius - marginval
            if x1 <= 1:
                x1 = 1
            y1 = origy - radius - marginval
            if y1 <= 1:
                y1 = 1
            x2 = origx + radius + marginval
            if x2 >= widthclip:
                x2 = widthclip
            y2 = origy + radius + marginval
            if y2 >= heightclip:
                y2 = heightclip
            colorsmallclip = colorbigclip[y1:y2, x1:x2]
            #Pillowでcolorsmallclipを保存しておく
            colorsmallcliporig = cv2.cvtColor(colorsmallclip, cv2.COLOR_BGR2RGB)
            colorsmallcliporig = Image.fromarray(colorsmallcliporig)
            
            if CROPMODE:
                #wellnameのみ書き込む
                drawtext = ImageDraw.Draw(colorsmallcliporig)
                drawtext.text((5, 5), wellname, fill = 'black', font = PICKFONT)
                result = colorsmallcliporig
            else:
                #大円の外側をマスク
                newx, newy, edgelenx, edgeleny = origx - x1, origy - y1, x2 - x1, y2 - y1
                masksimg = np.zeros((edgeleny, edgelenx), dtype = np.uint8)
                cv2.circle(masksimg, (newx, newy), radius, (255, 255, 255), -1)
                
                #明度で二値化
                rimmask = int(edgeleny / 80) + 1
                cv2.circle(masksimg, (newx, newy), radius, (127, 127, 127), int(rimmask))
                thresholdimg = colorsmallclip.copy()
                thresholdimg = cv2.circle(thresholdimg, (newx, newy), radius, (128, 128, 128), int(rimmask))
                thresholdimg = cv2.cvtColor(thresholdimg, cv2.COLOR_BGR2GRAY)
                thresholdimg = cv2.equalizeHist(thresholdimg)
                thresholdimg = np.where(masksimg >= thresholdimg, masksimg - thresholdimg, 255)
                _, thresholdimg = cv2.threshold(thresholdimg, 110, 255, cv2.THRESH_BINARY)
                thresholdimg = cv2.bitwise_not(thresholdimg)
            
                #findContoursでプラーク検出
                totalarea = int((edgelenx * edgeleny) / 10)
                contours, _ = cv2.findContours(thresholdimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                detectednum = 0
                if not len(contours) == 0:
                    for dots in contours:
                        idot = cv2.moments(dots)
                        if totalarea > idot['m00'] > 1:
                            idotcx, idotcy = int(idot['m10'] / idot['m00']) + 4, int(idot['m01'] / idot['m00']) + 4
                            cv2.drawContours(colorsmallclip, dots, -1, (0, 0, 130), 1)
                            cv2.drawMarker(colorsmallclip, (idotcx, idotcy), (0, 0, 255), markerType = cv2.MARKER_CROSS, markerSize = 6)
                            detectednum += 1
                            
                """
                #HoughCirclesでプラーク検出
                thresholdimg = cv2.GaussianBlur(thresholdimg, (15, 15), 2)
                smallcircles = cv2.HoughCircles(thresholdimg, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30)
                circlenum = 0
                if type(smallcircles) == np.ndarray:
                    smallcircles = np.uint16(np.around(smallcircles))
                    for cirs in smallcircles[0]:
                        print(cirs[2])
                        cv2.circle(colorsmallclip, (cirs[0], cirs[1]), cirs[2], (127, 127, 0), 1)
                        circlenum += 1
                """
                
                #Pillowに変換、文字書き込み
                colorsmallclip = cv2.cvtColor(colorsmallclip, cv2.COLOR_BGR2RGB)
                colorsmallclip = Image.fromarray(colorsmallclip)
                drawtext = ImageDraw.Draw(colorsmallclip)
                drawtext.text((5, 5), wellname + '\n' + str(detectednum), fill = 'black', font = PICKFONT)
                #白紙のイメージ上に並べて貼り付ける
                result = Image.new("RGB", (edgelenx * 2, edgeleny), 'white')
                result.paste(colorsmallclip)
                result.paste(colorsmallcliporig, (edgelenx, 0))
            
            #ファイル出力
            result.save(outputfilepath + str(datanametrunc) + "-" + wellname + ext)
            if not CROPMODE:
                csvout = open(outputfilepath + str(datanametrunc) + '_auto.csv', 'a')
                csvout.write(str(datanametrunc) + ',' + wellname + ',' + str(detectednum) + '\n')
                csvout.close()
if INTERACTMODE:
    tkMessageBox.showinfo('sabayomikun24', 'Task finished.')

