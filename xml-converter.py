import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import datetime
import xml.etree.ElementTree as ET
import sqlite3

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
#Создаём статусбар
        self.statusBar().showMessage('Готово')

#Описываем триггеры
        openZonx = QAction(QIcon('open.png'), '&Открыть zonx...', self)
        openZonx.setShortcut('Ctrl+O')
        openZonx.setStatusTip('Открыть файл')
        openZonx.triggered.connect(self.openZonx)

        exitAction = QAction(QIcon('exit.png'), '&Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.close)

#Собираем меню
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openZonx)
        fileMenu.addAction(exitAction)

#Собираем тулбар
        self.toolbar = self.addToolBar('Выход')
        self.toolbar.addAction(openZonx)
        self.toolbar.addAction(exitAction)

#Создаём элементы главного окна
        zonx_label = QLabel('Выберите файл .zonx', self.centralWidget)

        self.zonx_edit = QLineEdit()

        zonx_btn = QPushButton('...', self.centralWidget)
        zonx_btn.clicked.connect(self.openZonx)
        zonx_btn.resize(zonx_btn.sizeHint())

        self.zonx_text = QTextEdit()

        zonxtodb_btn = QPushButton('Импорт в новую БД', self.centralWidget)
        zonxtodb_btn.clicked.connect(self.ZonxToNewDB)
        zonxtodb_btn.resize(zonxtodb_btn.sizeHint())

        db_label = QLabel('Выберите файл БД', self.centralWidget)

        self.db_edit = QLineEdit()

        db_btn = QPushButton('...', self.centralWidget)
        db_btn.clicked.connect(self.openDB)
        db_btn.resize(db_btn.sizeHint())

        zonxtodb1_btn = QPushButton('Импорт в существующую БД', self.centralWidget)
        zonxtodb1_btn.clicked.connect(self.ZonxToDB)
        zonxtodb1_btn.resize(zonxtodb1_btn.sizeHint())

        dbtozonx1_btn = QPushButton('Экспорт из БД в zonx', self.centralWidget)
        dbtozonx1_btn.clicked.connect(self.DBToZonx)
        dbtozonx1_btn.resize(dbtozonx1_btn.sizeHint())

        quit_btn = QPushButton('Выход', self.centralWidget)
        quit_btn.clicked.connect(self.close)
        quit_btn.resize(quit_btn.sizeHint())

