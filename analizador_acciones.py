import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import pytz
import time
import logging

# ==============================================================================
# SECCIÓN 0: CONFIGURACIÓN DE LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==============================================================================
# SECCIÓN 1: CONSTANTES Y CONFIGURACIONES GLOBALES
# ==============================================================================
PONDERACION_FUNDAMENTAL = 0.35
PONDERACION_CONSISTENCIA_DIV = 0.20
PONDERACION_RENDIMIENTO_DIV = 0.15
PONDERACION_CRECIMIENTO_DIV = 0.10
PONDERACION_CRECIMIENTO_GENERAL = 0.10
PONDERACION_CONFIANZA_MGMT = 0.05
PONDERACION_TECNICA = 0.05
SECTORES_CICLICOS = ['Energy', 'Basic Materials', 'Industrials', 'Consumer Cyclical']
UMBRALES_POR_SECTOR = {
    'Technology': {'PE_BAJO': 20, 'PE_ALTO': 40, 'DEUDA_BAJA': 0.5, 'DEUDA_ALTA': 1.0, 'PB_BUENO': 5.0, 'PB_ALTO': 10.0},
    'Financial Services': {'PE_BAJO': 8, 'PE_ALTO': 15, 'DEUDA_BAJA': 1.0, 'DEUDA_ALTA': 2.5, 'PB_BUENO': 1.0, 'PB_ALTO': 1.5},
    'Healthcare': {'PE_BAJO': 18, 'PE_ALTO': 30, 'DEUDA_BAJA': 0.4, 'DEUDA_ALTA': 0.8, 'PB_BUENO': 4.0, 'PB_ALTO': 7.0},
    'Utilities': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 1.0, 'DEUDA_ALTA': 2.0, 'PB_BUENO': 1.5, 'PB_ALTO': 2.5, 'PAYOUT_ALTO_ACEPTABLE': 0.85},
    'Energy': {'PE_BAJO': 5, 'PE_ALTO': 12, 'DEUDA_BAJA': 0.3, 'DEUDA_ALTA': 1.0, 'PB_BUENO': 1.0, 'PB_ALTO': 2.0},
    'Basic Materials': {'PE_BAJO': 10, 'PE_ALTO': 20, 'DEUDA_BAJA': 0.3, 'DEUDA_ALTA': 0.7, 'PB_BUENO': 1.5, 'PB_ALTO': 3.0},
    'Industrials': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 0.5, 'DEUDA_ALTA': 1.0, 'PB_BUENO': 2.0, 'PB_ALTO': 4.0},
    'Consumer Cyclical': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 0.4, 'DEUDA_ALTA': 0.8, 'PB_BUENO': 2.5, 'PB_ALTO': 5.0},
    'Consumer Defensive': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 0.4, 'DEUDA_ALTA': 0.7, 'PB_BUENO': 2.5, 'PB_ALTO': 5.0},
    'Real Estate': {'PE_BAJO': 15, 'PE_ALTO': 30, 'DEUDA_BAJA': 0.6, 'DEUDA_ALTA': 1.5, 'PB_BUENO': 1.0, 'PB_ALTO': 2.0, 'PAYOUT_ALTO_ACEPTABLE': 0.90},
    'Communication Services': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 0.5, 'DEUDA_ALTA': 1.5, 'PB_BUENO': 2.0, 'PB_ALTO': 4.0},
    'default': {'PE_BAJO': 15, 'PE_ALTO': 25, 'DEUDA_BAJA': 0.4, 'DEUDA_ALTA': 0.7, 'PB_BUENO': 2.0, 'PB_ALTO': 4.0}
}
RSI_SOBREVENTA, RSI_SOBRECOMPRA = 30, 70
ROE_UMBRAL_BUENO, ROE_UMBRAL_ACEPTABLE = 0.15, 0.10
FACTORES_PENALIZACION_ADAPTATIVOS = {
    "beneficios_negativos": [{"umbral": 2, "factor": 0.80, "razon": "Beneficios negativos en >=2 de 5 anos (Critico)"}],
    "fcf_negativo": [{"umbral": 2, "factor": 0.90, "razon": "FCF negativo en >=2 de 5 anos (Grave)"}],
    "dividendo_crecimiento_maduro": [
        {"umbral": -0.01, "factor": 0.85, "razon": "Dividendo decreciente en empresa madura (Grave)"},
        {"umbral": 0.01, "factor": 0.97, "razon": "Dividendo estancado en empresa madura (Leve)"}
    ],
    "ingresos_crecimiento": [{"umbral": 0, "factor": 0.95, "razon": "Crecimiento de ingresos negativo (CAGR 5 anos < 0) (Moderado)"}],
    "roe": [{"umbral": ROE_UMBRAL_ACEPTABLE, "factor": 0.94, "razon": f"Baja rentabilidad promedio (ROE 5 anos < {ROE_UMBRAL_ACEPTABLE:.0%}) (Moderado)"}],
    "deuda": [{"umbral": "tendencia_creciente", "factor": 0.95, "razon": "Tendencia de deuda creciente en 5 anos (Moderado)"}]
}
CAGR_YEARS = 5
pd.set_option('future.no_silent_downcasting', True)


