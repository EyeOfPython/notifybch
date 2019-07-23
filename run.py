import os
from string import Template

from aiohttp import web
import aiohttp
import asyncio
import pickle
from cashaddress.convert import Address

import exchange_rate
import wallet
from tx_event import TxBitsocket, Tx

app_auth = os.environ['ONESIGNAL_APP_KEY']
app_id = os.environ['ONESIGNAL_APP_ID']
addresses_path = os.environ.get('ADDRESSES_PATH', 'addresses.pickle')

try:
    addresses = pickle.load(open(addresses_path, 'rb'))
    if isinstance(addresses, set):
        addresses = {address: {'currency': 'USD'} for address in addresses}
except:
    addresses = dict()
wallet = wallet.WalletDefault()
wallet.add_addresses([Address.from_string(address) for address in addresses.keys()])
exchange_rates = exchange_rate.ExchangeRateApi()
currency_infos = exchange_rate.CurrenciesInfoFixed()


def format_bch_amount(satoshis: int):
    fract_part = satoshis % 100_000_000
    fract_part_str = '{:0>8d}'.format(fract_part)
    parts = fract_part_str[:3], fract_part_str[3:6], fract_part_str[6:]
    for i, part in reversed(list(enumerate(parts))):
        if any(char != '0' for char in part):
            parts = parts[:i + 1]
            break
    else:
        parts = ()
    whole_part = satoshis // 100_000_000
    fract_part_str = '\xa0'.join(parts)
    if fract_part_str:
        return f'{whole_part:,}.{fract_part_str} BCH'
    else:
        return f'{whole_part:,} BCH'


def format_fiat_amount(satoshis: int, currency: str) -> str:
    sats_per_usd = exchange_rates.for_currency(currency)
    symbol = currency_infos.symbol_for_code(currency)
    fmt = currency_infos.format_for_code(currency)
    return '{}{:,.{n}f}'.format(symbol, satoshis / sats_per_usd, n=fmt['decimalPlaces'])


async def receive_tx(tx: Tx):
    amounts = {}
    for output in tx.outputs():
        address = output.address()
        if wallet.is_listening_to_address(address):
            amounts.setdefault(address.cash_address(), 0)
            amounts[address.cash_address()] += output.amount()
    print(amounts)
    async with aiohttp.ClientSession() as session:
        for bch_address, amount in amounts.items():
            currency = addresses[bch_address]['currency']
            url = 'https://explorer.bitcoin.com/bch/tx/' + tx.tx_hash()
            msg = f'Received {format_fiat_amount(amount, currency)} ({format_bch_amount(amount)})'
            async with session.post(
                    'https://onesignal.com/api/v1/notifications',
                    headers={"Authorization": f'Basic {app_auth}'},
                    json={
                        "app_id": app_id,
                        # "included_segments": ["All"],
                        "contents": {"en": msg},
                        "url": url,
                        "filters": [
                            {"field": "tag", "key": "bchAddress", "relation": "=", "value": bch_address},
                        ],
                    },
            ) as resp:
                print(resp.status)
                print(await resp.text())


async def listen_txs():
    async for message in wallet.listen():
        if message['type'] == 'mempool' and len(message['data']) > 0:
            for tx_dict in message['data']:
                await receive_tx(TxBitsocket(tx_dict))
        else:
            print('unknown message type:', message)


def save_addresses():
    pickle.dump(addresses, open(addresses_path, 'wb'))


asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(listen_txs()))
asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(exchange_rates.listen()))


template = Template(open('subscribe.html').read())
scan_template = open('scan.html').read()
currency_template = Template(open('select_currency.html').read())


async def handle(request):
    try:
        address = request.match_info.get('address', '<no address provided>')
        if address not in addresses:
            wallet.add_addresses([Address.from_string(address)])
            addresses[address] = {'currency': 'USD'}
            save_addresses()
    except:
        return web.Response(text=f'Invalid address: {address}')
    return web.Response(
        text=template.substitute(address=address, appId=app_id),
        content_type='text/html',
    )


async def handle_scan(request):
    return web.Response(text=scan_template, content_type='text/html')


async def handle_select_currency(request):
    try:
        address = request.match_info.get('address', '<no address provided>')
        address = Address.from_string(address).cash_address()
    except:
        return web.Response(text=f'Invalid address: {address}')
    if 'currency' in request.match_info:
        currency = request.match_info['currency']
        addresses.setdefault(address, {})['currency'] = currency
        save_addresses()
    selected_currency = addresses.get(address, {}).get('currency', None)
    selected_html = 'class="selected"'
    response = currency_template.substitute(
        currencies='\n'.join(
            f'<a href="/subscribe/select-currency/{address}/{currency}"'
            f'{selected_html if selected_currency == currency else ""}>'
            f'{currency}&nbsp;({currency_infos.symbol_for_code(currency)})'
            f'</a>'
            for currency in currency_infos.currencies()
        )
    )
    return web.Response(
        text=response,
        content_type='text/html',
    )


app = web.Application()
app.add_routes([web.get('/', handle_scan),
                web.get('/select-currency/{address}', handle_select_currency),
                web.get('/select-currency/{address}/{currency}', handle_select_currency),
                web.get('/{address}', handle)])

web.run_app(app, port=7010)

