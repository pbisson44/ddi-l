"""Stand-in for ddi-l's native XML core, on a platform with no compiled wheel.

ddi-l reads and writes XML with lxml or the standard library instead.
"""

raise ModuleNotFoundError(
    "ddi-l-native has no compiled core for this platform",
    name="ddi_l_native",
)
