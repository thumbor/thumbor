// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use utils_lib::{adjust_color_double, bytes_per_pixel, rgb_order};

enum CurveError {
    NotEnoughPoints,
}

impl From<CurveError> for PyErr {
    fn from(err: CurveError) -> Self {
        match err {
            CurveError::NotEnoughPoints => {
                PyValueError::new_err("Not enough points to compute spline.")
            }
        }
    }
}

fn get_curve(points: &Bound<'_, PyTuple>) -> PyResult<Vec<u8>> {
    let mut items = Vec::with_capacity(points.len() * 2);
    for p in points.iter() {
        let (x, y): (u8, u8) = p.extract()?;
        items.extend_from_slice(&[x, y]);
    }
    Ok(items)
}

fn calculate_second_derivative(points: &[u8], n: usize) -> Result<Vec<f64>, CurveError> {
    if n < 3 {
        return Err(CurveError::NotEnoughPoints);
    }

    let mut u = vec![0.0; n - 1];
    let mut y2 = vec![0.0; n];

    for i in 1..(n - 1) {
        let idx_i = i * 2;
        let idx_prev = (i - 1) * 2;
        let idx_next = (i + 1) * 2;

        let (x_prev, x_i, x_next) = (
            f64::from(points[idx_prev]),
            f64::from(points[idx_i]),
            f64::from(points[idx_next]),
        );

        let (y_prev, y_i, y_next) = (
            f64::from(points[idx_prev + 1]),
            f64::from(points[idx_i + 1]),
            f64::from(points[idx_next + 1]),
        );

        let sig = (x_i - x_prev) / (x_next - x_prev);
        let p = sig * y2[i - 1] + 2.0;

        let val1 = (y_next - y_i) / (x_next - x_i);
        let val2 = (y_i - y_prev) / (x_i - x_prev);

        y2[i] = (sig - 1.0) / p;
        u[i] = (6.0 * (val1 - val2) / (x_next - x_prev) - sig * u[i - 1]) / p;
    }

    for i in (0..(n - 1)).rev() {
        y2[i] = y2[i] * y2[i + 1] + u[i];
    }

    Ok(y2)
}

fn cubic_spline_interpolation(
    curve_points: &[u8],
    points_count: usize,
) -> Result<[u8; 256], CurveError> {
    let mut lut = [0; 256];

    if points_count < 2 {
        let fill_value = curve_points.get(1).copied().unwrap_or(0);
        lut.fill(fill_value);
        // A alteração está aqui:
        if let Some(&x) = curve_points.first() {
            lut[x as usize] = fill_value;
        }
        return Ok(lut);
    }

    if points_count == 2 {
        let (x0, y0) = (curve_points[0], curve_points[1]);
        let (x1, y1) = (curve_points[2], curve_points[3]);

        let y0_f64 = f64::from(y0);
        let y1_f64 = f64::from(y1);

        for val in lut.iter_mut().take(x0 as usize) {
            *val = y0;
        }

        let h = f64::from(x1 - x0);
        if h > 0.0 {
            for x in x0..x1 {
                let t = f64::from(x - x0) / h;
                let y = (1.0 - t) * y0_f64 + t * y1_f64;
                lut[x as usize] = adjust_color_double(y)
            }
        }

        for val in lut.iter_mut().skip(x1 as usize) {
            *val = y1;
        }

        return Ok(lut);
    }

    let y2 = calculate_second_derivative(curve_points, points_count)?;

    let mut k = 0;
    for i in 0..(points_count - 1) {
        let idx = i * 2;
        let (x_i, y_i_f64) = (curve_points[idx], f64::from(curve_points[idx + 1]));
        let (x_i_next, y_i_next_f64) = (curve_points[idx + 2], f64::from(curve_points[idx + 3]));

        let h = f64::from(x_i_next - x_i);
        if h == 0.0 {
            continue;
        }

        let (sd_i, sd_i_next) = (y2[i], y2[i + 1]);

        for x in x_i..x_i_next {
            let t = f64::from(x - x_i) / h;
            let a = 1.0 - t;
            let b = t;
            let term = (h * h / 6.0) * ((a * a * a - a) * sd_i + (b * b * b - b) * sd_i_next);
            let y = a * y_i_f64 + b * y_i_next_f64 + term;
            lut[x as usize] = adjust_color_double(y);
            k = x as usize;
        }
    }

    let last_value = curve_points[points_count * 2 - 1];
    if let Some(slice) = lut.get_mut((k + 1)..) {
        for val in slice {
            *val = last_value;
        }
    }
    lut[curve_points[points_count * 2 - 2] as usize] = last_value;

    Ok(lut)
}

#[pyfunction]
fn apply(
    image_mode: &str,
    buffer: &[u8],
    curve_a: Bound<'_, PyTuple>,
    curve_r: Bound<'_, PyTuple>,
    curve_g: Bound<'_, PyTuple>,
    curve_b: Bound<'_, PyTuple>,
) -> PyResult<Vec<u8>> {
    let curve_a_pts = get_curve(&curve_a)?;
    let curve_r_pts = get_curve(&curve_r)?;
    let curve_g_pts = get_curve(&curve_g)?;
    let curve_b_pts = get_curve(&curve_b)?;

    let master_lut = cubic_spline_interpolation(&curve_a_pts, curve_a_pts.len() / 2)?;
    let r_lut = cubic_spline_interpolation(&curve_r_pts, curve_r_pts.len() / 2)?;
    let g_lut = cubic_spline_interpolation(&curve_g_pts, curve_g_pts.len() / 2)?;
    let b_lut = cubic_spline_interpolation(&curve_b_pts, curve_b_pts.len() / 2)?;

    let mut final_r_lut = [0; 256];
    let mut final_g_lut = [0; 256];
    let mut final_b_lut = [0; 256];
    for i in 0..256 {
        final_r_lut[i] = master_lut[r_lut[i] as usize];
        final_g_lut[i] = master_lut[g_lut[i] as usize];
        final_b_lut[i] = master_lut[b_lut[i] as usize];
    }

    let num_bytes = bytes_per_pixel(image_mode);
    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');
    let a_idx = rgb_order(image_mode, 'A');
    let has_alpha = image_mode.contains('A');

    let mut output = Vec::with_capacity(buffer.len());

    for pixel in buffer.chunks_exact(num_bytes) {
        let mut new_pixel = [0; 4];
        new_pixel[r_idx] = final_r_lut[pixel[r_idx] as usize];
        new_pixel[g_idx] = final_g_lut[pixel[g_idx] as usize];
        new_pixel[b_idx] = final_b_lut[pixel[b_idx] as usize];
        if has_alpha {
            new_pixel[a_idx] = pixel[a_idx];
        }
        output.extend_from_slice(&new_pixel[..num_bytes]);
    }

    Ok(output)
}

#[pymodule]
fn _curve(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
