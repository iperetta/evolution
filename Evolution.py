#!/usr/local/bin/python3.6

# chmod +x Evolution.py

import os, sys
from PyQt5.QtWidgets import (qApp, QAction, QApplication, QDesktopWidget, QFileDialog,
    QGridLayout, QGroupBox, QHBoxLayout, QMainWindow, QMessageBox, QLabel, QLayout, 
    QPushButton, QSpacerItem, QSizePolicy, QSpinBox, QVBoxLayout, QToolButton, QToolBar,
    QWidget, QFrame)
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QImage, QColor, QFont
from PyQt5.QtCore import QByteArray, QRectF, QSize, Qt, QXmlStreamReader, QObject
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from time import sleep

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class Principal(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.path_img = self.path + '/img'

        self.setWindowIcon(QIcon(self.path_img + '/treelife_pq.png'))
        self.setWindowTitle('Evolução')
        self.appCenter()

        self.SleepTime = 0.5
        self.StartNPop = 50
        self.StopSignal = False
        self.Presas = True
        self.PresasColors = [0x000000] * 9
        self.Predador = False
        self.Population = np.zeros((self.StartNPop, 3))
        self.fitPopulation = np.zeros((self.StartNPop, ))
        self.BkgFileName = self.path_img + '/void.jpg'
        self.BkgImage = QImage(self.BkgFileName)
        self.MeanColorBkg = 0x000000

        self.background = QLabel()
        self.builtScenery()
        self.appMenuBar()
        self.appToolBar()
        self.statusbar = self.statusBar()
        self.centerAreaGrid = QHBoxLayout()
        self.centerArea = QWidget()
        self.centerArea.setLayout(self.centerAreaGrid)
        self.setCentralWidget(self.centerArea)
        subScene = QWidget()
        subSceneLayout = QVBoxLayout(subScene)
        subScene.setStyleSheet("background-color:black;")
        subSceneLayout.addWidget(self.background)
        self.centerAreaGrid.addWidget(subScene)
        self.centerAreaGrid.addStretch()
        self.centerAreaGrid.addWidget(self.myControlBox())

        self.statusbar.showMessage('Aguardando instruções')
        self.show()


    def builtScenery(self):
        # colors = [0xFF0000, 0x00FF00, 0x0000FF, 0x990000, 0x009900, 0x000099, 0x330000, 0x003300, 0x000033]
        # colors = [0x0e0907, 0x9f0d12, 0x1a5dd6, 0x418912, 0x9a7c67,0,0,0,0]
        colors = self.PresasColors
        scene = QPixmap.fromImage(self.BkgImage)        
        ps = 0.8
        pixmap = QPixmap(round(ps*scene.width()), round(ps*scene.height()))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.drawPixmap(0,0,pixmap.width(),pixmap.height(),scene)
        if self.Presas:
            svgPresas = self.renderGecko(colors)
            svgPresas.renderer().render(painter, QRectF(pixmap.rect()))
        if self.Predador:
            svgPredador = self.renderEagle()
            pp = 0.50
            predarect = [0, 0, round(pp*pixmap.width()), round(pp*pixmap.height())]
            svgPredador.renderer().render(painter, QRectF(*predarect))
        painter.end()
        self.background.setPixmap(pixmap)
        self.background.resize(800,600)
        self.background.update()
        self.update()


    def myControlBox(self):

        def valuechange():
            self.subGeraBox.setEnabled(False)

        myActions = self.appDictAction()
        stb = 25

        ctrBox = QWidget()
        ctrBoxLayout = QVBoxLayout(ctrBox)
        # ctrBox.setLayout(ctrBoxLayout)
        
        btnLoad = QPushButton(QIcon('landscape.png'), ' Carrega cenário')
        btnLoad.setStatusTip('Carregar imagem com cenário')
        btnLoad.setStyleSheet('QPushButton{font-size: 14px;}')
        btnLoad.clicked.connect(self.actLoadtrig)
        btnLoad.resize(btnLoad.sizeHint())
        btnLoad.setIconSize(QSize(btnLoad.width()-4, btnLoad.height()-6))
        ctrBoxLayout.addWidget(btnLoad)
        ctrBoxLayout.addStretch()


        subPopBox = QWidget()
        subPopBoxLayout = QGridLayout(subPopBox)

        subPopBoxLayout.addWidget(QHLine(), 0, 0, 1, 6)
        ptitle = QLabel('<b>Sobre População</b>')
        ptitle.setStyleSheet('QLabel{font-size: 14px; color: #003333;}')
        subPopBoxLayout.addWidget(ptitle, 1, 0, 1, 6, alignment=Qt.AlignCenter|Qt.AlignVCenter)

        self.NPopulation = QSpinBox()
        self.NPopulation.setMinimum(50)
        self.NPopulation.setMaximum(1000)
        self.NPopulation.setSingleStep(50)
        self.NPopulation.setValue(self.StartNPop)
        self.NPopulation.valueChanged.connect(valuechange)
        subPopBoxLayout.addWidget(QLabel("Número de indivíduos na população (50 a 1000):"), 2, 0, 1, 4)
        subPopBoxLayout.addWidget(self.NPopulation, 2, 4, 1, 2)

        self.PbXover = QSpinBox()
        self.PbXover.setMinimum(0)
        self.PbXover.setMaximum(100)
        self.PbXover.setSingleStep(5)
        self.PbXover.setValue(60)
        subPopBoxLayout.addWidget(QLabel("Recombina [%]:"), 3, 0, 1, 1)
        subPopBoxLayout.addWidget(self.PbXover, 3, 1, 1, 1)
        self.PbMuta = QSpinBox()
        self.PbMuta.setMinimum(0)
        self.PbMuta.setMaximum(100)
        self.PbMuta.setSingleStep(5)
        self.PbMuta.setValue(5)
        subPopBoxLayout.addWidget(QLabel("Mutação [%]:"), 3, 2, 1, 1)
        subPopBoxLayout.addWidget(self.PbMuta, 3, 3, 1, 1)
        self.PbDeath = QSpinBox()
        self.PbDeath.setMinimum(0)
        self.PbDeath.setMaximum(100)
        self.PbDeath.setSingleStep(5)
        self.PbDeath.setValue(15)
        subPopBoxLayout.addWidget(QLabel("Morte Natural [%]:"), 3, 4, 1, 1)
        subPopBoxLayout.addWidget(self.PbDeath, 3, 5, 1, 1)

        ctrBoxLayout.addWidget(subPopBox)
        ctrBoxLayout.addStretch()

        btnInit = QPushButton(QIcon(self.path_img + '/geckoIcon.png'), ' Inicializa População')
        btnInit.setStatusTip('Inicializa a população com indivíduos gerados aleatoriamente')
        btnInit.setStyleSheet('QPushButton{font-size: 14px;}')
        btnInit.clicked.connect(self.gaInitPop)
        btnInit.resize(btnInit.sizeHint())
        btnInit.setIconSize(QSize(btnInit.width()-4, btnInit.height()-6))

        ctrBoxLayout.addWidget(btnInit)
        ctrBoxLayout.addStretch()

        self.subGeraBox = QWidget()
        self.subGeraBox.setEnabled(False)
        self.subGeraBoxLayout = QGridLayout(self.subGeraBox)

        self.subGeraBoxLayout.addWidget(QHLine(), 0, 0, 1, 6)
        gtitle = QLabel('<b>Sobre Gerações</b>')
        gtitle.setStyleSheet('QLabel{font-size: 14px; color: #003333;}')
        self.subGeraBoxLayout.addWidget(gtitle, 1, 0, 1, 6, alignment=Qt.AlignCenter|Qt.AlignVCenter)

        sub00box = QWidget()
        sub00boxlayout = QGridLayout(sub00box)
        btnPreda = QToolButton()
        btnPreda.setDefaultAction(myActions['actPredador'])
        btnPreda.setIconSize(QSize(stb, stb))
        sub00boxlayout.addWidget(btnPreda, 0, 0, 1, 1, alignment=Qt.AlignRight|Qt.AlignVCenter)
        sub00boxlayout.addWidget(QLabel("◀ Ativa/Desativa Predador"), 0, 1, 1, 1)
        self.subGeraBoxLayout.addWidget(sub00box, 2, 0, 1, 3, alignment=Qt.AlignCenter|Qt.AlignVCenter)
        
        sub01box = QWidget()
        sub01boxlayout = QGridLayout(sub01box)
        geratual = QLabel("<b>Geração Atual:</b>   ")
        geratual.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.lblGeneration = QLabel('0')
        self.lblGeneration.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.lblGeneration.setStyleSheet('QLabel{font: bold 14px; color: #0000ff;}')
        sub01boxlayout.addWidget(geratual, 0, 0, 1, 1)
        sub01boxlayout.addWidget(self.lblGeneration, 0, 2, 1, 1, alignment=Qt.AlignRight|Qt.AlignVCenter)
        self.subGeraBoxLayout.addWidget(sub01box, 2, 3, 1, 3, alignment=Qt.AlignCenter|Qt.AlignVCenter)
        
        sub10box = QWidget()
        sub10boxlayout = QGridLayout(sub10box)
        self.MoreGenerations = QSpinBox()
        self.MoreGenerations.setMinimum(1)
        self.MoreGenerations.setMaximum(100)
        self.MoreGenerations.setValue(30)
        self.MoreGenerations.setSingleStep(5)
        self.MoreGenerations.setStyleSheet('QSpinBox{font-size: 14px;}')
        plussign = QLabel("<b>+</b>")
        plussign.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        plussign.setStyleSheet('QLabel{font-size: 14px;}')
        btnRun = QToolButton()
        btnRun.setDefaultAction(myActions['actRun'])
        btnRun.setIconSize(QSize(stb, stb))
        btnRunFast = QToolButton()
        btnRunFast.setDefaultAction(myActions['actRunFast'])
        btnRunFast.setIconSize(QSize(stb, stb))
        sub10boxlayout.addWidget(plussign, 0, 0, 1, 1)
        sub10boxlayout.addWidget(self.MoreGenerations, 0, 1, 1, 1)
        sub10boxlayout.addWidget(btnRun, 0, 2, 1, 1)
        sub10boxlayout.addWidget(btnRunFast, 0, 3, 1, 1)
        self.subGeraBoxLayout.addWidget(sub10box, 3, 0, 1, 3, alignment=Qt.AlignCenter|Qt.AlignVCenter)

        
        sub11box = QWidget()
        sub11boxlayout = QGridLayout(sub11box)
        btnStop = QToolButton()
        btnStop.setDefaultAction(myActions['actStop'])
        btnStop.setIconSize(QSize(stb, stb))
        # btnStop.setStyleSheet('border: none;')
        sub11boxlayout.addWidget(btnStop, 0, 0, 1, 1)
        self.subGeraBoxLayout.addWidget(sub11box, 3, 3, 1, 3, alignment=Qt.AlignCenter|Qt.AlignVCenter)

        ctrBoxLayout.addWidget(self.subGeraBox)
        ctrBoxLayout.addStretch()

        subFig = QWidget()
        subFigLayout = QVBoxLayout(subFig)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.resize(self.canvas.sizeHint())
        self.figtoolbar = NavigationToolbar(self.canvas, self)
        self.axes = self.figure.add_subplot(111)
        subFigLayout.addWidget(self.canvas)
        subFigLayout.addWidget(self.figtoolbar)

        ctrBoxLayout.addWidget(subFig)

        return ctrBox


    def appCenter(self):
        
        desktop = QDesktopWidget().availableGeometry()
        dskcenter = desktop.center()
        self.setGeometry(0, 0, round(0.75*desktop.width()), round(0.75*desktop.height()))
        qr = self.frameGeometry()
        qr.moveCenter(dskcenter)
        self.move(qr.topLeft())
    
    def appQuit(self):
        mbox = QMessageBox()
        mbox.setIcon(QMessageBox.Question)
        mbox.setWindowTitle('Atenção!')
        mbox.setText('Você está prestes a encerrar, tem certeza?')
        mbox.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        mbox.setDefaultButton(QMessageBox.No)
        btnY = mbox.button(QMessageBox.Yes)
        btnY.setText('&Sim')
        btnN = mbox.button(QMessageBox.No)
        btnN.setText('&Não')
        mbox.exec_()
        if mbox.clickedButton() == btnY:
            qApp.quit()


    def closeEvent(self, event):
        event.ignore()
        self.appQuit()

    def togglePredador(self, state):
        if not self.Predador:
            self.Predador = True
            self.statusbar.showMessage('Predador presente')
        else:
            self.Predador = False
            self.statusbar.showMessage('Predador ausente')
        self.builtScenery()


    def appStopSignal(self):
        self.StopSignal = True


    def appDictAction(self):
        actLoad = QAction(QIcon(self.path_img + '/landscape.png'),'&Carrega cenário', self)
        actLoad.setShortcut('CRTL+O')
        actLoad.setStatusTip('Carregar imagem com cenário')
        actLoad.triggered.connect(self.actLoadtrig)
        actRun = QAction(QIcon(self.path_img + '/run.png'),'&Rodar', self)
        actRun.setShortcut('F5')
        actRun.setStatusTip('Inicia evolução em gerações')
        actRun.triggered.connect(self.gaGoEvolution)
        actRunFast = QAction(QIcon(self.path_img + '/fast.png'),'Ro&dar Rápido', self)
        actRunFast.setShortcut('F6')
        actRunFast.setStatusTip('Inicia evolução em gerações (modo rápido)')
        actRunFast.triggered.connect(self.gaGoEvolutionX)
        actStop = QAction(QIcon(self.path_img + '/stop.png'),'&Parar', self)
        actStop.setShortcut('ESC')
        actStop.setStatusTip('Parar a evolução')
        actStop.triggered.connect(self.appStopSignal)
        actInfo = QAction(QIcon(self.path_img + '/info.png'),'&Informações', self)
        actInfo.setStatusTip('Informações sobre o programa')
        actInfo.triggered.connect(self.appInfo)
        actQuit = QAction(QIcon(self.path_img + '/exit.png'),'&Encerrar', self)
        actQuit.setShortcut('CRTL+Q')
        actQuit.setStatusTip('Encerrar o programa')
        actQuit.triggered.connect(self.appQuit)
        actPredador = QAction(QIcon(self.path_img + '/predador.png'),'P&redador', self, checkable=True)
        actPredador.setChecked(False)
        actPredador.triggered.connect(self.togglePredador)
        actInitPop = QAction(QIcon(self.path_img + '/geckoIcon.png'), 'Inicializa P&opulação', self)
        actInitPop.setShortcut('CRTL+I')
        actInitPop.setStatusTip('Inicializa a população com indivíduos gerados aleatoriamente')
        actInitPop.triggered.connect(self.gaInitPop)
        return {
            'actLoad' : actLoad,
            'actInitPop' : actInitPop,
            'actPredador' : actPredador,
            'actRun' : actRun,
            'actRunFast' : actRunFast,
            'actStop' : actStop,
            'actQuit' : actQuit,
            'actInfo' : actInfo,
        }

    def appMenuBar(self):
        self.menubar = self.menuBar()
        actdict = self.appDictAction()
        filemenu = self.menubar.addMenu('A&rquivo')
        filemenu.addAction(actdict['actLoad'])
        filemenu.addAction(actdict['actQuit'])
        evomenu = self.menubar.addMenu('&Evolução')
        evomenu.addAction(actdict['actPredador'])
        evomenu.addAction(actdict['actInitPop'])
        helpmenu = self.menubar.addMenu('&Ajuda')
        helpmenu.addAction(actdict['actInfo'])
    
    def appInfo(self):
        mbox = QMessageBox()
        myIcon = QPixmap(self.path_img + '/treelife_pq.png')
        mbox.setIconPixmap(myIcon)
        mbox.setWindowIcon(QIcon(self.path_img + '/treelife_pq.png'))
        mbox.setWindowTitle('Informações')
        mbox.setText(
            '<p align=\'center\'>Este programa foi desenvolvido em 2018 por<br>' + 
            '<i>Igor S. Peretta</i> (<a href=\"mailto:iperetta@ufu.br\">iperetta@ufu.br</a>)<br>' +
            'a partir do programa original de <i>Felipe Campelo Franca Pinto</i><br>' + 
            'apresentado em 2010 por <i>Frederico Gadelha Guimarães</i>.' +
            '<br><br>' +
            '<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Licença Creative Commons" style="border-width:0" src="' + self.path_img + '/88x31.png" /></a><br />Este obra está licenciado com uma Licença <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Atribuição-NãoComercial 4.0 Internacional</a>.' +
            '</p>'
        )
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()

    def appToolBar(self):
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        actdict = self.appDictAction()
        for key, action in actdict.items():
            if key in ['actInitPop','actQuit']:
                self.toolbar.addSeparator()
            if key not in ['actRun','actRunFast','actStop']:
                self.toolbar.addAction(action)
            
    def actLoadtrig(self):
        fdial = QFileDialog()
        fdial.setWindowIcon(QIcon(self.path_img + '/treelife_pq.png'))
        imgfile = fdial.getOpenFileName(self,'Carregar cenário', 
            self.path + '/cenarios',"JPG Files (*.jpg);; PNG Files (*.png);; All Files (*)",)
        if imgfile[0]:
            self.BkgFileName = imgfile[0]
        else:
            self.BkgFileName = self.path_img + '/void.jpg'
        scene = QImage(self.BkgFileName)
        self.BkgImage = scene.scaled(800, 600)
        self.MeanColorBkg = self.meanColorOfBkgImage()['color']
        self.builtScenery()


    def renderGecko(self, colors=[]):

        """
        Return grid of geckos as SvgWidget to be included in painter as:
        painter = QPainter(QPixmap(width,height))
        renderGecko(colors).renderer().render(painter, QRectF(pixmap.rect()))
        """
        def getGeckoOfColors(colors):
            return f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>
                        <svg
                            id=\"gecko\"
                            width=\"352.13858\"
                            height=\"277.13861\"
                            viewBox=\"0 0 352.13857 277.13861\">
                            <path
                                style=\"fill:#{colors[0]:06x}\"
                                d=\"m 8.78787,83.2198 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26911 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.163 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.27211 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68818 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40702 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.5471 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47537 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09115 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40431 0.74093,1.10818 1.62457,2.81949 1.96364,3.8029 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16586 -1.02615,-1.37204 -1.68642,-2.6804 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.832 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.45559 0.84305,-0.70257 1.42276,0.31852 1.22976,2.16606 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.76111 4.84944,-5.25967 0.40931,-1.41382 1.28298,-3.3678 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.4121 1.93027,-3.19492 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07933 -6.96278,17.28047 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26905 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.0376 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37737 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91015 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 C 61.70211,47.7106 60.98411,47.3886 56.70774,46.85017 47.12399,45.6435 38.14029,46.62455 30.84395,49.6746 c -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81741 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g0\" />
                            <path
                                style=\"fill:#{colors[1]:06x}\"
                                d=\"m 126.1674,83.2198 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26911 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.163 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.27211 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68818 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40702 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.5471 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47537 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09115 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40431 0.74093,1.10818 1.62457,2.81949 1.96364,3.8029 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16586 -1.02615,-1.37204 -1.68642,-2.6804 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.832 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.45559 0.84305,-0.70257 1.42276,0.31852 1.22976,2.16606 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.76111 4.84944,-5.25967 0.40931,-1.41382 1.28298,-3.3678 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.4121 1.93027,-3.19492 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07933 -6.96278,17.28047 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26905 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.0376 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37737 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91015 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88369 -5.40108,-2.42212 -9.58375,-1.20667 -18.56745,-0.22562 -25.86379,2.82443 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81741 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g1\" />
                            <path
                                style=\"fill:#{colors[2]:06x}\"
                                d=\"m 243.54693,83.2198 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26911 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.163 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.27211 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68818 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40702 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.5471 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47537 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09115 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40431 0.74093,1.10818 1.62457,2.81949 1.96364,3.8029 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16586 -1.02615,-1.37204 -1.68642,-2.6804 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.832 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.45559 0.84305,-0.70257 1.42276,0.31852 1.22976,2.16606 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.76111 4.84944,-5.25967 0.40931,-1.41382 1.28298,-3.3678 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.4121 1.93027,-3.19492 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07933 -6.96278,17.28047 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26905 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.0376 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37737 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91015 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88369 -5.40108,-2.42212 -9.58375,-1.20667 -18.56745,-0.22562 -25.86379,2.82443 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81741 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g2\" />
                            <path
                                style=\"fill:#{colors[3]:06x}\"
                                d=\"m 8.78787,175.59935 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20899 13.86397,-10.04598 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36497 -4.93171,-2.08767 -8.64658,-1.68819 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00434 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39468 0.48842,-0.40703 1.15634,-0.30599 2.73677,0.41407 3.43288,1.56404 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09114 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81948 1.96364,3.80289 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.7611 4.84944,-5.25967 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97438 1.52714,-2.41211 1.93027,-3.19493 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07934 -6.96278,17.28048 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32323 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28144 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86328 -0.69948,-2.86328 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81017 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91914 -7.49177,0.74421 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88369 -5.40108,-2.42212 -9.58375,-1.20667 -18.56745,-0.22561 -25.86379,2.82443 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g3\" />
                            <path
                                style=\"fill:#{colors[4]:06x}\"
                                d=\"m 126.1674,175.59935 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20899 13.86397,-10.04598 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36497 -4.93171,-2.08767 -8.64658,-1.68819 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00434 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39468 0.48842,-0.40703 1.15634,-0.30599 2.73677,0.41407 3.43288,1.56404 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09114 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81948 1.96364,3.80289 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.7611 4.84944,-5.25967 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97438 1.52714,-2.41211 1.93027,-3.19493 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07934 -6.96278,17.28048 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32323 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28144 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86328 -0.69948,-2.86328 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81017 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91914 -7.49177,0.74421 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88369 -5.40108,-2.42212 -9.58375,-1.20667 -18.56745,-0.22561 -25.86379,2.82443 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g4\" />
                            <path
                                style=\"fill:#{colors[5]:06x}\"
                                d=\"m 243.54693,175.59935 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20899 13.86397,-10.04598 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28081 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29664 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36497 -4.93171,-2.08767 -8.64658,-1.68819 -2.60412,0.28003 -3.14807,0.2218 -2.97087,-0.31805 0.13369,-0.40729 1.08308,-0.7173 2.47448,-0.808 1.80731,-0.11782 2.22704,-0.30643 2.10443,-0.94567 -0.2165,-1.12887 -2.18599,-2.00434 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39468 0.48842,-0.40703 1.15634,-0.30599 2.73677,0.41407 3.43288,1.56404 4.75502,1.04139 3.05958,-1.20945 -0.38507,-0.51123 -0.70696,-1.41434 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43097 0.63853,-0.9577 0.40961,-1.57284 1.1288,-1.09114 1.58235,1.05983 0.45783,2.17125 0.51277,2.2027 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81948 1.96364,3.80289 0.99558,2.88759 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01282 7.28463,-2.5481 1.3114,-0.53527 2.7599,-1.08612 3.2189,-1.22411 0.91403,-0.27477 1.11853,-1.34294 0.34858,-1.82077 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45775 -2.00615,-1.69553 -1.46197,-2.24196 0.16244,-0.1631 0.83273,-0.0507 1.48953,0.24981 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37319 -0.77505,-1.50498 -0.63473,-2.80608 0.30262,-2.80608 0.29507,0 0.6499,0.4355 0.78853,0.96779 0.1893,0.72687 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95124 1.15229,-0.83045 1.02681,1.17535 -0.12109,1.93551 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34028 3.83656,-1.7611 4.84944,-5.25967 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97438 1.52714,-2.41211 1.93027,-3.19493 0.40317,-0.78284 1.07644,-1.42333 1.49617,-1.42333 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.9186 4.47021,-1.3779 0.4184,0.34866 0.76071,1.20873 0.76071,1.91125 0,3.90965 -3.6947,13.07934 -6.96278,17.28048 -2.96692,3.81403 -3.52845,5.48814 -3.52845,10.51925 0,3.37758 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74863 0.40649,-1.06364 1.34566,-0.31926 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12704 1.14969,-0.75644 1.21279,-0.74617 1.46946,0.23942 0.15917,0.6112 0.64745,1.02979 1.20127,1.02979 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60051 -0.62227,0.83798 -1.77939,0.83798 -0.88806,0 -1.70591,0.26935 -1.81746,0.59856 -0.11156,0.3292 0.0298,0.59855 0.31378,0.59855 0.28414,0 0.51662,0.32323 0.51662,0.71827 0,0.84639 -0.65099,0.91468 -1.96868,0.20655 -0.52373,-0.28144 -1.5912,-0.52997 -2.37217,-0.55226 -2.15181,-0.0614 -3.64965,-2.15427 -4.04347,-5.64967 -0.17744,-1.57481 -0.49221,-2.86328 -0.69948,-2.86328 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81017 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91914 -7.49177,0.74421 l -5.61165,-0.20091 -0.13822,3.3774 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.06811 2.63231,-0.92979 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88369 -5.40108,-2.42212 -9.58375,-1.20667 -18.56745,-0.22561 -25.86379,2.82443 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g5\" />
                            <path
                                style=\"fill:#{colors[6]:06x}\"
                                d=\"m 8.78787,267.97888 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28082 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29663 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68819 -2.60412,0.28004 -3.14807,0.22181 -2.97087,-0.31805 0.13369,-0.40728 1.08308,-0.71729 2.47448,-0.808 1.80731,-0.11781 2.22704,-0.30643 2.10443,-0.94566 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40703 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20946 -0.38507,-0.51122 -0.70696,-1.41433 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43096 0.63853,-0.95769 0.40961,-1.57285 1.1288,-1.09115 1.58235,1.05982 0.45783,2.17126 0.51277,2.20271 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81949 1.96364,3.8029 0.99558,2.88758 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01283 7.28463,-2.5481 1.3114,-0.53528 2.7599,-1.08613 3.2189,-1.22411 0.91403,-0.27478 1.11853,-1.34295 0.34858,-1.82078 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45774 -2.00615,-1.69552 -1.46197,-2.24195 0.16244,-0.16311 0.83273,-0.0507 1.48953,0.2498 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37318 -0.77505,-1.50498 -0.63473,-2.80609 0.30262,-2.80609 0.29507,0 0.6499,0.43551 0.78853,0.96779 0.1893,0.72688 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95123 1.15229,-0.83045 1.02681,1.17536 -0.12109,1.9355 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34029 3.83656,-1.76111 4.84944,-5.25968 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.41209 1.93027,-3.19492 0.40317,-0.78283 1.07644,-1.42332 1.49617,-1.42332 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.91861 4.47021,-1.37791 0.4184,0.34867 0.76071,1.20873 0.76071,1.91126 0,3.90964 -3.6947,13.07932 -6.96278,17.28046 -2.96692,3.81404 -3.52845,5.48814 -3.52845,10.51925 0,3.37759 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74862 0.40649,-1.06364 1.34566,-0.31927 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12703 1.14969,-0.75643 1.21279,-0.74616 1.46946,0.23943 0.15917,0.6112 0.64745,1.02978 1.20127,1.02978 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60052 -0.62227,0.83799 -1.77939,0.83799 -0.88806,0 -1.70591,0.26935 -1.81746,0.59855 -0.11156,0.32921 0.0298,0.59856 0.31378,0.59856 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84638 -0.65099,0.91467 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55227 -2.15181,-0.0615 -3.64965,-2.15426 -4.04347,-5.64966 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.37739 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.0681 2.63231,-0.92978 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88368 -5.40108,-2.42211 -9.58375,-1.20667 -18.56745,-0.22562 -25.86379,2.82442 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g6\" />
                            <path
                                style=\"fill:#{colors[7]:06x}\"
                                d=\"m 126.1674,267.97888 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28082 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29663 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68819 -2.60412,0.28004 -3.14807,0.22181 -2.97087,-0.31805 0.13369,-0.40728 1.08308,-0.71729 2.47448,-0.808 1.80731,-0.11781 2.22704,-0.30643 2.10443,-0.94566 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40703 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20946 -0.38507,-0.51122 -0.70696,-1.41433 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43096 0.63853,-0.95769 0.40961,-1.57285 1.1288,-1.09115 1.58235,1.05982 0.45783,2.17126 0.51277,2.20271 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81949 1.96364,3.8029 0.99558,2.88758 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01283 7.28463,-2.5481 1.3114,-0.53528 2.7599,-1.08613 3.2189,-1.22411 0.91403,-0.27478 1.11853,-1.34295 0.34858,-1.82078 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45774 -2.00615,-1.69552 -1.46197,-2.24195 0.16244,-0.16311 0.83273,-0.0507 1.48953,0.2498 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37318 -0.77505,-1.50498 -0.63473,-2.80609 0.30262,-2.80609 0.29507,0 0.6499,0.43551 0.78853,0.96779 0.1893,0.72688 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95123 1.15229,-0.83045 1.02681,1.17536 -0.12109,1.9355 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34029 3.83656,-1.76111 4.84944,-5.25968 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.41209 1.93027,-3.19492 0.40317,-0.78283 1.07644,-1.42332 1.49617,-1.42332 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.91861 4.47021,-1.37791 0.4184,0.34867 0.76071,1.20873 0.76071,1.91126 0,3.90964 -3.6947,13.07932 -6.96278,17.28046 -2.96692,3.81404 -3.52845,5.48814 -3.52845,10.51925 0,3.37759 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74862 0.40649,-1.06364 1.34566,-0.31927 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12703 1.14969,-0.75643 1.21279,-0.74616 1.46946,0.23943 0.15917,0.6112 0.64745,1.02978 1.20127,1.02978 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60052 -0.62227,0.83799 -1.77939,0.83799 -0.88806,0 -1.70591,0.26935 -1.81746,0.59855 -0.11156,0.32921 0.0298,0.59856 0.31378,0.59856 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84638 -0.65099,0.91467 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55227 -2.15181,-0.0615 -3.64965,-2.15426 -4.04347,-5.64966 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.37739 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.0681 2.63231,-0.92978 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88368 -5.40108,-2.42211 -9.58375,-1.20667 -18.56745,-0.22562 -25.86379,2.82442 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g7\" />
                            <path
                                style=\"fill:#{colors[8]:06x}\"
                                d=\"m 243.54693,267.97888 c -0.52916,-0.85974 1.19718,-12.07142 2.42812,-15.76936 1.50297,-4.51516 4.7118,-9.75898 8.38372,-13.7005 3.04549,-3.26912 9.86277,-8.20898 13.86397,-10.04597 3.47319,-1.59458 12.7539,-3.92508 17.04743,-4.28082 1.9671,-0.16299 4.72868,-0.41519 6.13684,-0.56045 l 2.56028,-0.2641 -0.22559,-2.35751 c -0.12408,-1.29663 -0.59652,-2.76908 -1.04987,-3.2721 -1.23019,-1.36496 -4.93171,-2.08766 -8.64658,-1.68819 -2.60412,0.28004 -3.14807,0.22181 -2.97087,-0.31805 0.13369,-0.40728 1.08308,-0.71729 2.47448,-0.808 1.80731,-0.11781 2.22704,-0.30643 2.10443,-0.94566 -0.2165,-1.12887 -2.18599,-2.00435 -4.52763,-2.01261 -2.17096,-0.008 -2.89409,-0.54552 -1.87512,-1.39469 0.48842,-0.40703 1.15634,-0.30598 2.73677,0.41408 3.43288,1.56403 4.75502,1.04139 3.05958,-1.20946 -0.38507,-0.51122 -0.70696,-1.41433 -0.71531,-2.00691 -0.0218,-1.54709 1.33584,-1.35465 1.68913,0.23943 0.54862,2.47538 0.74457,2.99279 1.13347,2.99279 0.21402,0 0.50135,-0.43096 0.63853,-0.95769 0.40961,-1.57285 1.1288,-1.09115 1.58235,1.05982 0.45783,2.17126 0.51277,2.20271 5.41483,3.09977 1.77792,0.32536 2.34988,0.72105 3.47532,2.40432 0.74093,1.10817 1.62457,2.81949 1.96364,3.8029 0.99558,2.88758 1.55578,2.98296 7.08445,1.20613 2.69514,-0.86619 5.97322,-2.01283 7.28463,-2.5481 1.3114,-0.53528 2.7599,-1.08613 3.2189,-1.22411 0.91403,-0.27478 1.11853,-1.34295 0.34858,-1.82078 -0.26726,-0.16585 -1.02615,-1.37204 -1.68642,-2.68039 -0.72518,-1.437 -1.67045,-2.55825 -2.38752,-2.83201 -1.199,-0.45774 -2.00615,-1.69552 -1.46197,-2.24195 0.16244,-0.16311 0.83273,-0.0507 1.48953,0.2498 1.45771,0.66692 1.60498,-0.11957 0.44439,-2.37318 -0.77505,-1.50498 -0.63473,-2.80609 0.30262,-2.80609 0.29507,0 0.6499,0.43551 0.78853,0.96779 0.1893,0.72688 0.40503,0.84028 0.86665,0.4556 0.84305,-0.70258 1.42276,0.31851 1.22976,2.16605 -0.14935,1.42975 -0.14612,1.43174 0.8521,0.52463 1.04677,-0.95123 1.15229,-0.83045 1.02681,1.17536 -0.12109,1.9355 1.46126,3.03384 3.89798,2.70566 2.52657,-0.34029 3.83656,-1.76111 4.84944,-5.25968 0.40931,-1.41381 1.28298,-3.36779 1.94149,-4.34217 0.65851,-0.97437 1.52714,-2.41209 1.93027,-3.19492 0.40317,-0.78283 1.07644,-1.42332 1.49617,-1.42332 0.41976,0 2.43244,-0.90534 4.47266,-2.01186 3.16381,-1.71591 3.8214,-1.91861 4.47021,-1.37791 0.4184,0.34867 0.76071,1.20873 0.76071,1.91126 0,3.90964 -3.6947,13.07932 -6.96278,17.28046 -2.96692,3.81404 -3.52845,5.48814 -3.52845,10.51925 0,3.37759 0.14551,4.32501 0.66427,4.32501 0.36536,0 0.79306,-0.33688 0.95039,-0.74862 0.40649,-1.06364 1.34566,-0.31927 0.99541,0.78892 -0.35502,1.12323 -0.0657,1.14796 1.48601,0.12703 1.14969,-0.75643 1.21279,-0.74616 1.46946,0.23943 0.15917,0.6112 0.64745,1.02978 1.20127,1.02978 0.63352,0 0.88019,0.26906 0.76838,0.83798 -0.11804,0.60052 -0.62227,0.83799 -1.77939,0.83799 -0.88806,0 -1.70591,0.26935 -1.81746,0.59855 -0.11156,0.32921 0.0298,0.59856 0.31378,0.59856 0.28414,0 0.51662,0.32322 0.51662,0.71827 0,0.84638 -0.65099,0.91467 -1.96868,0.20655 -0.52373,-0.28145 -1.5912,-0.52997 -2.37217,-0.55227 -2.15181,-0.0615 -3.64965,-2.15426 -4.04347,-5.64966 -0.17744,-1.57481 -0.49221,-2.86329 -0.69948,-2.86329 -0.20723,0 -1.52073,1.03759 -2.91885,2.30577 -2.40558,2.18201 -4.91692,3.81018 -9.19088,5.95867 -1.63709,0.82295 -2.6055,0.91915 -7.49177,0.74422 l -5.61165,-0.20091 -0.13822,3.37739 -0.13821,3.37738 -1.9075,-0.0494 c -1.04912,-0.0272 -2.76587,-0.13493 -3.81499,-0.23942 -1.8321,-0.18247 -1.9075,-0.13486 -1.9075,1.20464 0,2.05275 -1.01266,2.03904 -1.69035,-0.0229 l -0.58844,-1.79035 -0.88732,1.10033 c -0.48802,0.60518 -0.88732,1.48104 -0.88732,1.94635 0,0.95749 -1.11653,2.07674 -1.59372,1.59758 -0.59844,-0.60091 -0.30871,-1.94816 0.69434,-3.22861 0.55446,-0.7078 0.9006,-1.39486 0.76921,-1.5268 -0.47901,-0.48099 -2.17589,-0.36777 -4.11397,0.27451 -1.42375,0.47182 -2.12966,0.51104 -2.50025,0.13893 -0.96755,-0.97156 0.11978,-1.55966 2.88363,-1.55966 2.10553,0 2.95352,-0.21562 3.57948,-0.91016 0.93615,-1.03872 0.78707,-1.18662 -1.93484,-1.9196 -1.08772,-0.29291 -2.10031,-0.85344 -2.25018,-1.24564 -0.40819,-1.0681 2.63231,-0.92978 4.04433,0.18399 0.6255,0.49339 2.24852,1.05019 3.6067,1.23734 2.33082,0.32116 2.45506,0.28513 2.21362,-0.64196 -0.40671,-1.56169 -1.12471,-1.88368 -5.40108,-2.42211 -9.58375,-1.20667 -18.56745,-0.22562 -25.86379,2.82442 -3.03974,1.27068 -4.45367,2.27624 -8.18001,5.81742 -5.24033,4.97996 -6.88149,7.29091 -8.88794,12.51535 -1.71304,4.46044 -3.84751,12.2663 -3.9045,14.27895 -0.0398,1.40472 -0.5324,1.82909 -1.08363,0.9335 z\"
                                id=\"g8\" />
                        </svg>"""
        svgWidget = QSvgWidget()
        svgWidget.renderer().load(bytearray(getGeckoOfColors(colors), encoding='utf-8'))
        return svgWidget


    def renderEagle(self):
        """
        Return eagle as SvgWidget to be included in painter as:
        painter = QPainter(QPixmap(width,height))
        renderGecko(colors).renderer().render(painter, QRectF(pixmap.rect()))
        """
        svgWidget = QSvgWidget()
        svgWidget.renderer().load(self.path_img + '/svg/eagle.svg')
        return svgWidget
        

    def meanColorOfBkgImage(self):
        img = self.BkgImage
        width = img.width()
        height = img.height()
        r = 0
        g = 0
        b = 0
        for x in range(width):
            for y in range(height):
                rgb_px = QColor(img.pixel(x,y)).getRgb()
                r = r + rgb_px[0]
                g = g + rgb_px[1]
                b = b + rgb_px[2]
        r = round(r/(width*height))
        g = round(g/(width*height))
        b = round(b/(width*height))
        c = (r << 16) | (g << 8) | b
        return {'hexcolor' : f'0x{r:02x}{g:02x}{b:02x}', 'R' : r, 'G' : g, 'B' : b, 'color' : c}


    def plot(self, datax, datay1, datay2): 
        # discards the old graph
        self.axes.clear()
        # plot data
        self.axes.plot(datax, datay1, 'b')
        self.axes.plot(datax, datay2, 'r')
        self.axes.legend(['média','melhor'])
        self.axes.set_title('Gerações')
        self.axes.set_ylabel('Aptidão')
        # refresh canvas
        self.canvas.draw()


    def get9ColorsFromPopulation(self):
        npop = self.NPopulation.value()
        randcolors = self.Population[np.random.randint(0, npop, size=9), :]
        colors = []
        for color in randcolors:
            c = (int(color[0]) << 16) | (int(color[1]) << 8) | int(color[2])
            colors.append(c)
        return colors


    def gaInitPop(self):
        self.StopSignal = False
        npop = self.NPopulation.value()
        self.Population = np.random.randint(0, 0x100, size=(npop, 3))
        self.fitPopulation = self.gaPopFitness(self.Population)
        self.PresasColors = self.get9ColorsFromPopulation()
        self.subGeraBox.setEnabled(True)
        self.lblGeneration.setText(f'0')
        self.generations = [0]
        self.meanFit = [np.mean(self.fitPopulation)]
        self.bestFit = [np.min(self.fitPopulation)]
        self.builtScenery()


    def gaFitness(self, individual):
        mcolor = self.MeanColorBkg
        refR = (mcolor & 0xFF0000) >> 16
        refG = (mcolor & 0x00FF00) >> 8
        refB = (mcolor & 0x0000FF)
        error = ((refR - individual[0])**2 + (refG - individual[1])**2 +  (refB - individual[2])**2)**0.5
        return error


    def gaPopFitness(self, apopulation):
        return np.array(list(self.gaFitness(i) for i in apopulation))


    def gaNaturalDeath(self):
        npop = self.NPopulation.value()
        lst = round(npop*(1 - self.PbDeath.value()/100.0))
        allidx = np.array(range(npop))
        rpidx = np.random.permutation(npop)
        self.Population = self.Population[allidx[rpidx[0:lst]],:]
        self.fitPopulation = self.fitPopulation[allidx[rpidx[0:lst]]]
        

    def gaReduction(self, Offspring, fitOffspring):
        self.gaNaturalDeath()
        newpop = np.concatenate((self.Population, Offspring))
        fitness = np.concatenate((self.fitPopulation, fitOffspring))
        nnpop = newpop.shape[0]
        allidx = np.array(range(nnpop))
        lst = self.NPopulation.value()
        if self.Predador:
            asidx = np.argsort(fitness)
            self.Population = newpop[allidx[asidx[0:lst]],:]
            self.fitPopulation = fitness[allidx[asidx[0:lst]]]
        else:
            rpidx = np.random.permutation(nnpop)
            self.Population = newpop[allidx[rpidx[0:lst]],:]
            self.fitPopulation = fitness[allidx[rpidx[0:lst]]]


    def gaTournament(self, ntourn):
        if self.Predador:
            fitness = self.fitPopulation
            rpidx = np.random.permutation(len(fitness))
            fittourn = fitness[rpidx[0:ntourn]]
            return rpidx[np.argmin(fittourn)]
        else:
            return np.random.randint(self.NPopulation.value())


    def gaXOver(self, parent1, parent2):
        nbits = 24
        bin1 = (int(parent1[0]) << 16) | (int(parent1[1]) << 8) | int(parent1[2])
        bin2 = (int(parent2[0]) << 16) | (int(parent2[1]) << 8) | int(parent2[2])
        for i in range(nbits):
            bit1 = (bin1 & (1 << i)) >> i
            bit2 = (bin2 & (1 << i)) >> i
            if bit1 != bit2 and np.random.rand() < 2.0/nbits:
                if bit1 == 0: # bit2 == 1
                    bin1 |=  (1 << i)
                else: # bit1 == 1, bit2 == 0
                    bin1 &= 0xFFFFFF & ~(1 << i)
        return [(bin1 & 0xFF0000) >> 16, (bin1 & 0x00FF00) >> 8, (bin1 & 0x0000FF)]


    def gaMutate(self, parent):
        nbits = 24
        bin1 = (int(parent[0]) << 16) | (int(parent[1]) << 8) | int(parent[2])
        for i in range(nbits):
            bit1 = (bin1 & (1 << i)) >> i
            if np.random.rand() < 2.0/nbits:
                if bit1 == 0:
                    bin1 |=  (1 << i) # bit1 = 1
                else:
                    bin1 &= 0xFFFFFF & ~(1 << i) # bit1 = 0
        return [(bin1 & 0xFF0000) >> 16, (bin1 & 0x00FF00) >> 8, (bin1 & 0x0000FF)]


    def Generation(self):
        npop = self.NPopulation.value()
        px = self.PbXover.value()/100.
        pm = self.PbMuta.value()/100.
        Offspring = np.zeros((npop, 3))
        fitOffspring = np.zeros((npop,))
        for i in range(npop):
            p1 = self.gaTournament(3)
            p2 = self.gaTournament(3)
            if np.random.rand() <= px:
                Offspring[i,:] = self.gaXOver(self.Population[p1,:], self.Population[p2,:])
            else:
                Offspring[i,:] = self.Population[p1,:]
            if np.random.rand() <= pm:
                Offspring[i,:] = self.gaMutate(Offspring[i,:])
        fitOffspring = self.gaPopFitness(Offspring)
        self.gaReduction(Offspring, fitOffspring)
        self.generations.append(self.generations[-1] + 1)
        self.meanFit.append(np.mean(self.fitPopulation))
        self.bestFit.append(np.min(self.fitPopulation))
        self.plot(self.generations, self.meanFit, self.bestFit)
        self.lblGeneration.setText(f'{int(self.lblGeneration.text())+1}')
        self.PresasColors = self.get9ColorsFromPopulation()
        self.builtScenery()


    def gaGoEvolutionX(self):
        self.SleepTime = 0.01
        self.gaGoEvolution_()

    def gaGoEvolution(self):
        self.SleepTime = 0.5
        self.gaGoEvolution_()

    def gaGoEvolution_(self):
        self.StopSignal = False
        ngen = self.MoreGenerations.value()
        for gen in range(ngen):
            if not self.StopSignal:
                self.Generation()
            else:
                self.StopSignal = False
                break
            QApplication.processEvents()
            sleep(self.SleepTime)


if __name__ == '__main__': 
    app = QApplication(sys.argv)
    mainp = Principal()
    sys.exit(app.exec_())