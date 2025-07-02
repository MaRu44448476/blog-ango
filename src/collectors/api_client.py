"""
仮想通貨APIクライアントモジュール
"""

import requests
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

class CryptoAPIClient:
    """仮想通貨API統合クライアント"""
    
    def __init__(self, config):
        """
        APIクライアントを初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # API設定
        self.coingecko_base_url = config.COINGECKO_BASE_URL
        self.coinmarketcap_base_url = config.COINMARKETCAP_BASE_URL
        self.cryptocompare_base_url = config.CRYPTOCOMPARE_BASE_URL
        
        # レート制限管理
        self.last_request_time = {}
        self.rate_limit_delay = 60 / config.API_RATE_LIMIT  # requests per minute to seconds per request
        
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoMediaSystem/1.0'
        })
    
    def _rate_limit_check(self, api_name: str):
        """レート制限チェック"""
        current_time = time.time()
        if api_name in self.last_request_time:
            time_since_last = current_time - self.last_request_time[api_name]
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time[api_name] = current_time
    
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, api_name: str = "unknown") -> Optional[Dict]:
        """
        APIリクエストを実行
        
        Args:
            url: リクエストURL
            params: パラメータ
            headers: ヘッダー
            api_name: API名（レート制限用）
            
        Returns:
            Dict: レスポンスデータ
        """
        self._rate_limit_check(api_name)
        
        try:
            start_time = time.time()
            
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.get(url, params=params, headers=request_headers, timeout=30)
            response_time = time.time() - start_time
            
            # API使用状況をログに記録
            self.logger.debug(f"{api_name} API リクエスト: {url} - {response.status_code} - {response_time:.2f}s")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                self.logger.warning(f"Rate limit exceeded for {api_name}")
                time.sleep(60)  # 1分待機
                return None
            else:
                self.logger.error(f"{api_name} API エラー: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{api_name} API リクエスト例外: {e}")
            return None
    
    def get_coingecko_market_data(self, vs_currency: str = "usd", limit: int = 100) -> List[Dict[str, Any]]:
        """
        CoinGeckoから市場データを取得
        
        Args:
            vs_currency: 比較通貨
            limit: 取得する通貨数
            
        Returns:
            List[Dict]: 市場データ
        """
        url = f"{self.coingecko_base_url}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h,7d"
        }
        
        headers = {}
        if self.config.COINGECKO_API_KEY:
            headers["x-cg-demo-api-key"] = self.config.COINGECKO_API_KEY
        
        data = self._make_request(url, params, headers, "coingecko")
        
        if data:
            market_data = []
            for coin in data:
                market_data.append({
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price": coin.get("current_price", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "volume_24h": coin.get("total_volume", 0),
                    "price_change_24h": coin.get("price_change_24h", 0),
                    "price_change_percentage_24h": coin.get("price_change_percentage_24h", 0),
                    "price_change_percentage_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                    "market_cap_rank": coin.get("market_cap_rank", 0),
                    "source": "coingecko",
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"CoinGecko市場データ {len(market_data)}件を取得")
            return market_data
        
        return []
    
    def get_coinmarketcap_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        CoinMarketCapから市場データを取得
        
        Args:
            limit: 取得する通貨数
            
        Returns:
            List[Dict]: 市場データ
        """
        if not self.config.COINMARKETCAP_API_KEY:
            self.logger.warning("CoinMarketCap APIキーが設定されていません")
            return []
        
        url = f"{self.coinmarketcap_base_url}/cryptocurrency/listings/latest"
        params = {
            "start": 1,
            "limit": limit,
            "convert": "USD"
        }
        
        headers = {
            "X-CMC_PRO_API_KEY": self.config.COINMARKETCAP_API_KEY
        }
        
        data = self._make_request(url, params, headers, "coinmarketcap")
        
        if data and "data" in data:
            market_data = []
            for coin in data["data"]:
                quote = coin.get("quote", {}).get("USD", {})
                market_data.append({
                    "symbol": coin.get("symbol", ""),
                    "name": coin.get("name", ""),
                    "price": quote.get("price", 0),
                    "market_cap": quote.get("market_cap", 0),
                    "volume_24h": quote.get("volume_24h", 0),
                    "price_change_24h": quote.get("price_change_24h", 0),
                    "price_change_percentage_24h": quote.get("percent_change_24h", 0),
                    "price_change_percentage_7d": quote.get("percent_change_7d", 0),
                    "market_cap_rank": coin.get("cmc_rank", 0),
                    "source": "coinmarketcap",
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"CoinMarketCap市場データ {len(market_data)}件を取得")
            return market_data
        
        return []
    
    def get_cryptocompare_data(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        CryptoCompareから市場データを取得
        
        Args:
            symbols: 取得する通貨シンボルのリスト
            
        Returns:
            List[Dict]: 市場データ
        """
        if not symbols:
            symbols = ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "MATIC", "SOL", "DOT", "AVAX"]
        
        if not self.config.CRYPTOCOMPARE_API_KEY:
            self.logger.warning("CryptoCompare APIキーが設定されていません")
            return []
        
        # 複数通貨の価格データを取得
        url = f"{self.cryptocompare_base_url}/pricemultifull"
        params = {
            "fsyms": ",".join(symbols),
            "tsyms": "USD"
        }
        
        headers = {
            "authorization": f"Apikey {self.config.CRYPTOCOMPARE_API_KEY}"
        }
        
        data = self._make_request(url, params, headers, "cryptocompare")
        
        if data and "RAW" in data:
            market_data = []
            for symbol, data_dict in data["RAW"].items():
                usd_data = data_dict.get("USD", {})
                market_data.append({
                    "symbol": symbol,
                    "name": symbol,
                    "price": usd_data.get("PRICE", 0),
                    "market_cap": usd_data.get("MKTCAP", 0),
                    "volume_24h": usd_data.get("TOTALVOLUME24HTO", 0),
                    "price_change_24h": usd_data.get("CHANGE24HOUR", 0),
                    "price_change_percentage_24h": usd_data.get("CHANGEPCT24HOUR", 0),
                    "source": "cryptocompare",
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"CryptoCompare市場データ {len(market_data)}件を取得")
            return market_data
        
        return []
    
    def get_market_data(self) -> List[Dict[str, Any]]:
        """
        全てのAPIから市場データを取得
        
        Returns:
            List[Dict]: 統合された市場データ
        """
        all_market_data = []
        
        # CoinGeckoデータを取得
        try:
            coingecko_data = self.get_coingecko_market_data()
            all_market_data.extend(coingecko_data)
        except Exception as e:
            self.logger.error(f"CoinGeckoデータ取得エラー: {e}")
        
        # CoinMarketCapデータを取得
        try:
            coinmarketcap_data = self.get_coinmarketcap_data()
            all_market_data.extend(coinmarketcap_data)
        except Exception as e:
            self.logger.error(f"CoinMarketCapデータ取得エラー: {e}")
        
        # CryptoCompareデータを取得
        try:
            cryptocompare_data = self.get_cryptocompare_data()
            all_market_data.extend(cryptocompare_data)
        except Exception as e:
            self.logger.error(f"CryptoCompareデータ取得エラー: {e}")
        
        # 重複を削除（同じ通貨の最新データを保持）
        unique_data = {}
        for item in all_market_data:
            symbol = item["symbol"]
            if symbol not in unique_data or item["source"] == "coingecko":  # CoinGeckoを優先
                unique_data[symbol] = item
        
        result = list(unique_data.values())
        self.logger.info(f"統合市場データ {len(result)}件を取得")
        return result
    
    def get_trending_coins(self) -> List[Dict[str, Any]]:
        """
        トレンド通貨を取得
        
        Returns:
            List[Dict]: トレンド通貨データ
        """
        url = f"{self.coingecko_base_url}/search/trending"
        
        headers = {}
        if self.config.COINGECKO_API_KEY:
            headers["x-cg-demo-api-key"] = self.config.COINGECKO_API_KEY
        
        data = self._make_request(url, None, headers, "coingecko")
        
        if data and "coins" in data:
            trending_data = []
            for coin_info in data["coins"]:
                coin = coin_info.get("item", {})
                trending_data.append({
                    "id": coin.get("id", ""),
                    "symbol": coin.get("symbol", ""),
                    "name": coin.get("name", ""),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc", 0),
                    "score": coin.get("score", 0),
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"トレンド通貨 {len(trending_data)}件を取得")
            return trending_data
        
        return []
    
    def get_fear_greed_index(self) -> Optional[Dict[str, Any]]:
        """
        恐怖貪欲指数を取得
        
        Returns:
            Dict: 恐怖貪欲指数データ
        """
        try:
            # Alternative.meのFear & Greed Index API（無料）
            url = "https://api.alternative.me/fng/"
            
            data = self._make_request(url, None, None, "feargreed")
            
            if data and "data" in data and len(data["data"]) > 0:
                index_data = data["data"][0]
                return {
                    "value": int(index_data.get("value", 0)),
                    "value_classification": index_data.get("value_classification", ""),
                    "timestamp": index_data.get("timestamp", ""),
                    "time_until_update": index_data.get("time_until_update", "")
                }
            
        except Exception as e:
            self.logger.error(f"恐怖貪欲指数取得エラー: {e}")
        
        return None
    
    def analyze_market_sentiment(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        市場センチメントを分析
        
        Args:
            market_data: 市場データ
            
        Returns:
            Dict: センチメント分析結果
        """
        if not market_data:
            return {}
        
        # 価格変動の統計
        price_changes_24h = [item.get("price_change_percentage_24h", 0) for item in market_data if item.get("price_change_percentage_24h") is not None]
        
        if not price_changes_24h:
            return {}
        
        positive_count = len([x for x in price_changes_24h if x > 0])
        negative_count = len([x for x in price_changes_24h if x < 0])
        total_count = len(price_changes_24h)
        
        average_change = sum(price_changes_24h) / len(price_changes_24h)
        
        # センチメント判定
        if positive_count / total_count > 0.7:
            sentiment = "強気"
        elif positive_count / total_count > 0.5:
            sentiment = "やや強気"
        elif negative_count / total_count > 0.7:
            sentiment = "弱気"
        elif negative_count / total_count > 0.5:
            sentiment = "やや弱気"
        else:
            sentiment = "中立"
        
        return {
            "overall_sentiment": sentiment,
            "positive_coins": positive_count,
            "negative_coins": negative_count,
            "total_coins": total_count,
            "positive_ratio": positive_count / total_count,
            "average_change_24h": average_change,
            "timestamp": datetime.now().isoformat()
        }