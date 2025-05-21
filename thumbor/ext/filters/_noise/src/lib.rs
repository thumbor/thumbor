// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::os::raw::{c_int, c_uint};

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

extern "C" {
    fn random() -> c_int;
    fn srandom(seed: c_uint);
}

fn set_seed(seed: u32) {
    unsafe {
        srandom(seed as c_uint);
    }
}

fn get_random() -> i32 {
    unsafe { random() as i32 }
}

/// apply(image_mode, amount, buffer, seed=None) -> bytes
///
/// Adds noise to the image buffer. `amount` controls noise intensity (0–100),
/// and `seed` allows deterministic output.
#[pyfunction(signature = (image_mode_str, amount, buffer, seed=None))]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    amount: i32,
    buffer: &[u8],
    seed: Option<u32>,
) -> Py<PyBytes> {
    let mut out_buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode_str);
    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    if amount > 0 {
        if let Some(s) = seed {
            set_seed(s);
        }

        out_buffer.chunks_exact_mut(num_bytes).for_each(|chunk| {
            let rand_val = (get_random() % amount) - (amount >> 1);

            let r = chunk[r_idx] as i32 + rand_val;
            let g = chunk[g_idx] as i32 + rand_val;
            let b = chunk[b_idx] as i32 + rand_val;

            chunk[r_idx] = adjust_color(r);
            chunk[g_idx] = adjust_color(g);
            chunk[b_idx] = adjust_color(b);
        });
    }

    PyBytes::new(py, &out_buffer).into()
}

#[pymodule]
fn _noise(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
