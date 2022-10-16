import sys
from os import listdir
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QTableWidgetItem, QFileDialog, QInputDialog, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import *
from BlurWindow.blurWindow import GlobalBlur
from PySide6 import QtUiTools
import yfinance as yf
from os.path import exists
import plotly.graph_objs as go
import pandas as pd
import qdarktheme
import pickle

# Changelog:
#
# 0_2:
# added list view and am no longer breaking up data based on folder, but rather on filename suffix
# 0_3:
# overhauled file loading dialog box
# added daily value calculation for comparison of two symobols
# 0_4:
# add data currency to csv's

class PyFinCalc_Settings:
    def __init__(self, directory):
        #'C:\\Users\\graha\\OneDrive\\Documents\\Coding\\Data Sources\\'

        # not using this class yet, but this will be used to generate an object
        # containing program settings data and persist

        PyFinCalc_Settings.directory = directory

class dfo:
    def __init__(self, name, df, type='hist', filename='',savedate=' '): #
        # df0 --> "data frame object"
        # an object that receives a name (for a stock symbol), an associated dataframe, and a data type
        self.name = name
        self.df = df
        #types: from MyApp __init__ function: self.data_type = ['_hist','_basis','_holdings']
        self.type = type
        self.filename = filename
        self.savedate = savedate

class portfolio:
    def __init__(self, name, dfolist=[], savedate=''): #
        self.name = name
        self.dfolist = dfolist
        self.savedate = savedate

