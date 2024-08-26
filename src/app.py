import time, datetime
import queue
import pandas as pd
import os
# EClient is for sending requests to the IB server
from ibapi.client import EClient
# EWrapper is for handling incoming messages
from ibapi.common import BarData
from ibapi.wrapper import EWrapper
from threading import Thread
from lightweight_charts import Chart

from ibapi.client import Contract, Order, ScannerSubscription
from ibapi.tag_value import TagValue
from gpt4o_technical_analyst import analyze_chart

import chart as ChartWrapper
##Docu
# https://ibkrcampus.com/ibkr-api-page/twsapi-doc/

## Connection Config
DEFAULT_HOST = '127.0.0.1'
DEFAULT_CLIENT_ID = 1
PAPER_TRADING_PORT = 7497
LIVE_TRADING_PORT = 7496
LIVE_TRADING=False

TRADING_PORT = PAPER_TRADING_PORT
if LIVE_TRADING:
  TRADING_PORT = LIVE_TRADING_PORT

## Initial Config
INITIAL_SYMBOL = "SMR"
WHAT_TO_SHOW = "TRADES"

data_queue = queue.Queue()
# IBClient acts as the client. Requires host address and port number
class IBClient(EWrapper, EClient):
  def __init__(self, host, port, client_id):
    # EClient envia peticiones a ITS
    EClient.__init__(self, self)
    
    self.connect(host, port, client_id)
    
    thread = Thread(target=self.run)
    thread.start()
    
  # Callback override fn Error from EWrapper
  def error(self, req_id, code, msg, misc):
    if code in [2104, 2106, 2158]:
      print(msg)
    else:
      print('Error {}: {}'.format(code, msg)) 
      chart.spinner(False)


  def nextValidId(self, orderId: int):
    super().nextValidId(orderId)
    self.orderId = orderId
    print(f"next valid id is {self.orderId}")


  # callback to log order status, we can put more behavior here if needed
  def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
    print(f"order status {orderId} {status} {filled} {remaining} {avgFillPrice}")   


  # Callback Override
  def historicalData(self, reqId: int, bar: BarData):
    print(bar)
    t= datetime.datetime.fromtimestamp(int(bar.date))
    # creation bar dictionary for each bar received
    data = {
        'date': t,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': int(bar.volume)
    }
    # print(data)
    # Put the data into the queue
    data_queue.put(data)
    
    
  def historicalDataEnd(self, reqId: int, start: str, end: str):
    print(f"End of data {start} {end}")
    updateChart()
    
  # callback for when a scan finishes
  def scannerData(self, req_id, rank, details, distance, benchmark, projection, legsStr):
    super().scannerData(req_id, rank, details, distance, benchmark, projection, legsStr)
    print("got scanner data")
    print(details.contract)

    data = {
        'secType': details.contract.secType,
        'secId': details.contract.secId,
        'exchange': details.contract.primaryExchange,
        'symbol': details.contract.symbol
    }

    # print(data)
    
    # Put the data into the queue
    data_queue.put(data)  
### End IBClient


  # callback for when the user changes the position of the horizontal line
def on_horizontal_line_move(chart, line):
  print(f'Horizontal line moved to: {line.price}')

def onSearch(chart: Chart, searched_string):
  getBarData(searched_string, chart.topbar['timeframe'].value) 
  chart.topbar['symbol'].set(searched_string)

  
def onTimeframeChange(chart: Chart):
  print("Changed timeframe")
  print(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)
  getBarData(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)

def onScreenshot(key):
  img= chart.screenshot()
  t=time.time()
  symbol = chart.topbar['symbol'].value
  os.makedirs(f"screenshots/{symbol}", exist_ok=True)  # succeeds even if directory exists.

  chart_filename = f"screenshots/{symbol}/screentshot-{t}.png"
  analysis_filename = f"screenshots/{symbol}/screentshot-{t}.md"
  with open(chart_filename, "wb") as f:
    f.write(img)
    
  
  analysis = analyze_chart(chart_filename)
  print(analysis)
  
  with open(analysis_filename, "w") as text_file:
      text_file.write(analysis)

### Retrieve Info
def getBarData(symbol, timeframe):
  contract = Contract()
  contract.symbol = symbol
  contract.secType = 'STK'
  contract.exchange = 'SMART'
  contract.currency = 'USD'
  
  print(f"Get bar data for {symbol} {timeframe}")
  
  chart.spinner(True)
  client.reqHistoricalData(2, contract, '', '30 D', timeframe, WHAT_TO_SHOW, True, 2, False, [])
  chart.watermark(symbol)
  

