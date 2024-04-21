import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datetime import datetime
import html


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(900, 600)
	    
        main = QWidget()
        
        self.setCentralWidget(main)
        
        main.setLayout(QHBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()
        self.webView.setFixedSize(1000, 450)
        
		
        
        controls_panel = QGridLayout()
       
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)
        

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)


        _label = QLabel('<h2> From: </h2>', self)
        _label.setFixedSize(80,35)
        self.from_box = QComboBox()
        self.from_box.setFixedSize(300,35) 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label, 0, 0)
        controls_panel.addWidget(self.from_box, 0, 1)
        

        _label = QLabel('<h2>To: </h2> ', self)
        _label.setFixedSize(80,35)
        self.to_box = QComboBox() 
        self.to_box.setFixedSize(300,35) 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label, 1, 0)
        controls_panel.addWidget(self.to_box, 1, 1)

        _label = QLabel('<h2>With: </h2>', self)
        _label.setFixedSize(80,35)
        self.with_box = QComboBox()
        self.with_box.setFixedSize(65,35) 
        self.with_box.addItems( ['Bus', 'Tram', 'Train', 'Metro', 'All'] )
        self.with_box.setCurrentIndex( 4 )
        controls_panel.addWidget(_label, 2, 0 )
        controls_panel.addWidget(self.with_box, 2, 1)

        _label = QLabel('<h2>Hops: </h2> ', self)
        _label.setFixedSize(80,35)
        self.hop_box = QComboBox()
        self.hop_box.setFixedSize(50,35) 
        self.hop_box.addItems( ['1', '2', '3'] )
        self.hop_box.setCurrentIndex( 2 )
        controls_panel.addWidget(_label, 3, 0 )
        controls_panel.addWidget(self.hop_box, 3, 1)

        self.go_button = QPushButton(" Go! ")
        self.go_button.setFixedSize(100,50)
        self.go_button.setStyleSheet("background-color: #99ff99; font-size: 20px;" )
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button, 4, 0)
        
        self.save_button = QPushButton("Save!")
        self.save_button.setFixedSize(200,50)
        self.save_button.setStyleSheet("background-color: #cccccc; font-size: 20px;" )
        self.save_button.clicked.connect(self.button_Save)
        controls_panel.addWidget(self.save_button, 4, 1)

        self.clear_button = QPushButton("Clear ")
        self.clear_button.setFixedSize(150,50)
        self.clear_button.setStyleSheet("background-color: #ff8080; font-size: 20px;")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.show_button = QPushButton("Show!")
        self.show_button.setFixedSize(150,50)
        self.show_button.setStyleSheet("background-color: #cccccc; font-size: 20px;")
        self.show_button.clicked.connect(self.button_Show)
        controls_panel.addWidget(self.show_button, 6, 0)
        
        self.line_box = QComboBox() 
        self.line_box.setFixedSize(150,50)
        self.line_box.setEditable(True)
        self.line_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.line_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(self.line_box, 6, 1)

        
        self.maptype_box = QComboBox()
        self.maptype_box.setFixedSize(200,50)
        self.maptype_box.setStyleSheet("background-color: #cccccc; font-size: 20px;")
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)
        self.connect_DB()


        self.startingpoint = True
                   
        self.show()
        self.draw = 0
        

    def connect_DB(self):
        self.conn = psycopg2.connect(database="l3info_10", user="l3info_10", host="10.11.11.22", password="L3INFO_10")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""SELECT distinct nom_long FROM nodes_TABLE ORDER BY nom_long """)
        self.conn.commit()
        rows1 = self.cursor.fetchall()

        self.cursor.execute("""SELECT distinct res_com FROM routeINT_TABLE ORDER BY res_com  """)
        self.conn.commit()
        rows2 = self.cursor.fetchall()

        for row in rows1 : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))
        for row in rows2 : 
            self.line_box.addItem(str(row[0]))

    def table_Click(self) :
        
        prev_lat = 0
        if (self.draw == 2 ) :  
            k = 0
            for line in range(0, len(self.rows)) :
                    lat = float(self.rows[line][1])
                    lon = float(self.rows[line][2]) 
                    if prev_lat != 0 :
                        self.webView.addSegment(prev_lat, prev_lon, lat, lon)
                    prev_lat = lat
                    prev_lon = lon
                    self.webView.addMarker(lat, lon)
                    k = k + 1

        elif (self.draw == 1 ) :
            k = 0
            for col in self.rows[self.tableWidget.currentRow()] :
                if (k % 3) == 0:
                    lst = col.split(',')
                    lat = float(lst[0])
                    lon = float(lst[1]) 
                    if prev_lat != 0:
                        self.webView.addSegment( prev_lat, prev_lon, lat, lon )
                    prev_lat = lat
                    prev_lon = lon

                    self.webView.addMarker( lat, lon )
                k = k + 1
            

    def button_Go(self):
        self.draw = 1 
        self.tableWidget.clearContents()
        while(self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
            self.tableWidget.removeColumn(0)
           

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _with = str(self.with_box.currentText())
        _hops = int(self.hop_box.currentText())
        self.rows = []

        if _with == 'Tram' :
            b = 0
        if _with == 'Metro' :
            b = 1
        if _with == 'Train' :
            b = 2
        if _with == 'Bus' :
            b = 3
        if _with == 'All' :
            b = -1

        if _hops >= 1 :
            if b == -1 :
                self.cursor.execute(""f" SELECT distinct  A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I )  as B, (SELECT distinct CONCAT(nodes_TABLE.lat,',',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as A WHERE A.nom_long = $${_fromstation}$$ AND B.nom_long =$${_tostation}$$ AND A.res_com = B.res_com""")
                self.conn.commit()  
                self.rows += self.cursor.fetchall()
            else : 
                self.cursor.execute(""f" SELECT distinct  A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I )  as B, (SELECT distinct CONCAT(nodes_TABLE.lat,',',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as A WHERE A.nom_long = $${_fromstation}$$ AND B.nom_long =$${_tostation}$$ AND A.res_com = B.res_com""")
                self.conn.commit()  
                self.rows += self.cursor.fetchall()

        if _hops >= 2 : 
            if b == -1 :
                self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long, C.res_com, D.geo_point_2d, D.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as A, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as B, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as C, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as D WHERE A.nom_long = $${_fromstation}$$ AND D.nom_long = $${_tostation}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()
            else :
                self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B.geo_point_2d, B.nom_long, C.res_com, D.geo_point_2d, D.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as A, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as B, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as C, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I) as D WHERE A.nom_long = $${_fromstation}$$ AND D.nom_long = $${_tostation}$$ AND A.res_com = B.res_com AND B.nom_long = C.nom_long AND C.res_com = D.res_com AND A.res_com <> C.res_com AND A.nom_long <> B.nom_long AND B.nom_long <> D.nom_long""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()

        if _hops >= 3 : 
            if b == -1 :
                self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B2.geo_point_2d, B2.nom_long, B2.res_com, C2.geo_point_2d, C2.nom_long, C2.res_com, D.geo_point_2d, D.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as A, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as B1, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as B2, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as C1, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as C2, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as D WHERE A.nom_long = $${_fromstation}$$ AND A.res_com = B1.res_com AND B1.nom_long = B2.nom_long AND B2.res_com = C1.res_com AND C1.nom_long = C2.nom_long AND C2.res_com = D.res_com AND D.nom_long = $${_tostation}$$ AND A.res_com <> B2.res_com AND B2.res_com <> C2.res_com AND A.res_com <> C2.res_com AND A.nom_long <> B1.nom_long AND B2.nom_long <> C1.nom_long AND C2.nom_long <> D.nom_long""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()
            else :
                self.cursor.execute(""f" SELECT distinct A.geo_point_2d, A.nom_long, A.res_com, B2.geo_point_2d, B2.nom_long, B2.res_com, C2.geo_point_2d, C2.nom_long, C2.res_com, D.geo_point_2d, D.nom_long FROM (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as A, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as B1, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as B2, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as C1, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as C2, (SELECT distinct CONCAT(nodes_TABLE.lat,', ',nodes_TABLE.lon) as geo_point_2d, nodes_TABLE.nom_long, routeINT_table.res_com FROM nodes_TABLE, routeINT_TABLE, combined_TABLE WHERE routeINT_TABLE.route_type ={b} AND combined_TABLE.route_type = routeINT_TABLE.route_type AND nodes_TABLE.from_stop_I=combined_TABLE.from_stop_I and routeINT_TABLE.route_I=combined_TABLE.route_I ) as D WHERE A.nom_long = $${_fromstation}$$ AND A.res_com = B1.res_com AND B1.nom_long = B2.nom_long AND B2.res_com = C1.res_com AND C1.nom_long = C2.nom_long AND C2.res_com = D.res_com AND D.nom_long = $${_tostation}$$ AND A.res_com <> B2.res_com AND B2.res_com <> C2.res_com AND A.res_com <> C2.res_com AND A.nom_long <> B1.nom_long AND B2.nom_long <> C1.nom_long AND C2.nom_long <> D.nom_long""")
                self.conn.commit()
                self.rows += self.cursor.fetchall()

        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        numrows = len(self.rows)
        numcols = len(self.rows[-1]) - math.floor(len(self.rows[-1]) / 3.0) - 1
        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)
        

        i = 0
        for row in self.rows : 
            j = 0           
            k = 0
            for col in row :
                if( j % 3 == 0) :
                    k = k + 1 
                else: 
                    test = self.tableWidget.setItem(i, j-k, QTableWidgetItem(str(col)))
                    
                j = j + 1
            i = i + 1

        header = self.tableWidget.horizontalHeader()
        
        
        j = 0
        while j < numcols : 
            header.setSectionResizeMode(j, (QHeaderView.ResizeToContents)) 
            j = j+1
        
        self.update()	

    def button_Show(self):
        self.draw = 2 
        while(self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
            self.tableWidget.removeColumn(0)

        _line = str(self.line_box.currentText())
        self.rows =[] 

        self.cursor.execute(""f" SELECT distinct nom_long, lat, lon, combined_TABLE.from_stop_i FROM routeINT_TABLE, combined_TABLE, nodes_TABLE  WHERE routeINT_TABLE.res_com = '{_line}' and routeINT_TABLE.route_i = combined_TABLE.route_i and combined_TABLE.from_stop_i = nodes_TABLE.from_stop_i;""")
        self.conn.commit()
        self.rows += self.cursor.fetchall()
        self.tableWidget.clearContents()
        
        
        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            return

        numrows = len(self.rows)
        numcols = 1
        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)
        

        i = 0
        for row in range(0, numrows) :
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.rows[i][0]  )))
            i = i + 1

        header = self.tableWidget.horizontalHeader()
        
        
        j = 0
        while j < numcols : 
            header.setSectionResizeMode(j, (QHeaderView.ResizeToContents)) 
            j = j+1
        
        self.update()	
    
    def button_Clear(self):
       #Remove table within its data 
        while(self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
            self.tableWidget.removeColumn(0)
       #Clear the map  
        self.webView.clearMap(self.maptype_box.currentIndex())
        self.startingpoint = True
        self.update()

    def button_Save(self):
        now = datetime.now()
        with open('history.txt', 'a') as f:
            numrows = len(self.rows)
            numcols = (len(self.rows[-1]) - math.floor(len(self.rows[-1]) / 3.0) - 1)
            f.write(str(now.strftime(" %d/%m/%Y %H:%M:%S")))
            f.write('\n')
            for i in range(0, numrows) :
                for n in range(5) :
                    f.write('\t')
                f.write(str(self.rows[i]))
                f.write('\n')
            f.write('\n')
   
    def mouseClick(self, lat, lng):
        self.webView.addPointMarker(lat, lng)

        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(""f" WITH mytable (distance, name) AS (SELECT ( ABS(nodes_TABLE.lat-{lat}) + ABS(nodes_TABLE.lon-{lng}) ), nodes_TABLE.nom_long FROM nodes_TABLE) SELECT A.name FROM mytable as A WHERE A.distance <=  (SELECT min(B.distance) FROM mytable as B)  """)
        self.conn.commit()
        rows = self.cursor.fetchall()
        
        if self.startingpoint :
            self.from_box.setCurrentIndex(self.from_box.findText(rows[0][0], Qt.MatchFixedString))      
        else :
            self.to_box.setCurrentIndex(self.to_box.findText(rows[0][0], Qt.MatchFixedString))
        self.startingpoint = not self.startingpoint

        self.update()
        

    def closeEvent(self, event):
       
        close = QMessageBox()
        close.setText("<h3>Do you want to leave ?</h3>")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        close = close.exec()
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']


        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.5,
                "weight": 6,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 6
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPointMarker(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)

        


    def setMap (self, i):
        self.mymap = folium.Map(location=[48.8619, 2.3519], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)

        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)


       
			
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
         

            

