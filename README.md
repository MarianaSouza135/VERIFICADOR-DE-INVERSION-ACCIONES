# Verificador de Inversión en Acciones

Este proyecto es una herramienta de línea de comandos desarrollada en Python para analizar acciones y determinar su potencial de inversión basándose en una combinación de análisis fundamental y técnico.

## Características

- **Análisis Multifactorial:** Evalúa acciones utilizando una variedad de métricas financieras y técnicas.
- **Puntuación Ponderada:** Asigna puntuaciones en diferentes categorías (fundamental, dividendos, técnico, etc.) y las pondera para generar un score final.
- **Umbrales por Sector:** Adapta los criterios de valoración según el sector industrial de la empresa.
- **Penalizaciones Dinámicas:** Aplica penalizaciones a la puntuación basadas en "banderas rojas" detectadas en las tendencias históricas (ej. FCF negativo, deuda creciente).
- **Generación de Informes:** Presenta un informe detallado en la consola con un resumen, desglose de puntuaciones y una recomendación final.

## Cómo Usarlo

1.  **Instalar dependencias:** Asegúrate de tener Python instalado y luego instala las librerías necesarias:
    ```bash
    pip install yfinance pandas pandas_ta pytz
    ```

2.  **Ejecutar el script:** Navega al directorio del proyecto y ejecuta el siguiente comando:
    ```bash
    python analizador_acciones.py
    ```

3.  **Analizar una acción:** Cuando el programa te lo pida, introduce el símbolo (ticker) de la acción que deseas analizar (por ejemplo, `AAPL`, `MSFT`, `GOOGL`).

4.  **Salir:** Escribe `salir` para terminar el programa.

## Aviso

Este es un análisis automatizado y no constituye asesoramiento financiero. Los resultados proporcionados por esta herramienta deben ser utilizados únicamente como un punto de partida para tu propia investigación y análisis. Realiza siempre tu propia diligencia debida antes de tomar cualquier decisión de inversión.
