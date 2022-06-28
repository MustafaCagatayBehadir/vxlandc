import ncs


class DiffIterator:
    def __init__(self):
        self._data = []

    def __call__(self, kp, op, ov, nv):
        self._data.append({
            "kp": str(kp),
            "op": op,
            "ov": ncs.maagic.as_pyval(ov) if ov else "",
            "nv": ncs.maagic.as_pyval(nv) if nv else ""
        })
