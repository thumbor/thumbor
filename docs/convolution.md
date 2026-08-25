# Convolution

Usage: `convolution(matrix_items, number_of_columns, should_normalize)`

## Description

This filter runs a convolution matrix (or kernel) on the image. See
[image kernels](http://en.wikipedia.org/wiki/Kernel) for details on the process.
Edge pixels are always extended outside the image area.

## Arguments

- `matrix_items` - Semicolon separated integer or decimal matrix items. Decimal
  values must include digits after the decimal point, e.g. `1.5`.
- `number_of_columns` - Number of columns in the matrix.
- `should_normalize` - Whether or not we should divide each matrix item by the
  sum of all items.

## Example

```{image} images/tom_before_brightness.jpg
---
alt: Picture before the convolution filter
---
```

Normalized Matrix:

```
1 2 1
2 4 2
2 1 2
```

```
http://localhost:8888/unsafe/filters:convolution(1;2;1;2;4;2;1;2;1,3,true)/<url>
```

```{image} images/tom_after_convolution1.jpg
---
alt: Picture after the convolution filter
---
```

Matrix:

```
-1 -1 -1
-1  8 -1
-1 -1 -1
```

```
http://thumbor/unsafe/filters:convolution(<matrix>,3,false)/<url>
```

```{image} images/tom_after_convolution2.jpg
---
alt: Picture after the convolution filter
---
```
