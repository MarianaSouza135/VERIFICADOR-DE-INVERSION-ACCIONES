# Stock Analysis Tool

A command-line tool developed in Python to analyze stocks and determine their investment potential based on a combination of fundamental and technical analysis.

---
*Read this in other languages: [English](#stock-analysis-tool), [Español](#herramienta-de-análisis-de-acciones)*

## How it Works: The Factor-Based Scoring System

The script uses a "judge" system, where each judge is a specialized module that evaluates a different aspect of the stock. The scores from each judge are weighted to calculate a final score.

-   **Fundamental Judge:** Analyzes the company's financial health. It evaluates key metrics like P/E (Price-to-Earnings), P/B (Price-to-Book), Debt-to-Equity ratio, and ROE (Return on Equity), comparing them against sector-specific thresholds.

-   **Dividend Consistency Judge:** Measures the reliability and history of dividend payments. It favors companies with a long track record of consecutive and stable payments.

-   **Dividend Yield Judge:** Assesses the attractiveness of the dividend relative to the current stock price. A higher yield gets a better score.

-   **Dividend Growth Judge:** Analyzes the rate at which the company has increased its dividends over time (CAGR). Solid and sustainable growth is a positive indicator.

-   **Overall Growth Judge:** Measures the company's revenue growth, a key indicator of business expansion.

-   **Technical (Timing) Judge:** Evaluates the investment's timing from a technical standpoint. It analyzes indicators like the RSI (Relative Strength Index) to detect overbought/oversold conditions and the price's position relative to its moving averages (SMA 50, SMA 200) to determine the trend.

## How to Use

1.  **Install dependencies:** Make sure you have Python installed, then navigate to the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the script:**
    ```bash
    python analizador_acciones.py
    ```

3.  **Analyze a stock:** When prompted, enter the stock ticker you want to analyze.

4.  **Exit:** Type `salir` to exit the program.

### Important Note on International Tickers

To analyze stocks from exchanges outside the US, you need to add the corresponding suffix to the ticker, according to the Yahoo Finance format. For example:

-   **Toronto Stock Exchange (Canada):** `TD.TO` (for Toronto-Dominion Bank)
-   **Frankfurt Stock Exchange (Germany):** `ADS.DE` (for Adidas)
-   **London Stock Exchange (UK):** `ULVR.L` (for Unilever)

You can look up the correct ticker on [Yahoo Finance](https://finance.yahoo.com/).

## Disclaimer

This is an automated analysis and does not constitute financial advice. The results provided by this tool should be used solely as a starting point for your own research and analysis. Always perform your own due diligence before making any investment decisions.

---

# Herramienta de Análisis de Acciones

Una herramienta de línea de comandos desarrollada en Python para analizar acciones y determinar su potencial de inversión basándose en una combinación de análisis fundamental y técnico.

## Cómo Funciona: El Sistema de Jueces

El script utiliza un sistema de "jueces", donde cada juez es un módulo especializado que evalúa un aspecto diferente de la acción. Las puntuaciones de cada juez se ponderan para calcular una puntuación final.

-   **Juez Fundamental:** Analiza la salud financiera de la empresa. Evalúa métricas clave como el PER (Price-to-Earnings), P/B (Price-to-Book), el nivel de Deuda/Capital y el ROE (Return on Equity), comparándolos con umbrales específicos del sector de la empresa.

-   **Juez Consistencia Dividendo:** Mide la fiabilidad y la historia del pago de dividendos. Valora positivamente a las empresas con un largo historial de pagos consecutivos y estables.

-   **Juez Rendimiento Dividendo:** Evalúa qué tan atractivo es el dividendo en relación con el precio actual de la acción (Dividend Yield). Una mayor rentabilidad obtiene una mejor puntuación.

-   **Juez Crecimiento Dividendo:** Analiza la tasa a la que la empresa ha aumentado sus dividendos a lo largo del tiempo (CAGR). Un crecimiento sólido y sostenible es un indicador positivo.

-   **Juez Crecimiento General:** Mide el crecimiento de los ingresos (revenue) de la empresa, un indicador clave de la expansión del negocio.

-   **Juez Técnico (Oportunidad):** Evalúa el "timing" de la inversión desde un punto de vista técnico. Analiza indicadores como el RSI (Relative Strength Index) para detectar condiciones de sobreventa/sobrecompra y la posición del precio respecto a sus medias móviles (SMA 50, SMA 200) para determinar la tendencia.

## Cómo Usarlo

1.  **Instalar dependencias:** Asegúrate de tener Python instalado, luego navega al directorio del proyecto y ejecuta:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Ejecutar el script:**
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
