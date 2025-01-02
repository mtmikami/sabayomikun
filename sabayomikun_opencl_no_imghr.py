#!/usr/bin/env python3
"""
Crops each well from 96-well plate images. And counts foci in the wells.
"""
import sys
import os
from os.path import expanduser
import shutil
import datetime
import csv
try:
    import numpy as np
except ModuleNotFoundError:
    print('numpy is not installed.')
    print('pip install numpy')
    sys.exit()
try:
    import cv2
except ModuleNotFoundError:
    print('opencv-python is not installed.')
    print('pip install opencv-python')
    sys.exit()
try:
    from PIL import ImageDraw, ImageFont, Image
except ModuleNotFoundError:
    print('Pillow is not installed.')
    print('pip install Pillow')
    sys.exit()
INTERACTMODE = True
BLUEMODE = False
for agvs in sys.argv:
    if agvs == 'batch':
        INTERACTMODE = False
if INTERACTMODE:
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
    if os.name == 'nt':
        IDIR = expanduser("~") + '/Desktop'
    else:
        IDIR = os.environ['HOME'] + '/Desktop'
    if not tkMessageBox.askokcancel('sabayomikun', 'Select input directory.'):
        sys.exit()
    INPUTPATH = tkFileDialog.askdirectory(initialdir=IDIR)
    if INPUTPATH == '':
        sys.exit()
    if not tkMessageBox.askokcancel('sabayomikun', 'Input directory is \n' + INPUTPATH + '\n\nSelect output Directory.'):
        sys.exit()
    OUTPUTPATH = tkFileDialog.askdirectory(initialdir=IDIR)
    if OUTPUTPATH == '':
        sys.exit()
    else:
        INPUTPATH = str(INPUTPATH) + '/'
        OUTPUTPATH = str(OUTPUTPATH) + '/'
    NATIVECOLFLAG = tkMessageBox.askquestion('sabayomikun', 'Input directory is \n' + INPUTPATH + '\nOutput directory is \n' + OUTPUTPATH + '\n\nOutput files in native color?')
    if NATIVECOLFLAG == str('no'):
        BLUEMODE = True
    TKROOT.update()
else:
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
    # batch mode
    elif os.path.exists('/mnt/hdd/Public/Crop/Input/'):
        INPUTPATH = '/mnt/hdd/Public/Crop/Input/'
    elif not os.name == 'nt':
        if os.path.exists(os.environ['HOME'] + '/Desktop/Crop/Input/'):
            INPUTPATH = os.environ['HOME'] + '/Desktop/Crop/Input/'
    elif os.name == 'nt':
        if os.path.exists(expanduser("~") + '/Desktop/Crop/Input/'):
            INPUTPATH = expanduser("~") + '/Desktop/Crop/Input/'
    # batch mode
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
    # batch mode
    elif os.path.exists('/mnt/hdd/Public/Crop/Output/'):
        OUTPUTPATH = '/mnt/hdd/Public/Crop/Output/'
    elif not os.name == 'nt':
        if os.path.exists(os.environ['HOME'] + '/Desktop/Crop/Output/'):
            OUTPUTPATH = os.environ['HOME'] + '/Desktop/Crop/Output/'
    elif os.name == 'nt':
        if os.path.exists(expanduser("~") + '/Desktop/Crop/Output/'):
            OUTPUTPATH = expanduser("~") + '/Desktop/Crop/Output/'
    # batch mode
    else:
        print('Output directory is not defined.')
        print('Use -o option.')
        sys.exit()
    if not os.path.isdir(OUTPUTPATH):
        print('Output directory is defined, but this is not directory.')
        print(OUTPUTPATH)
        sys.exit()
PICKMODE = True
DEEPPICKMODE = True
CHECKMODE = False
for agvs in sys.argv:
    if agvs == 'nopick':
        PICKMODE = False
    if agvs == 'nodeeppick':
        DEEPPICKMODE = False
    if agvs == 'blue':
        BLUEMODE = True
    if agvs == 'debug':
        CHECKMODE = True
    if agvs == 'check':
        CHECKMODE = True
PYOPENCVVER = cv2.__version__[0]
GAMMA = 0.18
GAMMA_CVT = np.zeros((256, 1), dtype='uint8')
for i in range(256):
    GAMMA_CVT[i][0] = 255 * (float(i) / 255) ** (1.0 / GAMMA)
