// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use utils_lib::{bytes_per_pixel, rgb_order};

#[inline]
fn minmax(x: f64, min: f64, max: f64) -> f64 {
    if x > max {
        max
    } else if x < min {
        min
    } else {
        x
    }
}

fn get_curve(points: &Bound<'_, PyTuple>) -> PyResult<Vec<u8>> {
    let size = points.len();
    let mut items = Vec::with_capacity(size * 2);

    for p in points.iter() {
        let pair = p.downcast::<PyTuple>()?;
        let x: u8 = pair.get_item(0)?.extract()?;
        let y: u8 = pair.get_item(1)?.extract()?;
        items.push(x);
        items.push(y);
    }

    Ok(items)
}

fn check_index(points_len: usize, idx: isize) -> bool {
    idx >= 0 && (idx as usize) < points_len
}

fn calculate_second_derivative(points: &[u8], size: usize) -> PyResult<Vec<f64>> {
    if size < 3 || points.len() < (size - 1) * 2 + 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Insufficient number of points or size too small.",
        ));
    }

    let mut matrix = vec![0.0; size * 3];
    let mut result = vec![0.0; size];
    let mut y2 = vec![0.0; size];

    matrix[1] = 1.0;

    #[allow(clippy::needless_range_loop)]
    for i in 1..(size - 1) {
        let j = i * 2;
        let k = i * 3;

        let j_isize = j as isize;

        let valid_indices = [
            j_isize + 3,
            j_isize + 2,
            j_isize + 1,
            j_isize,
            j_isize - 1,
            j_isize - 2,
        ]
        .iter()
        .all(|&idx| check_index(points.len(), idx));

        if !valid_indices {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(format!(
                "Index out of bounds at i = {}, j = {}, points.len() = {}",
                i,
                j,
                points.len()
            )));
        }

        // Agora pode fazer a indexação com segurança
        let pj = points[j] as i16;
        let pj_m1 = points[(j_isize - 1) as usize] as i16;
        let pj_m2 = points[(j_isize - 2) as usize] as i16;
        let pj_p1 = points[(j_isize + 1) as usize] as i16;
        let pj_p2 = points[(j_isize + 2) as usize] as i16;
        let pj_p3 = points[(j_isize + 3) as usize] as i16;

        matrix[k] = (points[j] - points[(j_isize - 2) as usize]) as f64 / 6.0;
        matrix[k + 1] =
            (points[(j_isize + 2) as usize] - points[(j_isize - 2) as usize]) as f64 / 3.0;
        matrix[k + 2] = (points[(j_isize + 2) as usize] - points[j]) as f64 / 6.0;

        let num1 = pj_p3 - pj_p1;
        let den1 = pj_p2 - pj;
        let num2 = pj_p1 - pj_m1;
        let den2 = pj - pj_m2;

        if den1 == 0 || den2 == 0 {
            return Err(PyErr::new::<pyo3::exceptions::PyZeroDivisionError, _>(
                format!(
                    "Division by zero at i = {}, j = {}. den1 = {}, den2 = {}",
                    i, j, den1, den2
                ),
            ));
        }

        result[i] = num1 as f64 / den1 as f64 - num2 as f64 / den2 as f64;
    }

    matrix[(size - 1) * 3 + 1] = 1.0;

    for i in 1..size {
        let j = i * 3;
        let divisor = matrix[j - 2];
        if divisor == 0.0 {
            return Err(PyErr::new::<pyo3::exceptions::PyZeroDivisionError, _>(
                "Division by zero in forward elimination",
            ));
        }
        let k = matrix[j] / divisor;
        matrix[j + 1] -= k * matrix[j - 1];
        matrix[j] = 0.0;
        result[i] -= k * result[i - 1];
    }

    for i in (0..(size - 1)).rev() {
        let j = i * 3;
        let divisor = matrix[j + 4];
        if divisor == 0.0 {
            return Err(PyErr::new::<pyo3::exceptions::PyZeroDivisionError, _>(
                "Division by zero in back substitution",
            ));
        }
        let k = matrix[j + 2] / divisor;
        matrix[j + 1] -= k * matrix[j + 3];
        matrix[j + 2] = 0.0;
        result[i] -= k * result[i + 1];
    }

    for i in 0..size {
        let divisor = matrix[i * 3 + 1];
        if divisor == 0.0 {
            return Err(PyErr::new::<pyo3::exceptions::PyZeroDivisionError, _>(
                "Division by zero when calculating second derivatives",
            ));
        }
        y2[i] = result[i] / divisor;
    }

    Ok(y2)
}

