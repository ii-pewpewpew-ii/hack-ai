import sys
import json
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal ,Qt ,QTimer
from PyQt6.QtGui import QIntValidator  
from PyQt6.QtWidgets import QFrame, QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget ,QLineEdit,QTabWidget, QComboBox , QScrollArea,QLabel ,QHBoxLayout ,QMessageBox
from uagents import Agent, Context
from enum import Enum
from pydantic import Field
import uuid
from src.messages.currency_request import AvailableCurrenciesRequest, SubscribeRequest
from src.messages.general import UAgentResponse, KeyValue, UAgentResponseType
from uagents.setup import fund_agent_if_low
import asyncio 
import time 

available_currencies_request = str(uuid.uuid4())

base_currency = "USD"
foreign_currency = "AED"

class User(QThread):

    message_received = pyqtSignal(dict)
    ctx = None 
    currency_agent_address = None 
    subscribed_list = dict()

    def __init__(self):
        super().__init__()

    def run(self):
        async def async_function():
            await asyncio.sleep(2)
            return "Async task completed"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        f = open("src/config.json")
        temp = json.load(f)
        # Create agent
        self.currency_agent_address = temp["currency_agent_address"]
        self.client = Agent(name="client", seed="alice phase", port=8008, endpoint=["http://127.0.0.1:8008/submit"])
        fund_agent_if_low(self.client.wallet.address())
        # start

        @self.client.on_interval(period=2000)
        async def handler(ctx: Context):
            self.ctx = ctx 
            await ctx.send(self.currency_agent_address, AvailableCurrenciesRequest(from_=self.client.address, request_id=available_currencies_request))

        @self.client.on_message(model=UAgentResponse, replies=SubscribeRequest)
        async def handle_currencies_response(ctx: Context, sender: str, msg: UAgentResponse):
            print(msg)
            if msg.type == UAgentResponseType.ERROR:
                self.message_received.emit({"type":"Error","data":"Cannot fetch details now"})
                ctx.logger.info("Cannot fetch details now")
                return
            elif msg.type == UAgentResponseType.OPTIONS:
                self.message_received.emit({"type":"Options", "data":msg.available_options})

            elif msg.type == UAgentResponseType.SUCCESS:
                self.message_received.emit({"type" : "Subscribe" , "data":msg.message})
                ctx.logger.info(f"Subscribed successfully")
            elif msg.type == UAgentResponseType.ALERT:
                self.message_received.emit({"type":"Alert","data":msg.message})
                ctx.logger.info(msg.message)

        self.client.run()

        loop.run_until_complete(async_function())
        loop.close()
   


