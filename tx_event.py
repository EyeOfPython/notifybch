from abc import ABCMeta, abstractmethod
from typing import Iterable, Dict

from cashaddress.convert import Address


class TxOutput(metaclass=ABCMeta):
    @abstractmethod
    def amount(self) -> int:
        pass

    @abstractmethod
    def address(self) -> Address:
        pass


class Tx(metaclass=ABCMeta):
    @abstractmethod
    def tx_hash(self) -> str:
        pass

    @abstractmethod
    def outputs(self) -> Iterable[TxOutput]:
        pass


class TxEventReceiver(metaclass=ABCMeta):
    @abstractmethod
    def receive(self, tx: Tx) -> None:
        pass


class TxBitsocket(Tx):
    def __init__(self, tx_dict: Dict) -> None:
        self._tx_dict = tx_dict

    def tx_hash(self) -> str:
        return self._tx_dict['tx']['h']

    def outputs(self) -> Iterable[TxOutput]:
        for output_dict in self._tx_dict['out']:
            yield TxOutputBitsocket(output_dict)


class TxOutputBitsocket(TxOutput):
    def __init__(self, output_dict: Dict) -> None:
        self._output_dict = output_dict

    def amount(self) -> int:
        return self._output_dict['e']['v']

    def address(self) -> Address:
        if 'a' in self._output_dict['e']:
            return Address.from_string('bitcoincash:' + self._output_dict['e']['a'])
        return None


def _test():
    bitsocket_event = {
        'type': 'mempool',
        'data': [
            {
                'tx': {'h': 'a685412fca8392e13a44a286464b82db925974c529abb78f201b7c8af179b8b2'},
                'in': [
                    {
                        'i': 0,
                        'b0': 'MEUCIQDsS2KPOwq3z5JulRtu+T373JPJVSV4/+NwAAtt+eQbUQIgJzcd+f3J4dke1uIAqgIN1fETIzJ2DHpLe+FV'
                              'wgH8VXxB',
                        'b1': 'AiciURMbskmRSHRxNy84tBPjdDs7H82ajPWu/Nz43m5M',
                        'str': '3045022100ec4b628f3b0ab7cf926e951b6ef93dfbdc93c9552578ffe370000b6df9e41b51022027371df9f'
                               'dc9e1d91ed6e200aa020dd5f1132332760c7a4b7be155c201fc557c41 02272251131bb24991487471372f3'
                               '8b413e3743b3b1fcd9a8cf5aefcdcf8de6e4c',
                        'e': {
                            'h': 'db6863722a3ee2168fcc16c7b4dd2c344c13adf677fff52caacddf2df606cc6f',
                            'i': 1,
                            'a': 'qraqx7hu9g8pduxktlfgyzdnma6nmkaxwsehstwwst'
                        },
                        'h0': '3045022100ec4b628f3b0ab7cf926e951b6ef93dfbdc93c9552578ffe370000b6df9e41b51022027371df9fd'
                              'c9e1d91ed6e200aa020dd5f1132332760c7a4b7be155c201fc557c41',
                        'h1': '02272251131bb24991487471372f38b413e3743b3b1fcd9a8cf5aefcdcf8de6e4c'
                    },
                    {
                        'i': 1,
                        'b0': 'MEQCICzaQD+Wfja9MRZlphWTM0ZpZQKFSkPVF80BOGDPD1WTAiAreRARHR9QQellWVMC30dLt8wXxRnos5826mIo'
                              'bvGc70E=',
                        'b1': 'A7q4xvKvWd5svIfwRxDwofonH7pvRfCEAcBCRtZDQLHa',
                        'str': '304402202cda403f967e36bd311665a615933346696502854a43d517cd013860cf0f559302202b7910111d1'
                               'f5041e965595302df474bb7cc17c519e8b39f36ea62286ef19cef41 03bab8c6f2af59de6cbc87f04710f0a'
                               '1fa271fba6f45f08401c04246d64340b1da',
                        'e': {
                            'h': '2a9a8bc039372ee99c31209ae46f0eae4ef61961c0428a29910bbd8c49d6299c',
                            'i': 1,
                            'a': 'qr8392rx2n5gm7q26gdqandrn5vdsa8yuqq8x7aw6k'
                        },
                        'h0': '304402202cda403f967e36bd311665a615933346696502854a43d517cd013860cf0f559302202b7910111d1f'
                              '5041e965595302df474bb7cc17c519e8b39f36ea62286ef19cef41',
                        'h1': '03bab8c6f2af59de6cbc87f04710f0a1fa271fba6f45f08401c04246d64340b1da'
                    }
                ],
                'out': [
                    {
                        'i': 0,
                        'b0': {'op': 169},
                        'b1': 'LkhJjHeHFAzZZFAKZdHZ36cu7W0=',
                        's1': ...,
                        'b2': {'op': 135},
                        'str': 'OP_HASH160 2e48498c7787140cd964500a65d1d9dfa72eed6d OP_EQUAL',
                        'e': {
                            'v': 9_800_000,
                            'i': 0,
                            'a': 'pqhysjvvw7r3grxev3gq5ew3m806wthdd5lqpmma3l'
                        },
                        'h1': '2e48498c7787140cd964500a65d1d9dfa72eed6d'
                    },
                    {
                        'i': 1,
                        'b0': {'op': 118},
                        'b1': {'op': 169},
                        'b2': 'qsP8c2ePrNVT8ZD8CDn4axL0i+Q=',
                        's2': ...,
                        'b3': {'op': 136},
                        'b4': {'op': 172},
                        'str': 'OP_DUP OP_HASH160 aac3fc73678facd553f190fc0839f86b12f48be4 OP_EQUALVERIFY OP_CHECKSIG',
                        'e': {
                            'v': 1_055_736,
                            'i': 1,
                            'a': 'qz4v8lrnv786e42n7xg0czpelp439aytusray7cnh4'
                        },
                        'h2': 'aac3fc73678facd553f190fc0839f86b12f48be4'
                    }
                ],
                '_id': '5c7dcd3d46b82e002f9ee6c3'
            }
        ]
    }
    tx_dict = bitsocket_event['data'][0]
    tx = TxBitsocket(tx_dict)
    assert tx.tx_hash() == 'a685412fca8392e13a44a286464b82db925974c529abb78f201b7c8af179b8b2'
    outputs = list(tx.outputs())
    assert outputs[0].amount() == 9_800_000
    assert outputs[0].address().cash_address() == 'bitcoincash:pqhysjvvw7r3grxev3gq5ew3m806wthdd5lqpmma3l'
    assert outputs[1].amount() == 1_055_736
    assert outputs[1].address().cash_address() == 'bitcoincash:qz4v8lrnv786e42n7xg0czpelp439aytusray7cnh4'


if __name__ == '__main__':
    _test()

