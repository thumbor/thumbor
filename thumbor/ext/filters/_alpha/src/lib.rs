// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

/// Applies an alpha filter assuming `delta` is an integer between 0 and 100.
///
/// apply(image_mode: str, delta: int, buffer: bytes) -> bytes
#[pyfunction]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    delta_int: i32,
    buffer: &[u8],
) -> PyResult<Py<PyBytes>> {
    let num_bytes = bytes_per_pixel(image_mode_str);
    let alpha_idx = rgb_order(image_mode_str, 'A');
    let delta_int = -(255 * delta_int) / 100;

    PyBytes::new_with(py, buffer.len(), |out| {
        out.copy_from_slice(buffer);
        out.chunks_exact_mut(num_bytes).for_each(|chunk| {
            let alpha = chunk[alpha_idx] as i32;
            chunk[alpha_idx] = adjust_color(alpha + delta_int);
        });

        Ok(())
    })
    .map(Into::into)
}

#[pymodule]
fn _alpha(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
