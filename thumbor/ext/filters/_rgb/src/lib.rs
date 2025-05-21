use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

/// Adjusts R, G, and B channels of an image buffer.
///
/// Arguments
/// - `image_mode` - Image mode, e.g., `"RGB"` or `"RGBA"`
/// - `delta_r` - Percentage adjustment to red channel
/// - `delta_g` - Percentage adjustment to green channel
/// - `delta_b` - Percentage adjustment to blue channel
/// - `buffer` - The raw image buffer (as bytes)
///
/// Returns
/// - Modified image buffer (as `bytes`)
#[pyfunction]
fn apply(
    image_mode: &str,
    delta_r: i32,
    delta_g: i32,
    delta_b: i32,
    buffer: &[u8],
    py: Python,
) -> PyResult<PyObject> {
    let num_bytes = bytes_per_pixel(image_mode);

    let delta_r = (255 * delta_r) / 100;
    let delta_g = (255 * delta_g) / 100;
    let delta_b = (255 * delta_b) / 100;

    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');

    if buffer.len() % num_bytes != 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Buffer length is not a multiple of bytes per pixel",
        ));
    }

    let mut out = buffer.to_vec();

    let size = out.len();
    let limit = size.saturating_sub(num_bytes);

    let mut i = 0;
    while i <= limit {
        let r = out[i + r_idx] as i32 + delta_r;
        let g = out[i + g_idx] as i32 + delta_g;
        let b = out[i + b_idx] as i32 + delta_b;

        out[i + r_idx] = adjust_color(r);
        out[i + g_idx] = adjust_color(g);
        out[i + b_idx] = adjust_color(b);

        i += num_bytes;
    }

    Ok(PyBytes::new(py, &out).into())
}

#[pymodule]
fn _rgb(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
