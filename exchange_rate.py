import asyncio
from abc import ABCMeta, abstractmethod
from typing import Iterable, Dict

import aiohttp


class ExchangeRate(metaclass=ABCMeta):
    @abstractmethod
    def for_currency(self, currency_name: str) -> float:
        pass

    @abstractmethod
    async def listen(self) -> None:
        pass

    @abstractmethod
    def currencies(self) -> Iterable[str]:
        pass


class ExchangeRateFixed(ExchangeRate):
    def for_currency(self, currency_name: str) -> float:
        if currency_name == 'JPY':
            return 6_765
        elif currency_name == 'EUR':
            return 861_474
        raise ValueError(f'Invalid currency: {currency_name}')

    async def listen(self) -> None:
        pass

    def currencies(self) -> Iterable[str]:
        return iter(['EUR', 'JPY'])


class ExchangeRateApi(ExchangeRate):
    API_URL = 'https://api.coinbase.com/v2/exchange-rates?currency=BCH'

    def __init__(self) -> None:
        self._api_url = self.API_URL
        self._last_result = {}

    def for_currency(self, currency_name: str) -> float:
        return self._last_result[currency_name]

    async def listen(self) -> None:
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(self._api_url) as response:
                    currencies_dict = await response.json()
                    self._last_result = {
                        currency_name: 100_000_000 / float(rate)
                        for currency_name, rate in currencies_dict['data']['rates'].items()
                    }
                await asyncio.sleep(100)

    def currencies(self) -> Iterable[str]:
        return iter(self._last_result.keys())


class CurrenciesInfo(metaclass=ABCMeta):
    @abstractmethod
    def currencies(self) -> Iterable[str]:
        pass

    @abstractmethod
    def name_for_code(self, currency_code: str) -> str:
        pass

    @abstractmethod
    def symbol_for_code(self, currency_code: str) -> str:
        pass

    @abstractmethod
    def format_for_code(self, currency_code: str) -> Dict:
        pass


