"""Publication plane core. Names resolve on first access (PEP 562), so importing one submodule
(for example receipt_writer, which is standard-library only) does not import publication_gate and
the governance modules it uses."""
from importlib import import_module

_EXPORTS = {
    "PublicationReceiptWriter": ".receipt_writer",
    "PublicationGate": ".publication_gate",
    "GateResult": ".publication_gate",
    "PublicationAction": ".publication_gate",
    "ResultSnapshot": ".result_snapshot",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(_EXPORTS[name], __name__), name)
    globals()[name] = value
    return value
