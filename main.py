
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QShortcut, QScrollArea, QLayout, QMessageBox, QToolTip, QCompleter, QGraphicsDropShadowEffect, QTreeView, QShortcut
from PyQt5.QtCore import Qt, QSize, QRect, QUrl, QThread, QByteArray, QStringListModel, QEvent
from PyQt5.QtGui import QKeyEvent, QKeySequence, QColor, QFontDatabase, QSyntaxHighlighter, QIcon, QPixmap, QDesktopServices, QKeySequence

import sys, ctypes, json, time, threading, requests, os
from twitch import TwitchData



def darker():
    c = QColor(FONT_COLOR)
    if c.value() > 120:
        return QColor().fromHsv(c.hue(),c.saturation(),c.value() - 120).name()
    else:
        return QColor().fromHsv(c.hue(),c.saturation(),c.value() + 120).name()


BLOCK_WIDTH = 330
BLOCK_HEIGHT = 70

FONT_SIZE = 14
BTN_SIZE = 25
ICON_SIZE = 11

FONT_COLOR = "#d6d6d6"
BACKGROUND_COLOR = "#121212"
BLOCK_COLOR = "#171717"

FONT_DARKER = darker()
FONT_FAMILY = "Outfit"


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
    def __init__(self, channel, parent):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)

        wrap = QHBoxLayout()
        wrap.setSpacing(0)
        wrap.setContentsMargins(0,0,0,0)

        self.channel = QLabel(str(channel))
        self.channel.setObjectName("label")
        wrap.addWidget(self.channel)
        wrap.addStretch(1)
        remove = QPushButton("\uE006")
        remove.setObjectName("icon")
        remove.mouseReleaseEvent = lambda e: self.removeChannel(e, remove, parent)
        wrap.addWidget(remove)

        self.setLayout(wrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+BLOCK_COLOR+"; border-radius: 3px;}")

    def removeChannel(self, e, w, parent):
        if app.widgetAt(e.globalPos()) == w:
            DATA["channelList"].remove(self.channel.text())
            parent.container.removeWidget(self)
            self.deleteLater()
            parent.updateChannels()







class Completer(QTreeView):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setIndentation(-1)
        self.setStyleSheet("QTreeView{padding-left: 10px; font-family: "+FONT_FAMILY+"; font-size: "+str(FONT_SIZE)+"px; border: none; color: "+FONT_COLOR+"; background-color: "+BACKGROUND_COLOR+"; selection-background-color: "+BLOCK_COLOR+"; selection-color: "+FONT_COLOR+"; outline: none;}QScrollArea{border: none;}QScrollBar:vertical{margin: 0; width: 7px; border: none;}QScrollBar::handle:vertical{background-color: "+BLOCK_COLOR+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+BACKGROUND_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}")


 


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
        centerLayout.setContentsMargins(12,12,12,12)
        topRow = QHBoxLayout()
        # left margin is temporary and static
        topRow.setContentsMargins(140,0,0,12)


        self.input = QLineEdit(placeholderText = "Enter streamer name")
        self.completer = QCompleter(DATA["channelList"])
        self.completer.setPopup(Completer())
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(lambda t: self.scrollToWidget(t, scroll))
        self.input.setCompleter(self.completer)

        add = QPushButton("\uE004")
        add.clicked.connect(self.addChannel)
        self.input.returnPressed.connect(add.click)

        self.channelCount = QLabel(str(len(DATA["channelList"])))
        self.channelCount.setObjectName("count")
        deleteAll = QPushButton("\uE005")
        deleteAll.clicked.connect(self.clearChannelList)

        for i in [self.input, add, self.channelCount, deleteAll]:
            if i == self.channelCount:
                topRow.addStretch(1)
            if i in [add, deleteAll]:
                i.setObjectName("icon")
            topRow.addWidget(i)


        scrollArea = QWidget()
        scrollArea.setObjectName("scroll")
        self.container = FlowLayout(self)
        scrollArea.setLayout(self.container)

        for i in DATA["channelList"]:
            self.container.addWidget(ManagerBlock(i, self))

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
        self.setStyleSheet("QWidget#main{background-color: rgba(0,0,0, 0.8)}QWidget#center{border-radius: 3px;}QWidget#center, QWidget#scroll{background-color: "+BACKGROUND_COLOR+";}QLineEdit{font-family: "+FONT_FAMILY+";padding-left: 10px; font-size: "+str(FONT_SIZE)+"px; border: none; color: "+FONT_COLOR+"; background-color: "+BACKGROUND_COLOR+"; height: "+str(BTN_SIZE)+"px; width: "+str(BTN_SIZE * 6)+"px;}")



    def scrollToWidget(self, text, scroll):
        for i in self.container.itemList:
            if i.widget().findChild(QLabel).text() == text:

                scroll.verticalScrollBar().setValue(i.geometry().y() - scroll.height() + i.geometry().height() + int(scroll.height() / 2))
                t = threading.Thread(target = self.revealBlock, args = [i.widget()])
                t.start()
                break


    def revealBlock(self, w):
        e = QGraphicsDropShadowEffect()
        e.setOffset(0)
        e.setBlurRadius(20)
        e.setColor(QColor(FONT_COLOR))
        w.setGraphicsEffect(e)

        time.sleep(1.5)
        try:
            w.setGraphicsEffect(None)
        except:
            pass


    def addChannel(self, e):
        text = self.input.text()
        if text:
            if not text.lower() in (c.lower() for c in DATA["channelList"]):
                self.container.addWidget(ManagerBlock(text, self))
                self.input.clear()
                DATA["channelList"].append(text)
                self.updateChannels()


    def clearChannelList(self, e):
        m = QMessageBox()
        m.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        q = m.question(self, "Clear the streamer list?", "Are you sure you want to clear the streamer list?", m.Yes | m.No)

        if q == m.Yes:
            for i in range(self.container.count()):
                self.container.itemAt(i).widget().deleteLater()
            DATA["channelList"] = []
            self.updateChannels()

    def updateChannels(self):
        self.completer.setModel(QStringListModel(DATA["channelList"]))
        self.channelCount.setText(str(len(DATA["channelList"])))
        main.saveData()


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
        y = rect.y()
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









