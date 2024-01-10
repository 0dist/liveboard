
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QShortcut, QScrollArea, QLayout, QMessageBox, QToolTip, QCompleter, QGraphicsDropShadowEffect, QTreeView, QShortcut, QStackedWidget, QSplitter
from PyQt5.QtCore import Qt, QSize, QRect, QUrl, QThread, QByteArray, QStringListModel
from PyQt5.QtGui import QColor, QFontDatabase, QIcon, QPixmap, QDesktopServices, QKeySequence

import sys, ctypes, json, time, threading, requests, os
sys.path.append("./platform")
from twitch import TwitchData
from youtube import YoutubeData



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

    for i in ["twitchList", "youtubeList"]:
        if not isinstance(DATA[i], list):
            DATA[i] = []

def saveData():
    with open("data.json", "w") as file:
        file.write('{"twitchList": [], "youtubeList": []}')

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
        self.setStyleSheet("QWidget{background-color: "+BLOCK_COLOR+"; border-radius: 3px;}QLabel#label{margin-left: 5px;}")

    def removeChannel(self, e, w, parent):
        if app.widgetAt(e.globalPos()) == w:
            data = parent.activeContainer[2]

            DATA[data].remove(self.channel.text())
            parent.activeContainer[0].removeWidget(self)
            self.deleteLater()
            parent.updateChannels(data)







class Completer(QTreeView):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setIndentation(-1)
        self.setStyleSheet("QTreeView{padding-left: 10px; font-family: "+FONT_FAMILY+"; font-size: "+str(FONT_SIZE)+"px; border: none; color: "+FONT_COLOR+"; background-color: "+BACKGROUND_COLOR+"; selection-background-color: "+BLOCK_COLOR+"; selection-color: "+FONT_COLOR+"; outline: none;}QScrollArea{border: none;}QScrollBar:vertical{margin: 0; width: 7px; border: none;}QScrollBar::handle:vertical{background-color: "+BLOCK_COLOR+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+BACKGROUND_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}")


 