VWELL = [chr(i) for i in range(65, 65 + 8)]
HWELL = (range(1, 13))
NUM_VSPLITS = 8
NUM_HSPLITS = 12
DATETIME = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
if os.name == 'nt':
    try:
        PICKFONT = ImageFont.truetype("arial.ttf", 25)
    except OSError:
        if INTERACTMODE:
            tkMessageBox.showinfo('sabayomikun', 'Font \"arial.ttf\" is not installed.')
        else:
            print('Font \"arial.ttf\" is not installed.')
        sys.exit()
else:
    try:
        PICKFONT = ImageFont.truetype("Arial.ttf", 25)
    except OSError:
        if INTERACTMODE:
            tkMessageBox.showinfo('sabayomikun', 'Font \"Arial.ttf\" is not installed.\napt install ttf-mscorefonts-installer')
        else:
            print('Font \"Arial.ttf\" is not installed.')
            print('apt install ttf-mscorefonts-installer')
        sys.exit()


def extractwell(v_imgf, cv_imgf, wellnamef, out_crop_debug_pathf, trial_nums, trial_expls, extf, maxrad):
    """
    extractwell
    """
    def trimimg(circlese, v_imge, margeval):
        pn0x = int(circlese[0][0][0]) + int(circlese[0][0][2]) + margeval
        pn0y = int(circlese[0][0][1]) + int(circlese[0][0][2]) + margeval
        pn1x = int(circlese[0][0][0]) - int(circlese[0][0][2]) - margeval
        pn1y = int(circlese[0][0][1]) - int(circlese[0][0][2]) - margeval
        maskf = np.zeros((500, 500), dtype=np.uint8)
        maskf = cv2.circle(maskf, (int(circlese[0][0][0]), int(circlese[0][0][1])), int(circlese[0][0][2]), color=(255, 255, 255), thickness=-1)
        v_imgm = v_imge.copy()
        v_imgm[maskf == 0] = [255, 255, 255]
        w_img = cv2.resize(v_imgm[pn1y:pn0y, pn1x:pn0x], dsize=(500, 500))
        return w_img
    # def trimimgchk

    def trimimgchk(circlese, v_imge, wellnamee, out_crop_debug_paths, trial_nums, trial_expls, trial_exts, exte, w_imgf):
        circle_tophit_img = v_imge.copy()
        for circle in circlese[0]:
            cv2.circle(circle_tophit_img, (int(circle[0]), int(circle[1])), int(circle[2]), (0, 255, 0), 2)
        cv2.circle(circle_tophit_img, (int(circlese[0][0][0]), int(circlese[0][0][1])), int(circlese[0][0][2]), (0, 0, 255), 2)
        textpathf = out_crop_debug_paths + wellnamee + '-circles' + trial_nums + trial_exts + '.txt'
        textfilef = open(textpathf, mode='w')
        np.savetxt(textfilef, circlesf[0], fmt='%d')
        textfilef.write('\n' + 'Tophit circle' + trial_expls + ' (Red)' + '\n')
        textfilef.write(str(circlese[0][0][0]) + ' ' + str(circlese[0][0][1]) + ' ' + str(circlese[0][0][2]))
        textfilef.close()
        cv2.imwrite(out_crop_debug_paths + wellnamee + '-circles' + trial_nums + trial_exts + exte, circle_tophit_img)
        cv2.imwrite(out_crop_debug_paths + wellnamee + '-cropped' + trial_nums + trial_exts + exte, w_imgf)
    # def trimimgchk

    def criparea(circlese, palnum):
        cripareaflag = False
        if (int(circlese[0]) - int(circlese[2]) - palnum >= 0 and
                int(circlese[1]) - int(circlese[2]) - palnum >= 0 and
                int(circlese[0]) + int(circlese[2]) + palnum <= 500 and
                int(circlese[1]) + int(circlese[2]) + palnum <= 500):
            cripareaflag = True
        return cripareaflag
    # def criparea

    def countdot(wellnamee, out_crop_picked_paths, exte, w_imgc, pickedarrf, depthswitch):
        w_imgp = w_imgc.copy()
        if depthswitch == 'shallow':
            low_color = np.array([10, 160, 160])
            high_color = np.array([50, 255, 255])
        if depthswitch == 'deep':
            low_color = np.array([00, 80, 80])
            high_color = np.array([60, 255, 255])
        UMatw_imgp = cv2.UMat(w_imgp)
        hsv = cv2.cvtColor(UMatw_imgp, cv2.COLOR_BGR2HSV)
        ex_img = cv2.inRange(hsv, low_color, high_color)
        ex_img = ex_img.get()
        if not PYOPENCVVER == str(3):
            contours, _ = cv2.findContours(ex_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        else:
            _, contours, _ = cv2.findContours(ex_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        pickednum = 0
        if depthswitch == 'shallow':
            dotsarea = 10
        if depthswitch == 'deep':
            dotsarea = 3
        for dots in contours:
            idot = cv2.moments(dots)
            if idot['m00'] > dotsarea:
                idotcx = int(idot['m10'] / idot['m00']) + 4
                idotcy = int(idot['m01'] / idot['m00']) + 4
                if BLUEMODE:
                    cv2.drawMarker(w_imgp, (idotcx, idotcy), (130, 0, 0), markerType=cv2.MARKER_CROSS, markerSize=6)
                    cv2.drawContours(w_imgp, dots, -1, (100, 0, 0), 1)
                else:
                    cv2.drawMarker(w_imgp, (idotcx, idotcy), (0, 100, 0), markerType=cv2.MARKER_CROSS, markerSize=6)
                    cv2.drawContours(w_imgp, dots, -1, (0, 70, 0), 1)
                pickednum += 1
        if not BLUEMODE:
            UMatw_imgp = cv2.UMat(w_imgp)
            w_imgp = cv2.cvtColor(UMatw_imgp, cv2.COLOR_BGR2RGB)
            w_imgp = w_imgp.get()
        w_img_pilf = Image.fromarray(w_imgp)
        drawpilf = ImageDraw.Draw(w_img_pilf)
        drawpilf.text((30, 30), wellnamee + '\n' + str(pickednum), fill='black', font=PICKFONT)
        if depthswitch == 'shallow':
            w_img_pilf.save(out_crop_picked_paths + wellnamee + exte)
        if depthswitch == 'deep':
            w_img_pilf.save(out_crop_picked_paths + wellnamee + exte)
        pickedarrf.append(pickednum)
    # def countdot

    w_img_flag = False
    if not PYOPENCVVER == str(2):
        circlesf = cv2.HoughCircles(cv_imgf, cv2.HOUGH_GRADIENT, 1, 20, param1=70, param2=60, minRadius=140, maxRadius=maxrad)
    else:
        circlesf = cv2.HoughCircles(cv_imgf, cv2.cv.CV_HOUGH_GRADIENT, 1, 20, param1=70, param2=60, minRadius=140, maxRadius=maxrad)
    if circlesf is not None:
        circlesf = np.uint16(np.around(circlesf))
        mgsval = 15
        while mgsval > 0:
            if criparea(circlesf[0][0], mgsval):
                w_img = trimimg(circlesf, v_imgf, mgsval)
                w_img_flag = True
                if CHECKMODE:
                    zerostring = ''
                    if mgsval < 10:
                        zerostring = '0'
                    trimimgchk(circlesf, v_imgf, wellnamef, out_crop_debug_pathf, trial_nums, trial_expls, '_margin' + zerostring + str(mgsval), extf, w_img)
            mgsval -= 2
            if w_img_flag:
                break
        else:
            circlesf_nooversize = np.empty((0, 3), int)
            for circle in circlesf[0]:
                if criparea(circle, 5):
                    circlesf_nooversize = np.append(circlesf_nooversize, [circle], axis=0)
            circlesf_nooversize = np.array([circlesf_nooversize[np.argsort(circlesf_nooversize[:, 2])[::-1]]])
            if not circlesf_nooversize.size == 0:
                w_img_flag = True
                w_img = trimimg(circlesf_nooversize, v_imgf, 5)
                if CHECKMODE:
                    circle_nooversize_img = v_imgf.copy()
                    for circle in circlesf[0]:
                        cv2.circle(circle_nooversize_img, (int(circle[0]), int(circle[1])), int(circle[2]), (255, 0, 0), 2)
                    for circle_nooversize in circlesf_nooversize[0]:
                        cv2.circle(circle_nooversize_img, (int(circle_nooversize[0]), int(circle_nooversize[1])), int(circle_nooversize[2]), (0, 255, 0), 2)
                    cv2.circle(circle_nooversize_img, (int(circlesf_nooversize[0][0][0]), int(circlesf_nooversize[0][0][1])), int(circlesf_nooversize[0][0][2]), (122, 122, 0), 2)
                    cv2.circle(circle_nooversize_img, (int(circlesf[0][0][0]), int(circlesf[0][0][1])), int(circlesf[0][0][2]), (0, 0, 255), 2)
                    textpathf = out_crop_debug_pathf + wellnamef + '-circles' + trial_nums + '_max' + '.txt'
                    textfilef = open(textpathf, mode='w')
                    np.savetxt(textfilef, circlesf_nooversize[0], fmt='%d')
                    textfilef.write('\n' + 'Maximal circle' + trial_expls + ' (Dark Green)' + '\n')
                    textfilef.write(str(circlesf_nooversize[0][0][0]) + ' ' + str(circlesf_nooversize[0][0][1]) + ' ' + str(circlesf_nooversize[0][0][2]))
                    textfilef.write('\n' + 'Tophit circle' + trial_expls + ' (Red)' + '\n')
                    textfilef.write(str(circlesf[0][0][0]) + ' ' + str(circlesf[0][0][1]) + ' ' + str(circlesf[0][0][2]))
                    textfilef.close()
                    cv2.imwrite(out_crop_debug_pathf + wellnamef + '-circles' + trial_nums + '_max' + ext, circle_nooversize_img)
                    cv2.imwrite(out_crop_debug_pathf + wellnamef + '-cropped' + trial_nums + '_max' + ext, w_img)
    if w_img_flag:
        if PICKMODE:
            countdot(wellname, out_crop_picked_path, ext, w_img, picked, 'shallow')
        if DEEPPICKMODE:
            countdot(wellname, out_crop_deeppicked_path, ext, w_img, deeppicked, 'deep')
        if BLUEMODE:
            w_img_cfrgb = w_img.copy()
        else:
            UMatw_img = cv2.UMat(w_img)
            w_img_cfrgb = cv2.cvtColor(UMatw_img, cv2.COLOR_BGR2RGB)
            w_img_cfrgb = w_img_cfrgb.get()
        w_img_cfrgb = Image.fromarray(w_img_cfrgb)
        drawcfrgb = ImageDraw.Draw(w_img_cfrgb)
        drawcfrgb.text((30, 30), wellnamef + '\n', fill='black', font=PICKFONT)
        w_img_cfrgb.save(out_crop_cv_path + wellnamef + ext)
    return w_img_flag
    # def extractwell


for imputfiles in os.listdir(INPUTPATH):
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
        if os.path.exists(OUTPUTPATH + basename):
            shutil.move(OUTPUTPATH + basename, OUTPUTPATH + basename + '_old_' + DATETIME)
        shutil.move(file_path, OUTPUTPATH + basename)
        continue
    if not ext:
        ext = '.' + imagetype.lower()
    if os.path.exists(OUTPUTPATH + rootname):
        shutil.move(OUTPUTPATH + rootname, OUTPUTPATH + rootname + '_old_' + DATETIME)
    os.makedirs(OUTPUTPATH + rootname)
    out_crop_cv_path = OUTPUTPATH + rootname + '/'
    if PICKMODE:
        if os.path.exists(OUTPUTPATH + rootname + '-detected1'):
            shutil.move(OUTPUTPATH + rootname + '-detected1', OUTPUTPATH + rootname + '-detected1' + '_old_' + DATETIME)
        os.makedirs(OUTPUTPATH + rootname + '-detected1' + '/')
        out_crop_picked_path = OUTPUTPATH + rootname + '-detected1' + '/'
        picked = []
    if DEEPPICKMODE:
        if os.path.exists(OUTPUTPATH + rootname + '-detected2'):
            shutil.move(OUTPUTPATH + rootname + '-detected2', OUTPUTPATH + rootname + '-detected2' + '_old_' + DATETIME)
        os.makedirs(OUTPUTPATH + rootname + '-detected2' + '/')
        out_crop_deeppicked_path = OUTPUTPATH + rootname + '-detected2' + '/'
        deeppicked = []
    if CHECKMODE:
        if os.path.exists(OUTPUTPATH + rootname + '-check'):
            shutil.move(OUTPUTPATH + rootname + '-check', OUTPUTPATH + rootname + '-check' + '_old_' + DATETIME)
        os.makedirs(OUTPUTPATH + rootname + '-check')
    out_crop_debug_path = OUTPUTPATH + rootname + '-check' + '/'
    imputimg = cv2.flip(cv2.resize(cv2.imread(file_path, cv2.IMREAD_COLOR), dsize=(7200, 4800)), 1)
    for h_img, vwellnm in zip(np.vsplit(imputimg, NUM_VSPLITS), VWELL):
        for v_img, hwellnm in zip(np.hsplit(h_img, NUM_HSPLITS), HWELL):
            v_img = cv2.resize(v_img, dsize=(500, 500))
            UMatv_img = cv2.UMat(v_img)
            cv_img = cv2.cvtColor(UMatv_img, cv2.COLOR_BGR2GRAY)
            cv_img = cv2.medianBlur(cv_img, 5)
            cv_img = cv2.LUT(cv_img, GAMMA_CVT)
            cv_img = cv_img.get()
            wellname = vwellnm + str(hwellnm)
            if CHECKMODE:
                cv2.imwrite(out_crop_debug_path + wellname + '-pre-cropped' + ext, v_img)
            w_img_ext_flag = False
            radius = 190
            while radius < 250:
                w_img_ext_flag = extractwell(v_img, cv_img, wellname, out_crop_debug_path, '_radius' + str(radius), ', radius = ' + str(radius), ext, radius)
                radius += 10
                if w_img_ext_flag:
                    break
            if not w_img_ext_flag:
                cv2.imwrite(out_crop_cv_path + wellname + ext, v_img)
                if PICKMODE:
                    picked.append(str('ND'))
                if DEEPPICKMODE:
                    deeppicked.append(str('ND'))
                if CHECKMODE:
                    if not PYOPENCVVER == str(2):
                        circles_g = cv2.HoughCircles(cv_img, cv2.HOUGH_GRADIENT, 1, 20, param1=70, param2=60, minRadius=140, maxRadius=250)
                    else:
                        circles_g = cv2.HoughCircles(cv_img, cv2.cv.CV_HOUGH_GRADIENT, 1, 20, param1=70, param2=60, minRadius=140, maxRadius=250)
                    circle_undersize_img = v_img.copy()
                    if circles_g is not None:
                        circles_g = np.uint16(np.around(circles_g))
                        circles_center = np.empty((0, 3), int)
                        for circle_g in circles_g[0]:
                            if (int(circle_g[0]) - int(circle_g[2]) - 15 >= 0 and
                                    int(circle_g[1]) - int(circle_g[2]) - 15 >= 0 and
                                    int(circle_g[0]) + int(circle_g[2]) + 15 <= 500 and
                                    int(circle_g[1]) + int(circle_g[2]) + 15 <= 500):
                                cv2.circle(circle_undersize_img, (int(circle_g[0]), int(circle_g[1])), int(circle_g[2]), (255, 0, 0), 2)
                                circles_center = np.append(circles_center, [circle_g], axis=0)
                        cv2.circle(circle_undersize_img, (int(circles_g[0][0][0]), int(circles_g[0][0][1])), int(circles_g[0][0][2]), (0, 0, 255), 2)
                        textpath = out_crop_debug_path + wellname + '-undersize' + '.txt'
                        textfile = open(textpath, mode='a')
                        if not circles_center.size == 0:
                            np.savetxt(textfile, circles_center, fmt='%d')
                        textfile.write('\n' + 'Tophit circle (Red)' + '\n')
                        textfile.write(str(circles_g[0][0][0]) + ' ' + str(circles_g[0][0][1]) + ' ' + str(circles_g[0][0][2]))
                        textfile.close()
                        cv2.imwrite(out_crop_debug_path + wellname + '-undersize' + ext, circle_undersize_img)
                    else:
                        textpath = out_crop_debug_path + wellname + '-nocircle' + '.txt'
                        textfile = open(textpath, mode='w')
                        textfile.write('No circle')
                        textfile.close()
                        cv2.imwrite(out_crop_debug_path + wellname + '-nocircle' + ext, v_img)
    if PICKMODE:
        pickedarr = [picked[x:x + 12] for x in range(0, len(picked), 12)]
        csvout = open(out_crop_picked_path + rootname + '-detected1.csv', 'w')
        csvwriter = csv.writer(csvout, lineterminator='\n')
        csvwriter.writerows(pickedarr)
        csvout.close()
    if DEEPPICKMODE:
        deeppickedarr = [deeppicked[x:x + 12] for x in range(0, len(deeppicked), 12)]
        csvoutd = open(out_crop_deeppicked_path + rootname + '-detected2.csv', 'w')
        csvwriterd = csv.writer(csvoutd, lineterminator='\n')
        csvwriterd.writerows(deeppickedarr)
        csvoutd.close()
    cv2.imwrite(out_crop_cv_path + rootname + '-flipped' + ext, cv2.flip(cv2.imread(file_path, cv2.IMREAD_COLOR), 1))
    if not INTERACTMODE:
        if os.path.exists(OUTPUTPATH + basename):
            if str(file_path).replace('//', '/') != str(OUTPUTPATH + basename).replace('//', '/'):
                shutil.move(OUTPUTPATH + basename, OUTPUTPATH + basename + '_old_' + DATETIME)
        shutil.move(file_path, OUTPUTPATH + basename)
if INTERACTMODE:
    tkMessageBox.showinfo('sabayomikun', 'Task finished.')

