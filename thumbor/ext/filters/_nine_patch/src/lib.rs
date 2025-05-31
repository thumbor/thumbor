use pyo3::prelude::*;
use pyo3::types::PyBytes;
use utils_lib::{adjust_color_double, bytes_per_pixel, rgb_order};

#[derive(Debug)]
struct Bitmap<'a> {
    width: i32,
    height: i32,
    stride: i32,
    alpha_idx: i32,
    buffer: &'a mut [u8],
}

fn get_subpixel(b: &Bitmap, x: i32, y: i32, s: i32) -> i32 {
    let pixel = ((y * b.width + x) * b.stride) as usize;
    b.buffer[pixel + s as usize] as i32
}

fn set_subpixel(b: &mut Bitmap, x: i32, y: i32, s: i32, value: i32) {
    let pixel = ((y * b.width + x) * b.stride) as usize;
    b.buffer[pixel + s as usize] = value as u8;
}

fn is_stretchy(b: &Bitmap, x: i32, y: i32) -> bool {
    for s in 0..b.stride {
        let expected = if s == b.alpha_idx { 255 } else { 0 };
        if get_subpixel(b, x, y, s) != expected {
            return false;
        }
    }
    true
}

fn compute_stretchy_width(b: &Bitmap) -> i32 {
    let mut result = 0;
    for x in 1..(b.width - 1) {
        if is_stretchy(b, x, 0) {
            result += 1;
        }
    }
    result
}

fn compute_stretchy_height(b: &Bitmap) -> i32 {
    let mut result = 0;
    for y in 1..(b.height - 1) {
        if is_stretchy(b, 0, y) {
            result += 1;
        }
    }
    result
}

fn next_row(b: &Bitmap, y: i32) -> i32 {
    let stretchy = is_stretchy(b, 0, y);
    for n in (y + 1)..(b.height - 1) {
        if is_stretchy(b, 0, n) != stretchy {
            return n;
        }
    }
    b.height - 1
}

fn next_column(b: &Bitmap, x: i32) -> i32 {
    let stretchy = is_stretchy(b, x, 0);
    for n in (x + 1)..(b.width - 1) {
        if is_stretchy(b, n, 0) != stretchy {
            return n;
        }
    }
    b.width - 1
}

fn interpolate_subpixel(
    b: &Bitmap,
    x: i32,
    y: i32,
    x_fraction: f64,
    y_fraction: f64,
    s: i32,
) -> i32 {
    let a = get_subpixel(b, x, y, s);
    let b_ = get_subpixel(b, x + 1, y, s);
    let c = get_subpixel(b, x, y + 1, s);
    let d = get_subpixel(b, x + 1, y + 1, s);

    if a == b_ && a == c && a == d {
        return a;
    }

    let combined = (a as f64) * (1.0 - x_fraction) * (1.0 - y_fraction)
        + (b_ as f64) * x_fraction * (1.0 - y_fraction)
        + (c as f64) * (1.0 - x_fraction) * y_fraction
        + (d as f64) * x_fraction * y_fraction;

    adjust_color_double(combined) as i32
}

#[allow(clippy::too_many_arguments)]
fn paste_rectangle(
    source: &Bitmap,
    sx: i32,
    sy: i32,
    sw: i32,
    sh: i32,
    target: &mut Bitmap,
    tx: i32,
    ty: i32,
    tw: i32,
    th: i32,
) {
    if tx + tw > target.width || ty + th > target.height {
        return;
    }

    let x_ratio = (sw - 1) as f64 / tw as f64;
    let y_ratio = (sh - 1) as f64 / th as f64;

    for y in 0..th {
        let source_y = (y_ratio * y as f64) as i32;
        let y_fraction = y_ratio * y as f64 - source_y as f64;

        for x in 0..tw {
            let source_x = (x_ratio * x as f64) as i32;
            let x_fraction = x_ratio * x as f64 - source_x as f64;

            let source_alpha = 255
                - interpolate_subpixel(
                    source,
                    sx + source_x,
                    sy + source_y,
                    x_fraction,
                    y_fraction,
                    source.alpha_idx,
                );
            let target_alpha = 255 - get_subpixel(target, tx + x, ty + y, target.alpha_idx);

            for s in 0..source.stride {
                if s == source.alpha_idx {
                    continue;
                }

                let source_value = interpolate_subpixel(
                    source,
                    sx + source_x,
                    sy + source_y,
                    x_fraction,
                    y_fraction,
                    s,
                );
                let target_value = get_subpixel(target, tx + x, ty + y, s);
                let pixel = ((1.0 - (source_alpha as f64 / 255.0)) * source_value as f64)
                    + ((1.0 - (target_alpha as f64 / 255.0))
                        * target_value as f64
                        * (source_alpha as f64 / 255.0));
                set_subpixel(target, tx + x, ty + y, s, adjust_color_double(pixel) as i32);
            }
        }
    }
}

fn unpack_bitmap<'a>(
    image_mode: &str,
    buffer: &'a mut [u8],
    width: i32,
    height: i32,
) -> Bitmap<'a> {
    let stride = bytes_per_pixel(image_mode) as i32;
    let alpha_idx = rgb_order(image_mode, 'A') as i32;

    Bitmap {
        width,
        height,
        stride,
        alpha_idx,
        buffer,
    }
}

