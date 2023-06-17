
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QShortcut, QScrollArea, QLayout, QMessageBox, QToolTip
from PyQt5.QtCore import Qt, QSize, QRect, QUrl, QPoint, QThread, QByteArray
from PyQt5.QtGui import QKeyEvent, QKeySequence, QColor, QFontDatabase, QSyntaxHighlighter, QIcon, QPixmap, QDesktopServices

import sys, ctypes, json
from twitch import TwitchData



def darker(var):
    c = QColor(var)
    if var == FONT_COLOR:
        i = 120
    else:
        i = 80
    if c.value() > 120:
        return QColor().fromHsv(c.hue(),c.saturation(),c.value() - i).name()
    else:
        return QColor().fromHsv(c.hue(),c.saturation(),c.value() + i).name()


BLOCK_WIDTH = 330
BLOCK_HEIGHT = 70

FONT_SIZE = 14
BTN_SIZE = 25
ICON_SIZE = 16

FONT_COLOR = "#e0e0e0"
BACKGROUND_COLOR = "#141414"
BLOCK_COLOR = "#1c1c1c"
ICON_COLOR = "#cfcfcf"

ICON_DARKER = darker(ICON_COLOR)
FONT_DARKER = darker(FONT_COLOR)


def openData():
    global DATA
    with open("data.json", "r") as file:
        DATA = json.load(file)
    if not isinstance(DATA["channelList"], list):
        DATA["channelList"] = []

def saveData():
    with open("data.json", "w") as file:
        file.write('{"channelList": []}')

try:
    openData()
except:
    saveData()
    openData()