fn cubic_spline_interpolation(points: &[u8], count_p: usize, size: usize) -> Vec<u8> {
    let mut items = vec![points[1]; size];

    let sd = calculate_second_derivative(points, count_p).unwrap_or(vec![0.0; count_p]);

    for i in 0..(count_p - 1) {
        let current_x = points[i * 2];
        let current_y = points[i * 2 + 1];
        let next_x = points[i * 2 + 2];
        let next_y = points[i * 2 + 3];

        for x in current_x..next_x {
            let t = (x - current_x) as f64 / (next_x - current_x) as f64;
            let a = 1.0 - t;
            let b = t;
            let h = (next_x - current_x) as f64;

            let y = a * current_y as f64
                + b * next_y as f64
                + (h * h / 6.0) * ((a * a * a - a) * sd[i] + (b * b * b - b) * sd[i + 1]);

            items[x as usize] = minmax(y.round(), 0.0, 255.0) as u8;
        }
    }

    let start = points[count_p * 2 - 2] as usize;
    let value = points[count_p * 2 - 1];

    for item in items.iter_mut().skip(start) {
        *item = value;
    }

    items
}

/// Applies color curve adjustments to the image buffer.
///
/// Parameters:
/// - image_mode (str): The mode of the image (e.g., "RGB", "RGBA").
/// - buffer (bytes): The raw image data buffer.
/// - curve_a (tuple): Adjustment curve for alpha channel.
/// - curve_r (tuple): Adjustment curve for red channel.
/// - curve_g (tuple): Adjustment curve for green channel.
/// - curve_b (tuple): Adjustment curve for blue channel.
///
/// Returns:
/// - str: The result of the operation as a string.
#[pyfunction]
fn apply(
    image_mode: &str,
    buffer: &[u8],
    curve_a: Bound<'_, PyTuple>,
    curve_r: Bound<'_, PyTuple>,
    curve_g: Bound<'_, PyTuple>,
    curve_b: Bound<'_, PyTuple>,
) -> PyResult<Vec<u8>> {
    let points_a = cubic_spline_interpolation(&get_curve(&curve_a)?, curve_a.len(), 256);
    let points_r = cubic_spline_interpolation(&get_curve(&curve_r)?, curve_r.len(), 256);
    let points_g = cubic_spline_interpolation(&get_curve(&curve_g)?, curve_g.len(), 256);
    let points_b = cubic_spline_interpolation(&get_curve(&curve_b)?, curve_b.len(), 256);

    let num_bytes = bytes_per_pixel(image_mode);
    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');

    let mut output = buffer.to_vec();

    for i in (0..buffer.len()).step_by(num_bytes) {
        let r = buffer[i + r_idx] as usize;
        let g = buffer[i + g_idx] as usize;
        let b = buffer[i + b_idx] as usize;

        let mut r = points_r[r];
        let mut g = points_g[g];
        let mut b = points_b[b];

        r = points_a[r as usize];
        g = points_a[g as usize];
        b = points_a[b as usize];

        output[i + r_idx] = r as u8;
        output[i + g_idx] = g as u8;
        output[i + b_idx] = b as u8;
    }

    Ok(output)
}

#[pymodule]
fn _curve(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
