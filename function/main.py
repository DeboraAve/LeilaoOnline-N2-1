# main_testes.py
# Executa testes manuais: lambdas isoladas e integração do fluxo


from function.fila import get_queue, clear_queues
from function.banco import listar_lances, listar_itens
from function.submeteLance import submeteLance
from function.gerenciaLancesItem import gerenciaLancesItem
from function.registraLancesItens import registraLancesItens
from threading import Event
import time
import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def teste_unitario_submete():
    clear_queues()
    payload = { 'itemId': 'ITEM-001', 'bidderId': 'CLIENTE-1', 'quantity': 2, 'price': 300.0 }
    res = submeteLance(payload)
    print('submeteLance ->', res)
    q = get_queue('filaLances')
    print('filaLances size (deveria ser 1):', q.qsize())

def teste_unitario_gerencia():
    clear_queues()
    # colocar 2 mensagens para o mesmo item
    submeteLance({ 'itemId': 'ITEM-002', 'bidderId': 'A', 'quantity': 1, 'price': 200.0 })
    submeteLance({ 'itemId': 'ITEM-002', 'bidderId': 'B', 'quantity': 3, 'price': 190.0 })
    stop = Event()
    t = gerenciaLancesItem(stop, batch_window_ms=150)
    # aguardar flush da janela
    time.sleep(0.4)
    stop.set()
    t.join(timeout=1)
    q = get_queue('filaLanceItem')
    print('filaLanceItem size (deveria ser >=1):', q.qsize())

def teste_unitario_registra():
    clear_queues()
# simular envio direto à fila de persistencia
    q = get_queue('filaLanceItem')
    msg = { 'itemId': 'ITEM-003', 'lances': [ { 'itemId': 'ITEM-003', 'bidderId': 'Z', 'quantity': 1, 'price': 610.0, 'timestamp': int(time.time()*1000) } ] }
    q.put(msg)
    stop = Event()
    t = registraLancesItens(stop)
    time.sleep(0.2)
    stop.set()
    t.join(timeout=1)
    lances = listar_lances()
    print('lances count (>=1):', len(lances))


def teste_integracao():
    clear_queues()
    stop_mgr = Event()
    stop_reg = Event()
    t1 = gerenciaLancesItem(stop_mgr, batch_window_ms=80)
    t2 = registraLancesItens(stop_reg)

# submeter muitos lances
    submeteLance({ 'itemId': 'ITEM-001', 'bidderId': 'C', 'quantity': 2, 'price': 260.0 })
    submeteLance({ 'itemId': 'ITEM-002', 'bidderId': 'D', 'quantity': 1, 'price': 185.0 })
    submeteLance({ 'itemId': 'ITEM-001', 'bidderId': 'E', 'quantity': 1, 'price': 270.0 })

    time.sleep(1.0)


# parar consumidores
    stop_mgr.set()
    stop_reg.set()
    t1.join(timeout=1)
    t2.join(timeout=1)


# verificar DB
    lances = listar_lances()
    print('Total lances no DB:', len(lances))
    try:
        with open(DATA_DIR / 'lancesItens.json', 'r', encoding='utf-8') as f: print('Conteudo lancesItens.json:')
        print(f.read())
    except Exception as e:
        print('erro lendo lancesItens.json', e)


    if __name__ == '__main__':
        print('Itens disponíveis:')
        print(j)