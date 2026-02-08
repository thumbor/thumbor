// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

/// contrast filter module
///
/// apply(image_mode: str, delta: int, buffer: bytes) -> bytes
///
/// Applies a contrast filter assuming `delta` is an integer between -100 and 100.
/// `buffer` is a raw image byte buffer. Returns the adjusted image as a new buffer.
#[pyfunction]
fn apply(py: Python<'_>, image_mode_str: &str, delta: i32, buffer: &[u8]) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();

    let num_bytes = bytes_per_pixel(image_mode_str);
    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    let mut delta_int = delta + 100;
    delta_int = (delta_int * delta_int) / 100;

    for pixel in buffer.chunks_exact_mut(num_bytes) {
        let r = pixel[r_idx] as i32;
        let g = pixel[g_idx] as i32;
        let b = pixel[b_idx] as i32;

        let new_r = ((delta_int * (r - 128)) / 100) + 128;
        let new_g = ((delta_int * (g - 128)) / 100) + 128;
        let new_b = ((delta_int * (b - 128)) / 100) + 128;

        pixel[r_idx] = adjust_color(new_r);
        pixel[g_idx] = adjust_color(new_g);
        pixel[b_idx] = adjust_color(new_b);
    }

    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _contrast(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
