// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color_double, bytes_per_pixel, rgb_order};

const MAX_RGB_DOUBLE: f64 = 255.0;
const SMALL_DOUBLE: f64 = 1.0e-12;

fn alpha_composite_color_channel(color1: u8, alpha1: u8, color2: u8, alpha2: u8) -> f64 {
    ((1.0 - (alpha1 as f64 / MAX_RGB_DOUBLE)) * (color1 as f64))
        + ((1.0 - (alpha2 as f64 / MAX_RGB_DOUBLE))
            * (color2 as f64)
            * (alpha1 as f64 / MAX_RGB_DOUBLE))
}

/// composite filter module
///
/// apply(image_mode, buffer1, width1, height1, buffer2, width2, height2, pos_x, pos_y) -> bytes
///
/// Merges two images specified by buffer1 and buffer2, taking in consideration both alpha channels.
#[pyfunction(signature = (
    image_mode_str,
    buffer1,
    width1,
    height1,
    buffer2,
    width2,
    height2,
    x_pos,
    y_pos,
    merge=true
))]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python<'_>,
    image_mode_str: &str,
    buffer1: &[u8],
    width1: usize,
    height1: usize,
    buffer2: &[u8],
    width2: usize,
    height2: usize,
    mut x_pos: isize,
    mut y_pos: isize,
    merge: Option<bool>,
) -> Py<PyBytes> {
    let merge = merge.unwrap_or(true);
    let num_bytes = bytes_per_pixel(image_mode_str);
    let r_idx = rgb_order(image_mode_str, 'R');
    let g_idx = rgb_order(image_mode_str, 'G');
    let b_idx = rgb_order(image_mode_str, 'B');
    let a_idx = rgb_order(image_mode_str, 'A');

    let mut out_buffer = buffer1.to_vec();

    let mut start_x = 0usize;
    let mut start_y = 0usize;

    if x_pos < 0 {
        start_x = (-x_pos) as usize;
        x_pos = 0;
    }
    if y_pos < 0 {
        start_y = (-y_pos) as usize;
        y_pos = 0;
    }

    for y in start_y..height2 {
        let y_offset = y_pos - start_y as isize + y as isize;
        if y_offset < 0 || (y_offset as usize) >= height1 {
            break;
        }
        let line_offset1 = (y_offset as usize) * width1 * num_bytes;
        let line_offset2 = y * width2 * num_bytes;

        for x in start_x..width2 {
            let x_offset = x_pos - start_x as isize + x as isize;
            if x_offset < 0 || (x_offset as usize) >= width1 {
                break;
            }

            let idx1 = line_offset1 + (x_offset as usize) * num_bytes;
            let idx2 = line_offset2 + x * num_bytes;

            let r1 = out_buffer[idx1 + r_idx] as i32;
            let g1 = out_buffer[idx1 + g_idx] as i32;
            let b1 = out_buffer[idx1 + b_idx] as i32;
            let a1 = out_buffer[idx1 + a_idx] as i32;

            let r2 = buffer2[idx2 + r_idx] as i32;
            let g2 = buffer2[idx2 + g_idx] as i32;
            let b2 = buffer2[idx2 + b_idx] as i32;
            let a2 = buffer2[idx2 + a_idx] as i32;

            let a1_inv = (MAX_RGB_DOUBLE as i32) - a1;
            let a2_inv = (MAX_RGB_DOUBLE as i32) - a2;

            let (r, g, b, a) = if merge {
                let delta = (a2_inv as f64 / MAX_RGB_DOUBLE) * (a1_inv as f64 / MAX_RGB_DOUBLE);
                let a_comp = MAX_RGB_DOUBLE * delta;

                let mut delta_inv = 1.0 - delta;
                delta_inv = if delta_inv <= SMALL_DOUBLE {
                    1.0
                } else {
                    1.0 / delta_inv
                };

                let r = delta_inv
                    * alpha_composite_color_channel(r2 as u8, a2_inv as u8, r1 as u8, a1_inv as u8);
                let g = delta_inv
                    * alpha_composite_color_channel(g2 as u8, a2_inv as u8, g1 as u8, a1_inv as u8);
                let b = delta_inv
                    * alpha_composite_color_channel(b2 as u8, a2_inv as u8, b1 as u8, a1_inv as u8);

                (r, g, b, a_comp)
            } else if a1_inv == 0 {
                (r2 as f64, g2 as f64, b2 as f64, a2_inv as f64)
            } else {
                (r1 as f64, g1 as f64, b1 as f64, a1_inv as f64)
            };

            let a = MAX_RGB_DOUBLE - a;

            out_buffer[idx1 + r_idx] = adjust_color_double(r);
            out_buffer[idx1 + g_idx] = adjust_color_double(g);
            out_buffer[idx1 + b_idx] = adjust_color_double(b);
            out_buffer[idx1 + a_idx] = adjust_color_double(a);
        }
    }

    PyBytes::new(py, &out_buffer).into()
}

#[pymodule]
fn _composite(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
