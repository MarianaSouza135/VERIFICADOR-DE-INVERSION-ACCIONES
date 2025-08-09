# Verificador de Inversión en Acciones

Este proyecto es una herramienta de línea de comandos desarrollada en Python para analizar acciones y determinar su potencial de inversión basándose en una combinación de análisis fundamental y técnico.

## Cómo Funciona: El Sistema de Jueces

El script utiliza un sistema de "jueces", donde cada juez es un módulo especializado que evalúa un aspecto diferente de la acción. Las puntuaciones de cada juez se ponderan para calcular una puntuación final.

- **Juez Fundamental:** Analiza la salud financiera de la empresa. Evalúa métricas clave como el PER (Price-to-Earnings), P/B (Price-to-Book), el nivel de Deuda/Capital y el ROE (Return on Equity), comparándolos con umbrales específicos del sector de la empresa.

- **Juez Consistencia Dividendo:** Mide la fiabilidad y la historia del pago de dividendos. Valora positivamente a las empresas con un largo historial de pagos consecutivos y estables.

- **Juez Rendimiento Dividendo:** Evalúa qué tan atractivo es el dividendo en relación con el precio actual de la acción (Dividend Yield). Una mayor rentabilidad obtiene una mejor puntuación.

- **Juez Crecimiento Dividendo:** Analiza la tasa a la que la empresa ha aumentado sus dividendos a lo largo del tiempo (CAGR). Un crecimiento sólido y sostenible es un indicador positivo.

- **Juez Crecimiento General:** Mide el crecimiento de los ingresos (revenue) de la empresa, un indicador clave de la expansión del negocio.

- **Juez Técnico (Oportunidad):** Evalúa el "timing" de la inversión desde un punto de vista técnico. Analiza indicadores como el RSI (Relative Strength Index) para detectar condiciones de sobreventa/sobrecompra y la posición del precio respecto a sus medias móviles (SMA 50, SMA 200) para determinar la tendencia.

## Cómo Usarlo

1.  **Instalar dependencias:** Asegúrate de tener Python instalado y luego instala las librerías necesarias:
    ```bash
    pip install yfinance pandas pandas_ta pytz
    ```

2.  **Ejecutar el script:** Navega al directorio del proyecto y ejecuta el siguiente comando:
    ```bash
    python analizador_acciones.py
    ```

3.  **Analizar una acción:** Cuando el programa te lo pida, introduce el símbolo (ticker) de la acción que deseas analizar.

4.  **Salir:** Escribe `salir` para terminar el programa.

### Nota Importante sobre Tickers Internacionales

Para analizar acciones de bolsas fuera de Estados Unidos, necesitas añadir el sufijo correspondiente al ticker, según el formato de Yahoo Finance. Por ejemplo:

-   **Bolsa de Toronto (Canadá):** `TD.TO` (para Toronto-Dominion Bank)
-   **Bolsa de Frankfurt (Alemania):** `ADS.DE` (para Adidas)
-   **Bolsa de Londres (Reino Unido):** `ULVR.L` (para Unilever)

Puedes buscar el ticker correcto en [Yahoo Finance](https://finance.yahoo.com/).

## Aviso

Este es un análisis automatizado y no constituye asesoramiento financiero. Los resultados proporcionados por esta herramienta deben ser utilizados únicamente como un punto de partida para tu propia investigación y análisis. Realiza siempre tu propia diligencia debida antes de tomar cualquier decisión de inversión.