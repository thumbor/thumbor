# Strip ICC

Usage: `strip_icc()`

## Description

This filter removes any ICC information in the resulting image. Even though the
image might be smaller, removing ICC information may result in loss of quality.

## Arguments

No arguments

## Example

```
http://localhost:8888/unsafe/filters:strip_icc()/<url>
```