class StreamPreview(QWidget): 
    def __init__(self, login):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.login = login
        self.path = ""+self.login+"-preview.jpg"

        self.centerWrap = QHBoxLayout()
        self.setLayout(self.centerWrap)

        self.thread = TwitchThread(self)
        self.thread.start()
        self.thread.finished.connect(self.showPreview)
        self.setStyleSheet("background-color: rgba(0,0,0, 0.8)")

    def showPreview(self):
        img = QLabel()
        img.setFixedSize(854, 480)
        img.setPixmap(QPixmap(self.path))
        self.centerWrap.addWidget(img, Qt.AlignCenter)


    def mouseReleaseEvent(self, e):
        if app.widgetAt(e.globalPos()) == self:
            self.deleteLater()
            try:
                os.remove(self.path)
            except:
                pass




class ProfileBlock(QWidget):
    def __init__(self, login, channel, title, game, viewers):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.login = login
        self.mouseReleaseEvent = self.showPreview

        wrap = QHBoxLayout()
        textWrap = QVBoxLayout()
        wrap.setSpacing(0)
        wrap.setContentsMargins(0,0,0,0)


        img = QLabel()
        img.setFixedSize(BLOCK_HEIGHT, BLOCK_HEIGHT)
        img.setObjectName("img")
        img.setPixmap(QPixmap("images/"+login+".png").scaled(BLOCK_HEIGHT, BLOCK_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img.mouseReleaseEvent = self.openInBrowser
        wrap.addWidget(img)

        topText = QHBoxLayout()
        topText.addWidget(QLabel(channel))
        topText.addStretch(1)

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
        self.setStyleSheet("QWidget, QToolTip{font-family: "+FONT_FAMILY+"; color: "+FONT_COLOR+"; font-size: "+str(FONT_SIZE)+"px; border: 0px solid red; background-color: "+BLOCK_COLOR+";}QLabel#title, QLabel#game, QLabel#viewers{color: "+FONT_DARKER+"; font-size: 12px;}")


    def showPreview(self, e):
        w = app.widgetAt(e.globalPos())
        if w.parent() == self or w == self:
            main.wrapGrid.addWidget(StreamPreview(self.login), 0, 0)

    def openInBrowser(self, e):
        try:
            w = app.widgetAt(e.globalPos())
            if w.parent() == self or w == self:
                QDesktopServices.openUrl(QUrl("https://twitch.tv/"+self.login+""))
        except:
            pass









class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        global progress
        self.setFixedHeight(int(BTN_SIZE * 1.5))
        self.setAttribute(Qt.WA_StyledBackground)

        buttonWrap = QHBoxLayout()
        buttonWrap.setContentsMargins(0,0,5,0)
        buttonWrap.setSpacing(5)
        buttonWrap.addStretch(1)

        self.managerBtn = QPushButton("\uE001")
        progress = QLabel()
        progress.setObjectName("count")
        btns = [progress, QPushButton("\uE000"), self.managerBtn, QPushButton("\uE002")]
        for i in btns:
            buttonWrap.addWidget(i)
            if i is not progress:
                i.setObjectName("icon")

        btns[1].clicked.connect(lambda: main.refreshBlocks())
        self.managerBtn.mouseReleaseEvent = self.showManager
        btns[3].clicked.connect(self.sort)

        self.setLayout(buttonWrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+BACKGROUND_COLOR+";}QPushButton#icon{background-color: "+BLOCK_COLOR+";}")


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
            if not hasattr(self.parent, "login"):
                twitch.getData(DATA["channelList"], progress)
            else:
                with open(self.parent.path, "wb") as f:
                    f.write(requests.get("https://static-cdn.jtvnw.net/previews-ttv/live_user_"+self.parent.login+"-854x480.jpg").content)
        except:
            pass
        if not hasattr(self.parent, "login"):
            self.parent.sortBlocks()
            progress.setText("")




class Main(QWidget): 
    def __init__(self):
        super().__init__()
        global twitch
        twitch = TwitchData()
        self.reversed = False
        QFontDatabase().addApplicationFont("resource/Outfit-Regular.ttf")
        QFontDatabase().addApplicationFont("resource/lbicons.ttf")

        self.wrapGrid = QGridLayout()
        base = QVBoxLayout()
        base.setSpacing(0)
        for i in [self.wrapGrid, base]:
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


        self.wrapGrid.addLayout(base, 0, 0)
        self.manager = ChannelManager()
        self.wrapGrid.addWidget(self.manager, 0, 0)
        self.setLayout(self.wrapGrid)
        self.updateStylesheet()
        self.setWindowGeometry()


        self.thread = TwitchThread(self)
        self.thread.start()
        self.thread.finished.connect(self.generateBlocks)
        # self.generateBlocks()
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.refreshBlocks)

    def updateStylesheet(self):
        self.setStyleSheet("QWidget#main{background-color: "+BACKGROUND_COLOR+";}QScrollArea{border: none;}QScrollBar:vertical{margin: 0; width: 7px; border: none;}QScrollBar::handle:vertical{background-color: "+BLOCK_COLOR+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+BACKGROUND_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QPushButton#icon{font-family: lbicons; color: "+FONT_COLOR+"; font-size: "+str(ICON_SIZE)+"px; border-radius: 3px; background-color: "+BLOCK_COLOR+"; width: "+str(BTN_SIZE)+"px; height: "+str(BTN_SIZE)+"px;}QPushButton#icon:pressed{color: "+FONT_DARKER+"}QLabel#label, QLabel#count{margin-left: 5px; font-size: "+str(FONT_SIZE)+"px; font-family: "+FONT_FAMILY+"; color: "+FONT_COLOR+";}QLabel#count{font-size: "+str(FONT_SIZE - 2)+"px; margin-right: 3px;}")

    def setWindowGeometry(self):
        try:
            self.restoreGeometry(QByteArray.fromBase64(DATA["windowGeometry"].encode()))
        except:
             self.resize(self.screen().availableGeometry().size() / 2)


    def refreshBlocks(self):
        self.reversed = False
        self.thread.start()

    def sortBlocks(self):
        self.reversed = True if not self.reversed else False
        twitch.liveChannels.sort(key = lambda x:x["viewers"], reverse = self.reversed)

    def generateBlocks(self):
        for i in range(self.profileGrid.count()):
            self.profileGrid.itemAt(i).widget().deleteLater()

        for i in twitch.liveChannels:
            self.profileGrid.addWidget(ProfileBlock(i["login"], i["channel"], i["title"], i["game"], str(format(i["viewers"], ",d").replace(",", "."))))


    def saveData(self):
        with open("data.json", "w") as f:
            json.dump(DATA, f)

    def closeEvent(self, e):
        DATA["windowGeometry"] = bytearray(self.saveGeometry().toBase64()).decode("utf-8")
        self.saveData()
        # temporary
        for img in os.listdir("."):
            if img.endswith("-preview.jpg"):
                os.remove(img)










if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("resource/logo.png"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('app')
    main = Main()
    main.show()
    sys.exit(app.exec())


            

        