# ddi-l-native (stand-in)

This wheel stands in for [ddi-l](https://github.com/pbisson44/ddi)'s native XML
core on a platform with no compiled `ddi-l-native` wheel. It contains no code
ddi-l runs: ddi-l sees that the native core is missing and reads and writes XML
with lxml or the standard library, so installing ddi-l never compiles Rust.

Compiled wheels exist for Linux (x86_64, aarch64), macOS and Windows (x64), for
CPython 3.11 and later; pip prefers them wherever they fit.
