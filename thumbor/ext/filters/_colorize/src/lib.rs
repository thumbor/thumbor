// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, colorize, rgb_order};

/// apply(image_mode, red_pct, green_pct, blue_pct, fill_r, fill_g, fill_b, buffer) -> bytes
///
/// Applies a colorize filter by blending RGB values towards the specified fill color.
/// Each channel is adjusted proportionally to its blend percentage.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    red_percent: i32,
    green_percent: i32,
    blue_percent: i32,
    fill_red: i32,
    fill_green: i32,
    fill_blue: i32,
    buffer: &[u8],
) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode_str);

    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    buffer.chunks_exact_mut(num_bytes).for_each(|chunk| {
        chunk[r_idx] = adjust_color(colorize(chunk[r_idx], red_percent, fill_red));
        chunk[g_idx] = adjust_color(colorize(chunk[g_idx], green_percent, fill_green));
        chunk[b_idx] = adjust_color(colorize(chunk[b_idx], blue_percent, fill_blue));
    });

    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _colorize(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
