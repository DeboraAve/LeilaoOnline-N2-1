# registraLancesItens.py
# define: def registraLancesItens(stop_event=None)
# Consome de 'filaLanceItem' e grava no arquivo lancesItens.json via banco.gravar_lances


from .fila import get_queue
from .banco import gravar_lances
from threading import Thread, Event
import time




def registraLancesItens(stop_event: Event = None):
    in_q = get_queue('filaLanceItem')
    if stop_event is None:
        stop_event = Event()


    def run():
        while not stop_event.is_set():
            try:
                msg = in_q.get(timeout=0.1)
            except Exception:
                msg = None


            if msg is not None:
        # msg: { itemId, lances: [ ... ] }
                itemId = msg.get('itemId')
                lances = msg.get('lances', [])
        # podemos acrescentar validações aqui
                if lances:
                    gravar_lances(lances)
            time.sleep(0.01)


    t = Thread(target=run, daemon=True)
    t.start()
    return t