class Updater():

    def __init__(self,window) :
        self.window = window

    def handle_response(self,message):

        print(message)
        
        type__ = message["type"]

        if type__ == "Options":
            self.update_currencies(message["data"])
        
        elif type__=="Alert" :
            self.update_news(message["data"])

        elif type__ == "Subscribe" : 
            self.update_subscribe(message["data"])
        else :
            pass 
    
    def update_currencies(self,data):
        for i in data :
            temp = i.key+"("+i.value+")"
            self.window.combobox1.addItem(i.key)
            self.window.combobox2.addItem(i.key)
        

    def update_news(self,data):
        message  = QLabel(data)
        message.setWordWrap(True)
        self.window.alert_tab_layout.addWidget(message)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine) 
        divider.setFrameShadow(QFrame.Shadow.Sunken)  
        divider.setStyleSheet("background-color: #007BFF;")
        self.window.alert_tab_layout.addWidget(divider)
        pass 

    def update_subscribe(self,data):
        
        data = json.loads(data)
        temp = data["currency_base"]+"_"+ data["currency_exchange"]
        self.window.message_emitter.subscribed_list[temp] = data["threshold"]
        label = QLabel()

        label.setText(f"<html><p style='color: white; font-size: 16px;font-weight:700'>{data['currency_base']} vs {data['currency_exchange']}</p>"
                  f"<p style='color:  #007BFF; font-size: 18px;'>Threshold : {data['threshold']}</p></html>")
        label.setStyleSheet("padding:10px;margin-bottom:20px")
           
        self.window.subscribed_tab_layout.addWidget(label)
        
        self.window.display_message("LOW","Subscription successfull")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message Checker")
        self.setFixedSize(700,700)

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.central_widget.setStyleSheet("""
            QTabWidget::tab-bar {
                background: #333;
                border: none;
            }
            QTabBar::tab {
                background: #555;
                color: white;
                padding: 8px 20px;

            }
            QTabBar::tab:selected {
                background: #007BFF;
            }
        """)
        self.central_widget.setTabPosition(QTabWidget.TabPosition.South)

        self.update = Updater(self)

        self.message_emitter = User()
        self.message_emitter.message_received.connect(self.update.handle_response)
        self.message_emitter.start()

        self.options_tab = QWidget()
        self.central_widget.addTab(self.options_tab,"Settings")

        self.combobox1_label = QLabel("Choose Base Currency")
        self.combobox2_label = QLabel("Choose Foreign Currency")
        self.combobox1 = QComboBox()
        self.combobox2 = QComboBox()
        self.combobox1_wrapper = QWidget()

        self.c1 = QHBoxLayout()
        self.c1.addWidget(self.combobox1_label)
        self.c1.addWidget(self.combobox1)
        self.combobox1_wrapper.setLayout(self.c1)

        self.combobox2_wrapper = QWidget()
        self.c2 = QHBoxLayout()
        self.c2.addWidget(self.combobox2_label)
        self.c2.addWidget(self.combobox2)
        self.combobox2_wrapper.setLayout(self.c2)

        self.add_button = QPushButton("Add Subscription")
        self.add_button.setStyleSheet(
    "background-color: #007BFF; color: white; border: none; padding: 7px; "
    "border: 2px solid rgba(0, 0, 0, 0.2); /* Custom shadow effect */"
    "margin-bottom : 2rem"
)

        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self.run_async_function)

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter a number")
        self.number_input.setFixedWidth(100)
        int_validator = QIntValidator(self)
        self.number_input.setValidator(int_validator)

        self.options_message = QLabel()
        self.options_message.setStyleSheet("color:red;")

        self.c3 = QHBoxLayout()
        self.c3.addWidget(QLabel("Enter Threshold"))
        self.c3.addWidget(self.number_input)
        self.input_wrapper = QWidget()
        self.input_wrapper.setLayout(self.c3)

        self.options_tab_layout = QVBoxLayout()
        self.options_tab_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.options_tab_layout.addWidget(self.combobox1_wrapper)
        self.options_tab_layout.addWidget(self.combobox2_wrapper)
        self.options_tab_layout.addWidget(self.input_wrapper)
        self.options_tab_layout.addWidget(self.add_button)
        self.options_tab_layout.addWidget(self.options_message)

        self.options_tab.setLayout(self.options_tab_layout)
    
        self.alert_tab = QWidget()
        self.alert_tab_layout = QVBoxLayout()
        self.alert_tab.setLayout(self.alert_tab_layout)
        
        scroll_area_1 = QScrollArea(self)
        scroll_area_1.setWidgetResizable(True)
        scroll_area_1.setWidget(self.alert_tab)
        scroll_area_1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area_1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area_1.setStyleSheet("background-color: #333;color:white")

        #####################
        self.subscribed_tab = QWidget()
        self.subscribed_tab_layout = QVBoxLayout()
        self.subscribed_tab.setLayout(self.subscribed_tab_layout)
        self.subscribed_tab_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.subscribed_tab_layout.setSpacing(0)
        self.subscribed_tab_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area_2 = QScrollArea(self)
        scroll_area_2.setWidgetResizable(True)
        scroll_area_2.setWidget(self.subscribed_tab)
        scroll_area_2.setStyleSheet("background-color: #333;color:white")

        self.central_widget.addTab(scroll_area_1,"Notifications")
        self.central_widget.addTab(scroll_area_2,"Subscribed currencies")
        
    def display_message(self,severity,message):

        if severity=="HIGH":
            self.options_message.setStyleSheet("color:red")
        else :
            self.options_message.setStyleSheet("color:green")

        self.options_message.setText(message)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hideLabel)
        self.timer.start(3000) 

    def hideLabel(self):
        self.options_message.setText("")
        self.timer.stop()

    async def show_popup_notification(self):
        
        msg = QMessageBox()
        msg.setWindowTitle("ALERT")
        
        base_currency = self.combobox1.currentText()
        foreign_currency = self.combobox2.currentText()

        temp = base_currency+"_"+foreign_currency 

        if temp in self.message_emitter.subscribed_list:
            self.display_message("HIGH","You Already subsribed with this combo")
            return 

        if base_currency=="":
            self.display_message("HIGH","Please Wait")
            return

        if self.number_input.text()=="":
            self.display_message("HIGH","Please Enter Threshold")
            return 
        
        flag = True 

        if base_currency==foreign_currency:
            flag = False 

        if flag : 
            msg.setText(base_currency+" vs "+foreign_currency)

            msg.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok)
        
            result = msg.exec()

            if result == QMessageBox.StandardButton.Ok:
                subscribe_request_id = str(uuid.uuid4())
                self.display_message("LOW","Please Wait....")
                await self.message_emitter.ctx.send(self.message_emitter.currency_agent_address, SubscribeRequest(subscriber_address=self.message_emitter.client.address, currency_base=base_currency, currency_exchanged=foreign_currency, threshold= self.number_input.text(), request_id=subscribe_request_id))

        else :
            self.display_message("HIGH","Both Currencies are same")

    # def show_popup_notification_async(self):
    #     # Create a QTimer to run the asynchronous function in the event loop
    #     timer = QTimer()
    #     timer.timeout.connect(self.run_async_function)
    #     timer.start(0)

    def run_async_function(self):
        asyncio.run(self.show_popup_notification())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
