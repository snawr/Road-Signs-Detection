import cv2
import numpy as np
import filters
import gui
import Classifier
#from skimage.filters import (threshold_otsu, threshold_niblack, threshold_sauvola)
from nick import nick

video_dir = 'videos\VIDEO_DAY.mp4'    # ŚCIEŻKA FILMU
cap = cv2.VideoCapture(video_dir)           # POBRANIE FILMU DO ZMIENNEJ
font = cv2.FONT_HERSHEY_SIMPLEX
#test_image = cv2.imread(r'images\CAR_PHOTO_RIGHT.jpg')  # WCZYTANIE OBRAZU, OPCJONALNIE

### OKNO KONFIGURACJI (ROZDZIAŁ 5.2) ###
cv2.namedWindow("settings",cv2.WINDOW_NORMAL)
cv2.resizeWindow("settings", 400, 300)
### INICJALIZACJA SUWAKÓW ###
cv2.createTrackbar("c_quality", "settings", 25, 99, gui.nothing)    #name, window, default, max, fcn
cv2.createTrackbar("c_max_num", "settings", 150, 200, gui.nothing)
cv2.createTrackbar("H_thresh", "settings", 35, 200, gui.nothing)
cv2.createTrackbar("H_minLineL", "settings", 10, 100, gui.nothing)
cv2.createTrackbar("H_maxGap", "settings", 10, 50, gui.nothing)
cv2.createTrackbar("Gaussian_C", "settings", 18, 40, gui.nothing)
cv2.createTrackbar("BIN_Thresh", "settings", 90, 255, gui.nothing)
cv2.createTrackbar("BIN_d", "settings", 3, 5, gui.nothing)
cv2.createTrackbar("BIN_k/10^d", "settings", 30, 99, gui.nothing)
cv2.createTrackbar("WinSize*2", "settings", 3, 99, gui.nothing)
cv2.createTrackbar("ROI_Lower", "settings", 88, 100, gui.nothing)
cv2.createTrackbar("ROI_Upper", "settings", 65, 100, gui.nothing)
cv2.createTrackbar("ROI_Left", "settings", 14, 100, gui.nothing)
cv2.createTrackbar("ROI_Right", "settings", 80, 100, gui.nothing)
cv2.createTrackbar("ROI_Offset", "settings", 22, 50, gui.nothing)
### INICJALIZACJA ZMIENNYCH ###
fastforward_index = 0   # ZMIENNA PRZEWIJANIA FILMU
frame_count = 0         # ZMIENNA OBLICZANIA FPS - OBECNIE WYŁĄCZONE
variance = []           # LISTA WARTOŚCI WARIANCJI
### GŁÓWNA PĘTLA PROGRAMU
while True:
    ret, frameORG = cap.read()  # ret = WARTOŚĆ LOGICZNA POWODZENIA ODCZYTANIA KLATKI (TRUE/FALSE), frameORG = OCZYTANA KLATKA
    ### PRZEWIJANIE KLATEK ###
    if fastforward_index != 0:
        fastforward_index-=1
        print(fastforward_index)
        continue
    ### POMIJANIE NIEOSTRYCH KLATEK (ROZDZIAŁ 5.1) ###
    # variance, skip = gui.skipBlurry(frameORG, 80, variance)
    # if skip:
    #     #continue   #ODKOMENTOWAĆ ŻEBY WŁĄCZYĆ POMIJANIE KLATEK
    #     pass


    ### POBIERANIE AKTUALNYCH WARTOŚCI Z SUWAKÓW I DOSTOSOWANIE ICH ZAKRESÓW###
    # max(1,X) BO WARTOŚĆ TA MUSI BYĆ WIĘKSZA OD 0
    lines_threshhold = max(1, cv2.getTrackbarPos("H_thresh", "settings"))  # PRÓG DLA TRANSFORMACJI HOUGHA
    lines_minLineLength = max(1, cv2.getTrackbarPos("H_minLineL", "settings"))  # MINIMALNA DŁUGOŚĆ DLA TRANSFORMACJI HOUGHA
    lines_maxGap = max(1, cv2.getTrackbarPos("H_maxGap", "settings"))  # MAKSYMALNA PRZERWA DLA TRANSFORMACJI HOUGHA
    quality = max(1, cv2.getTrackbarPos("c_quality", "settings")) / 100  # "JAKOŚĆ" NAROŻNIKÓW METODĄ SHI-TOMASI
    max_corn = max(1, cv2.getTrackbarPos("c_max_num", "settings"))  # MAKSYMALNA ILOŚĆ NAROŻNIKÓW
    Gaussian_C = cv2.getTrackbarPos("Gaussian_C", "settings") - 20  # STAŁA C W METODZIE BRADLEYA
    BIN_thresh = max(1, cv2.getTrackbarPos("BIN_Thresh", "settings")) # PRÓG DO METODY GLOBALNEJ
    BIN_d = cv2.getTrackbarPos("BIN_d", "settings")     # STOPIEŃ PODZIELENIA STAŁEJ K NP. BIN_d = 3 -> k/10^3
    BIN_k = max(0.001, cv2.getTrackbarPos("BIN_k/10^d", "settings")) / 10**BIN_d  # STAŁA K DLA BINARYZACJI ADAPTACYJNYCH
    BIN_WinSize = max(1, cv2.getTrackbarPos("WinSize*2", "settings"))*2 + 1 # ROZMIAR OTOCZENIA PIKSELA
    ROI_Lower = cv2.getTrackbarPos("ROI_Lower", "settings")/100     # WYMIARY ROI
    ROI_Upper = cv2.getTrackbarPos("ROI_Upper", "settings")/100     #
    ROI_Left = cv2.getTrackbarPos("ROI_Left", "settings")/100       #
    ROI_Right = cv2.getTrackbarPos("ROI_Right", "settings")/100     #
    ROI_Offset = cv2.getTrackbarPos("ROI_Offset", "settings")/100   #NACHYLENIE TRAPEZA ROI
    ### LISTA KONFIGURACJI ROI ###
    ROI_poly = [ROI_Left, ROI_Lower,  # BOT LEFT     %width, %height
                ROI_Right, ROI_Lower,  # BOT RIGHT    %width, %height
                ROI_Right - ROI_Offset, ROI_Upper,  # TOP RIGHT      %width, %height
                ROI_Left + ROI_Offset, ROI_Upper  # TOP LEFT       %width, %height
                ]

    ### OBLICZANIE FPS ###
    #fps = gui.eval_fps(frame_count)
    #frame_count += 1
    # cv2.putText(frameORG, "fps: "+str(fps), (10, 30), font, 0.8, (255, 255,255), 2, cv2.LINE_AA)

    if not ret: # JEŚLI FILM SIĘ SKOŃCZY
        cap = cv2.VideoCapture(video_dir)   # WCZYTAJ FILM OD NOWA
        continue

    # frameORG = test_image     #ODKOMENTOWAĆ W PRZYPADKU UŻYWANIA OBRAZU

    ### WSTĘPNE PRZETWARZANIE OBRAZU ###

    ### ROZMYCIE OBRAZU ###
    frameBLUR = cv2.GaussianBlur(frameORG, (5, 5), 0)

    ### OBSZAR ZAINTERESOWANIA ###
    frameROI_ORG = filters.region_of_interest(frameORG, ROI_poly)   #KLATKA OGRANICZONA DO OBSZARU ZAINTERESOWANIA
    ROI = filters.draw_region(frameORG, ROI_poly)                   #WIZUALIZACJA OBSZARU ZAINTERESOWANIA

    ### DETEKCJA KRAWĘDZI METODĄ CANNY ###
    #cannyEdges = cv2.Canny(frameBLUR, 75, 150)
    #cannyROI = filters.region_of_interest(cannyEdges, ROI_poly)
    #cannyBGR = cv2.cvtColor(cannyEdges, cv2.COLOR_GRAY2BGR)
    #cannyROI_BGR = filters.region_of_interest(cannyBGR)

    ### KONWERSJA DO SKALI SZAROŚCI ###
    frameGRAY = cv2.cvtColor(frameBLUR, cv2.COLOR_BGR2GRAY)
    # frame_HSV = cv2.cvtColor(frameBLUR, cv2.COLOR_BGR2HSV)
    # frame_HSV_V = frame_HSV[...,2]

    ### FILTRACJA OBSZARÓW O NISKIEJ JASNOŚCI ###
    # white_mask = filters.isLight(frameORG)
    # frameORG_filtered = cv2.bitwise_and(frameORG, frameORG, mask= white_mask)

    ### BINARYZACJA ###

    ### GLOBALNA ###
    # _, binary_global = cv2.threshold(frameGRAY, BIN_thresh, 255, cv2.THRESH_BINARY)
    # binary_global = binary_global.astype(np.float32) * 255

    ### OTSU ###
    # retur, binary_otsu = cv2.threshold(frameGRAY, 0, 255, cv2.THRESH_OTSU)
    # binary_otsu = binary_otsu.astype(np.float32) * 255

    ### ADAPTACYJNA ###

    ### BRADLEY ###
    # binary_gaus = cv2.adaptiveThreshold(frameGRAY, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, BIN_WinSize, Gaussian_C)  # ostatnią zmienną odejmuje się od wyniku
    # gaus_ROI = filters.region_of_interest(binary_gaus, ROI_poly)

    ### NIBLACK ###
    # thresh_niblack = threshold_niblack(frameGRAY, window_size=BIN_WinSize, k=BIN_k)
    # binary_niblack = frameGRAY > thresh_niblack
    # niblack_uint8 = binary_niblack.astype(np.uint8)*255   # ABY POPRAWNIE WYŚWIETLIĆ OBRAZ

    ### SAUVOLA ###
    # thresh_sauvola = threshold_sauvola(frameGRAY, window_size=BIN_WinSize, k=BIN_k)
    # binary_sauvola = frameGRAY > thresh_sauvola
    # sauvola_uint8 = binary_sauvola.astype(np.uint8)*255   # ABY POPRAWNIE WYŚWIETLIĆ OBRAZ

    ### NICK ###
    binary_nick = nick(frameGRAY, window= (BIN_WinSize,BIN_WinSize), k= BIN_k)
    nick_ROI = filters.region_of_interest(binary_nick, ROI_poly)
    #thresh_nick_ROI_filtered = cv2.bitwise_and(thresh_nick_ROI, thresh_nick_ROI, mask= white_mask) #NAŁOŻENIE MASKI OBSZARÓW JASNOŚCI

    ### DETEKCJA LINII PROSTYCH TRANSFORMACJĄ HOUGHA ###
    lines = cv2.HoughLinesP(nick_ROI, 1, np.pi/180, lines_threshhold, minLineLength=lines_minLineLength, maxLineGap=lines_maxGap)  #img,imgBGR, pixel res, angle res, threshhold lower = more lines, minLineLength, MaxDistance
    # lines_filtered = cv2.bitwise_and(onlyLINES, onlyLINES, mask= white_mask)  #NAŁOŻENIE MASKI BEZPOŚREDNIO NA LINIE

    ### NAROŻNIKI METODĄ SHI-TOMASI ###
    # onlyCORNERS = filters.display_corners(cannyROI,frameORG, max_corn, quality, 20)  # (img, imgBGR,  maxCorners, quality ratio, minDistance)
    # #frameROI_GRAY = np.float32(frameGRAY)

    ### METODA HARISSA ###
    # frameORG2 = frameORG.copy()
    # gray = np.float32(frameROI_GRAY)
    # dst = cv2.cornerHarris(gray, 3, 3, BIN_k)
    # dst = cv2.dilate(dst, None)
    # dst = cv2.dilate(dst, None)
    # frameORG2[dst > 0.01 * dst.max()] = [0, 0, 255]

    ### FILTRACJA LINII NA PODSTAWIE KĄTÓW ###
    lines_fwd_arrow_tip = filters.group_lines(lines, [20, 85])  # returns array of lines with angle between given values
    lines_turn_arrow_tip = filters.group_lines(lines, [20, 60])
    lines_vertical = filters.group_lines(lines, [50, 90])
    lines_horizontal = filters.group_lines(lines, [0,10])
    lines_road = filters.group_lines(lines, [20,60])
    all_lines = filters.group_lines(lines, [0,90])

    ### FILTRACJA POWTARZAJĄCYCH SIĘ LINII ###
    all_lines = filters.remove_duplicates(all_lines, 0)
    lines_vertical = filters.remove_duplicates(lines_vertical, 0)
    lines_vertical = filters.remove_duplicates(lines_vertical, 2)
    lines_horizontal = filters.remove_duplicates(lines_horizontal, 0)
    lines_horizontal = filters.remove_duplicates(lines_horizontal, 2)
    lines_road = filters.remove_duplicates(lines_road, 0)

    ### DETEKCJA LINII DROGOWYCH ###
    lines_solid = filters.length_filter(lines_road, [200,1000])         # LINIE CIĄGŁE
    lines_dotted = filters.length_filter(lines_road, [30,100])          # LINIE PRZERYWANE
    frame_solid = filters.display_lines(frameORG, lines_solid, 'red')   #
    frame_dotted = filters.display_lines(frameORG, lines_dotted, 'green')
    frame_road_lines = cv2.addWeighted(frame_dotted, 1, frame_solid, 1, 1)  # ŁĄCZY W 1 OBRAZ  # ŁĄCZY W 1 OBRAZ

    ### PODZIAŁ NA LINIE O KĄTACH DODATNICH I UJEMNYCH ###
    fwd_pos_lines, fwd_neg_lines = filters.group_divide(lines_fwd_arrow_tip)    #separates into positive and negative angle arrays
    turn_pos_lines, turn_neg_lines = filters.group_divide(lines_turn_arrow_tip)

    ### DETEKCJA ZWROTU STRZAŁKI ###
    fwd_arrow_tip = filters.find_corner(fwd_pos_lines, fwd_neg_lines)
    turn_arrow_tip = filters.find_corner(turn_pos_lines, turn_neg_lines)

    ### ROZPOZNAWANIE ZNAKÓW
    frame_arrows = Classifier.classify(frameORG, fwd_arrow_tip, turn_arrow_tip, lines_vertical, lines_horizontal)
    frame_arrows = cv2.addWeighted(frame_arrows, 0.8, frame_road_lines, 1, 1)  # DODAJE OBRAZ LINII DROGOWYCH
    ### WYŚWIETLENIE LINII
    onlyLINES = filters.display_lines(frameORG, all_lines)
    frameLINES = cv2.addWeighted(frameORG, 1, onlyLINES, 0.8, 1)  # łączy oba obiekty z podana waga

    ### WYDRUK WARTOŚCI LIST DO TERMINALA ###
    print('variance: ' + str(variance[-1]))
    print('total lines: '+ str(len(all_lines)))
    print('lines vertical: '+ str(len(lines_vertical)))
    print('lines horizontal: ' + str(len(lines_horizontal)))
    print('line corners: '+ str(len(turn_arrow_tip)))
    print('all lines: ' + str(all_lines))
    print('lines vertical: ' + str(lines_vertical))
    print('lines horizontal: ' + str(lines_horizontal))
    print('lines forward: ' + str(fwd_arrow_tip))
    print('lines turn: ' + str(turn_arrow_tip))
    print('lines lanes: ' + str(lines_solid))
    print('==================================')

    ### WYŚWIETLANIE OBRAZÓW ###
    #cv2.imshow('ROI', ROI)
    #cv2.imshow('org', frameORG)
    #cv2.imshow('filtered', frame_road_lines)
    # cv2.imshow('canny', cannyROI)
    # cv2.imshow('Gaus', binary_gaus)
    #cv2.imshow('Gaus_ROI', gaus_ROI)
    #cv2.imshow('Gaus_lines',gaus_frameLINES)
    #cv2.imshow('Niblack', niblack_uint8)
    # cv2.imshow('Sauvola', sauvola_uint8)
    cv2.imshow('Nick', binary_nick)
    cv2.imshow('Nick_lines', onlyLINES)
    #cv2.imshow('corners', onlyCORNERS)
    cv2.imshow('arrows',frame_arrows)

    # OBRAZY DO ZAPISANIA PODCZAS ZRZUTU EKRANU. PO PRZECINKU
    imagesToSave = [frameORG, frame_arrows]

    ### OPERACJE Z KLAWIATURY ###
    keyPressed = cv2.waitKey(1)     # FUNKCJA CZEKA 1MS NA WCIŚNIĘCIE PRZYCISKU
    ### Q = WYJŚCIE Z PROGRAMU ###
    if keyPressed == ord('q'):
        break
    ### S = PAUZA, PONOWNE NACIŚNIĘCIE ODTWARZA DALEJ ###
    if keyPressed == ord('s'):  #
        while(1):
            pauseKeyPressed = cv2.waitKey(1)
            if pauseKeyPressed == ord('s'):
                break
    ### SPACJA PODCZAS PAUZY ZAPISUJE ZRZUT EKRANU DO FOLDERU screenshots ###
            if pauseKeyPressed == ord(' '):
                # gui.screenshot(imagesToSave)
                pass
    ### R = ŁADUJE FILM OD NOWA ###
    if keyPressed == ord('r'):
        cap = cv2.VideoCapture(video_dir)  # jesli ret == false czyli film sie skonczyl, wczytaj film od nowa
        continue
    ### F = POMIJA NASTĘPNE 200 KLATEK FILMU ###
    if keyPressed == ord('f'):  #funkcja pomijania klatek
        fastforward_index = 200 #30 klatek == ~1s
        print('FORWARDING 200 frames')
        continue
    ### V = WYŚWIETLA WYKRES WARIANCJI Z OSTATNICH 100 KLATEK FILMU ###
    if keyPressed == ord('v'):
        gui.skipBlurry(frameORG, 80, variance[-100:], True)     #True -> plots last 100 var values with threshold
cap.release()  # ODBLOKOWUJE OBRAZ Z PLIKU
cv2.destroyAllWindows()  # ZAMYKA WSZYSTKIE OKNA, KONIEC PROGRAMU