# ==============================================================================
# SECCIÓN 2: CLASE PRINCIPAL DEL ANALIZADOR
# ==============================================================================
class AnalizadorAccion:
    def __init__(self, simbolo):
        self.simbolo = simbolo
        self.datos_completos = None
        self.info = {}
        self.tendencias = {}
        self.hist_indicadores = None
        self.scores = {}
        self.probabilidad_base = 0
        self.factor_penalizacion = 1.0
        self.razones_penalizacion = {}
        self.probabilidad_ajustada = 0
        self._cargar_datos()

    def _cargar_datos(self):
        logging.info(f"Iniciando análisis para {self.simbolo}...")
        self.datos_completos = self._obtener_datos_accion()
        if self.datos_completos:
            self.info = self.datos_completos.get('info', {})
            self.tendencias = self._analizar_tendencias_historicas()
            self.hist_indicadores = self._calcular_indicadores_tecnicos()

    def _obtener_datos_accion(self):
        logging.info(f"Obteniendo datos de yfinance para {self.simbolo}...")
        try:
            stock = yf.Ticker(self.simbolo)
            info = stock.info
            if not info or info.get('marketCap') is None:
                logging.warning(f"No se encontró información válida para {self.simbolo}. Se omite.")
                return None
            precios_hist = stock.history(period='1y', auto_adjust=True)
            if precios_hist.empty:
                logging.warning(f"No se pudieron obtener precios históricos para {self.simbolo}.")
                return None
            return {
                'info': info, 'dividendos': stock.dividends,
                'precios_historicos': precios_hist, 'precio_actual': precios_hist['Close'].iloc[-1],
                'nombre': info.get('longName', 'N/A'), 'sector': info.get('sector', 'N/A'),
                'financials': stock.financials, 'balance_sheet': stock.balance_sheet, 'cashflow': stock.cashflow
            }
        except Exception as e:
            logging.error(f"Error crítico obteniendo datos para {self.simbolo}: {e}")
            return None

    def _analizar_tendencias_historicas(self):
        tendencias = {}
        financials = self.datos_completos.get('financials')
        cashflow = self.datos_completos.get('cashflow')
        balance_sheet = self.datos_completos.get('balance_sheet')
        dividendos = self.datos_completos.get('dividendos')
        if any(df is None or df.empty for df in [financials, cashflow, balance_sheet]):
            return tendencias
        try:
            financials_t = financials.iloc[:, :4]
            cashflow_t = cashflow.iloc[:, :4]
            balance_sheet_t = balance_sheet.iloc[:, :4]
            if 'Net Income' in financials_t.index: tendencias['anios_eps_neg'] = (financials_t.loc['Net Income'].fillna(0) < 0).sum()
            if 'Total Cash From Operating Activities' in cashflow_t.index and 'Capital Expenditures' in cashflow_t.index:
                fcf = cashflow_t.loc['Total Cash From Operating Activities'].fillna(0) - cashflow_t.loc['Capital Expenditures'].fillna(0)
                tendencias['anios_fcf_neg'] = (fcf < 0).sum()
            if 'Net Income' in financials_t.index and 'Total Stockholder Equity' in balance_sheet_t.index:
                net_income_roe = financials_t.loc['Net Income'].fillna(0)
                equity = balance_sheet_t.loc['Total Stockholder Equity'].replace(0, pd.NA).ffill().bfill()
                if not equity.empty and equity.notna().all(): tendencias['roe_promedio_5a'] = (net_income_roe / equity).mean()
            if 'Total Revenue' in financials_t.index:
                ingresos = financials_t.loc['Total Revenue'].dropna()
                if len(ingresos) > 1 and ingresos.iloc[-1] > 0: tendencias['ingresos_cagr_5a'] = ((ingresos.iloc[0] / ingresos.iloc[-1])**(1/len(ingresos))) - 1
            if 'Total Liab' in balance_sheet_t.index:
                deuda_total = balance_sheet_t.loc['Total Liab'].dropna()
                if len(deuda_total) > 1: tendencias['deuda_creciente'] = deuda_total.iloc[0] > deuda_total.iloc[-1]
            if dividendos is not None and not dividendos.empty:
                dividendos_anuales = dividendos.resample('YE').sum()
                dividendos_anuales = dividendos_anuales[dividendos_anuales > 0]
                tendencias['dividendos_anuales_data'] = dividendos_anuales
                anios_con_pago = sorted(pd.to_datetime(dividendos.index.normalize()).year.unique(), reverse=True)
                anios_consecutivos = 0
                if anios_con_pago and anios_con_pago[0] >= datetime.now().year - 1:
                    for i, anio in enumerate(anios_con_pago):
                        if anio == anios_con_pago[0] - i: anios_consecutivos += 1
                        else: break
                tendencias['anios_consecutivos_dividendo'] = anios_consecutivos
            else:
                tendencias['anios_consecutivos_dividendo'] = 0
        except (KeyError, IndexError) as e:
            logging.warning(f"Falta la métrica histórica '{e}' para {self.simbolo}.")
        return tendencias

    def _calcular_indicadores_tecnicos(self):
        hist_df = self.datos_completos.get('precios_historicos')
        if hist_df is None or len(hist_df) < 26: return None
        try:
            df_copy = hist_df.copy()
            df_copy.ta.sma(length=50, append=True); df_copy.ta.sma(length=200, append=True)
            df_copy.ta.rsi(append=True); df_copy.ta.macd(append=True)
            for col in ['SMA_50', 'SMA_200', 'RSI_14', 'MACDh_12_26_9']:
                if col not in df_copy.columns: df_copy[col] = pd.NA
            return df_copy
        except Exception as e:
            logging.error(f"No se pudieron calcular los indicadores técnicos para {self.simbolo}: {e}")
            return None

    def _calcular_puntuacion_tecnica(self):
        puntuaciones, razones = [], []
        if self.hist_indicadores is None or self.hist_indicadores.empty:
            return 50.0, ["No hay datos técnicos suficientes para analizar."]
        ultimo = self.hist_indicadores.iloc[-1]
        precio_actual = self.datos_completos.get('precio_actual', 0)
        rsi = ultimo.get('RSI_14'); macd_hist = ultimo.get('MACDh_12_26_9')
        sma50 = ultimo.get('SMA_50'); sma200 = ultimo.get('SMA_200')
        if pd.notna(rsi):
            if rsi < RSI_SOBREVENTA: puntuaciones.append(100); razones.append(f"RSI ({rsi:.1f}) en sobreventa, posible rebote.")
            elif rsi > RSI_SOBRECOMPRA: puntuaciones.append(0); razones.append(f"RSI ({rsi:.1f}) en sobrecompra, posible corrección.")
            else: puntuaciones.append(100 - (rsi - RSI_SOBREVENTA) * 100 / (RSI_SOBRECOMPRA - RSI_SOBREVENTA)); razones.append(f"RSI ({rsi:.1f}) en zona neutral.")
        if pd.notna(macd_hist):
            puntuaciones.append(90 if macd_hist > 0 else 10)
            razones.append("Histograma MACD positivo, señal alcista." if macd_hist > 0 else "Histograma MACD negativo, señal bajista.")
        puntuacion_sma = 50
        if pd.notna(precio_actual) and pd.notna(sma50) and pd.notna(sma200):
            if sma50 > sma200 and precio_actual > sma50: puntuacion_sma = 100; razones.append("Tendencia alcista fuerte (Precio > SMA50 > SMA200).")
            elif sma50 < sma200 and precio_actual < sma50: puntuacion_sma = 0; razones.append("Tendencia bajista fuerte (Precio < SMA50 < SMA200).")
            elif precio_actual > sma50 and precio_actual > sma200: puntuacion_sma = 85; razones.append("Tendencia general alcista (Precio > ambas SMAs).")
            elif precio_actual < sma50 and precio_actual < sma200: puntuacion_sma = 15; razones.append("Tendencia general bajista (Precio < ambas SMAs).")
            else: razones.append("Medias móviles en conflicto o cruzándose.")
        puntuaciones.append(puntuacion_sma)
        score = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 50.0
        return score, razones

    def _calcular_puntuacion_fundamental(self):
        puntuaciones, razones = [], []
        if not self.info: return 0.0, ["No hay datos fundamentales disponibles."]
        sector = self.info.get('sector', 'N/A')
        umbrales = UMBRALES_POR_SECTOR.get(sector, UMBRALES_POR_SECTOR['default'])
        def to_float(v): return float(v) if v is not None else None
        pe = to_float(self.info.get('trailingPE'))
        if pe and pe > 0: 
            if pe < umbrales['PE_BAJO']: puntuaciones.append(100); razones.append(f"PER ({pe:.1f}) bajo para el sector.")
            elif pe <= umbrales['PE_ALTO']: puntuaciones.append(75); razones.append(f"PER ({pe:.1f}) aceptable para el sector.")
            else: puntuaciones.append(25); razones.append(f"PER ({pe:.1f}) alto para el sector.")
        else: puntuaciones.append(0); razones.append("PER negativo o no disponible.")
        pb = to_float(self.info.get('priceToBook'))
        if pb and pb > 0:
            if pb < umbrales['PB_BUENO']: puntuaciones.append(100); razones.append(f"P/B ({pb:.1f}) bajo, posible infravaloración.")
            elif pb <= umbrales['PB_ALTO']: puntuaciones.append(50); razones.append(f"P/B ({pb:.1f}) normal para el sector.")
            else: puntuaciones.append(0); razones.append(f"P/B ({pb:.1f}) alto, posible sobrevaloración.")
        else: puntuaciones.append(50); razones.append("P/B no disponible.")
        deuda_ratio = to_float(self.info.get('debtToEquity'))
        if deuda_ratio is not None:
            deuda_ratio /= 100
            if deuda_ratio < umbrales['DEUDA_BAJA']: puntuaciones.append(100); razones.append(f"Deuda/Capital ({deuda_ratio:.1%}) muy baja.")
            elif deuda_ratio <= umbrales['DEUDA_ALTA']: puntuaciones.append(75); razones.append(f"Deuda/Capital ({deuda_ratio:.1%}) manejable.")
            else: puntuaciones.append(0); razones.append(f"Deuda/Capital ({deuda_ratio:.1%}) alta.")
        else: puntuaciones.append(50); razones.append("Ratio Deuda/Capital no disponible.")
        roe = to_float(self.info.get('returnOnEquity'))
        if roe is not None:
            if roe > ROE_UMBRAL_BUENO: puntuaciones.append(100); razones.append(f"ROE ({roe:.1%}) excelente, alta rentabilidad.")
            elif roe > ROE_UMBRAL_ACEPTABLE: puntuaciones.append(75); razones.append(f"ROE ({roe:.1%}) aceptable.")
            else: puntuaciones.append(25); razones.append(f"ROE ({roe:.1%}) bajo.")
        else: puntuaciones.append(25); razones.append("ROE no disponible.")
        payout = to_float(self.info.get('payoutRatio'))
        payout_aceptable = umbrales.get('PAYOUT_ALTO_ACEPTABLE', 0.8)
        if payout is not None:
            if 0 < payout <= 0.6: puntuaciones.append(100); razones.append(f"Payout Ratio ({payout:.1%}) bajo y sostenible.")
            elif payout <= payout_aceptable: puntuaciones.append(75); razones.append(f"Payout Ratio ({payout:.1%}) aceptable.")
            else: puntuaciones.append(0); razones.append(f"Payout Ratio ({payout:.1%}) alto o negativo.")
        else: puntuaciones.append(50); razones.append("Payout Ratio no disponible.")
        score = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0.0
        return score, razones

    def _score_rendimiento(self, rendimiento):
        if rendimiento is None or pd.isna(rendimiento) or rendimiento <= 0: return 0.0, ["No paga dividendos o no hay datos."]
        razon = f"Rendimiento por dividendo del {rendimiento:.2f}%"
        if rendimiento >= 4.5: return 100.0, [razon + " (Excelente)"]
        if rendimiento >= 2.5: return 50.0 + (rendimiento - 2.5) * 25.0, [razon + " (Bueno)"]
        return rendimiento * 20.0, [razon + " (Bajo)"]

    def _score_crecimiento_div(self, crecimiento, anios_consecutivos):
        sector = self.info.get('sector', 'N/A')
        if sector in SECTORES_CICLICOS: return 50.0, ["Crecimiento no prioritario en sector cíclico."]
        if anios_consecutivos < 2: return 50.0, ["No hay historial suficiente para evaluar crecimiento."]
        if crecimiento is None or pd.isna(crecimiento): return 25.0, ["No se pudo calcular el crecimiento del dividendo."]
        razon = f"Crecimiento del dividendo (CAGR {CAGR_YEARS}a) del {crecimiento:.2f}%"
        if crecimiento >= 8.0: return 100.0, [razon + " (Excelente)"]
        elif crecimiento >= 4.0: return 75.0, [razon + " (Bueno)"]
        elif crecimiento >= 0: return 50.0, [razon + " (Estable)"]
        else: return 0.0 if anios_consecutivos >= 5 else 25.0, [razon + " (Negativo)"]

    def _evaluar_historial_pagos_div(self):
        anios = self.tendencias.get('anios_consecutivos_dividendo', 0)
        if anios >= 10: return 100.0, [f"{anios} años de dividendos. Un historial muy sólido."]
        elif anios >= 5: return 75.0, [f"{anios} años de dividendos. Un buen historial."]
        elif anios > 0: return 25.0, [f"{anios} años de dividendos. Historial corto."]
        else: return 0.0, ["No hay un historial reciente de pago de dividendos."]

    def _calcular_rendimiento_dividendos(self):
        dividendos = self.datos_completos.get('dividendos')
        precio_actual = self.datos_completos.get('precio_actual', 0)
        if dividendos is None or dividendos.empty or precio_actual <= 0: return None
        hace_un_anio = pd.Timestamp.now(tz=pytz.utc) - timedelta(days=365)
        try:
            if dividendos.index.tz is None: dividendos.index = dividendos.index.tz_localize('UTC')
            total_dividendos = dividendos[dividendos.index >= hace_un_anio].sum()
            return (total_dividendos / precio_actual) * 100
        except Exception: return None

    def _calcular_crecimiento_dividendos(self, num_anios_cagr=CAGR_YEARS):
        if self.tendencias.get('anios_consecutivos_dividendo', 0) < 2: return None
        try:
            dividendos_anuales = self.tendencias.get('dividendos_anuales_data')
            if dividendos_anuales is None or len(dividendos_anuales) < 2: return None
            ultimo_anio_completo = datetime.now().year - 1
            if dividendos_anuales.index.year.max() > ultimo_anio_completo:
                 dividendos_anuales = dividendos_anuales[dividendos_anuales.index.year <= ultimo_anio_completo]
            if len(dividendos_anuales) < 2: return None
            num_anios_a_usar = min(num_anios_cagr, len(dividendos_anuales))
            div_recientes = dividendos_anuales.tail(num_anios_a_usar)
            if len(div_recientes) < 2: return None
            dividendo_inicio, dividendo_fin = div_recientes.iloc[0], div_recientes.iloc[-1]
            num_periodos = div_recientes.index.year[-1] - div_recientes.index.year[0]
            if dividendo_inicio <= 0 or num_periodos <= 0: return None
            return (((dividendo_fin / dividendo_inicio)**(1 / num_periodos)) - 1) * 100
        except Exception as e:
            logging.error(f"Error calculando CAGR de dividendos para {self.simbolo}: {e}")
            return None

    def _score_crecimiento_general(self):
        crecimiento = self.info.get('revenueGrowth')
        if crecimiento is None: return 50.0, ["Crecimiento de ingresos no disponible."]
        razon = f"Crecimiento de ingresos (interanual) del {crecimiento:.1%}"
        if crecimiento >= 0.05: return 100.0, [razon + " (Sólido)"]
        elif crecimiento >= 0.01: return 75.0, [razon + " (Moderado)"]
        else: return 25.0, [razon + " (Bajo o negativo)"]

    def _score_confianza_management(self): 
        return 50.0, ["Puntuación neutral. Requiere análisis cualitativo de la directiva."]

    def _calcular_penalizacion_dinamica(self):
        factor_total = 1.0; razones = {}
        sector = self.info.get('sector', 'N/A')
        if not self.tendencias: return 1.0, {}
        if self.tendencias.get('anios_eps_neg', 0) >= 2:
            p = FACTORES_PENALIZACION_ADAPTATIVOS["beneficios_negativos"][0]; factor_total *= p["factor"]; razones["Beneficios"] = (p["razon"], p["factor"])
        if self.tendencias.get('anios_fcf_neg', 0) >= 2:
            p = FACTORES_PENALIZACION_ADAPTATIVOS["fcf_negativo"][0]; factor_total *= p["factor"]; razones["FCF"] = (p["razon"], p["factor"])
        if sector not in SECTORES_CICLICOS:
            crecimiento_div_raw = self.scores.get('crecimiento_div_raw')[0]
            anios_consecutivos = self.tendencias.get('anios_consecutivos_dividendo', 0)
            if crecimiento_div_raw is not None:
                if anios_consecutivos >= 5:
                    for p in FACTORES_PENALIZACION_ADAPTATIVOS["dividendo_crecimiento_maduro"]:
                        if crecimiento_div_raw < p["umbral"]:
                            factor_total *= p["factor"]; razones["Crec. Div."] = (p["razon"], p["factor"])
                            break
                elif crecimiento_div_raw < -0.01:
                    factor_penalizacion_joven = 0.96
                    razon = f"Dividendo joven ({anios_consecutivos} años) con crecimiento negativo (Moderado)"
                    factor_total *= factor_penalizacion_joven; razones["Crec. Div."] = (razon, factor_penalizacion_joven)
        if self.tendencias.get('ingresos_cagr_5a', 1) < 0:
            p = FACTORES_PENALIZACION_ADAPTATIVOS["ingresos_crecimiento"][0]; factor_total *= p["factor"]; razones["Crec. Ing."] = (p["razon"], p["factor"])
        if self.tendencias.get('roe_promedio_5a', 1) < ROE_UMBRAL_ACEPTABLE:
            p = FACTORES_PENALIZACION_ADAPTATIVOS["roe"][0]; factor_total *= p["factor"]; razones["ROE"] = (p["razon"], p["factor"])
        if self.tendencias.get('deuda_creciente', False):
            p = FACTORES_PENALIZACION_ADAPTATIVOS["deuda"][0]; factor_total *= p["factor"]; razones["Deuda"] = (p["razon"], p["factor"])
        return max(factor_total, 0.65), razones

    def _calcular_probabilidad_inversion(self):
        def clamp(score): return max(0.0, min(100.0, float(score or 0.0)))
        ponderaciones = [PONDERACION_FUNDAMENTAL, PONDERACION_CONSISTENCIA_DIV, PONDERACION_RENDIMIENTO_DIV, PONDERACION_CRECIMIENTO_DIV, PONDERACION_CRECIMIENTO_GENERAL, PONDERACION_CONFIANZA_MGMT, PONDERACION_TECNICA]
        lista_scores = [
            self.scores['fundamental'][0], self.scores['consistencia_div'][0], self.scores['rendimiento_div_score'][0],
            self.scores['crecimiento_div_score'][0], self.scores['crecimiento_general'][0], self.scores['confianza_mgmt'][0], self.scores['tecnica'][0]
        ]
        probabilidad = sum(clamp(s) * p for s, p in zip(lista_scores, ponderaciones))
        return round(max(0.0, min(100.0, probabilidad)), 2)

    def ejecutar_analisis(self):
        if not self.datos_completos: return
        crecimiento_div_raw = self._calcular_crecimiento_dividendos()
        rendimiento_div = self._calcular_rendimiento_dividendos()
        anios_consecutivos_div = self.tendencias.get('anios_consecutivos_dividendo', 0)
        self.scores = {
            'fundamental': self._calcular_puntuacion_fundamental(),
            'tecnica': self._calcular_puntuacion_tecnica(),
            'consistencia_div': self._evaluar_historial_pagos_div(),
            'crecimiento_div_raw': (crecimiento_div_raw, []),
            'crecimiento_general': self._score_crecimiento_general(),
            'confianza_mgmt': self._score_confianza_management()
        }
        self.scores['rendimiento_div_score'] = self._score_rendimiento(rendimiento_div)
        self.scores['crecimiento_div_score'] = self._score_crecimiento_div(crecimiento_div_raw, anios_consecutivos_div)
        self.probabilidad_base = self._calcular_probabilidad_inversion()
        self.factor_penalizacion, self.razones_penalizacion = self._calcular_penalizacion_dinamica()
        self.probabilidad_ajustada = self.probabilidad_base * self.factor_penalizacion

    def generar_informe(self):
        if not self.datos_completos or not self.scores: return
        nombre_empresa = self.info.get('longName', 'Desconocido')
        sector = self.info.get('sector', 'N/A')
        precio_actual = self.datos_completos.get('precio_actual', 0)
        
        def generar_alcances():
            puntos_fuertes = []
            umbrales = UMBRALES_POR_SECTOR.get(sector, UMBRALES_POR_SECTOR['default'])
            if self.info.get('trailingPE') and self.info['trailingPE'] < umbrales['PE_BAJO']: puntos_fuertes.append("Valoración atractiva (PER bajo).")
            if self.info.get('returnOnEquity') and self.info['returnOnEquity'] > ROE_UMBRAL_BUENO: puntos_fuertes.append(f"Excelente rentabilidad (ROE > {ROE_UMBRAL_BUENO:.0%}).")
            if self.scores.get('rendimiento_div_score')[0] > 80: puntos_fuertes.append("Rendimiento por dividendo muy atractivo.")
            if self.scores.get('crecimiento_div_score')[0] > 80: puntos_fuertes.append("Fuerte crecimiento del dividendo.")
            if self.info.get('payoutRatio') and 0 < self.info['payoutRatio'] < 0.6: puntos_fuertes.append("Dividendo sostenible (Payout Ratio bajo).")
            rsi = self.hist_indicadores.iloc[-1].get('RSI_14') if self.hist_indicadores is not None else None
            if rsi and rsi < RSI_SOBREVENTA: puntos_fuertes.append(f"Momento técnico: Acción en sobreventa (RSI < {RSI_SOBREVENTA}).")
            return puntos_fuertes

        def obtener_nivel_riesgo():
            if self.factor_penalizacion >= 0.98: return "Bajo", "[+]"
            if self.factor_penalizacion >= 0.92: return "Moderado", "[!" ]"
            if self.factor_penalizacion >= 0.85: return "Alto", "[!!]"
            return "Critico", "[!!!]"

        def generar_resumen_empresa():
            resumen = self.info.get('longBusinessSummary', "No hay un resumen del negocio disponible.")
            return resumen[:800].rsplit(' ', 1)[0] + '...' if len(resumen) > 800 else resumen

        def generar_recomendacion():
            riesgo_txt, _ = obtener_nivel_riesgo()
            score = self.probabilidad_ajustada
            if sector in SECTORES_CICLICOS and score >= 60: return "COMPRA CÍCLICA: Buen momento del ciclo."
            if score >= 80 and riesgo_txt == 'Bajo': return "COMPRA FUERTE: Perfil ideal según tu estrategia."
            elif 70 <= score < 80 and riesgo_txt in ['Bajo', 'Moderado']: return "COMPRA POTENCIAL: Requiere análisis adicional."
            elif 55 <= score < 70: return "ZONA DE MONITOREO: No comprar aún, seguir evolución."
            else: return "DESCARTAR: No cumple criterios de inversión."

        def _imprimir_resumen_juez(nombre, datos_juez, peso):
            score, razones = datos_juez
            print(f"  - {nombre:<29} {score:>5.1f} / 100  (Peso: {peso:.0%})")
            for razon in razones:
                print(f"      - {razon}")

        print("\n" + "="*70)
        print(f"  INFORME DE ANÁLISIS v8.0 (Con Resumen de Jueces) PARA: {nombre_empresa} ({self.simbolo})")
        print(f"  Sector: {sector} | Precio Actual: ${precio_actual:.2f}")
        print("="*70)
        print(f"\n[+] PUNTUACION GENERAL: {self.probabilidad_ajustada:.2f} / 100.00")
        print(f"    RECOMENDACIÓN AUTOMÁTICA: {generar_recomendacion()}")
        nivel_riesgo_txt, nivel_riesgo_icono = obtener_nivel_riesgo()
        print(f" *  Nivel de Riesgo Basado en Tendencias: {nivel_riesgo_icono} {nivel_riesgo_txt}")
        if self.factor_penalizacion < 1.0:
            print(f"   (Puntuación base: {self.probabilidad_base:.2f}, ajustada por un factor de x{self.factor_penalizacion:.2f})")
            if self.razones_penalizacion:
                print("   Detalle de Penalizaciones Aplicadas:")
                for tipo, (razon, _) in self.razones_penalizacion.items(): print(f"     - {razon}")
        print("\n" + "="*28 + " PERFIL DE LA EMPRESA " + "="*27)
        print(generar_resumen_empresa())
        print("\n" + "="*24 + " DESGLOSE DE PUNTUACIONES " + "="*24)
        _imprimir_resumen_juez("Juez Fundamental", self.scores['fundamental'], PONDERACION_FUNDAMENTAL)
        _imprimir_resumen_juez("Juez Consistencia Dividendo", self.scores['consistencia_div'], PONDERACION_CONSISTENCIA_DIV)
        _imprimir_resumen_juez("Juez Rendimiento Dividendo", self.scores['rendimiento_div_score'], PONDERACION_RENDIMIENTO_DIV)
        _imprimir_resumen_juez("Juez Crecimiento Dividendo", self.scores['crecimiento_div_score'], PONDERACION_CRECIMIENTO_DIV)
        _imprimir_resumen_juez("Juez Crecimiento General", self.scores['crecimiento_general'], PONDERACION_CRECIMIENTO_GENERAL)
        _imprimir_resumen_juez("Juez Técnico (Oportunidad)", self.scores['tecnica'], PONDERACION_TECNICA)
        print("\n" + "="*25 + " CONCLUSIONES Y ALCANCES " + "="*24)
        puntos_fuertes = generar_alcances()
        if not puntos_fuertes and not self.razones_penalizacion:
            print("\nAnálisis neutral, sin métricas especialmente destacables.")
        else:
            if puntos_fuertes:
                print("\n[+] PUNTOS FUERTES:")
                for punto in puntos_fuertes: print(f"  - {punto}")
            if self.razones_penalizacion:
                print("\n[!] PUNTOS DÉBILES Y BANDERAS ROJAS (basado en tendencias):")
                for tipo, (razon, _) in self.razones_penalizacion.items(): print(f"  - {razon}")
        print("\n" + "="*70)
        print("AVISO: Este es un análisis automatizado. Úselo como punto de partida para su propia investigación.")

if __name__ == "__main__":
    while True:
        ticker_input = input("\nIntroduce el símbolo de la acción a analizar (o escribe 'salir' para terminar): ").strip().upper()
        if ticker_input in ['SALIR', 'EXIT', 'QUIT', 'Q']: break
        if not ticker_input: continue
        try:
            analizador = AnalizadorAccion(ticker_input)
            if analizador.datos_completos:
                analizador.ejecutar_analisis()
                analizador.generar_informe()
        except Exception as e:
            logging.critical(f"OCURRIÓ UN ERROR INESPERADO AL PROCESAR {ticker_input}: {e}", exc_info=True)
            print("\n" + "!"*70)
            print(f" OCURRIÓ UN ERROR INESPERADO AL ANALIZAR {ticker_input}")
            print(" Revise el log para más detalles. Puede deberse a datos faltantes o un problema de conexión.")
            print("!"*70)
    print("\nHas salido del analizador.")
    input("Presiona Enter para cerrar la ventana...")