# Consume los datos de la cola. Cuando acaba, lo transforma en un dataframe para manipularlo.
def updateChart():

  try: 
    bars = []
    while True: # Keep checking the queue for new data
      data = data_queue.get_nowait()
      bars.append(data)
  except queue.Empty:
    print("Empty queue, no more data")
  finally: 
    df = pd.DataFrame(bars)
    print(df)
    if not (df.empty):
      chart.set(df)
      printHorizontalLine(df)
      printMovingAverageLine(df)

    # once we get the data back, we don't need a spinner anymore
    chart.spinner(False)
    
def printHorizontalLine(df): 
  chart.horizontal_line(df['high'].max(), func=on_horizontal_line_move)
  

def printMovingAverageLine(df):
  # if there were any indicator lines on the chart already (eg. SMA), clear them so we can recalculate
  if current_lines:
    for line in current_lines:
      line.delete()
  
  # calculate any new lines to render
  # create a line with SMA label on the chart
  line = chart.create_line(name='SMA 50')
  line.set(pd.DataFrame({
      'time': df['date'],
      f'SMA 50': df['close'].rolling(window=50).mean()
  }).dropna())
  current_lines.append(line)


def getContract(symbol):
  contract = Contract()
  contract.symbol = symbol
  contract.secType = 'STK'
  contract.exchange = 'SMART'
  contract.currency = 'USD'
  
  return contract

# handles when the user uses an order hotkey combination
def onPlaceOrder(key):
  symbol = chart.topbar['symbol'].value
  
  # Build contract object
  contract = getContract(symbol)
  
  # build order object
  order = Order()
  order.orderType = "MKT"
  order.totalQuantity = 1
  
  # get next order id
  client.reqIds(-1)
  time.sleep(1)
  
  # set action to buy or sell depending on key pressed
  # shift+O is for a buy order
  if (key == 'O'):
    print("Buy Order")
    order.action = "BUY"
  
  # shift+P is for a sell order
  if (key == 'P'):
    print("Sell Order")
    order.action = "SELL"
    
  ## Place the order
  if client.orderId:
    print("got orderId, placiong buy order")
    client.placeOrder(client.orderId, contract, order)
  

# implement an Interactive Brokers market scanner
def doScan(scan_code):
    scannerSubscription = ScannerSubscription()
    scannerSubscription.instrument = "STK"
    scannerSubscription.locationCode = "STK.US.MAJOR"
    scannerSubscription.scanCode = scan_code

    tagValues = []
    tagValues.append(TagValue("optVolumeAbove", "1000"))
    tagValues.append(TagValue("avgVolumeAbove", "10000"))

    client.reqScannerSubscription(7002, scannerSubscription, [], tagValues)
    time.sleep(1)

    displayScan()

    client.cancelScannerSubscription(7002)
    

# called when we want to render scan results
def displayScan():
  # create a table on the UI, pass callback function for when a row is clicked
  def on_row_click(row):
    chart.topbar['symbol'].set(row['symbol'])
    getBarData(row['symbol'], '5 mins')

  table = chart.create_table(
                  width=0.4, 
                  height=0.5,
                  headings=('symbol', 'value'),
                  widths=(0.7, 0.3),
                  alignments=('left', 'center'),
                  position='left', 
                  func=on_row_click
              )
  # poll queue for any new scan results
  try:
    while True:
      data = data_queue.get_nowait()
      # create a new row in the table for each scan result
      table.new_row(data['symbol'], '')
  except queue.Empty:
      print("empty queue")
  finally:
      print("done")



### Main
if __name__ == '__main__':

  client = IBClient(DEFAULT_HOST, TRADING_PORT, DEFAULT_CLIENT_ID)
  chart = ChartWrapper.initChart(INITIAL_SYMBOL, onSearch, onTimeframeChange, onScreenshot, onPlaceOrder)
  current_lines = []
  
  # contract = getContract(INITIAL_SYMBOL)
  getBarData(INITIAL_SYMBOL, '5 mins')  
  
  # run a market scanner
  time.sleep(2)
  doScan("HOT_BY_VOLUME")

  
  chart.show(block=True)