class ManagerBlock(QWidget):
    def __init__(self, channel):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)

        wrap = QHBoxLayout()
        wrap.setContentsMargins(0,0,0,0)
        self.channel = QLabel(str(channel))
        self.channel.setObjectName("label")
        wrap.addWidget(self.channel)
        wrap.addStretch(1)
        remove = QPushButton("\uE006")
        remove.setObjectName("icon")
        remove.mouseReleaseEvent = lambda e: self.removeChannel(e, remove)
        wrap.addWidget(remove)

        self.setLayout(wrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget{font-size: "+str(FONT_SIZE)+"px; background-color: "+BLOCK_COLOR+";}QLabel{margin-left: 5px; color: "+FONT_COLOR+";}QPushButton#icon{font-size: 12px;}")


    def removeChannel(self, e, w):
        if app.widgetAt(e.globalPos()) == w:
            DATA["channelList"].remove(self.channel.text())
            self.deleteLater()










class ChannelManager(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("main")

        centerWrap = QHBoxLayout()
        centerWid = QWidget()
        centerWid.setObjectName("center")
        centerWid.setFixedSize(500, 350)


        centerLayout = QVBoxLayout()
        centerLayout.setSpacing(0)
        centerLayout.setContentsMargins(15,15,15,15)
        topRow = QHBoxLayout()
        topRow.addStretch(1)
        topRow.setContentsMargins(0,0,0,15)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter channel name")
        add = QPushButton("\uE004")
        add.clicked.connect(self.addChannel)
        self.input.returnPressed.connect(add.click)
        deleteAll = QPushButton("\uE005")
        deleteAll.clicked.connect(self.clearChannelList)

        for i in [self.input, add, deleteAll]:
            if i == deleteAll:
                topRow.addStretch(1)
            topRow.addWidget(i)
            i.setObjectName("icon")


        scrollArea = QWidget()
        scrollArea.setObjectName("scroll")
        self.container = FlowLayout(self)
        scrollArea.setLayout(self.container)

        for i in DATA["channelList"]:
            self.container.addWidget(ManagerBlock(i))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollArea)

        centerLayout.addLayout(topRow)
        centerLayout.addWidget(scroll)

        centerWid.setLayout(centerLayout)
        centerWrap.addWidget(centerWid, Qt.AlignCenter)
        self.setLayout(centerWrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget#main{background-color: rgba(0,0,0, 0.8);}QWidget#center, QWidget#scroll{background-color: "+BACKGROUND_COLOR+";}QLineEdit{font-size: "+str(FONT_SIZE)+"px; border: none; color: "+FONT_COLOR+"; background-color: "+BACKGROUND_COLOR+"; height: "+str(BTN_SIZE)+"px; width: "+str(BTN_SIZE * 6)+"px;}")


    def addChannel(self, e):
        text = self.input.text()
        if text:
            if not text.lower() in (c.lower() for c in DATA["channelList"]):
                self.container.addWidget(ManagerBlock(text))
                self.input.clear()
                DATA["channelList"].append(text)


    def clearChannelList(self, e):
        m = QMessageBox()
        m.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        q = m.question(self, "Clear the channel list?", "Are you sure you want to clear the channel list?", m.Yes | m.No)

        if q == m.Yes:
            for i in range(self.container.count()):
                self.container.itemAt(i).widget().deleteLater()
            DATA["channelList"] = []


    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if not self.childAt(e.pos()):
            self.hide()












class FlowLayout(QLayout):
    def __init__(self, manager):
        super().__init__()
        self.itemList = []
        self.manager = manager

    def addItem(self, item):
        if not self.manager:
            self.itemList.append(item)
        else:
            self.itemList.insert(0, item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def sizeHint(self):
        return self.minimumSize()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0)) if not self.manager else self.doManagerLayout(QRect(0, 0, width, 0))

    def minimumSize(self):
        return QSize(BLOCK_WIDTH, BLOCK_HEIGHT)

    def setGeometry(self, rect):
        self.doLayout(rect) if not self.manager else self.doManagerLayout(rect)

    def doLayout(self, rect):
        margin = 12
        y = rect.y() + margin
        x = height = 0 
        gap = - margin

        for item in self.itemList:
            width = item.sizeHint().width()
            gap += width + margin

            if gap + width + margin > rect.width():
                break
        gap = int((rect.width() - gap) / 2)


        for item in self.itemList:
            width = item.sizeHint().width()
            height = item.sizeHint().height()
            nextX = x + width + margin

            if nextX > rect.width() + margin:
                x = 0
                nextX = x + width + margin
                y = y + height + margin

            item.setGeometry(QRect(x + gap, y, width, height))
            x = nextX
        return y + height


    def doManagerLayout(self, rect):
        margin = 8
        y = rect.y()
        x = height = 0

        for item in self.itemList:
            width = int((rect.width() - margin * 2) / 3)
            height = item.sizeHint().height()
            nextX = x + width + margin

            if nextX - margin > rect.width():
                x = 0
                nextX = x + width + margin
                y = y + height + margin

            item.setGeometry(QRect(x, y, width, height))
            x = nextX
        return y + height












class ProfileBlock(QWidget): 
    def __init__(self, channel, title, game, viewers):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.channel = channel

        wrap = QHBoxLayout()
        textWrap = QVBoxLayout()
        wrap.setSpacing(0)
        wrap.setContentsMargins(0,0,0,0)


        img = QLabel()
        img.setFixedSize(BLOCK_HEIGHT, BLOCK_HEIGHT)
        img.setObjectName("img")
        img.setPixmap(QPixmap("images/"+channel+".png").scaled(BLOCK_HEIGHT, BLOCK_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        wrap.addWidget(img)

        topText = QHBoxLayout()
        channel = QLabel(channel)
        channel.setObjectName("channel")
        topText.addWidget(channel, Qt.AlignLeft)
        viewers = QLabel(viewers)
        viewers.setObjectName("viewers")
        topText.addWidget(viewers)
        textWrap.addLayout(topText)

        if game:
            game = QLabel(game)
            game.setObjectName("game")
            textWrap.addWidget(game)

        strTitle = QLabel(title)
        strTitle.setToolTip(title)
        strTitle.setObjectName("title")
        strTitle.setWordWrap(True)
        strTitle.setAlignment(Qt.AlignTop)
        textWrap.addWidget(strTitle)


        textWrap.addStretch(1)
        textWrap.setContentsMargins(7,2,7,5)
        wrap.addLayout(textWrap)

        self.setLayout(wrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget, QToolTip{font-family: Gantari; color: "+FONT_COLOR+"; font-size: "+str(FONT_SIZE)+"px; border: 0px solid red; background-color: "+BLOCK_COLOR+";}QLabel#title, QLabel#game, QLabel#viewers{color: "+FONT_DARKER+"; font-size: 12px;}")


    # def mouseReleaseEvent(self, e):
    #     super().mouseReleaseEvent(e)
    #     try:
    #         QDesktopServices.openUrl(QUrl("https://twitch.tv/"+self.channel+""))
    #     except:
    #         pass









class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        global progress
        self.setFixedHeight(int(BTN_SIZE * 1.3))
        self.setAttribute(Qt.WA_StyledBackground)

        buttonWrap = QHBoxLayout()
        buttonWrap.setContentsMargins(0,0,5,0)
        buttonWrap.setSpacing(5)
        buttonWrap.addStretch(1)

        self.managerBtn = QPushButton("\uE001")
        btns = [progress := QLabel(), QPushButton("\uE000"), self.managerBtn, QPushButton("\uE002")]
        for i in btns:
            buttonWrap.addWidget(i)
            i.setObjectName("icon")

        btns[1].clicked.connect(self.refresh)
        self.managerBtn.mouseReleaseEvent = self.showManager
        btns[3].clicked.connect(self.sort)

        self.setLayout(buttonWrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+BACKGROUND_COLOR+";}QLabel{font-family: Gantari; font-size: 12px; color: "+FONT_COLOR+";}")


    def refresh(self, e):
        main.reversed = False
        main.thread.start()

    def sort(self):
        main.sortBlocks()
        main.generateBlocks()

    def clearLayout(self):
        for i in range(main.profileGrid.count()):
            main.profileGrid.itemAt(i).widget().deleteLater()

    def showManager(self, e):
        self.managerBtn.clearFocus()
        main.manager.show()














class TwitchThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        try:
            twitch.getData(DATA["channelList"], progress)
        except:
            pass
        self.parent.sortBlocks()



class Main(QWidget): 
    def __init__(self):
        super().__init__()
        global twitch
        twitch = TwitchData()
        self.reversed = False
        QFontDatabase().addApplicationFont("resource/Gantari-Regular.ttf")
        QFontDatabase().addApplicationFont("resource/lbicons.ttf")

        wrapGrid = QGridLayout()
        base = QVBoxLayout()
        base.setSpacing(0)
        for i in [wrapGrid, base]:
            i.setContentsMargins(0,0,0,0)


        scrollArea = QWidget()
        self.profileGrid = FlowLayout(False)
        scrollArea.setLayout(self.profileGrid)
        scrollArea.setObjectName("main")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(scrollArea)

        base.addWidget(Dashboard())
        base.addWidget(scroll)


        wrapGrid.addLayout(base, 0, 0)
        self.manager = ChannelManager()
        wrapGrid.addWidget(self.manager, 0, 0)
        self.setLayout(wrapGrid)
        self.updateStylesheet()
        self.setWindowGeometry()


        self.thread = TwitchThread(self)
        self.thread.start()
        self.thread.finished.connect(self.generateBlocks)

    def updateStylesheet(self):
        self.setStyleSheet("QWidget#main{background-color: "+BACKGROUND_COLOR+";}QScrollArea{border: none;}QScrollBar:vertical{margin: 0; width: 7px; border: none;}QScrollBar::handle:vertical{background-color: "+BLOCK_COLOR+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+BACKGROUND_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QPushButton#icon{font-family: lbicons; color: "+ICON_COLOR+"; font-size: "+str(ICON_SIZE)+"px; border: none; background-color: "+BACKGROUND_COLOR+"; width: "+str(BTN_SIZE)+"px; height: "+str(BTN_SIZE)+"px;}QPushButton#icon:pressed{color: "+ICON_DARKER+"}QLabel#label, QLineEdit{font-family: Gantari;}")

    def setWindowGeometry(self):
        try:
            self.restoreGeometry(QByteArray.fromBase64(DATA["windowGeometry"].encode()))
        except:
             self.resize(self.screen().availableGeometry().size() / 2)


    def sortBlocks(self):
        self.reversed = True if not self.reversed else False
        twitch.liveChannels.sort(key = lambda x:x["viewers"], reverse = self.reversed)

    def generateBlocks(self):
        for i in range(self.profileGrid.count()):
            self.profileGrid.itemAt(i).widget().deleteLater()

        for i in twitch.liveChannels:
            self.profileGrid.addWidget(ProfileBlock(i["channel"], i["title"], i["game"], str(format(i["viewers"], ",d").replace(",", "."))))
        progress.setText("")


    def closeEvent(self, e):
        DATA["windowGeometry"] = bytearray(self.saveGeometry().toBase64()).decode("utf-8")

        with open("data.json", "w") as f:
            json.dump(DATA, f)










if __name__ == "__main__":
    app = QApplication([])
    # app.setWindowIcon(QIcon("resource/icon.ico"))
    # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('app')
    main = Main()
    main.show()
    sys.exit(app.exec())


            

        