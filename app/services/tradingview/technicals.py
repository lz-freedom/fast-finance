"""
TradingView Technical Analysis - Indicators Computation
Migrated from tradingview_ta/technicals.py
"""

class Recommendation:
    BUY = "BUY"
    STRONG_BUY = "STRONG_BUY"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    NEUTRAL = "NEUTRAL"
    ERROR = "ERROR"

class Compute:
    @staticmethod
    def MA(ma, close):
        """Compute Moving Average Recommendation"""
        if ma < close:
            return Recommendation.BUY
        elif ma > close:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def RSI(rsi, rsi1):
        """Compute Relative Strength Index Recommendation"""
        if rsi < 30 and rsi1 < rsi:
            return Recommendation.BUY
        elif rsi > 70 and rsi1 > rsi:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def Stoch(k, d, k1, d1):
        """Compute Stochastic Recommendation"""
        if k < 20 and d < 20 and k > d and k1 < d1:
            return Recommendation.BUY
        elif k > 80 and d > 80 and k < d and k1 > d1:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def CCI20(cci20, cci201):
        """Compute Commodity Channel Index 20 Recommendation"""
        if cci20 < -100 and cci20 > cci201:
            return Recommendation.BUY
        elif cci20 > 100 and cci20 < cci201:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def ADX(adx, adxpdi, adxndi, adxpdi1, adxndi1):
        """Compute Average Directional Index Recommendation"""
        if adx > 20 and adxpdi1 < adxndi1 and adxpdi > adxndi:
            return Recommendation.BUY
        elif adx > 20 and adxpdi1 > adxndi1 and adxpdi < adxndi:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def AO(ao, ao1, ao2):
        """Compute Awesome Oscillator Recommendation"""
        if (ao > 0 and ao1 < 0) or (ao > 0 and ao1 > 0 and ao > ao1 and ao2 > ao1):
            return Recommendation.BUY
        elif (ao < 0 and ao1 > 0) or (ao < 0 and ao1 < 0 and ao < ao1 and ao2 < ao1):
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def Mom(mom, mom1):
        """Compute Momentum Recommendation"""
        if mom < mom1:
            return Recommendation.SELL
        elif mom > mom1:
            return Recommendation.BUY
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def MACD(macd, signal):
        """Compute MACD Recommendation"""
        if macd > signal:
            return Recommendation.BUY
        elif macd < signal:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL
        
    @staticmethod
    def BBBuy(close, bblower):
        """Compute Bollinger Bands Buy Recommendation"""
        if close < bblower:
            return Recommendation.BUY
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def BBSell(close, bbupper):
        """Compute Bollinger Bands Sell Recommendation"""
        if close > bbupper:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def PSAR(psar, open_val):
        """Compute Parabolic SAR Recommendation"""
        if psar < open_val:
            return Recommendation.BUY
        elif psar > open_val:
            return Recommendation.SELL
        else:
            return Recommendation.NEUTRAL

    @staticmethod
    def Recommend(value):
        """Compute General Recommendation based on score"""
        if value is None:
             return Recommendation.ERROR
             
        if -1 <= value < -0.5:
            return Recommendation.STRONG_SELL
        elif -0.5 <= value < -0.1:
            return Recommendation.SELL
        elif -0.1 <= value <= 0.1:
            return Recommendation.NEUTRAL
        elif 0.1 < value <= 0.5:
            return Recommendation.BUY
        elif 0.5 < value <= 1:
            return Recommendation.STRONG_BUY
        else:
            return Recommendation.ERROR

    @staticmethod
    def Simple(value):
        """Compute Simple Recommendation (-1, 0, 1)"""
        if value == -1:
            return Recommendation.SELL
        elif value == 1:
            return Recommendation.BUY
        else:
            return Recommendation.NEUTRAL
