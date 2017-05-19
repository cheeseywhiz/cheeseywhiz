"""79 characters long                                                      """
import time
import sys
import praw
import prawcore
import webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

reddit = praw.Reddit('cheeseywhiz')

class InputDialog(QMainWindow):
    """Enter subreddit: [Enter]
    [input field]
    [Action:]
    """
    def __init__(self):
        super().__init__()
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setWindowFlags(Qt.WindowStaysOnTopHint
                            |Qt.WindowCloseButtonHint
                            |Qt.WindowMinimizeButtonHint
                            |Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle('Get Reddit Link')
        self.setCentralWidget(InputWidget(self))
        self.minimumWidth_ = 248
        self.setMinimumWidth(self.minimumWidth_)
        self.setFixedSize(self.minimumSize())
        self.show()

class InputWidget(QWidget):
    """Argument to class is parent object (self)
    Gathers all elements to be displayed in the main dialog
    """
    def __init__(self,caller):
        self.caller = caller
        super().__init__()
        self.init_elements()
        self.init_connections()
        self.setLayout(self.input_layout())
    
    def init_elements(self):
        self.inputField = InputField(self)
        self.linksDropdown = ActionsDropdown(self,['Part of submission:',
                                                   'Comments',
                                                   'Link'])
        self.sortDropdown = ActionsDropdown(self,['Sort:',
                                                  'Hot',
                                                  'Top',
                                                  'New'])
        self.timesDropdown = ActionsDropdown(self,['Time limit:',
                                                   'all',
                                                   'year',
                                                   'month',
                                                   'week',
                                                   'day',
                                                   'hour'])
        self.statusLine = QLabel('Waiting on subreddit...')

    def init_connections(self):
        self.get_inputEvent([self.inputField])
        self.get_optionChangeEvent([self.sortDropdown])

    def input_layout(self):
        layout = QVBoxLayout()
        widgets = [self.label_InputField_widget(),
                   self.linksDropdown,
                   self.sortDropdown,
                   self.timesDropdown,
                   self.statusLine]
        for widget in widgets: layout.addWidget(widget)
        self.timesDropdown.hide()
        self.statusLine.hide()
        return layout

    def label_InputField_widget(self):
        row = QWidget()
        rowLayout = QHBoxLayout()
        rowLayout.setContentsMargins(0,0,0,0)
        rowLayout.addWidget(QLabel('Enter subreddit:'))
        rowLayout.addWidget(self.inputField)
        row.setLayout(rowLayout)
        return row

    def get_inputEvent(self,sources):
        for source in sources:
            source.inputEvent.connect(self.on_input_event)

    def get_optionChangeEvent(self,sources):
        for source in sources:
            source.optionChangeEvent.connect(self.on_sort_change_event)

    def on_input_event(self,self_):
        link = self_.linksDropdown.currentIndex()
        sort = self_.sortDropdown.currentIndex()
        userInput = self_.inputField.text()
        self.statusLine.show()
        try:
            if userInput == '': raise Exception('No subreddit entered')
            self_.open_link(link,sort,userInput)
        except prawcore.exceptions.Redirect as error:
            self_.statusLine.setText('Subreddit not found')
        except prawcore.exceptions.NotFound as error:
            self_.statusLine.setText('Subreddit not found')
        except Exception as error:
            self_.statusLine.setText(str(type(error)))

    def on_sort_change_event(self,self_):
        if self.sortDropdown.currentIndex() == 2:
            self.timesDropdown.show()
        else:
            if self.timesDropdown.isVisible():
                self.timesDropdown.hide()
                self.setMinimumWidth(self.caller.minimumWidth_)
                self.caller.setFixedSize(self.minimumSize())

    def open_link(self,link,sort,userInput):
        self.statusLine.setText('Opening...')
        QCoreApplication.processEvents()
        time = self.timesDropdown.currentIndex()
        subreddit = reddit.subreddit(userInput)
        timeDictionary = {0:'all',
                          1:'all',
                          2:'year',
                          3:'month',
                          4:'week',
                          5:'day',
                          6:'hour'}
        timeString = timeDictionary[time]
        sortDictionary = {0:(subreddit.hot(limit=5),'hottest'),
                          1:(subreddit.hot(limit=5),'hottest'),
                          2:(subreddit.top(time_filter=timeString,limit=5),
                             'top/'+timeString),
                          3:(subreddit.new(limit=5),'newest')}
        posts, sortString = sortDictionary[sort]
        submission = [post for post in posts if not post.stickied][0]
        linkDictionary = {0:(submission.shortlink,'Opened comments from '),
                          1:(submission.shortlink,'Opened comments from '),
                          2:(submission.url,'Opened link from ')}
        url,linkString = linkDictionary[link]
        webbrowser.open(url)
        self.statusLine.setText(linkString+sortString+' in /r/'+userInput)

class InputField(QLineEdit):
    """InputField(parent): Argument allows for parent to receive signal.
    Sends signal inputEvent on return.
    """
    inputEvent = pyqtSignal('QObject')
    def __init__(self,caller):
        self.caller = caller
        super().__init__()
        self.returnPressed.connect(self.on_return_pressed)

    def on_return_pressed(self):
        self.inputEvent.emit(self.caller)

    def mousePressEvent(self,event): self.selectAll()

class ActionsDropdown(QComboBox):
    """Drop down box with the first element being uneditable
    """
    optionChangeEvent = pyqtSignal('QObject')
    def __init__(self,caller,actions):
        self.caller = caller
        super().__init__()
        for action in actions: self.addItem(action)
        index = self.model().index(0,0)
        self.model().setData(index,QVariant(0),Qt.UserRole-1)
        self.currentIndexChanged.connect(self.on_index_change)

    def on_index_change(self,event):
        self.optionChangeEvent.emit(self.caller)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    id = InputDialog()
    sys.exit(app.exec_())
