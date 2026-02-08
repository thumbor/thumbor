// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;

use utils_lib::{bytes_per_pixel, rgb_order};

/// Auto detects the color to fill the image with, assuming `buffer` as a
/// Python string. Returns a tuple in the format (r, g, b).
///
/// Parameters:
/// - image_mode (str): The image mode (e.g., "RGB" ou "RGBA").
/// - buffer (bytes): The image data buffer as a Python bytes/string.
///
/// Returns:
/// - tuple: A tuple containing (r, g, b) values representing the fill color.
#[pyfunction]
fn apply(image_mode: &str, buffer: &[u8]) -> PyResult<(u64, u64, u64)> {
    let num_bytes = bytes_per_pixel(image_mode);
    if num_bytes == 0 || !buffer.len().is_multiple_of(num_bytes) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Invalid image data or mode",
        ));
    }

    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');

    let mut r: u64 = 0;
    let mut g: u64 = 0;
    let mut b: u64 = 0;

    for chunk in buffer.chunks_exact(num_bytes) {
        r += chunk[r_idx] as u64;
        g += chunk[g_idx] as u64;
        b += chunk[b_idx] as u64;
    }

    let image_area = buffer.len() / num_bytes;
    Ok((
        (r / image_area as u64),
        (g / image_area as u64),
        (b / image_area as u64),
    ))
}

#[pymodule]
fn _fill(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
