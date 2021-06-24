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
            print("Не выбран zonx файл", err)
            raise

        try:
            #Создаём нвый файл базы данных с именем файла зоны+текущие дата и время
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
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

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
                PRIMARY KEY("AwId"))""")
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка создания таблицы БД Airways:", err)
            raise
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

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
        else:
            db.commit()

#Начинаем запись в БД из файла зоны

#Собираем базовые параметры зоны в кортеж values
        values = []
        params = []
        datetoday = datetime.date.today()
        values.append(zone_name)
        values.append(datetoday)

        for tag in zone.findall('n'):
            if tag.attrib['n'] == "BASE_PARAMETER":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "WorkRect":
                        params = tag1.attrib['v'].split(',')
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
        else:
            db.commit()

#Собираем дневную тему Theme1, ночную тему Theme1 и шрифты

        values1 = []
        values2 = []


        for tag in zone.findall('n'):
            if tag.attrib['n'] == "THEME1":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] != "FONT":
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
                            else:
                                db.commit()
            elif tag.attrib['n'] == "THEME2":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] != "FONT":
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
                            else:
                                db.commit()

        try:
            cursor.execute("insert into Themes values ('zone', '1', ?, ?, ?)", values1)
            cursor.execute("insert into Themes values ('zone', '2', ?, ?, ?)", values2)
            result = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Ошибка записи в таблицу Themes БД:", err)
            raise
        else:
            db.commit()

#Собираем точки и построчно записываем в БД
        for tag in zone.findall('n'):
            if tag.attrib['n'] == "ATC_STRUCTURE":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "WAYPOINTS":
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "15":
                                            try:
                                                cursor.execute("insert into Waypoints values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                                                result = cursor.fetchall()
                                            except sqlite3.DatabaseError as err:
                                                print("Ошибка записи в таблицу БД Waypoints:", err)
                                                raise
                                            else:
                                                db.commit()
                                        else:
                                            values.append(tag4.attrib['z'])

#Собираем маршруты и построчно записываем в БД
        for tag in zone.findall('n'):
            if tag.attrib['n'] == "ATC_STRUCTURE":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "AIRWAYS":
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4":
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    try:
                                                        values1.append(tag6.attrib['z'])
                                                    except:
                                                        values1.append('')

                                                try:
                                                    cursor.execute("insert into AirwaysWP values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД AirwaysWP:", err)
                                                    raise
                                                else:
                                                    db.commit()
                                        elif tag4.attrib['n'] != "12":
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into Airways values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД Airways:", err)
                                        raise
                                    else:
                                        db.commit()

#Собираем сектора и построчно записываем в БД
        for tag in zone.findall('n'):
            if tag.attrib['n'] == "ATC_STRUCTURE":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "FIR_UIR_AIRSPACES":
                        for tag2 in tag1.findall('n'):
                            if tag2.attrib['n'] == "values":
                                for tag3 in tag2.findall('n'):
                                    values = []
                                    values.append(tag3.attrib['n'].replace('r', ''))
                                    for tag4 in tag3.findall('n'):
                                        if tag4.attrib['n'] == "4":
                                            for tag5 in tag4.findall('n'):
                                                values1 = []
                                                values1.append(values[0])
                                                values1.append(tag5.attrib['n'].replace('r', ''))
                                                for tag6 in tag5.findall('n'):
                                                    if tag6.attrib['n'] == "2":
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
                                                                db.commit()
                                                    else:
                                                        values1.append(tag6.attrib['z'])
                                                try:
                                                    cursor.execute("insert into Sectors values (?, ?, ?, ?)", values1)
                                                    result = cursor.fetchall()
                                                except sqlite3.DatabaseError as err:
                                                    print("Ошибка записи в таблицу БД Sectors:", err)
                                                    raise
                                                else:
                                                    db.commit()
                                        else:
                                            values.append(tag4.attrib['z'])
                                    try:
                                        cursor.execute("insert into FirUir values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)", values)
                                        result = cursor.fetchall()
                                    except sqlite3.DatabaseError as err:
                                        print("Ошибка записи в таблицу БД FirUir:", err)
                                        raise
                                    else:
                                        db.commit()

#Собираем зоны ожидания и построчно записываем в БД
        for tag in zone.findall('n'):
            if tag.attrib['n'] == "ATC_STRUCTURE":
                for tag1 in tag.findall('n'):
                    if tag1.attrib['n'] == "HOLDING_AREAS":
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
                                    else:
                                        db.commit()

        db.close()

        self.db_edit.setText(db_filename)

#Импорт файла зоны в существующую базу данных
    def ZonxToDB(self):
        print("DB")

#Эеспорт БД в файл .zonx_btn
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
        except:
            print("Не удаётся открыть БД", err)
            raise

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

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"THEME1")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"THEME2")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"ATC_STRUCTURE")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"AIRPORTS")

        n2 = ET.SubElement(zone, 'n')
        n2.set('n',"GlobalNote")

        ET.dump(zone)
        tree = ET.ElementTree(zone)

        indent(zone)

        zone_filename = os.path.splitext(db_filename)[0]

        tree.write(zone_filename + ".zonx", encoding="windows-1251", xml_declaration=True)

        db.close()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
