import asyncio
import base64
import json
import traceback
from abc import ABCMeta, abstractmethod
from typing import List

import aiostream
from aiohttp_sse_client import client as sse_client
from cashaddress.convert import Address


class Wallet(metaclass=ABCMeta):
    @abstractmethod
    def add_addresses(self, addresses: List[Address]) -> None:
        pass

    @abstractmethod
    def remove_address(self, address: Address) -> None:
        pass

    @abstractmethod
    def is_listening_to_address(self, address: Address) -> bool:
        pass

    @abstractmethod
    async def listen(self):
        pass


class WalletDefault(Wallet):
    def __init__(self) -> None:
        self._listening_addresses = []
        self._new_address_future: asyncio.Future = None

    def add_addresses(self, addresses: List[Address]) -> None:
        self._listening_addresses.extend(addresses)
        if self._new_address_future is not None:
            try:
                self._new_address_future.set_exception(NewAddressException())
            except:
                pass

    def remove_address(self, address: Address) -> None:
        try:
            self._listening_addresses.remove(address)
        except ValueError:
            pass

    def is_listening_to_address(self, address: Address) -> bool:
        cash_addr = address.cash_address()
        for wallet_address in self._listening_addresses:
            if wallet_address.cash_address() == cash_addr:
                return True
        return False

    async def listen(self):
        while True:
            query = {
                "v": 3, "q": {
                    "find": {
                        "out.e.a": {
                            "$in": [
                                address.cash_address().split(':')[1]
                                for address in self._listening_addresses
                            ],
                        },
                    },
                },
            }
            print('listen to', query, self._listening_addresses)
            encoded = base64.b64encode(json.dumps(query).encode()).decode()
            self._new_address_future = asyncio.get_event_loop().create_future()
            async with sse_client.EventSource(f'https://bitsocket.fountainhead.cash/s/{encoded}') as sock:
                print('connected.')
                try:
                    async for message in aiostream.stream.merge(
                            sock,
                            aiostream.stream.just(self._new_address_future),
                    ):
                        message_dict = json.loads(message.data)
                        print(message_dict)
                        if message_dict['type'] == 'open':
                            continue
                        yield message_dict
                except NewAddressException:
                    self._new_address_future = asyncio.get_event_loop().create_future()
                except Exception:
                    traceback.print_exc()
                    self._new_address_future = asyncio.get_event_loop().create_future()
                except KeyboardInterrupt:
                    return


class NewAddressException(Exception):
    pass

