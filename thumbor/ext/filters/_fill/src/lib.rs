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
/// - delta (int): The delta value used in the fill operation.
/// - buffer (bytes): The image data buffer as a Python bytes/string.
///
/// Returns:
/// - tuple: A tuple containing (r, g, b) values representing the fill color.
#[pyfunction]
fn apply(image_mode: &str, buffer: &[u8]) -> PyResult<(u64, u64, u64)> {
    let size = buffer.len();
    let num_bytes = bytes_per_pixel(image_mode);
    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');

    // Validate the inputs
    if num_bytes == 0 || size < num_bytes {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Invalid image data or mode",
        ));
    }

    let image_area = size / num_bytes;
    let mut r: u64 = 0;
    let mut g: u64 = 0;
    let mut b: u64 = 0;

    // Sum the values of R, G, and B channels for all pixels
    for i in (0..size).step_by(num_bytes) {
        r += buffer[i + r_idx] as u64;
        g += buffer[i + g_idx] as u64;
        b += buffer[i + b_idx] as u64;
    }

    // Compute the average for each channel
    r /= image_area as u64;
    g /= image_area as u64;
    b /= image_area as u64;

    Ok((r, g, b))
}

#[pymodule]
fn _fill(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
