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
const SMALL_DOUBLE: f64 = 1e-12;

#[inline]
fn alpha_composite_channel(c1: u8, a1: u8, c2: u8, a2: u8) -> f64 {
    let a1f = a1 as f64 / MAX_RGB_DOUBLE;
    let a2f = a2 as f64 / MAX_RGB_DOUBLE;
    (1.0 - a1f) * (c1 as f64) + (1.0 - a2f) * (c2 as f64) * a1f
}

#[inline]
#[allow(clippy::too_many_arguments)]
fn blend_pixels(
    r1: u8,
    g1: u8,
    b1: u8,
    a1: u8,
    r2: u8,
    g2: u8,
    b2: u8,
    a2: u8,
    merge: bool,
) -> (u8, u8, u8, u8) {
    let a1_inv = 255 - a1;
    let a2_inv = 255 - a2;

    if !merge {
        return if a1_inv == 0 {
            (r2, g2, b2, a2_inv)
        } else {
            (r1, g1, b1, a1_inv)
        };
    }

    let delta = (a2_inv as f64 / MAX_RGB_DOUBLE) * (a1_inv as f64 / MAX_RGB_DOUBLE);
    let a_comp = MAX_RGB_DOUBLE * delta;

    let delta_inv = if 1.0 - delta <= SMALL_DOUBLE {
        1.0
    } else {
        1.0 / (1.0 - delta)
    };

    let r = delta_inv * alpha_composite_channel(r2, a2_inv, r1, a1_inv);
    let g = delta_inv * alpha_composite_channel(g2, a2_inv, g1, a1_inv);
    let b = delta_inv * alpha_composite_channel(b2, a2_inv, b1, a1_inv);
    let a = MAX_RGB_DOUBLE - a_comp;

    (
        adjust_color_double(r),
        adjust_color_double(g),
        adjust_color_double(b),
        adjust_color_double(a),
    )
}

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

/// composite filter module
///
/// apply(image_mode, buffer1, width1, height1, buffer2, width2, height2, pos_x, pos_y) -> bytes
///
/// Merges two images specified by buffer1 and buffer2, taking in consideration both alpha channels.
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
        let y_out = y_pos + y as isize - start_y as isize;
        if y_out < 0 || y_out as usize >= height1 {
            break;
        }

        let offset1 = y_out as usize * width1 * num_bytes;
        let offset2 = y * width2 * num_bytes;

        for x in start_x..width2 {
            let x_out = x_pos + x as isize - start_x as isize;
            if x_out < 0 || x_out as usize >= width1 {
                break;
            }

            let idx1 = offset1 + x_out as usize * num_bytes;
            let idx2 = offset2 + x * num_bytes;

            let r1 = out_buffer[idx1 + r_idx];
            let g1 = out_buffer[idx1 + g_idx];
            let b1 = out_buffer[idx1 + b_idx];
            let a1 = out_buffer[idx1 + a_idx];

            let r2 = buffer2[idx2 + r_idx];
            let g2 = buffer2[idx2 + g_idx];
            let b2 = buffer2[idx2 + b_idx];
            let a2 = buffer2[idx2 + a_idx];

            let (r, g, b, a) = blend_pixels(r1, g1, b1, a1, r2, g2, b2, a2, merge);

            out_buffer[idx1 + r_idx] = r;
            out_buffer[idx1 + g_idx] = g;
            out_buffer[idx1 + b_idx] = b;
            out_buffer[idx1 + a_idx] = a;
        }
    }

    PyBytes::new(py, &out_buffer).into()
}

#[pymodule]
fn _composite(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