#Собираем сетку главного окна
        h1box = QHBoxLayout()
        h1box.addWidget(self.zonx_edit)
        h1box.addWidget(zonx_btn)

        h2box = QHBoxLayout()
        h2box.addWidget(zonxtodb_btn)
        h2box.addStretch(1)

        h3box = QHBoxLayout()
        h3box.addWidget(self.db_edit)
        h3box.addWidget(db_btn)

        h4box = QHBoxLayout()
        h4box.addWidget(zonxtodb1_btn)
        h4box.addWidget(dbtozonx1_btn)
        h4box.addStretch(1)

        hbbox = QHBoxLayout()
        hbbox.addStretch(1)
        hbbox.addWidget(quit_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(zonx_label)
        vbox.addLayout(h1box)
        vbox.addWidget(self.zonx_text)
        vbox.addLayout(h2box)
        vbox.addWidget(db_label)
        vbox.addLayout(h3box)
        vbox.addLayout(h4box)
        vbox.addLayout(hbbox)

        self.centralWidget.setLayout(vbox)

#Отображаем главное окно
        self.setGeometry(300,300, 1000, 300)
        self.setWindowTitle('Zone XML Converter')
        self.setWindowIcon(QIcon('logo1.png'))
        self.show()

#Обработка события выхода из программы
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Выход', "Вы уверены, что хотите выйти?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

#Обработка события открытия файла зоны
    def openZonx(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть zonx', os.getcwd()) [0]
        self.zonx_edit.setText(fname)
        f = open(fname, "r")

        with f:
            data = f.read()
            self.zonx_text.setText(data)

#Обработка события открытия базы данных
    def openDB(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть БД', os.getcwd()) [0]
        self.db_edit.setText(fname)

#Создание новой базы данных и заливка в неё файла зоны
    def ZonxToNewDB(self):
        try:
            zone = ET.parse(self.zonx_edit.text()).getroot()
        except:
            print("Не выбран zonx файл")
            raise

        try:
            #Создаём новый файл базы данных с именем файла зоны+текущие дата и время
            now = datetime.datetime.now()
            zone_name = os.path.basename(self.zonx_edit.text())
            zone_name = os.path.splitext(zone_name)[0]
            db_filename = os.path.splitext(self.zonx_edit.text())[0] + now.strftime("-%d-%m-%Y-%H-%M") + ".db"
            db_file = open(db_filename, "w+")
            db_file.close()
        except:
            print("Не могу создать файл БД", err)
            raise

        try:
            db = sqlite3.connect(db_filename)
        except:
            print("Не могу соединиться с БД", err)
            raise

        cursor = db.cursor()

#Создаём структуру БД
        try:
            cursor.execute("""CREATE TABLE "Zones" (
                "Name"	TEXT NOT NULL UNIQUE,
                "Date"	NUMERIC NOT NULL,
                "WorkRectangle1"	INTEGER NOT NULL,
                "WorkRectangle2"	INTEGER NOT NULL,
                "WorkRectangle3"	INTEGER NOT NULL,
                "WorkRectangle4"	INTEGER NOT NULL,
                "ScaleMin"	INTEGER NOT NULL,
                "ScaleMax"	INTEGER NOT NULL,
                "RefPoint"	INTEGER NOT NULL,
                "AFTN"	TEXT NOT NULL,
                "RegionID"	TEXT NOT NULL,
                "MeasureMode"	TEXT NOT NULL,
                "PaletteNumber"	INTEGER NOT NULL,
                "MagneticDeclination" INTEGER NOT NULL,
                "MagneticDeclinationEna" INTEGER NOT NULL,
                PRIMARY KEY("Name"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Zones:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Fonts" (
                "FontID"	INTEGER,
                "ThemeID"	INTEGER NOT NULL,
                "ZoneID"	TEXT NOT NULL,
                "FontName"	TEXT NOT NULL,
                "FontSize"	INTEGER NOT NULL,
                "FontBold"	INTEGER NOT NULL,
                "FontItalic"	INTEGER NOT NULL,
                PRIMARY KEY("FontID","ThemeID","ZoneID"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Fonts:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Themes" (
                "ZoneName"	TEXT NOT NULL,
                "ThemeMode"	INTEGER NOT NULL,
                "PaletteID"	TEXT NOT NULL,
                "PointTypeID"	TEXT NOT NULL,
                "LineTypeID"	TEXT NOT NULL,
                PRIMARY KEY("ZoneName","ThemeMode"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Themes:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Waypoints" (
	           "WpId"	INTEGER NOT NULL UNIQUE,
	           "Name"	TEXT NOT NULL,
	           "ID"	TEXT NOT NULL,
               "Region"	TEXT,
               "Info"	TEXT,
               "Type"	INTEGER,
               "Pos"	TEXT NOT NULL,
               "DrawFlag"	INTEGER,
               "ColorSignIdx"	INTEGER,
               "ColorNameIdx"	INTEGER,
               "ColorIDIdx"	INTEGER,
               "ShiftName"	TEXT,
               "ShiftID"	TEXT,
               "BeginDT"	TEXT,
               "EndDT"	TEXT,
               "LastDT"	TEXT,
               PRIMARY KEY("WpId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Waypoints:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "WaypointRunways" (
	           "WpId"	INTEGER NOT NULL,
	           "WpRunwayId"	INTEGER NOT NULL,
	           "AirportId"	TEXT NOT NULL,
               "RunwayId"	TEXT,
               PRIMARY KEY("WpId","WpRunwayId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД WaypointRunways:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Airways" (
                "AwId"	INTEGER NOT NULL UNIQUE,
                "Name"	TEXT,
                "ID"	TEXT,
                "Info"	NUMERIC,
                "Type"	TEXT,
                "RegionsB"	TEXT,
                "RegionsE"	TEXT,
                "ColorCenterLineIdx"	INTEGER,
                "ColorBoundIdx"	INTEGER,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                "Airports"	TEXT,
                PRIMARY KEY("AwId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Airways:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "AirwaysWP" (
                "AwId"	INTEGER NOT NULL,
                "WpNumber"	INTEGER NOT NULL,
                "WpId"	INTEGER NOT NULL,
                "Type"	INTEGER,
                "Width"	INTEGER,
                "ListFL"	TEXT,
                "DrawFlag"	INTEGER,
                "BoundPoint1"	INTEGER,
                "BoundPoint2"	INTEGER,
                "BoundPoint3"	INTEGER,
                "BoundPoint4"	INTEGER,
                "HandChanged"	INTEGER,
                PRIMARY KEY("AwId","WpNumber","WpId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД AirwaysWP:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "FirUir" (
                "FirId"	INTEGER NOT NULL,
                "Name"	TEXT NOT NULL,
                "ID"	TEXT NOT NULL,
                "Info"	TEXT,
                "Type"	TEXT,
                "ListExBounds"	TEXT,
                "ListTransferPointsIdx"	TEXT,
                "Freq"	TEXT,
                "DrawFlag"	TEXT,
                "ColorLineIdx"	TEXT,
                "ColorFillIdx"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                "ListAirways"	TEXT,
                PRIMARY KEY("FirId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД FirUir:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Sectors" (
                "FirId"	INTEGER NOT NULL,
                "SectorNumber"	INTEGER NOT NULL,
                "Hmin"	TEXT NOT NULL,
                "Hmax"	TEXT,
                PRIMARY KEY("FirId","SectorNumber"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Sectors:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "SectorPoints" (
                "FirId"	INTEGER NOT NULL,
                "SectorNumber"	INTEGER NOT NULL,
                "PointID"	INTEGER NOT NULL,
                "Pos"	TEXT,
                "DrawFlag"	TEXT,
                PRIMARY KEY("FirId","SectorNumber","PointID"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД SectorPoints:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Holdings" (
                "HoldId"	INTEGER NOT NULL,
                "Name"	TEXT NOT NULL,
                "ID"	TEXT NOT NULL,
                "Patterns"	TEXT,
                "Programme"	TEXT,
                "Info"	TEXT,
                "Type"	TEXT,
                "IndexWPT"	TEXT,
                "Course"	TEXT,
                "Radius"	TEXT,
                "LPU"	TEXT,
                "FLmin"	TEXT,
                "FLmax"	TEXT,
                "EnterPoint1"	TEXT,
                "CenterPoint1"	TEXT,
                "ExitPoint1"	TEXT,
                "AngleStart1"	TEXT,
                "AngleSweep1"	TEXT,
                "EnterPoint2"	TEXT,
                "CenterPoint2"	TEXT,
                "ExitPoint2"	TEXT,
                "AngleStart2"	TEXT,
                "AngleSweep2"	TEXT,
                "DrawFlag"	TEXT,
                "ColorIdx"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("HoldId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Holdings:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Routes" (
                "RouteId"	INTEGER NOT NULL,
                "Name"	TEXT NOT NULL,
                "ID"	TEXT NOT NULL,
                "Info"	TEXT,
                "Type"	TEXT,
                "Airports"	TEXT,
                "DrawFlag"	TEXT,
                "ColorIdx"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("RouteId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Routes:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "RoutePoints" (
                "RouteId"	INTEGER NOT NULL,
                "WpId"	INTEGER NOT NULL,
                "IndexWPT"	TEXT NOT NULL,
                "Type"	TEXT NOT NULL,
                "Radius"	TEXT,
                "EnterPoint"	TEXT,
                "CenterPoint"	TEXT,
                "ExitPoint"	TEXT,
                "AngleStart"	TEXT,
                "AngleSweep"	TEXT,
                "Hmin"	TEXT,
                "Hmax"	TEXT,
                PRIMARY KEY("RouteId","WpId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД RoutePoints:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Restrictive" (
                "RestId"	INTEGER NOT NULL,
                "Name"	TEXT NOT NULL,
                "ID"	INTEGER NOT NULL,
                "Info"	TEXT NOT NULL,
                "Type"	TEXT,
                "Hmin"	TEXT,
                "Hmax"	TEXT,
                "DrawFlag"	TEXT,
                "Transp"	TEXT,
                "ColorLineIdx"	TEXT,
                "ColorFillIdx"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("RestId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Restrictive:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "RestPoints" (
                "RestId"	INTEGER NOT NULL,
                "PointId"	INTEGER NOT NULL,
                "Pos"	TEXT NOT NULL,
                PRIMARY KEY("RestId","PointId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД RestPoints:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Airports" (
                "AirportId"	INTEGER NOT NULL,
                "Name"	TEXT NOT NULL,
                "ID"	INTEGER NOT NULL,
                "ExtraID"	TEXT NOT NULL,
                "Info"	TEXT NOT NULL,
                "Type"	TEXT,
                "RefPoint"	TEXT,
                "TransmitionLevel"	TEXT,
                "AirportElevation"	TEXT,
                "MagneticDeclination"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("AirportId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Airports:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Runways" (
                "AirportId"	INTEGER NOT NULL,
                "RunwayId"	INTEGER NOT NULL,
                "Name"	TEXT,
                "ID"	TEXT,
                "DigitalID"     TEXT,
                "Info"	TEXT,
                "Type"	TEXT,
                "PosTh1"	TEXT,
                "PosTh2"	TEXT,
                "Glideslope"	TEXT,
                "Touchdown"	TEXT,
                "ElevationTh1"	TEXT,
                "ElevationTh2"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("AirportId","RunwayId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Runways:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Minimums" (
                "AirportId"	INTEGER NOT NULL,
                "RunwayId"	INTEGER NOT NULL,
                "MinID"	INTEGER NOT NULL,
                "Type"	TEXT,
                "PlaneCat"	TEXT,
                "Hmin"	TEXT,
                "Lmin"	TEXT,
                PRIMARY KEY("AirportId","RunwayId","MinID"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Minimums:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "Patterns" (
                "AirportId"	INTEGER NOT NULL,
                "PattId"	INTEGER NOT NULL,
                "Name"	TEXT,
                "ID"	TEXT,
                "Runways" TEXT,
                "Programme" TEXT,
                "Info"	TEXT,
                "Type"	TEXT,
                "AltitudeFAF"	TEXT,
                "ColorIdx"	TEXT,
                "BeginDT"	TEXT,
                "EndDT"	TEXT,
                "LastDT"	TEXT,
                PRIMARY KEY("AirportId","PattId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Patterns:", err)
            raise

        try:
            cursor.execute("""CREATE TABLE "PatternPoints" (
                "AirportId"	INTEGER NOT NULL,
                "PattId"	INTEGER NOT NULL,
                "PointID"	INTEGER NOT NULL,
                "IndexWPT"	TEXT,
                "Course"	TEXT,
                "Radius"	TEXT,
                "TurnType"	TEXT,
                "Hmin"	TEXT,
                "Hmax"	TEXT,
                "IAS"	TEXT,
                "CenterPoint"	TEXT,
                "TANPoint"	TEXT,
                "AngleStart"	TEXT,
                "AngleSweep"	TEXT,
                "EnterPoint"	TEXT,
                "RadiusRNAV"	TEXT,
                "FlybyAttr"	TEXT,
                PRIMARY KEY("AirportId","PattId","PointID"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД PatternPoints:", err)
            raise

        db.commit()

#Начинаем запись в БД из файла зоны

#Собираем базовые параметры зоны в кортеж values
        values = []
        params = []
        datetoday = datetime.date.today()
        values.append(str(zone_name))
        values.append(datetoday)

        for tag in zone.findall('n'):
            if tag.attrib['n'] == "BASE_PARAMETER":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "WorkRect":
                        params = tag1.attrib['v'].split(',') #разбиваем строку с рабочим квадратом на 4 отдельных параметра
                        for i in params:
                            values.append(i)
                    else:
                        values.append(tag1.attrib['v'])

#Записываем базовые параметры зоны в БД
        try:
            cursor.execute("insert into Zones values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка записи в таблицу БД Zones:", err)
            raise

#Собираем дневную тему Theme1, ночную тему Theme1 и шрифты

        values1 = []
        values2 = []


        for tag in zone.findall('n'):
            if tag.attrib['n'] == "THEME1":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] != "FONT": #Собираем шрифты
                        values1.append(str(tag1.attrib['v']))
                    else:
                        for tag2 in tag1.findall('n'):
                            values = []
                            values.append(tag2.attrib['n'])
                            for tag3 in tag2.findall('n'):
                                values.append(tag3.attrib['v'])
                            try:
                                cursor.execute("insert into Fonts values (?, '1', 'zone', ?, ?, ?, ?)", values)
                                result = cursor.fetchall()
                            except sqlite3.DatabaseError as err:
                                print("Ошибка записи в таблицу Fonts БД:", err)
                                raise
            elif tag.attrib['n'] == "THEME2":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] != "FONT":#Собираем шрифты
                        values2.append(str(tag1.attrib['v']))
                    else:
                        for tag2 in tag1.findall('n'):
                            values = []
                            values.append(tag2.attrib['n'])
                            for tag3 in tag2.findall('n'):
                                values.append(tag3.attrib['v'])
                            try:
                                cursor.execute("insert into Fonts values (?, '2', 'zone', ?, ?, ?, ?)", values)
                                result = cursor.fetchall()
                            except sqlite3.DatabaseError as err:
                                print("Ошибка записи в таблицу Fonts БД:", err)
                                raise
        try:
            cursor.execute("insert into Themes values ('zone', '1', ?, ?, ?)", values1)
            cursor.execute("insert into Themes values ('zone', '2', ?, ?, ?)", values2)
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка записи в таблицу Themes БД:", err)
            raise

        for tag in zone.findall('n'):
            if tag.attrib['n'] == "ATC_STRUCTURE":#Собираем ветку ATC_STRUCTURE
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "WAYPOINTS":#Собираем точки и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "15":
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    values1.append(tag6.attrib['z'])
                                                try:
                                                    cursor.execute("insert into WaypointRunways values (?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД WaypointRunways:", err)
                                                    raise
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Waypoints values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Waypoints:", err)
                                        raise
                    elif tag1.attrib['n'] == "AIRWAYS":#Собираем маршруты и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4": #Собираем точки маршрутов
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    try:
                                                        values1.append(tag6.attrib['z'])
                                                    except:
                                                        values1.append('')#Если в теге нет атрибута z, в БД добавляем пустое занчение
                                                try:
                                                    cursor.execute("insert into AirwaysWP values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД AirwaysWP:", err)
                                                    raise
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Airways values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Airways:", err)
                                        raise
                    elif tag1.attrib['n'] == "FIR_UIR_AIRSPACES":#Собираем сектора и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4":#Собираем области секторов
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    if tag6.attrib['n'] == "2":#Собираем точки областей
                                                        for tag7 in tag6.findall('n'):
                                                            values2 = []
                                                            values2.append(values1[0])
                                                            values2.append(values1[1])
                                                            values2.append(tag7.attrib['n'].replace('r', ''))
                                                            for tag8 in tag7.findall('n'):
                                                                values2.append(tag8.attrib['z'])
                                                            try:
                                                                cursor.execute("insert into SectorPoints values (?, ?, ?, ?, ?)", values2)
                                                                result = cursor.fetchall()
                                                            except sqlite3.DatabaseError as err:
                                                                print("Ошибка записи в таблицу БД SectorPoints:", err)
                                                                raise
                                                    else:
                                                        values1.append(tag6.attrib['z'])
                                                try:
                                                    cursor.execute("insert into Sectors values (?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД Sectors:", err)
                                                    raise
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into FirUir values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД FirUir:", err)
                                        raise
                    elif tag1.attrib['n'] == "HOLDING_AREAS":#Собираем зоны ожидания и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Holdings values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ? ,?, ?, ?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Holdings:", err)
                                        raise
                    elif tag1.attrib['n'] == "ROUTES":#Собираем маршруты и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4":#Собираем маршрутные точки
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    values1.append(tag6.attrib['z'])
                                                try:
                                                    cursor.execute("insert into RoutePoints values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД RoutePoints:", err)
                                                    raise
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Routes values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Routes:", err)
                                        raise
                    elif tag1.attrib['n'] == "RESTRICTIVE_AIRSPACES":#Собираем зоны ограничений и построчно записываем в БД
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4":#Собираем точки зон ограничений
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    values1.append(tag6.attrib['z'])
                                                try:
                                                    cursor.execute("insert into RestPoints values (?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД RestPoints:", err)
                                                    raise
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Restrictive values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Restrictive:", err)
                                        raise
            elif tag.attrib['n'] == "AIRPORTS":#Собираем аэропорты и построчно записываем в БД
                for tag1 in tag.findall('n'):
                    values = []#Список с параметрами аэропорта
                    values.append(tag1.attrib['n'])
                    for tag2 in tag1.findall('n'):
                        if tag2.attrib['n'] == "RUNWAYS":
                            for tag3 in tag2.findall('n'):
                                if tag3.attrib['n'] == "values":
                                    for tag4 in tag3.findall('n'):
                                        values1 = []#Список с параметрами курсов
                                        values1.append(values[0])
                                        values1.append(tag4.attrib['n'].replace('r', ''))
                                        for tag5 in tag4.findall('n'):
                                            if tag5.attrib['n'] == "11":
                                                for tag6 in tag5.findall('n'):
                                                    values2 = []#Список параметров минимумов
                                                    values2.append(values1[0])
                                                    values2.append(values1[1])
                                                    values2.append(tag6.attrib['n'].replace('r', ''))
                                                    for tag7 in tag6.findall('n'):
                                                        values2.append(tag7.attrib['z'])
                                                    try:
                                                        cursor.execute("insert into Minimums values (?, ?, ?, ?, ?, ?, ?)", values2)
                                                        result = cursor.fetchall()
                                                    except sqlite3.DatabaseError as err:
                                                        print("Ошибка записи в таблицу БД Minimums:", err)
                                                        raise
                                            else:
                                                values1.append(tag5.attrib['z'])
                                        try:
                                            cursor.execute("insert into Runways values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values1)
                                            result = cursor.fetchall()
                                        except sqlite3.DatabaseError as err:
                                            print("Ошибка записи в таблицу БД Runways:", err)
                                            raise
                        elif tag2.attrib['n'] == 'OBSTACLES':
                            continue
                        elif tag2.attrib['n'] == 'RESTRICTIVE_BEARINGS':
                            continue
                        elif tag2.attrib['n'] == 'PATTERNS':
                            for tag3 in tag2.findall('n'):
                                if tag3.attrib['n'] == "values":
                                    for tag4 in tag3.findall('n'):
                                        values1 = []#Список параметров паттерна
                                        values1.append(values[0])
                                        values1.append(tag4.attrib['n'].replace('r', ''))
                                        for tag5 in tag4.findall('n'):
                                            if tag5.attrib['n'] == "6":
                                                for tag6 in tag5.findall('n'):
                                                    values2 = []
                                                    values2.append(values1[0])
                                                    values2.append(values1[1])
                                                    values2.append(tag6.attrib['n'].replace('r', ''))
                                                    for tag7 in tag6.findall('n'):
                                                        try:
                                                            values2.append(tag7.attrib['z'])
                                                        except:
                                                            values2.append('')
                                                    try:
                                                        cursor.execute("insert into PatternPoints values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values2)
                                                        result = cursor.fetchall()
                                                    except sqlite3.DatabaseError as err:
                                                        print("Ошибка записи в таблицу БД PatternPoints:", err)
                                                        raise
                                            else:
                                                values1.append(tag5.attrib['z'])
                                        try:
                                            cursor.execute("insert into Patterns values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values1)
                                            result = cursor.fetchall()
                                        except sqlite3.DatabaseError as err:
                                            print("Ошибка записи в таблицу БД Patterns:", err)
                                            raise
                        else:
                            values.append(tag2.attrib['v'])
                    try:
                        cursor.execute("insert into Airports values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                        result = cursor.fetchall()
                    except sqlite3.DatabaseError as err:
                        print("Ошибка записи в таблицу БД Airports:", err)
                        raise


        db.commit()

        db.close()

        self.db_edit.setText(db_filename)

#Импорт файла зоны в существующую базу данных
    def ZonxToDB(self):
        print("DB")

#Экспорт БД в файл .zonx_btn
    def DBToZonx(self):

        #Делаем красивую табуляцию и переоды строки
        def indent(elem, level=0):
            i = "\n" + level*"\t"
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "\t"
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        db_filename = self.db_edit.text()

        try:
            db = sqlite3.connect(db_filename)
            cursor = db.cursor()
            cursor1 = db.cursor()
        except:
            print("Не удаётся открыть БД", err)
            raise
#Выгружаем базовые параметры зоны
        zone = ET.Element('n')
        zone.set('ver','1.1')

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"Spec")
        n2.set('v',"ATC STRUCTURE")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"Ver")
        n2.set('v',"1.00")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"BASE_PARAMETER")

        cursor.execute("SELECT * from Zones")
        result = cursor.fetchone()
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"WorkRect")
        n3.set('v',str(result[2]) + "," + str(result[3]) + "," + str(result[4]) + "," + str(result[5]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"ScaleMin")
        n3.set('v',str(result[6]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"ScaleMax")
        n3.set('v',str(result[7]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"RefPoint")
        n3.set('v',str(result[8]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"AFTN")
        n3.set('v',str(result[9]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"REGION")
        n3.set('v',str(result[10]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"MeasureMode")
        n3.set('v',str(result[11]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"PaletteNumber")
        n3.set('v',str(result[12]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"MagneticDeclination")
        n3.set('v',str(result[13]))
        n3 = ET.SubElement(n2,'n')
        n3.set('n',"MagneticDeclinationEnable")
        n3.set('v',str(result[14]))
#Выгружаем стили
        for i in [1,2]:
            n2 = ET.SubElement(zone, 'n')
            n2.set('n',"THEME"+str(i))
            cursor.execute("""SELECT * from Themes WHERE ThemeMode = ? """, (i,))
            row = cursor.fetchone()
            n3 = ET.SubElement(n2, 'n')
            n3.set('n',"ListPaletteID")
            n3.set('v',row[2])
            n3 = ET.SubElement(n2, 'n')
            n3.set('n',"ListPointtypeID")
            n3.set('v',row[3])
            n3 = ET.SubElement(n2, 'n')
            n3.set('n',"ListLinetypeID")
            n3.set('v',row[4])
            n3 = ET.SubElement(n2, 'n')
            n3.set('n',"FONT")
            cursor.execute("""SELECT * from Fonts WHERE ThemeID = ? """, (i,))
            records = cursor.fetchall()
            for row in records:
                n4 = ET.SubElement(n3, 'n')
                n4.set('n', str(row[0]))
                n5 = ET.SubElement(n4, 'n')
                n5.set('n', "FontName")
                n5.set('v', row[3])
                n5 = ET.SubElement(n4, 'n')
                n5.set('n', "FontSize")
                n5.set('v', str(row[4]))
                n5 = ET.SubElement(n4, 'n')
                n5.set('n', "FontBold")
                n5.set('v', str(row[5]))
                n5 = ET.SubElement(n4, 'n')
                n5.set('n', "FontItalic")
                n5.set('v', str(row[6]))
#Выгружаем точки
        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"ATC_STRUCTURE")
        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"WAYPOINTS")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Region")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Pos")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorSignIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorNameIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorIDIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ShiftName")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ShiftID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"RUNWAYS")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"AirportID")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"RunwayID")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from Waypoints""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                if i != 15:
                    n6.set('z', str(row[i+1]))
                elif i == 15: #Выгружаем привязку точек к аэродромам и курсам
                    cursor.execute("""SELECT * from WaypointRunways WHERE WpId = ?""", (row[0],))
                    records1 = cursor.fetchall()
                    for row1 in records1:
                        n7 = ET.SubElement(n6, 'n')
                        n7.set('n', "r" + str(row1[1]))
                        n8 = ET.SubElement(n7, 'n')
                        n8.set('n', "0")
                        n8.set('z', str(row1[2]))
                        n8 = ET.SubElement(n7, 'n')
                        n8.set('n', "1")
                        n8.set('z', str(row1[3]))

        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"AIRWAYS")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"POINTS")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"IndexWPT")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Type")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Width")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"ListFL")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"DrawFlag")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"BoundPoint1")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"BoundPoint2")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"BoundPoint3")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"BoundPoint4")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"HandChanged")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"RegionsB")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"RegionsE")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorCenterLineIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorBoundIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Airports")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from Airways""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                if i < 4:
                    n6.set('z', str(row[i+1]))
                elif i == 4:
                    cursor.execute("""SELECT * from AirwaysWP WHERE AwId = ?""", (row[0],))
                    records1 = cursor.fetchall()
                    for row1 in records1:
                        n7 = ET.SubElement(n6, 'n')
                        n7.set('n', "r" + str(row1[1]))
                        for j in range(len(row1) - 2):
                            n8 = ET.SubElement(n7, 'n')
                            n8.set('n', str(j))
                            if row1[j+2] != '':
                                n8.set('z', str(row1[j+2]))
                elif i > 4:
                    n6.set('z', str(row[i]))

        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"FIR_UIR_AIRSPACES")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"SECTORS")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Hmin")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Hmax")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"POINTS")
        n7 = ET.SubElement(n6, 'n')
        n7.set('n',"Pos")
        n7 = ET.SubElement(n6, 'n')
        n7.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ListExBounds")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ListTransferPointsIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Freq")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorLineIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorFillIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ListAirways")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from FirUir""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                if i < 4:
                    n6.set('z', str(row[i+1]))
                elif i == 4:
                    cursor.execute("""SELECT * from Sectors WHERE FirId = ?""", (row[0],))
                    records1 = cursor.fetchall()
                    for row1 in records1:
                        n7 = ET.SubElement(n6, 'n')
                        n7.set('n', "r" + str(row1[1]))
                        for j in range(len(row1) - 1):
                            n8 = ET.SubElement(n7, 'n')
                            n8.set('n', str(j))
                            if j < 2:
                                n8.set('z', str(row1[j+2]))
                            elif j == 2:
                                cursor.execute("""SELECT * from SectorPoints WHERE FirId = ? AND SectorNumber = ?""", (row[0], row1[1],))
                                records2 = cursor.fetchall()
                                for row2 in records2:
                                    n9 = ET.SubElement(n8, 'n')
                                    n9.set('n', "r" + str(row2[2]))
                                    n10 = ET.SubElement(n9, 'n')
                                    n10.set('n', "0")
                                    n10.set('z', str(row2[3]))
                                    n10 = ET.SubElement(n9, 'n')
                                    n10.set('n', "1")
                                    n10.set('z', str(row2[4]))
                elif i > 4:
                    n6.set('z', str(row[i]))

        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"HOLDING_AREAS")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Patterns")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Programme")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"IndexWPT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Course")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Radius")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LPU")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"FLmin")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"FLmax")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EnterPoint1")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"CenterPoint1")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ExitPoint1")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"AngleStart1")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"AngleSweep1")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EnterPoint2")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"CenterPoint2")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ExitPoint2")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"AngleStart2")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"AngleSweep2")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from Holdings""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)-1):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                n6.set('z', str(row[i+1]))

        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"ROUTES")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"POINTS")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"IndexWPT")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Type")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Radius")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"EnterPoint")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"CenterPoint")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"ExitPoint")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"AngleStart")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"AngleSweep")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Hmin")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Hmax")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Airports")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from Routes""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                if i < 4:
                    n6.set('z', str(row[i+1]))
                elif i == 4:
                    cursor.execute("""SELECT * from RoutePoints WHERE RouteId = ?""", (row[0],))
                    records1 = cursor.fetchall()
                    for row1 in records1:
                        n7 = ET.SubElement(n6, 'n')
                        n7.set('n', "r" + str(row1[1]))
                        for j in range(len(row1) - 2):
                            n8 = ET.SubElement(n7, 'n')
                            n8.set('n', str(j))
                            n8.set('z', str(row1[j+2]))
                elif i > 4:
                    n6.set('z', str(row[i]))

        n3 = ET.SubElement(n2, 'n')
        n3.set('n',"RESTRICTIVE_AIRSPACES")
        n3.set('t',"table")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"geometry")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Name")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ID")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Info")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Type")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"POINTS")
        n6 = ET.SubElement(n5, 'n')
        n6.set('n',"Pos")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Hmin")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Hmax")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"DrawFlag")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"Transp")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorLineIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"ColorFillIdx")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"BeginDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"EndDT")
        n5 = ET.SubElement(n4, 'n')
        n5.set('n',"LastDT")
        n4 = ET.SubElement(n3, 'n')
        n4.set('n',"values")
        cursor.execute("""SELECT * from Restrictive""")
        records = cursor.fetchall()
        for row in records:
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"r" + str(row[0]))
            for i in range(len(row)):
                n6 = ET.SubElement(n5, 'n')
                n6.set('n', str(i))
                if i < 4:
                    n6.set('z', str(row[i+1]))
                elif i == 4:
                    cursor.execute("""SELECT * from RestPoints WHERE RestId = ?""", (row[0],))
                    records1 = cursor.fetchall()
                    for row1 in records1:
                        n7 = ET.SubElement(n6, 'n')
                        n7.set('n', "r" + str(row1[1]))
                        n8 = ET.SubElement(n7, 'n')
                        n8.set('n', '0')
                        n8.set('z', str(row1[2]))
                elif i > 4:
                    n6.set('z', str(row[i]))

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"AIRPORTS")
        cursor.execute("""SELECT * from Airports""")
        records = cursor.fetchall()
        for row in records:
            n3 = ET.SubElement(n2, 'n')
            if len(str(row[0])) == 1:
                n3.set('n',"00" + str(row[0]))
            elif len(str(row[0])) == 2:
                n3.set('n',"0" + str(row[0]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"Name")
            n4.set('v',str(row[1]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"ID")
            n4.set('v',str(row[2]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"ExtraID")
            n4.set('v',str(row[3]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"Info")
            n4.set('v',str(row[4]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"Type")
            n4.set('v',str(row[5]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"RefPoint")
            n4.set('v',str(row[6]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"TransmitionLevel")
            n4.set('v',str(row[7]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"AirportElevation")
            n4.set('v',str(row[8]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"MagneticDeclination")
            n4.set('v',str(row[9]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"BeginDT")
            n4.set('v',str(row[10]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"EndDT")
            n4.set('v',str(row[11]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"LastDT")
            n4.set('v',str(row[12]))
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"RUNWAYS")
            n4.set('t',"table")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"geometry")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Name")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ID")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"DigitalID")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Info")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Type")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"PosTh1")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"PosTh2")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Glideslope")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Touchdown")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ElevationTh1")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ElevationTh2")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"MINIMUM")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Type")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"PlaneCat")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Hmin")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Lmin")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"BeginDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"EndDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"LastDT")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"values")
            cursor.execute("""SELECT * from Runways WHERE AirportId = ?""", (row[0],))
            records1 = cursor.fetchall()
            for row1 in records1:
                n6 = ET.SubElement(n5, 'n')
                n6.set('n',"r" + str(row1[1]))
                for i in range(len(row1)-1):
                    n7 = ET.SubElement(n6, 'n')
                    n7.set('n', str(i))
                    if i < 11:
                        n7.set('z', str(row1[i+2]))
                    elif i == 11:
                        cursor.execute("""SELECT * from Minimums WHERE AirportId = ? AND RunwayId = ?""", (row[0], row1[1],))
                        records2 = cursor.fetchall()
                        for row2 in records2:
                            n8 = ET.SubElement(n7, 'n')
                            n8.set('n', "r" + str(row2[2]))
                            for j in range(len(row2)-3):
                                n9 = ET.SubElement(n8, 'n')
                                n9.set('n', str(j))
                                n9.set('z', str(row2[j+3]))
                    elif i > 11:
                        n7.set('z', str(row1[i+1]))

            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"OBSTACLES")
            n4.set('t',"table")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"geometry")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Name")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ID")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Info")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Type")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Pos")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Hmin")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Radius")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"DrawFlag")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ColorSignIdx")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ColorNameIdx")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ShiftName")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"BeginDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"EndDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"LastDT")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"values")
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"RESTRICTIVE_BEARINGS")
            n4.set('t',"table")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"geometry")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Name")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ID")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Info")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Type")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Pos")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Azimuth")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"DistBeg")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"DistEnd")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Delta")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Hmin")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"DrawFlag")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Transp")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ColorIdx")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"BeginDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"EndDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"LastDT")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"values")
            n4 = ET.SubElement(n3, 'n')
            n4.set('n',"PATTERNS")
            n4.set('t',"table")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"geometry")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Name")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ID")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Runways")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Programme")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Info")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"Type")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"POINTS")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"IndexWPT")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Course")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Radius")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"TurnType")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Hmin")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"Hmax")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"IAS")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"CenterPoint")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"TANPoint")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"AngleStart")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"AngleSweep")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"EnterPoint")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"RadiusRNAV")
            n7 = ET.SubElement(n6, 'n')
            n7.set('n',"FlybyAttr")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"AltitudeFAF")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"ColorIdx")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"BeginDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"EndDT")
            n6 = ET.SubElement(n5, 'n')
            n6.set('n',"LastDT")
            n5 = ET.SubElement(n4, 'n')
            n5.set('n',"values")
            cursor.execute("""SELECT * from Patterns WHERE AirportId = ?""", (row[0],))
            records1 = cursor.fetchall()
            for row1 in records1:
                n6 = ET.SubElement(n5, 'n')
                n6.set('n',"r" + str(row1[1]))
                for i in range(len(row1)-1):
                    n7 = ET.SubElement(n6, 'n')
                    n7.set('n', str(i))
                    if i < 6:
                        n7.set('z', str(row1[i+2]))
                    elif i == 6:
                        cursor.execute("""SELECT * from PatternPoints WHERE AirportId = ? AND PattId = ?""", (row[0], row1[1],))
                        records2 = cursor.fetchall()
                        for row2 in records2:
                            n8 = ET.SubElement(n7, 'n')
                            n8.set('n', "r" + str(row2[2]))
                            for j in range(len(row2)-3):
                                n9 = ET.SubElement(n8, 'n')
                                n9.set('n', str(j))
                                n9.set('z', str(row2[j+3]))
                    elif i > 6:
                        n7.set('z', str(row1[i+1]))

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"GlobalNote")

        tree = ET.ElementTree(zone)

        indent(zone)

        zone_filename = os.path.splitext(db_filename)[0]

        tree.write(zone_filename + ".zonx", encoding="windows-1251", xml_declaration=True)

        cursor.close()
        db.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