class CurrenciesInfoFixed(CurrenciesInfo):
    # source: https://www.xe.com/symbols.php
    CURRENCIES_INFO = [
        ('United States Dollar', 'USD', '$', 2),
        ('United Kingdom Pound', 'GBP', '£', 2),
        ('Bitcoin Cash', 'BCH', 'BCH', 8),
        ('Canada Dollar', 'CAD', '$', 2),
        ('Euro Member Countries', 'EUR', '€', 2),
        ('Hong Kong Dollar', 'HKD', '$', 2),
        ('Japan Yen', 'JPY', '¥', 0),
        ('Korea (South) Won', 'KRW', '₩', 0),
        ('New Zealand Dollar', 'NZD', '$', 2),
        ('Sweden Krona', 'SEK', 'kr', 2),
        ('Switzerland Franc', 'CHF', 'CHF', 2),
        ('Albania Lek', 'ALL', 'Lek', 2),
        ('Afghanistan Afghani', 'AFN', '؋', 2),
        ('Argentina Peso', 'ARS', '$', 2),
        ('Aruba Guilder', 'AWG', 'ƒ', 2),
        ('Australia Dollar', 'AUD', '$', 2),
        ('Azerbaijan Manat', 'AZN', '₼', 2),
        ('Bahamas Dollar', 'BSD', '$', 2),
        ('Barbados Dollar', 'BBD', '$', 2),
        ('Belarus Ruble', 'BYN', 'Br', 2),
        ('Belize Dollar', 'BZD', 'BZ$', 2),
        ('Bermuda Dollar', 'BMD', '$', 2),
        ('Bolivia Bolíviano', 'BOB', '$b', 2),
        ('Bosnia and Herzegovina Convertible Marka', 'BAM', 'KM', 2),
        ('Botswana Pula', 'BWP', 'P', 2),
        ('Bulgaria Lev', 'BGN', 'лв', 2),
        ('Brazil Real', 'BRL', 'R$', 2),
        ('Brunei Darussalam Dollar', 'BND', '$', 2),
        ('Cambodia Riel', 'KHR', '៛', 2),
        ('Cayman Islands Dollar', 'KYD', '$', 2),
        ('Chile Peso', 'CLP', '$', 0),
        ('China Yuan Renminbi', 'CNY', '¥', 2),
        ('Colombia Peso', 'COP', '$', 2),
        ('Costa Rica Colon', 'CRC', '₡', 2),
        ('Croatia Kuna', 'HRK', 'kn', 2),
        ('Cuba Peso', 'CUP', '₱', 2),
        ('Czech Republic Koruna', 'CZK', 'Kč', 2),
        ('Denmark Krone', 'DKK', 'kr', 2),
        ('Dominican Republic Peso', 'DOP', 'RD$', 2),
        ('East Caribbean Dollar', 'XCD', '$', 2),
        ('Egypt Pound', 'EGP', '£', 2),
        ('El Salvador Colon', 'SVC', '$', 2),
        ('Falkland Islands (Malvinas) Pound', 'FKP', '£', 2),
        ('Fiji Dollar', 'FJD', '$', 2),
        ('Ghana Cedi', 'GHS', '¢', 2),
        ('Gibraltar Pound', 'GIP', '£', 2),
        ('Guatemala Quetzal', 'GTQ', 'Q', 2),
        ('Guernsey Pound', 'GGP', '£', 2),
        ('Guyana Dollar', 'GYD', '$', 2),
        ('Honduras Lempira', 'HNL', 'L', 2),
        ('Hungary Forint', 'HUF', 'Ft', 2),
        ('Iceland Krona', 'ISK', 'kr', 2),
        ('India Rupee', 'INR', '', 2),
        ('Indonesia Rupiah', 'IDR', 'Rp', 0),
        ('Iran Rial', 'IRR', '﷼', 2),
        ('Isle of Man Pound', 'IMP', '£', 2),
        ('Israel Shekel', 'ILS', '₪', 2),
        ('Jamaica Dollar', 'JMD', 'J$', 2),
        ('Jersey Pound', 'JEP', '£', 2),
        ('Kazakhstan Tenge', 'KZT', 'лв', 2),
        ('Korea (North) Won', 'KPW', '₩', 2),
        ('Kyrgyzstan Som', 'KGS', 'лв', 2),
        ('Laos Kip', 'LAK', '₭', 2),
        ('Lebanon Pound', 'LBP', '£', 2),
        ('Liberia Dollar', 'LRD', '$', 2),
        ('Macedonia Denar', 'MKD', 'ден', 2),
        ('Malaysia Ringgit', 'MYR', 'RM', 2),
        ('Mauritius Rupee', 'MUR', '₨', 2),
        ('Mexico Peso', 'MXN', '$', 2),
        ('Mongolia Tughrik', 'MNT', '₮', 2),
        ('Mozambique Metical', 'MZN', 'MT', 2),
        ('Namibia Dollar', 'NAD', '$', 2),
        ('Nepal Rupee', 'NPR', '₨', 2),
        ('Netherlands Antilles Guilder', 'ANG', 'ƒ', 2),
        ('Nicaragua Cordoba', 'NIO', 'C$', 2),
        ('Nigeria Naira', 'NGN', '₦', 2),
        ('Norway Krone', 'NOK', 'kr', 2),
        ('Oman Rial', 'OMR', '﷼', 2),
        ('Pakistan Rupee', 'PKR', '₨', 0),
        ('Panama Balboa', 'PAB', 'B/.', 2),
        ('Paraguay Guarani', 'PYG', 'Gs', 2),
        ('Peru Sol', 'PEN', 'S/.', 2),
        ('Philippines Peso', 'PHP', '₱', 2),
        ('Poland Zloty', 'PLN', 'zł', 2),
        ('Qatar Riyal', 'QAR', '﷼', 2),
        ('Romania Leu', 'RON', 'lei', 2),
        ('Russia Ruble', 'RUB', '₽', 2),
        ('Saint Helena Pound', 'SHP', '£', 2),
        ('Saudi Arabia Riyal', 'SAR', '﷼', 2),
        ('Serbia Dinar', 'RSD', 'Дин.', 0),
        ('Seychelles Rupee', 'SCR', '₨', 2),
        ('Singapore Dollar', 'SGD', '$', 2),
        ('Solomon Islands Dollar', 'SBD', '$', 2),
        ('Somalia Shilling', 'SOS', 'S', 2),
        ('South Africa Rand', 'ZAR', 'R', 2),
        ('Sri Lanka Rupee', 'LKR', '₨', 2),
        ('Suriname Dollar', 'SRD', '$', 2),
        ('Syria Pound', 'SYP', '£', 2),
        ('Taiwan New Dollar', 'TWD', 'NT$', 2),
        ('Thailand Baht', 'THB', '฿', 2),
        ('Trinidad and Tobago Dollar', 'TTD', 'TT$', 2),
        ('Turkey Lira', 'TRY', '', 2),
        ('Tuvalu Dollar', 'TVD', '$', 2),
        ('Ukraine Hryvnia', 'UAH', '₴', 2),
        ('Uruguay Peso', 'UYU', '$U', 2),
        ('Uzbekistan Som', 'UZS', 'лв', 2),
        ('Venezuela Bolívar', 'VEF', 'Bs', 2),
        ('Viet Nam Dong', 'VND', '₫', 2),
        ('Yemen Rial', 'YER', '﷼', 2),
        ('Zimbabwe Dollar', 'ZWD', 'Z$', 0),
    ]

    def __init__(self) -> None:
        self._currencies_info = {
            code: {'name': name, 'symbol': symbol, 'format': {'decimalPlaces': decimal_places}}
            for name, code, symbol, decimal_places in self.CURRENCIES_INFO
        }

    def currencies(self) -> Iterable[str]:
        return iter(self._currencies_info.keys())

    def name_for_code(self, currency_code: str) -> str:
        return self._currencies_info[currency_code]['name']

    def symbol_for_code(self, currency_code: str) -> str:
        return self._currencies_info[currency_code]['symbol']

    def format_for_code(self, currency_code: str) -> Dict:
        return self._currencies_info[currency_code]['format']

