# Simulador de filas usando queue.Queue
from queue import Queue


# Mapa simples de filas nomeadas: string -> Queue
_QUEUES = {}


def get_queue(name: str) -> Queue:
    if name not in _QUEUES:
        _QUEUES[name] = Queue()
        return _QUEUES[name]


def clear_queues():
    global _QUEUES
    _QUEUES = {}