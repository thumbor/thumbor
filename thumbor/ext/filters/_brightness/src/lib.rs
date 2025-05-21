// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

/// apply(delta, buffer) -> bytes
///
/// Applies a brightness filter assuming 'delta' as an integer value between -100 and 100,
/// and 'buffer' as a Python bytes object. Returns the modified buffer.
#[pyfunction(signature = (image_mode_str, delta, buffer))]
fn apply(py: Python<'_>, image_mode_str: &str, delta: i32, buffer: &[u8]) -> Py<PyBytes> {
    let mut out_buffer = buffer.to_vec();
    let size = out_buffer.len();

    let num_bytes = bytes_per_pixel(image_mode_str);
    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    let delta_int = (255 * delta) / 100;

    let limit = size.saturating_sub(num_bytes);
    let mut i = 0;

    while i <= limit {
        let r = out_buffer[i + r_idx] as i32 + delta_int;
        let g = out_buffer[i + g_idx] as i32 + delta_int;
        let b = out_buffer[i + b_idx] as i32 + delta_int;

        out_buffer[i + r_idx] = adjust_color(r);
        out_buffer[i + g_idx] = adjust_color(g);
        out_buffer[i + b_idx] = adjust_color(b);

        i += num_bytes;
    }

    PyBytes::new(py, &out_buffer).into()
}

#[pymodule]
fn _brightness(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
