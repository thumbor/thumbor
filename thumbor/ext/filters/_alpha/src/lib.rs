// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{bytes_per_pixel, rgb_order};

/// Applies an alpha filter assuming `delta` is an integer between 0 and 100.
///
/// apply(image_mode: str, delta: int, buffer: bytes) -> bytes
#[pyfunction]
fn apply(py: Python<'_>, image_mode_str: &str, delta_int: i32, buffer: &[u8]) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode_str);
    let alpha_idx = rgb_order(image_mode_str, 'A');
    let delta_int = -(255 * delta_int) / 100;

    buffer.chunks_exact_mut(num_bytes).for_each(|chunk| {
        let mut alpha = chunk[alpha_idx] as i32;
        alpha = (alpha + delta_int).clamp(0, 255);
        chunk[alpha_idx] = alpha as u8;
    });

    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _alpha(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
