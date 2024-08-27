# IB Trading Bot

Este proyecto es un bot de trading desarrollado en Python, que se conecta a la API de Interactive Brokers (IB) para realizar análisis de datos históricos, ejecutar órdenes y realizar escaneos de mercado. El bot también ofrece una interfaz gráfica para visualizar datos y realizar interacciones con gráficos.

## Funcionalidades

### 1. Conexión a Interactive Brokers (IB)
El programa se conecta a Interactive Brokers utilizando la clase `IBClient`, que extiende `EClient` y `EWrapper` para enviar solicitudes y manejar mensajes recibidos de la API de IB. Esta conexión puede configurarse para operar en modo de trading en papel (Paper Trading) o en vivo (Live Trading).

- **Parámetros de conexión**:
  - `DEFAULT_HOST`: Dirección del servidor IB.
  - `DEFAULT_CLIENT_ID`: ID del cliente para identificar la sesión.
  - `PAPER_TRADING_PORT`: Puerto para conexión en modo Paper Trading.
  - `LIVE_TRADING_PORT`: Puerto para conexión en modo Live Trading.
  - `LIVE_TRADING`: Booleano que define si se utiliza Paper Trading o Live Trading.

### 2. Recuperación de Datos Históricos
El bot permite recuperar datos históricos para un símbolo específico, los cuales se procesan y se muestran en un gráfico.

- **Funciones clave**:
  - `getBarData(symbol, timeframe)`: Solicita datos históricos para un símbolo y un marco temporal específico.
  - `historicalData`: Callback que procesa y guarda los datos recibidos en una cola.
  - `updateChart()`: Consume los datos de la cola, los transforma en un DataFrame de pandas y los muestra en un gráfico.

### 3. Visualización y Análisis de Gráficos
El bot cuenta con una interfaz gráfica basada en `lightweight_charts` que permite visualizar datos históricos, agregar líneas de tendencia y realizar análisis técnicos.

- **Características del gráfico**:
  - Línea horizontal movible con callback `on_horizontal_line_move`.
  - Línea de promedio móvil (SMA 50) con la función `printMovingAverageLine(df)`.
  - Captura de pantalla del gráfico y análisis automatizado con `onScreenshot`.

### 4. Ejecución de Órdenes
El bot puede ejecutar órdenes de compra y venta directamente desde la interfaz utilizando combinaciones de teclas.

- **Funciones de ejecución**:
  - `onPlaceOrder(key)`: Maneja la ejecución de órdenes basadas en la tecla presionada. Utiliza `O` para comprar y `P` para vender.
  - `orderStatus`: Callback que registra el estado de la orden.

### 5. Escaneo del Mercado
El bot implementa un escáner de mercado que busca oportunidades de trading basadas en ciertos criterios predefinidos, como volumen y actividad.

- **Funciones de escaneo**:
  - `doScan(scan_code)`: Realiza un escaneo de mercado utilizando un código de escaneo específico.
  - `scannerData`: Callback que procesa los resultados del escaneo y los coloca en la cola.
  - `displayScan()`: Muestra los resultados del escaneo en una tabla interactiva en la interfaz.

### 6. Interfaz Gráfica
La interfaz gráfica permite al usuario interactuar con los datos y realizar acciones directamente desde el gráfico.

- **Componentes de la interfaz**:
  - **Búsqueda de símbolo**: Permite cambiar el símbolo que se visualiza en el gráfico.
  - **Cambio de marco temporal**: Ajusta el marco temporal del gráfico.
  - **Captura y análisis de gráficos**: Captura y analiza gráficamente el estado actual del mercado.

## Instalación y Ejecución

### Requisitos Previos
- Python 3.x
- Paquetes requeridos: `ibapi`, `pandas`, `lightweight_charts`, `gpt4o_technical_analyst`

### Instalación de Paquetes
Puedes instalar los paquetes necesarios utilizando `pip`:

```bash
pip install ibapi pandas lightweight_charts
```

## Ejecución
Para ejecutar el bot de trading, simplemente corre el archivo principal:

```bash
python <nombre_del_archivo>.py
```

## Lineas de trabajo futuro
#### Modulo de Prediccion
- Uso de Modelos de Prediccion de Series Temporales
  - Usar Temporal Relational Ranking for Stock Prediction https://arxiv.org/abs/1809.09441 Git: https://github.com/fulifeng/Temporal_Relational_Stock_Ranking
  - https://builtin.com/data-science/time-series-forecasting-python
  - https://www.quantconnect.com/research/15263/forecasting-stock-prices-using-a-temporal-cnn-model/
- Uso de modelos de lenguaje
-- Usarlo para predecir movimientos alcistas / bajistas y crear limites automaticos con avisos. 
- Live Prediction con PolyMarket (https://www.youtube.com/watch?v=6ny-ZEdQMCc)


#### Modulo de Automatizacion / Avisos
- Añadir backtesting 
- Añadir automatizaciones llegado a cierto umbral 

#### Otros 
- Convert to WebApp (https://www.youtube.com/watch?v=OFnOEIyqSRg&list=PLvzuUVysUFOuoRna8KhschkVVUo2E2g6G)
- Usar QUantComm framework (https://www.youtube.com/watch?v=joXDV5eqOoY&t=2231s)
- 


### Configuración
Puedes configurar el modo de trading (en vivo o en papel) modificando la variable LIVE_TRADING en el archivo principal.

Para más información sobre la API de Interactive Brokers, consulta la documentación oficial.

## Notas
Asegúrate de estar conectado al servidor de IB antes de ejecutar el programa.
La funcionalidad de análisis de gráficos requiere que el módulo gpt4o_technical_analyst esté correctamente instalado y configurado.

## Contribuciones
Las contribuciones son bienvenidas. Si tienes sugerencias o mejoras, no dudes en enviar un pull request.
