// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use utils_lib::{bytes_per_pixel, rgb_order};

/// Applies a histogram equalization algorithm filter.
///
/// apply(image_mode: str, buffer: bytes) -> bytes
/// Assumes `buffer` is a raw RGB(A) byte array and returns the equalized version.
#[pyfunction]
fn apply(py: Python<'_>, image_mode_str: &str, buffer: &[u8]) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let num_bytes = bytes_per_pixel(image_mode_str);
    let area = buffer.len() / num_bytes;

    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    let mut red_hist = [0usize; 256];
    let mut green_hist = [0usize; 256];
    let mut blue_hist = [0usize; 256];

    buffer.chunks_exact(num_bytes).for_each(|chunk| {
        let r = chunk[r_idx] as usize;
        let g = chunk[g_idx] as usize;
        let b = chunk[b_idx] as usize;

        red_hist[r] += 1;
        green_hist[g] += 1;
        blue_hist[b] += 1;
    });

    let mut red_cum = [0usize; 256];
    let mut green_cum = [0usize; 256];
    let mut blue_cum = [0usize; 256];

    let mut r_cdf = 0;
    let mut g_cdf = 0;
    let mut b_cdf = 0;

    for i in 0..256 {
        r_cdf += red_hist[i];
        g_cdf += green_hist[i];
        b_cdf += blue_hist[i];

        if red_hist[i] > 0 {
            red_cum[i] = r_cdf;
        }
        if green_hist[i] > 0 {
            green_cum[i] = g_cdf;
        }
        if blue_hist[i] > 0 {
            blue_cum[i] = b_cdf;
        }
    }

    let r_min_cdf = red_cum.iter().find(|&&v| v > 0).copied().unwrap_or(0);
    let g_min_cdf = green_cum.iter().find(|&&v| v > 0).copied().unwrap_or(0);
    let b_min_cdf = blue_cum.iter().find(|&&v| v > 0).copied().unwrap_or(0);

    buffer.chunks_exact_mut(num_bytes).for_each(|chunk| {
        let r = chunk[r_idx] as usize;
        let g = chunk[g_idx] as usize;
        let b = chunk[b_idx] as usize;

        chunk[r_idx] = equalize_value(red_cum[r], r_min_cdf, area);
        chunk[g_idx] = equalize_value(green_cum[g], g_min_cdf, area);
        chunk[b_idx] = equalize_value(blue_cum[b], b_min_cdf, area);
    });

    PyBytes::new(py, &buffer).into()
}

fn equalize_value(cum_freq: usize, min_cdf: usize, area: usize) -> u8 {
    if area == min_cdf {
        return 0;
    }
    let val = ((cum_freq - min_cdf) as f64 / (area - min_cdf) as f64) * 255.0;
    val.clamp(0.0, 255.0).round() as u8
}

#[pymodule]
fn _equalize(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