class MainApp(QWidget):

    def __init__(self):
        super().__init__()
        
        # Load PySide6 .ui file for the program as created in QT Designer
        self.ui = QtUiTools.QUiLoader().load("PyFinCalc.ui", self)

        # Main container for all data loaded into the program.
        self.data_list = []

        # need to set this up as an enumerated datatype
        self.data_type = ['hist','basis','holdings']

        # create list of all the checkbox widgets so that they update automatically
        self.list_cboxes_hist = [self.ui.cbox_hist,self.ui.cbox_hist2]        
        self.list_cboxes_basis = [self.ui.cbox_basis]

        # auto load data from previous sessions
        if auto_load_data:
            self.load_persistent_data_list(pkl_filename)
            self.ui.lbl_autoloaded.setText('Data from: '+pkl_filename)

        # Button setup
        self.ui.btn_load2.clicked.connect(self.load_data_from_list_widget)
        self.ui.btn_get_hist.clicked.connect(lambda a=' ': self.get_hist_data(a))
        self.ui.button_plot.clicked.connect(self.plot_hist)    
        self.ui.button_price.clicked.connect(self.get_current_price)    
        self.ui.button_calc.clicked.connect(self.invest_compare_plot_caller)    
        self.ui.btn_save.clicked.connect(self.save_data_list)
        self.ui.btn_load3.clicked.connect(self.load_persistent_data_list)
        self.ui.btn_choose_folder.clicked.connect(self.choose_folder)
        self.ui.btn_view_data.clicked.connect(self.show_data)

        # Setup combobox of valid yfinance historical data timeframes
        valid_timeframe_inputs = ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
        for i in valid_timeframe_inputs:
            self.ui.cbox_timeframe.addItem(i)

        # Tab view setup
        self.ui.tabWidget.setDocumentMode(True)
        #self.ui.tabWidget.tab.setDocumentMode(True)
        #pane.setAttribute(Qt.WA_TranslucentBackground)
        #self.ui.tabWidget.pane.setStyleSheet("background: transparent")

        # Label setup
        self.ui.label_price.setText('')
        self.ui.lb_title.setStyleSheet("font-size: 18px")
        self.ui.label_status.setStyleSheet("font-size: 14px")
        self.ui.label_status.setText('Text')

        # HTML viewing widget setup (for Pyplot)
        self.ui.widget_web.setAttribute(Qt.WA_TranslucentBackground)
        self.ui.widget_web.setStyleSheet("background: transparent")
        self.ui.widget_web.page().setBackgroundColor(Qt.transparent)

        self.ui.plot_window_2.setAttribute(Qt.WA_TranslucentBackground)
        self.ui.plot_window_2.setStyleSheet("background: transparent")
        self.ui.plot_window_2.page().setBackgroundColor(Qt.transparent)        

        # Overall widget setup for transparency effects
        self.ui.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        GlobalBlur(self.winId(),Acrylic=True,Dark=True,QWidget=self)
        self.setStyleSheet("background-color: rgba(70, 70, 70, 70)")
        self.setWindowTitle('PyFinCalc 0.')

    def save_data_list(self):
        input, pressed = QInputDialog.getText(self, '', 'Input file name to save data list to')
        if pressed:
            with open(input, 'wb') as outp:
                pickle.dump(self.data_list, outp, pickle.HIGHEST_PROTOCOL)
            return

    def load_persistent_data_list(self, filename):
        with open(filename, 'rb') as inp:
            datalist = pickle.load(inp)
        for dfo in datalist:
            print('type: '+dfo.type)
            #before adding, ensure an existing item is not already present
            if self.find_dfo(dfo.name, dfo.type):
                self.update_error_screen('Data already loaded, cannot add')
                #early return since we already have the data loaded
                return            
            # as long as data hasn't been loaded, load and add to the list structure. 
            # To do: need to add data validation to ensure type is what i want
            else:
                #self.update_error_screen('Data not yet loaded, loading now. Symbol: '+symbol+' -- Type: '+type)
                self.add_dfo_to_data_list(dfo)
        return

    def init_list_widget(self, listwgt, list, type=False):
        if type:
            print('list type is: '+type)
            for i in list:
                if i.type == type:
                    var = i.filename
                    listwgt.addItem(var)
        # for simple list of strings getting added to list view
        else:
            for i in list:
                listwgt.addItem(i)
        return

    def find_dfo(self, symbol, type, filename='na'):
        if filename == 'na':
            #finds item from main list, returns either the specified df or False
            dfo_or_no = next((dfo for dfo in self.data_list if (dfo.name==symbol)&(dfo.type==type)), None)
        else:
            dfo_or_no = next((dfo for dfo in self.data_list if dfo.filename==filename), None)
        return dfo_or_no 

    def plot_hist(self):

        # Get symbol of what is to be plotted
            # find_dfo will return none if a df object with specified name and type is not found
        temp = self.find_dfo(self.ui.cbox_hist.currentText(),self.data_type[0])
        if temp:
            df = temp.df
            self.update_error_screen('Data is loaded. Generating plot') ######

            figlayout = go.Layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=80, b=20)
                )

            fig = go.Figure([go.Scatter(x=df['Date'], y=df['Close'])], layout=figlayout)
            fig.update_layout(
                yaxis=dict(
                    title_text="Y-axis Title",
                    titlefont=dict(size=25),
                ),
                title=dict(
                    text=temp.name+' Price History',
                    #x=0.5,
                    #y=0.95,
                    font=dict(
                        #family="Arial",
                        size=30
                        )            
                ),
            )
            #html = self.build_plot(fig)
            #self.ui.widget_web.setHtml(html)

            self.ui.widget_web.setHtml(fig.to_html(include_plotlyjs='cdn'))

        else:
            self.update_error_screen('Data not loaded, cannot plot') ######
        return

    def pic_plot(self, dfo1, dfo2):
        self.update_error_screen('Generating plot') #####

        y_data_column = 'Value'
        x_data_column = 'Date'
        df = dfo1.df
        df2 = dfo2.df
        
        if True:
            fig = go.Figure()
            fig.add_trace(go.Scatter(name=dfo1.name, x=df[x_data_column], y=df[y_data_column]))
            fig.add_trace(go.Scatter(name=dfo2.name, x=df2[x_data_column], y=df2[y_data_column]))

            fig.update_layout(
                yaxis=dict(
                    title_text=y_data_column,
                    titlefont=dict(size=25),
                ),
                xaxis=dict(
                    title_text=x_data_column,
                    titlefont=dict(size=25),
                ),
                font_color = "white",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',                
                margin=dict(l=20, r=20, t=80, b=20),
                title=dict(
                    text=f"{dfo1.name} vs {dfo2.name} Same-Day Investment Comparison",
                    #x=0.5,
                    #y=0.95,
                    font=dict(
                        #family="Arial",
                        size=30
                        )            
                ),
            )

            self.ui.plot_window_2.setHtml(fig.to_html(include_plotlyjs='cdn'))

        else:
            self.update_error_screen('Data not loaded, cannot plot') ######
        return

    def load_data_from_list_widget(self):
      
        selectedItemsList = self.ui.listwgt_file_list.selectedItems()
        for file in selectedItemsList:
            filename = file.text()
            # extract out the symbol and data type
            symbol, type_j = filename.rsplit('_', maxsplit=1)
            type, _ = type_j.rsplit('.', maxsplit=1)
            savedate = ''
            
            #before adding, ensure an existing item is not already present
            dfo = self.find_dfo(symbol, type)
            if dfo:
                self.update_error_screen('Data already loaded, cannot add')
                qm = QMessageBox
                answer = qm.question(self,'','Do you want to delete '+dfo.filename+' and replace?',qm.Yes | qm.No, qm.Yes)
                if answer == qm.No:
                    return
                else:
                    try:
                        print('removing '+dfo.filename)
                        self.data_list.remove(dfo)
                        print('removed')
                        self.add_dfo_to_data_list(dfo(symbol, pd.read_csv(self.list_folderpath+'/'+filename), type, filename, savedate))
                    except:
                        self.update_error_screen('Cannot remove item, not currently loaded in program')
            # as long as data hasn't been loaded, load and add to the list structure. 
            # To do: need to add data validation to ensure type is what i want
            else:
                self.update_error_screen('Data not yet loaded, loading now. Symbol: '+symbol+' -- Type: '+type)
                #print('in else statement in load data from list widget')
                print(f"symbol: {symbol} type: {type} savedate: {savedate}")
                print(f"read_csv input: {self.list_folderpath}/{filename}")
                tempdf = pd.read_csv(f"{self.list_folderpath}/{filename}")
                print(tempdf.head())
                temp = dfo('ET', tempdf, 'basis', 'ET_basis.csv', savedate='10-10-2022')
                print('df head: ')
                print(temp.df.head())
                #self.add_dfo_to_data_list(dfo(symbol, pd.read_csv(f"{self.list_folderpath}/{filename}"), type, filename, savedate))
        return    

    def choose_folder(self):
        self.list_folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.init_list_widget(self.ui.listwgt_file_list, listdir(self.list_folderpath))

        return

    def show_data(self):
        filename = self.ui.cbox_all_data.currentText()
        dfo = self.find_dfo('','',filename)
        if dfo.df.any:
            self.display_df_in_table(self.ui.tableWidget, dfo.df) 
        return
    
    def display_df_in_table(self, table, df):

        if df.size == 0:
            return
        df = df.fillna('')

            #ignore first two rows
            #df.columns = df.iloc[1]
            #df = df.iloc[2:]
            # Keep only the columns of data of interest
            #df = df[['Symbol','Company','Sector','No Years','Price','Low','High','Div Yield','5Y Avg Yield','DGR 1Y','DGR 3Y','DGR 5Y','DGR 10Y','Industry']]

        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        for row in df.iterrows():
            values = row[1]        
            for col_index, value in enumerate(values):
                tableitem = QTableWidgetItem(str(value))
                table.setItem(row[0],col_index,tableitem)

    def add_dfo_to_data_list(self, dfo):

        # perform operations to ensure all formats are correct
        dfo = self.clean_data(dfo)

        # add dfo to data_list, the central variable holding all the loaded data
        self.data_list.append(dfo)
        print("dfo added")
        # update any lists around the program that use the data list
        #self.update_lists(dfo)
        self.update_textboxes(dfo)

        # update labels and dropdown boxes that use the list of loaded symbols
        self.update_cboxes()

        return

    def clean_data(self, dfo):
        #if dfo.df['Date'].any:
        #    dfo.df['Date'] = pd.to_datetime(dfo.df['Date']).dt.date
        if dfo.savedate:
            return dfo
        try:
            if dfo.df['Date'].any:
                dfo.df['Date'] = pd.to_datetime(dfo.df['Date']).dt.date
                dfo.savedate = dfo.df['Date'].max()
        except:
            dfo.savedate, ok = QInputDialog.getText(self, 'Date for '+dfo.filename,'Input date of information as "YYYY-MM-DD":',QLineEdit.Normal)
        return dfo

    def update_cboxes(self):
        # update combo box of file names
        self.ui.cbox_all_data.clear()
        for dco in self.data_list:
            self.ui.cbox_all_data.addItem(dco.filename)

        # update _basis type combo boxes
        for QComboBox in self.list_cboxes_basis:
            QComboBox.clear()
            for dco in self.data_list:
                if dco.type == self.data_type[1]:
                    QComboBox.addItem(dco.name)

        # update _hist type combo boxes
        for QComboBox in self.list_cboxes_hist:
            QComboBox.clear()
            for dco in self.data_list:
                if dco.type == self.data_type[0]:
                    QComboBox.addItem(dco.name)

        return

    def update_lists(self, dfo):
        #Update lists on data page
        if dfo.type == 'hist':
            self.ui.listwgt_file_list_hist.addItem(dfo.filename)
        if dfo.type == 'basis':
            self.ui.listwgt_file_list_basis.addItem(dfo.filename)
        if dfo.type == 'holdings':
            self.ui.listwgt_file_list_holdings.addItem(dfo.filename)                        

        return

    def update_textboxes(self, dfo):
        #Update lists on data page
        if dfo.type == 'hist':
            currentText = self.ui.text_hist.toPlainText()
            extra = ' - Date: '+str(dfo.savedate)
            self.ui.text_hist.setPlainText(currentText+dfo.filename+extra+'\n')
        if dfo.type == 'basis':
            currentText = self.ui.text_basis.toPlainText()
            extra = ' - Date: '+str(dfo.savedate)
            self.ui.text_basis.setPlainText(currentText+dfo.filename+extra+'\n')
        if dfo.type == 'holdings':
            currentText = self.ui.text_holdings.toPlainText()
            extra = ' - Date: '+str(dfo.savedate)
            self.ui.text_holdings.setPlainText(currentText+dfo.filename+extra+'\n')
        return

    def alt_invest_calc(self, nameA, nameB, fActPrice, fAltPrice):
        # alt_invest_calc
        # returns:
        # (1) dataframe with six columns of data indicating what the actual and 
        #     potential gains would be by investing in an alternate investment 
        # args: 
        # (1) dataframe as returned by load_gs_cost_basis()
        #
        #     this is a dataframe of specific days a stock was purchased and the purchase price
        # (2) dataframe of an alternate investment (i.e. the S&P) as returned by
        #     get_historical_data()
        #     
        #     this historical data is used to find corresponding days of the actual 
        #     investment and what would have happened had you instead invested in the
        #     alternate investment
        # (3) float of current price of the actual investment
        # (4) float of current price of the alternate investment

        df = pd.DataFrame()

        dfo_A_basis = self.find_dfo(nameA, 'basis')

        dfo_A = self.find_dfo(nameA, 'hist')

        dfo_B = self.find_dfo(nameB, 'hist')

        dfAltMatch = pd.DataFrame()
        dfActMatch = pd.DataFrame()

        # holds entries from alternate history dataframe
        dfAltMatch = dfo_B.df[dfo_B.df["Date"].isin(dfo_A_basis.df["Date"])]

        # hold entries from actual investment
        dfActMatch = dfo_A_basis.df[dfo_A_basis.df["Date"].isin(dfo_B.df["Date"])]

        # reset row numbers from both
        dfAltMatch = dfAltMatch.reset_index(drop=True)
        dfActMatch = dfActMatch.reset_index(drop=True)

        print(dfAltMatch.tail())

        print(dfActMatch.tail())

        #Rows: dollars invested, date, use closing price, qty of spy, cost basis of SPY

        #grab invested dollars from alternate
        df[['Date','Invested']] = dfActMatch[['Date','Invested']]

        # save original (QQQ) share qty
        df['Act_Shares'] = dfActMatch['Quantity']

        # calculate QQQ price basis
        # QQQ_PricePerShare
        df['Act_Price'] = df['Invested']/df['Act_Shares']

        # act gain
        df['ActualGain'] = df['Act_Shares']*(fActPrice-df['Act_Price'])

        # calculate hypothetical qty of shares from the invested
        # SPY_Shares
        df['Alt_Shares'] = df['Invested']/dfAltMatch['Close']

        # SPY_PricePerShare
        df['Alt_Price'] = dfAltMatch['Close']

        # alt gain
        df['PotentialGain'] = df['Alt_Shares']*(fAltPrice- df['Alt_Price'])

        return df

    def alt_invest_calc_daily(self, nameA, nameB):
        self.update_error_screen('comparing investing in '+nameA+' and '+nameB)

        dfo_A_basis = self.find_dfo(nameA, 'basis')
        df_ab = dfo_A_basis.df
        
        # if history data is not already loaded, go grab it
        try:
            dfo_A = self.find_dfo(nameA, 'hist')
            df_a_hist = dfo_A.df
        except:
            df_a_hist = self.get_hist_data(nameA)

        try:
            dfo_B = self.find_dfo(nameB, 'hist')
            df_b_hist = dfo_B.df
        except:
            df_b_hist = self.get_hist_data(nameB)

        # #1 Get date of first purchase in basis
        start_date = df_ab['Date'].min()
        
        # #2 chop off history data prior to start date
        df_a_hist = df_a_hist[~(df_a_hist['Date'] < start_date)]
        df_b_hist = df_b_hist[~(df_b_hist['Date'] < start_date)]

        # #2b chop off ends of whichever is longer      
        end_date = min(df_a_hist['Date'].max(),df_b_hist['Date'].max())
        df_a_hist = df_a_hist[~(df_a_hist['Date'] > end_date)]
        df_b_hist = df_b_hist[~(df_b_hist['Date'] > end_date)]

        # reset row numbers from both
        df_a_hist = df_a_hist.reset_index(drop=True)
        df_b_hist = df_b_hist.reset_index(drop=True)

        df_a = pd.DataFrame()
        df_b = pd.DataFrame()
        df_a[['Date','Price']] = df_a_hist[['Date','Close']]
        df_a[['Qty','Value']] = 0.0
        df_b[['Date','Price']] = df_b_hist[['Date','Close']]        
        df_b[['Qty','Value']] = 0.0
        
        # loop through all of the history files *must be same length*
        qty = 0.0
        qty_b = 0.0
        df_bb = df_ab #make pseudo cost basis tracker if we had bought 
        df_bb['Symbol'] = nameB
        for i, row in enumerate(df_a.itertuples(), 0): 
            for j, rowj in enumerate(df_ab.itertuples(), 0): #look through the basis file to find transaction dates
                if row.Date == rowj.Date:
                    qty = qty + rowj.Quantity
                    df_bb['Quantity'].iloc[j] = rowj.Invested/df_b['Price'].iloc[i]
                    qty_b = qty_b + df_bb['Quantity'].iloc[j]
            # at the end of each day for the entire history dataframe:
            df_a['Qty'].iloc[i] = qty
            df_b['Qty'].iloc[i] = qty_b
    
        df_a['Value'] = df_a['Qty']*df_a['Price']
        df_b['Value'] = df_b['Qty']*df_b['Price']

        dfo_a = dfo(nameA, df_a, 'hist')
        dfo_b = dfo(nameB, df_b, 'hist')

        return dfo_a, dfo_b

    def invest_compare_plot_caller(self):

        COST_price = 465.57
        SCHD_price = 67.73
        SPY_price = 361.0

        #output = self.alt_invest_calc('SCHD','SPY', SCHD_price, SPY_price)
        #print(output)

        dfo_a, dfo_b = self.alt_invest_calc_daily(self.ui.cbox_basis.currentText(),self.ui.cbox_hist2.currentText())
        self.pic_plot(dfo_a, dfo_b)
        #self.update_error_screen(output)
        return

    def get_hist_data(self, symbol):
        # establish function-level variables that will be used and generate filepath string
        if symbol == ' ':
            symbol = self.ui.input_symbol_data_tab.text()
            timeframe = self.ui.cbox_timeframe.currentText()
        else:
            timeframe = '5y'
        symbol = symbol.upper()
        filename = symbol+'_hist.csv'
        filenamefull = filepath+filename
        tickerObj = yf.Ticker(symbol)
        df_hist_j = tickerObj.history(period = timeframe)
        df_hist_j.to_csv(filenamefull)
        df_hist = pd.read_csv(filenamefull)
        self.add_dfo_to_data_list(dfo(symbol, df_hist, 'hist', filename))
        return df_hist

    def update_error_screen(self, msg):
        current = self.ui.label_status.text()
        new = msg+'<br>'+current
        self.ui.label_status.setText(new)

    def get_current_price(self):
        #yf returns the price differently for stock and etf
        if self.ui.rbutton_stock.isChecked():
            yf_arg_string = 'currentPrice'
        else:
            yf_arg_string = 'regularMarketPrice'

        price = yf.Ticker(self.ui.input_symbol.text()).info[yf_arg_string]
        self.ui.label_price.setText('$'+str(price))

if __name__ == '__main__':

    pkl_filename = '10-11-data.pkl'
    auto_load_data = True
    filepath = 'C:\\Users\\graha\\OneDrive\\Documents\\Coding\\PyFinCalc\\Data\\'
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())  
    pyfincalc_main = MainApp()
    pyfincalc_main.showMaximized()
    #pyfincalc_main.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing window...')