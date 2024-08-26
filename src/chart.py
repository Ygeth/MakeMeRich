from lightweight_charts import Chart

### Chart Section
def initChart(symbol, onSearchFn, onTimeframeChangeFn, onScreenshotFn, onPlaceOrderFn):
  ## Chart init
  chart = Chart(toolbox=True, width=1000, inner_width=0.6, inner_height=1)
  chart.legend(True)
  
  # Topbar
  chart.topbar.textbox('symbol', symbol)
  chart.topbar.switcher('timeframe', ('15 mins', '1 hour', '1 day'), default='1 hour', 
                        func=onTimeframeChangeFn)
  chart.topbar.button('screenshot', 'Screenshot', func=onScreenshotFn)

  # set up a function to call when searching for symbol
  chart.events.search += onSearchFn
  
  # HotKeys
  # hotkey to place a buy order
  chart.hotkey('shift', 'O', onPlaceOrderFn)

  # hotkey to place a sell order
  chart.hotkey('shift', 'P', onPlaceOrderFn)
  return chart

