// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color_double, bytes_per_pixel, rgb_order};

fn compute_histogram(channel: usize, buffer: &[u8], pixel_size: usize) -> [usize; 256] {
    let mut hist = [0usize; 256];
    buffer.chunks_exact(pixel_size).for_each(|chunk| {
        hist[chunk[channel] as usize] += 1;
    });
    hist
}

fn compute_cdf(hist: &[usize; 256]) -> ([usize; 256], usize) {
    let mut cdf = [0usize; 256];
    let mut cum = 0;
    let mut min_cdf = None;

    for (i, &count) in hist.iter().enumerate() {
        cum += count;
        cdf[i] = cum;
        if count > 0 && min_cdf.is_none() {
            min_cdf = Some(cum);
        }
    }

    (cdf, min_cdf.unwrap_or(0))
}

fn equalize_value(cum_freq: usize, min_cdf: usize, area: usize) -> u8 {
    if area == min_cdf {
        return 0;
    }
    let val = ((cum_freq - min_cdf) as f64 / (area - min_cdf) as f64) * 255.0;
    adjust_color_double(val)
}

/// Applies a histogram equalization algorithm filter.
///
/// apply(image_mode: str, buffer: bytes) -> bytes
/// Assumes `buffer` is a raw RGB(A) byte array and returns the equalized version.
#[pyfunction]
fn apply(py: Python<'_>, image_mode_str: &str, buffer: &[u8]) -> Py<PyBytes> {
    let mut buffer = buffer.to_vec();
    let pixel_size = bytes_per_pixel(image_mode_str);
    let area = buffer.len() / pixel_size;

    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');

    let red_hist = compute_histogram(r_idx, &buffer, pixel_size);
    let green_hist = compute_histogram(g_idx, &buffer, pixel_size);
    let blue_hist = compute_histogram(b_idx, &buffer, pixel_size);

    let (red_cdf, r_min) = compute_cdf(&red_hist);
    let (green_cdf, g_min) = compute_cdf(&green_hist);
    let (blue_cdf, b_min) = compute_cdf(&blue_hist);

    buffer.chunks_exact_mut(pixel_size).for_each(|chunk| {
        chunk[r_idx] = equalize_value(red_cdf[chunk[r_idx] as usize], r_min, area);
        chunk[g_idx] = equalize_value(green_cdf[chunk[g_idx] as usize], g_min, area);
        chunk[b_idx] = equalize_value(blue_cdf[chunk[b_idx] as usize], b_min, area);
    });

    PyBytes::new(py, &buffer).into()
}

#[pymodule]
fn _equalize(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
