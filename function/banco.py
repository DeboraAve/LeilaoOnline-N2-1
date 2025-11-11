# Simulador de banco usando arquivos JSON em /data
import json
from pathlib import Path
from threading import Lock

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

_lock = Lock()

def _read_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write_json(filename: str, obj):
    path = DATA_DIR / filename
    with _lock:
        with path.open('w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)


# API mínima usada pelas lambdas


def listar_itens():
    return _read_json('itensLeilao.json')


def buscar_item_por_id(itemId: str):
    itens = listar_itens()
    for it in itens:
        if it.get('itemId') == itemId:
            return it
        return None

def listar_lances():
    return _read_json('lancesItens.json')

def gravar_lances(novos_lances):
# adiciona os novos lances ao array e salva ordenando por timestamp asc
    atual = listar_lances()
    combinado = atual + list(novos_lances)
    combinado.sort(key=lambda x: x.get('timestamp', 0))
    _write_json('lancesItens.json', combinado)
    return combinado

def salvar_log_fila(payload):
# manter log em filaLances.json (apenas append)
    arr = _read_json('filaLances.json')
    arr.append(payload)
    _write_json('filaLances.json', arr)