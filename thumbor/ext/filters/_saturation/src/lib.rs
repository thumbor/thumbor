// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

/// Image saturation adjustment module
///
/// apply(image_mode: str, change: float, buffer: bytes) -> bytes
///
/// Adjusts the saturation of a raw image buffer (RGB or RGBA).
#[pyfunction]
fn apply(py: Python<'_>, image_mode: &str, change: f32, buffer: &[u8]) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode);

    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');

    let size = buffer.len().saturating_sub(num_bytes);
    let mut i = 0;

    while i <= size {
        let r = buffer[i + r_idx] as f32;
        let g = buffer[i + g_idx] as f32;
        let b = buffer[i + b_idx] as f32;

        let p = (r * r * 0.299 + g * g * 0.587 + b * b * 0.114).sqrt();

        let new_r = p + (r - p) * change;
        let new_g = p + (g - p) * change;
        let new_b = p + (b - p) * change;

        buffer[i + r_idx] = adjust_color(new_r as i32);
        buffer[i + g_idx] = adjust_color(new_g as i32);
        buffer[i + b_idx] = adjust_color(new_b as i32);

        i += num_bytes;
    }
    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _saturation(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
