// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString, PyTuple};
use std::cmp::{max, min};

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

fn normalize_kernel(
    _py: Python<'_>,
    kernel: Bound<'_, PyTuple>,
    should_normalize: bool,
) -> Vec<f64> {
    let mut items = Vec::with_capacity(kernel.len());
    let mut sum = 0.0;

    for item in kernel.iter() {
        let val = if let Ok(f) = item.extract::<f64>() {
            f
        } else if let Ok(i) = item.extract::<i64>() {
            i as f64
        } else if let Ok(s) = item.extract::<&str>() {
            s.parse::<f64>().unwrap_or(0.0)
        } else if let Ok(py_str) = item.downcast::<PyString>() {
            py_str
                .to_str()
                .ok()
                .and_then(|s| s.parse::<f64>().ok())
                .unwrap_or(0.0)
        } else {
            0.0
        };

        sum += val;
        items.push(val);
    }

    if should_normalize && sum != 0.0 {
        for v in &mut items {
            *v /= sum;
        }
    }

    items
}

/// apply(image_mode, buffer, width, height, kernel, columns_count, normalize) -> bytes
///
/// Applies a convolution filter using a given kernel.
#[pyfunction(signature = (image_mode_str, buffer, width, height, kernel, columns_count, normalize))]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    buffer: &[u8],
    width: usize,
    height: usize,
    kernel: Bound<'_, PyTuple>,
    columns_count: usize,
    normalize: bool,
) -> PyResult<Py<PyBytes>> {
    let kernel_size = kernel.len();
    if kernel_size % columns_count != 0
        || kernel_size % 2 == 0
        || (kernel_size / columns_count) % 2 == 0
    {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("erro..."));
    }

    let kernel_vec = normalize_kernel(py, kernel, normalize);
    let num_bytes = bytes_per_pixel(image_mode_str);
    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');
    let a_idx = rgb_order(image_mode_str, 'A');

    let mut out_buffer = buffer.to_vec();
    let copy_buffer = buffer.to_vec();

    let rows_count = kernel_size / columns_count;
    let mid_x = columns_count / 2;
    let mid_y = rows_count / 2;
    let max_width_idx = width - 1;
    let max_height_idx = height - 1;
    let width_bytes_count = width * num_bytes;

    for img_y in 0..height {
        for img_x in 0..width {
            let mut sum_r = 0.0;
            let mut sum_g = 0.0;
            let mut sum_b = 0.0;
            let mut sum_a = 0.0;

            for pos_y in (img_y as isize - mid_y as isize)..=(img_y as isize + mid_y as isize) {
                for pos_x in (img_x as isize - mid_x as isize)..=(img_x as isize + mid_x as isize) {
                    let kernel_x = (pos_x - img_x as isize + mid_x as isize) as usize;
                    let kernel_y = (pos_y - img_y as isize + mid_y as isize) as usize;
                    let kernel_value = kernel_vec[kernel_y * columns_count + kernel_x];

                    let clamped_y = min(max(pos_y, 0), max_height_idx as isize) as usize;
                    let clamped_x = min(max(pos_x, 0), max_width_idx as isize) as usize;
                    let tmp_idx = clamped_y * width_bytes_count + clamped_x * num_bytes;

                    sum_r += copy_buffer[tmp_idx + r_idx] as f64 * kernel_value;
                    sum_g += copy_buffer[tmp_idx + g_idx] as f64 * kernel_value;
                    sum_b += copy_buffer[tmp_idx + b_idx] as f64 * kernel_value;
                    if num_bytes > 3 {
                        sum_a += copy_buffer[tmp_idx + a_idx] as f64 * kernel_value;
                    }
                }
            }

            let img_idx = img_y * width * num_bytes + img_x * num_bytes;
            out_buffer[img_idx + r_idx] = adjust_color(sum_r as i32);
            out_buffer[img_idx + g_idx] = adjust_color(sum_g as i32);
            out_buffer[img_idx + b_idx] = adjust_color(sum_b as i32);
            if num_bytes > 3 {
                out_buffer[img_idx + a_idx] = adjust_color(sum_a as i32);
            }
        }
    }
    Ok(PyBytes::new(py, &out_buffer).into())
}

#[pymodule]
fn _convolution(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