class ChannelManager(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.hide()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("main")
        self.parent = parent

        centerWrap = QHBoxLayout()
        centerWrap.setContentsMargins(0,0,0,0)
        centerWid = QWidget()
        centerWid.setObjectName("center")
        centerWid.setFixedSize(500, 350)


        centerLayout = QVBoxLayout()
        centerLayout.setSpacing(0)
        m = 12
        centerLayout.setContentsMargins(m,m,m,m)
        topRow = QHBoxLayout()
        topRow.setContentsMargins(0,0,0,m)
        topRow.setSpacing(6)


        self.input = QLineEdit()
        self.completer = QCompleter()
        self.completer.setPopup(Completer())
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.scrollToWidget)
        self.input.setCompleter(self.completer)

        add = QPushButton("\uE004")
        add.clicked.connect(self.addChannel)
        self.input.returnPressed.connect(add.click)

        self.channelCount = QLabel()
        self.channelCount.setObjectName("count")
        deleteAll = QPushButton("\uE005")
        deleteAll.clicked.connect(self.clearChannelList)

        for i in [switchTwitch := QPushButton("\uE007"), switchYoutube := QPushButton("\uE008"), self.input, add, self.channelCount, deleteAll]:
            if i == self.channelCount:
                topRow.addStretch(1)
            if i in [switchTwitch, switchYoutube, add, deleteAll]:
                i.setObjectName("icon")
            topRow.addWidget(i)

        switchYoutube.clicked.connect(lambda: self.switchYoutube())
        switchTwitch.clicked.connect(lambda: self.switchTwitch())


        self.stackLayout = QStackedWidget()
        self.initiateLayouts()
        centerLayout.addLayout(topRow)
        centerLayout.addWidget(self.stackLayout)

        centerWid.setLayout(centerLayout)
        centerWrap.addWidget(centerWid, Qt.AlignCenter)
        self.setLayout(centerWrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget#main{background-color: rgba(0,0,0, 0.8)}QWidget#center{border-radius: 3px;}QWidget#center, QWidget#scroll{background-color: "+BACKGROUND_COLOR+";}QLineEdit{font-family: "+FONT_FAMILY+";padding-left: 10px; font-size: "+str(FONT_SIZE)+"px; border: none; color: "+FONT_COLOR+"; background-color: "+BACKGROUND_COLOR+"; height: "+str(BTN_SIZE)+"px; width: "+str(BTN_SIZE * 8)+"px}")


    def initiateLayouts(self):
        self.twitchContainer = [l := FlowLayout(self), self.containerLayout(l, "twitchList"), "twitchList", "Twitch"]
        self.youtubeContainer = [l := FlowLayout(self), self.containerLayout(l, "youtubeList"), "youtubeList", "Youtube"]

        for i in [self.twitchContainer[1], self.youtubeContainer[1]]:
            self.stackLayout.addWidget(i)


    def containerLayout(self, container, listData):
        scrollArea = QWidget()
        scrollArea.setObjectName("scroll")
        scrollArea.setLayout(container)

        for i in DATA[listData]:
            container.addWidget(ManagerBlock(i, self))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollArea)
        return scroll


    def switchManagerLayout(self):
        index = self.stackLayout.currentIndex() if DATA["layout"] != "stack" else main.activeLayout.currentIndex()
        [self.switchTwitch, self.switchYoutube][index]()

    def switchTwitch(self):
        self.activeContainer = self.twitchContainer
        self.stackLayout.setCurrentIndex(0)
        self.input.setPlaceholderText(""+self.activeContainer[3]+" streamer name")
        self.updateChannels(self.activeContainer[2])

    def switchYoutube(self):
        self.activeContainer = self.youtubeContainer
        self.stackLayout.setCurrentIndex(1)
        self.input.setPlaceholderText(""+self.activeContainer[3]+" handle name")
        self.updateChannels(self.activeContainer[2])


    def scrollToWidget(self, text):
        scroll = self.activeContainer[1]
        for i in self.activeContainer[0].itemList:
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
        data = self.activeContainer[2]
        if text:
            if not text.lower() in (c.lower() for c in DATA[data]):
                self.activeContainer[0].addWidget(ManagerBlock(text, self))
                self.input.clear()
                DATA[data].append(text)
                self.updateChannels(data)


    def clearChannelList(self, e):
        widget = self.activeContainer[0]
        data = self.activeContainer[2]
        platform = self.activeContainer[3]

        m = QMessageBox()
        m.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        q = m.question(self, "Clear the "+platform+" channel list?", "Are you sure you want to clear the "+platform+" channel list?", m.Yes | m.No)

        if q == m.Yes:
            for i in range(widget.count()):
                widget.itemAt(i).widget().deleteLater()
            DATA[data] = []
            self.updateChannels(data)

    def updateChannels(self, dataList):
        self.completer.setModel(QStringListModel(DATA[dataList]))
        self.channelCount.setText(str(len(DATA[dataList])))
        self.parent.saveData()


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

        self.thread = RequestThread(self, "")
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
    def __init__(self, platform, stream, login, channel, title, game, viewers):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.login = login
        self.stream = stream
        self.mouseReleaseEvent = self.showPreview if platform == "twitch" else None

        wrap = QHBoxLayout()
        textWrap = QVBoxLayout()
        wrap.setSpacing(0)
        wrap.setContentsMargins(0,0,0,0)


        img = QLabel()
        img.setFixedSize(BLOCK_HEIGHT, BLOCK_HEIGHT)
        img.setObjectName("img")
        img.setPixmap(QPixmap("images/"+platform+"/"+login+".png").scaled(BLOCK_HEIGHT, BLOCK_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img.mouseReleaseEvent = self.openInBrowser
        wrap.addWidget(img)

        topText = QHBoxLayout()
        topText.addWidget(QLabel(channel))
        topText.addStretch(1)

        if viewers != "-1":
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
                QDesktopServices.openUrl(QUrl(self.stream))
        except:
            pass









class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        global twitchCount, youtubeCount
        self.setFixedHeight(int(BTN_SIZE * 1.5))
        self.setAttribute(Qt.WA_StyledBackground)

        buttonWrap = QHBoxLayout()
        m = 5
        buttonWrap.setContentsMargins(m,0,m,0)
        buttonWrap.setSpacing(m)

        switchLayoutBtn = QPushButton("\uE009")
        switchLayoutBtn.setStyleSheet("margin-right: 10px;")
        switchTwitchBtn = QPushButton("\uE007")
        switchYoutubeBtn = QPushButton("\uE008")
        for i in [twitchCount := QLabel(), youtubeCount := QLabel()]:
            i.setObjectName("count")
        self.managerBtn = QPushButton("\uE001")
        self.managerBtn.setStyleSheet("margin-left: 10px;")


        btns = [switchLayoutBtn, switchTwitchBtn, switchYoutubeBtn, twitchCount, youtubeCount, QPushButton("\uE000"), QPushButton("\uE002"), self.managerBtn]
        for i in btns:
            if i == twitchCount:
                buttonWrap.addStretch(1)
            if i not in [twitchCount, youtubeCount]:
                i.setObjectName("icon")
            buttonWrap.addWidget(i)


        btns[5].clicked.connect(lambda: main.refreshBlocks(""))
        self.managerBtn.mouseReleaseEvent = self.showManager
        btns[6].clicked.connect(self.sort)

        switchTwitchBtn.clicked.connect(lambda: main.switchStackLayout(0))
        switchYoutubeBtn.clicked.connect(lambda: main.switchStackLayout(1))
        switchLayoutBtn.clicked.connect(lambda: main.switchLayout())

        self.setLayout(buttonWrap)
        self.updateStylesheet()

    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+BACKGROUND_COLOR+";}QPushButton#icon{background-color: "+BLOCK_COLOR+";}")


    def sort(self, e):
        main.reversed = True if not main.reversed else False
        main.sortBlocks()
        main.generateTwitchBlocks()
        main.generateYoutubeBlocks()

    def showManager(self, e):
        if app.widgetAt(e.globalPos()) == self.managerBtn:
            self.managerBtn.clearFocus()
            main.manager.raise_()
            main.manager.show()
            main.manager.switchManagerLayout()














class RequestThread(QThread):
    def __init__(self, parent, platform):
        super().__init__()
        self.parent = parent
        self.platform = platform

    def run(self):
        try:
            if not hasattr(self.parent, "login"):
                if self.platform == "twitch":
                    twitch.getData(DATA["twitchList"], twitchCount)
                    self.clearCount(twitchCount)
                else:
                    youtube.getData(DATA["youtubeList"], youtubeCount)
                    self.clearCount(youtubeCount)
            else:
                with open(self.parent.path, "wb") as f:
                    f.write(requests.get("https://static-cdn.jtvnw.net/previews-ttv/live_user_"+self.parent.login+"-854x480.jpg").content)
        except:
            pass
        if not hasattr(self.parent, "login"):
            self.parent.sortBlocks()

    def clearCount(self, count):
        count.hide()
        count.clear()





class Main(QWidget): 
    def __init__(self):
        super().__init__()
        global twitch, youtube
        twitch = TwitchData()
        youtube = YoutubeData()

        self.reversed = True
        QFontDatabase().addApplicationFont("resource/Outfit-Regular.ttf")
        QFontDatabase().addApplicationFont("resource/lbicons.ttf")

        self.wrapGrid = QGridLayout()
        self.mainWindow = QVBoxLayout()
        self.mainWindow.setSpacing(0)
        for i in [self.wrapGrid, self.mainWindow]:
            i.setContentsMargins(0,0,0,0)


        self.stackLayout = QStackedWidget()
        self.splitLayout = QSplitter()
        self.splitLayout.setChildrenCollapsible(False)
        self.splitLayout.setHandleWidth(5)
        self.splitLayout.splitterMoved.connect(lambda: self.splitterMove())

        try:
            DATA["layout"]
        except:
            DATA["layout"] = "stack"
        self.activeLayout = self.stackLayout if DATA["layout"] == "stack" else self.splitLayout


        self.populateLayout()
        self.mainWindow.addWidget(Dashboard())
        self.mainWindow.addWidget(self.activeLayout)
        # restore previous state
        self.setSpliterGeometry()
        self.switchStackLayout(None)


        self.wrapGrid.addLayout(self.mainWindow, 0, 0)
        self.manager = ChannelManager(self)
        self.wrapGrid.addWidget(self.manager, 0, 0)
        self.setLayout(self.wrapGrid)

        self.updateStylesheet()
        self.setWindowGeometry()


        self.twitchThread = RequestThread(self, "twitch")
        self.youtubeThread = RequestThread(self, "youtube")
        for t, b in [(self.twitchThread, self.generateTwitchBlocks), (self.youtubeThread, self.generateYoutubeBlocks)]:
            t.start()
            t.finished.connect(b)



        QShortcut(QKeySequence("Ctrl+Shift+R"), self).activated.connect(lambda: self.refreshBlocks(""))
        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(lambda: self.switchStackLayout(""))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(lambda: self.switchStackLayout(""))
        QShortcut(QKeySequence("Esc"), self).activated.connect(lambda: self.manager.hide())

    def updateStylesheet(self):
        self.setStyleSheet("QWidget#main{background-color: "+BACKGROUND_COLOR+";}QScrollArea{border: none;}QScrollBar:vertical{margin: 0; width: 7px; border: none;}QScrollBar::handle:vertical{background-color: "+BLOCK_COLOR+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+BACKGROUND_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QPushButton#icon{font-family: lbicons; color: "+FONT_COLOR+"; font-size: "+str(ICON_SIZE)+"px; border-radius: 3px; background-color: "+BLOCK_COLOR+"; width: "+str(BTN_SIZE)+"px; height: "+str(BTN_SIZE)+"px;}QPushButton#icon:pressed{color: "+FONT_DARKER+"}QLabel#label, QLabel#count{font-size: "+str(FONT_SIZE)+"px; font-family: "+FONT_FAMILY+"; color: "+FONT_COLOR+";}QLabel#count{font-size: "+str(FONT_SIZE - 2)+"px;}QSplitter::handle{background-color: "+BLOCK_COLOR+";}")

    def setWindowGeometry(self):
        try:
            self.restoreGeometry(QByteArray.fromBase64(DATA["windowGeometry"].encode()))
        except:
             self.resize(self.screen().availableGeometry().size() / 2)

    def setSpliterGeometry(self):
        try:
            self.splitLayout.restoreState(QByteArray.fromBase64(DATA["splitGeometry"].encode()))
        except:
            pass


    def switchStackLayout(self, tab):
        if self.activeLayout == self.stackLayout:
            if isinstance(tab, str):
                self.activeLayout.setCurrentIndex(0) if self.activeLayout.currentIndex() == 1 else self.activeLayout.setCurrentIndex(1)
            elif isinstance(tab, int):
                self.activeLayout.setCurrentIndex(tab)
            else:
                try:
                    self.activeLayout.setCurrentIndex(DATA["activeTab"])
                except:
                    pass
            DATA["activeTab"] = self.activeLayout.currentIndex()


    def switchLayout(self):
        self.activeLayout.setParent(None)

        for i in self.activeLayout.children():
            if type(i) == QScrollArea:
                i.deleteLater()

        self.activeLayout = self.stackLayout if self.activeLayout == self.splitLayout else self.splitLayout

        self.populateLayout()
        self.mainWindow.addWidget(self.activeLayout)
        self.switchStackLayout(None) if self.activeLayout == self.stackLayout else self.setSpliterGeometry()

        DATA["layout"] = "split" if DATA["layout"] == "stack" else "stack"


    def populateLayout(self):
        if not hasattr(self, "twitchGrid"):
            self.twitchGrid = FlowLayout(False)
            self.youtubeGrid = FlowLayout(False)
            
        for i in [self.twitchGrid, self.youtubeGrid]:
            self.activeLayout.addWidget(self.platformLayout(i))

    def platformLayout(self, grid):
        scrollArea = QWidget()
        scrollArea.setLayout(grid)
        scrollArea.setObjectName("main")
        QShortcut(QKeySequence("Ctrl+R"), scrollArea).activated.connect(lambda: self.refreshBlocks(grid))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(BLOCK_WIDTH)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(scrollArea)
        return scroll


    def refreshBlocks(self, grid):
        match grid:
            case self.twitchGrid:
                self.twitchThread.start()
            case self.youtubeGrid:
                self.youtubeThread.start()
            case "":
                self.twitchThread.start()
                self.youtubeThread.start()

    def sortBlocks(self):
        for i in [twitch.liveChannels, youtube.liveChannels]:
            i.sort(key = lambda x:x["viewers"], reverse = self.reversed)


    def generateTwitchBlocks(self):
        self.generateBlocks(self.twitchGrid, twitch.liveChannels)

    def generateYoutubeBlocks(self):
        self.generateBlocks(self.youtubeGrid, youtube.liveChannels)

    def generateBlocks(self, grid, platform):
        for i in range(grid.count()):
            grid.itemAt(i).widget().deleteLater()

        for i in platform:
            grid.addWidget(ProfileBlock(i["platform"], i["stream"], i["login"], i["channel"], i["title"], i["game"], str(format(i["viewers"], ",d").replace(",", "."))))
        grid.update()


    def splitterMove(self):
        DATA["splitGeometry"] = bytearray(self.splitLayout.saveState().toBase64()).decode("utf-8")


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
    app.setWindowIcon(QIcon("resource/logo.ico"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("liveboard") if sys.platform == "win32" else None
    main = Main()
    main.show()
    sys.exit(app.exec())


            

        