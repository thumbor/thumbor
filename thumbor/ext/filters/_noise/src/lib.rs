// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

struct SimpleRng(u64);

impl SimpleRng {
    fn new(seed: u64) -> Self {
        SimpleRng(seed)
    }

    fn next(&mut self) -> u32 {
        self.0 = self.0.wrapping_mul(1103515245).wrapping_add(12345);
        ((self.0 >> 16) & 0x7FFF) as u32
    }

    fn gen_range(&mut self, low: i32, high: i32) -> i32 {
        let r = self.next() as i32;
        low + (r % (high - low + 1))
    }
}

/// apply(image_mode, amount, buffer, seed=None) -> bytes
///
/// Adds noise to the image buffer. `amount` controls noise intensity (0–100),
/// and `seed` allows deterministic output.
#[pyfunction]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    amount_int: i32,
    buffer: &[u8],
    seed: Option<u64>,
) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode_str);

    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    if amount_int > 0 {
        let mut rng = SimpleRng::new(seed.unwrap_or(42));
        let size = buffer.len().saturating_sub(num_bytes);
        let mut i = 0;
        let half = amount_int >> 1;

        while i <= size {
            let noise = rng.gen_range(-(half), half);

            let r = buffer[i + r_idx] as i32 + noise;
            let g = buffer[i + g_idx] as i32 + noise;
            let b = buffer[i + b_idx] as i32 + noise;

            buffer[i + r_idx] = adjust_color(r);
            buffer[i + g_idx] = adjust_color(g);
            buffer[i + b_idx] = adjust_color(b);

            i += num_bytes;
        }
    }

    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _noise(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
