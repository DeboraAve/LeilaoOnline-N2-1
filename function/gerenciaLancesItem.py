# define: def gerenciaLancesItem(stop_event=None, batch_window_ms=100)
# Implementação simples que consome a fila 'filaLances', agrupa por itemId por uma janela
# e envia batches para 'filaLanceItem'. Para teste, expomos start/stop helpers.

from .fila import get_queue
from .banco import buscar_item_por_id
from threading import Thread, Event
import time

def gerenciaLancesItem(stop_event: Event = None, batch_window_ms: int = 100):
#Função que roda em loop consumindo a fila 'filaLances'.
#Se stop_event for None, cria-se um Event interno que nunca é setado (loop).
#Retorna o Thread em execução para o caller poder juntá-lo.
    in_q = get_queue('filaLances')
    out_q = get_queue('filaLanceItem')
    if stop_event is None:
        stop_event = Event()


    def run():
        buffers = {} # itemId -> [msgs]
        timers = {}


    def flush_item(itemId):
        items = buffers.pop(itemId, [])
        timers.pop(itemId, None)
        if items:
            out_q.put({'itemId': itemId, 'lances': items})

        while not stop_event.is_set():
                try:
                    msg = in_q.get(timeout=0.1)
                except Exception:
        # tempo para checar timers
                    msg = None
                if msg is not None:
        # valida item existe
                    itemId = msg.get('itemId')
                if not buscar_item_por_id(itemId):
        # descartar ou log
                    continue
                lst = buffers.setdefault(itemId, [])
                lst.append(msg)
        # reiniciar timer
                timers[itemId] = time.time() + (batch_window_ms / 1000.0)


        # checar timers expirados
                now = time.time()
                expired = [k for k, t in timers.items() if t <= now]
                for k in expired:
                    flush_item(k)
                time.sleep(0.01)

        # antes de sair, flush tudo
        for k in list(buffers.keys()):
            out_q.put({'itemId': k, 'lances': buffers[k]})

    t = Thread(target=run, daemon=True)
    t.start()
    return t