# submeteLance.py
# define: def submeteLance

from .fila import get_queue
from .banco import buscar_item_por_id, salvar_log_fila
from time import time


def _validate(payload: dict):
    if not isinstance(payload, dict):
        return False, 'payload must be an object'
    if not payload.get('itemId') or not payload.get('bidderId'):
        return False, 'itemId and bidderId required'
    q = payload.get('quantity')
    if not isinstance(q, int) or q <= 0:
        return False, 'quantity must be positive integer'
        p = payload.get('price')
    if not (isinstance(p, int) or isinstance(p, float)) or p <= 0:
        return False, 'price must be positive number'
    if buscar_item_por_id(payload.get('itemId')) is None:
        return False, 'item not found'
    return True, None


def submeteLance(event: dict):
#Valida e publica a mensagem na fila 'filaLances'. Retorna dict com status."""
    ok, reason = _validate(event)
    if not ok:
        return {'status': 'error', 'reason': reason}

    msg = dict(event)
    if 'timestamp' not in msg:
        msg['timestamp'] = int(time() * 1000)

    q = get_queue('filaLances')
    q.put(msg)

    try:
        salvar_log_fila({'action': 'put', 'queue': 'filaLances', 'message': msg})
    except Exception:
        pass
    return {'status': 'ok'}