import os
from string import Template

from aiohttp import web
import aiohttp
import asyncio
import pickle
from cashaddress.convert import Address

import wallet
from tx_event import TxBitsocket, Tx

app_auth = os.environ['ONESIGNAL_APP_KEY']
app_id = os.environ['ONESIGNAL_APP_ID']
addresses_path = os.environ.get('ADDRESSES_PATH', 'addresses.pickle')

try:
    addresses = pickle.load(open(addresses_path, 'rb'))
except:
    addresses = set()
wallet = wallet.WalletDefault()
wallet.add_addresses([Address.from_string(address) for address in addresses])


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
    whole_part_str = str(satoshis // 100_000_000)
    fract_part_str = '\xa0'.join(parts)
    if fract_part_str:
        return f'{whole_part_str}.{fract_part_str} BCH'
    else:
        return f'{whole_part_str} BCH'


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
            url = 'https://explorer.bitcoin.com/bch/tx/' + tx.tx_hash()
            msg = f'Received {format_bch_amount(amount)}'
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


asyncio.get_event_loop().call_soon(lambda: asyncio.ensure_future(listen_txs()))


template = Template(open('subscribe.html').read())
scan_template = open('scan.html').read()


async def handle(request):
    try:
        address = request.match_info.get('address', '<no address provided>')
        wallet.add_addresses([Address.from_string(address)])
    except:
        return web.Response(text=f'Invalid address: {address}')
    addresses.add(address)
    pickle.dump(addresses, open(addresses_path, 'wb'))
    return web.Response(
        text=template.substitute(address=address, appId=app_id),
        content_type='text/html',
    )

async def handle_scan(request):
    return web.Response(text=scan_template, content_type='text/html')

app = web.Application()
app.add_routes([web.get('/', handle_scan),
                web.get('/{address}', handle)])

web.run_app(app, port=7010)