/// Returns a tuple of (left, top, right, bottom) containing the padding encoded
/// in the nine patch. The padding is the number of non-black pixels along the
/// right or bottom edge of the image. This does not include the corner pixel.
///
/// Arguments
/// - `image_mode` - Image mode string, e.g. "RGBA"
/// - `nine_patch_buffer` - The raw image buffer of the nine patch as bytes
/// - `nine_patch_w` - Width of the nine patch image
/// - `nine_patch_h` - Height of the nine patch image
///
/// Returns
/// A tuple `(left, top, right, bottom)` representing the padding values.
#[pyfunction]
fn get_padding(
    image_mode: &str,
    nine_patch_buffer: &[u8],
    nine_patch_w: i32,
    nine_patch_h: i32,
) -> PyResult<(i32, i32, i32, i32)> {
    let mut nine_patch_vec = nine_patch_buffer.to_vec();
    let nine_patch = unpack_bitmap(image_mode, &mut nine_patch_vec, nine_patch_w, nine_patch_h);

    let mut left = 0;
    let mut top = 0;
    let mut right = 0;
    let mut bottom = 0;

    for x in 1..(nine_patch.width - 1) {
        if is_stretchy(&nine_patch, x, nine_patch.height - 1) {
            left = x - 1;
            break;
        }
    }
    for x in (1..=(nine_patch.width - 2)).rev() {
        if is_stretchy(&nine_patch, x, nine_patch.height - 1) {
            right = nine_patch.width - 2 - x;
            break;
        }
    }
    for y in 1..(nine_patch.height - 1) {
        if is_stretchy(&nine_patch, nine_patch.width - 1, y) {
            top = y - 1;
            break;
        }
    }
    for y in (1..=(nine_patch.height - 2)).rev() {
        if is_stretchy(&nine_patch, nine_patch.width - 1, y) {
            bottom = nine_patch.height - 2 - y;
            break;
        }
    }

    Ok((left, top, right, bottom))
}

/// Adjusts the size of a target image by applying a nine-patch stretch from a source nine-patch image.
///
/// Arguments
/// - `py` - Python interpreter token
/// - `image_mode` - Image mode string, e.g. `"RGBA"`
/// - `target_buffer` - Raw image buffer of the target image as bytes
/// - `target_w` - Width of the target image
/// - `target_h` - Height of the target image
/// - `nine_patch_buffer` - Raw image buffer of the nine patch as bytes
/// - `nine_patch_w` - Width of the nine patch image
/// - `nine_patch_h` - Height of the nine patch image
///
/// Returns
/// A new image buffer with the nine-patch applied and stretched as needed.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python,
    image_mode: &str,
    target_buffer: &[u8],
    target_w: i32,
    target_h: i32,
    nine_patch_buffer: &[u8],
    nine_patch_w: i32,
    nine_patch_h: i32,
) -> PyResult<PyObject> {
    let mut target_vec = target_buffer.to_vec();
    let mut nine_patch_vec = nine_patch_buffer.to_vec();
    let mut target = unpack_bitmap(image_mode, &mut target_vec, target_w, target_h);
    let nine_patch = unpack_bitmap(image_mode, &mut nine_patch_vec, nine_patch_w, nine_patch_h);

    let source_stretchy_width = compute_stretchy_width(&nine_patch);
    let source_stretchy_height = compute_stretchy_height(&nine_patch);

    let fixed_width = nine_patch.width - 2 - source_stretchy_width;
    let fixed_height = nine_patch.height - 2 - source_stretchy_height;

    let mut target_stretchy_width = target.width - fixed_width;
    let mut target_stretchy_height = target.height - fixed_height;

    if target_stretchy_width < 0 {
        target_stretchy_width = 0;
    }
    if target_stretchy_height < 0 {
        target_stretchy_height = 0;
    }

    let mut source_y = 1;
    let mut target_y = 0;

    while source_y < nine_patch.height - 1 {
        let row_stretchy = is_stretchy(&nine_patch, 0, source_y);
        let source_height = next_row(&nine_patch, source_y) - source_y;
        let target_height = if row_stretchy {
            ((source_height as f64 / source_stretchy_height as f64) * target_stretchy_height as f64
                + 0.5) as i32
        } else {
            source_height
        };

        let mut source_x = 1;
        let mut target_x = 0;
        while source_x < nine_patch.width - 1 {
            let col_stretchy = is_stretchy(&nine_patch, source_x, 0);
            let source_width = next_column(&nine_patch, source_x) - source_x;
            let target_width = if col_stretchy {
                ((source_width as f64 / source_stretchy_width as f64)
                    * target_stretchy_width as f64
                    + 0.5) as i32
            } else {
                source_width
            };

            paste_rectangle(
                &nine_patch,
                source_x,
                source_y,
                source_width,
                source_height,
                &mut target,
                target_x,
                target_y,
                target_width,
                target_height,
            );

            source_x += source_width;
            target_x += target_width;
        }

        source_y += source_height;
        target_y += target_height;
    }

    Ok(PyBytes::new(py, target.buffer).into())
}

#[pymodule]
fn _nine_patch(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    m.add_function(wrap_pyfunction!(get_padding, &m)?)?;
    Ok(())
}
