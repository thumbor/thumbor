// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::exceptions::{PyIndexError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes};
use std::f32;

use utils_lib::{bytes_per_pixel, rgb_order};

/// Apply a rounded corner effect to the given image buffer.
///
/// Parameters:
/// - `aa_enabled` (u8): Whether to apply anti-aliasing (0 for false, non-zero for true).
/// - `image_mode` (str): Image mode (e.g., "RGB", "RGBA").
/// - `a_radius` (int): Horizontal radius of the corner ellipse.
/// - `b_radius` (int): Vertical radius of the corner ellipse.
/// - `r` (int): Red component (0–255) of the corner color.
/// - `g` (int): Green component (0–255) of the corner color.
/// - `b` (int): Blue component (0–255) of the corner color.
/// - `width` (int): Width of the image in pixels.
/// - `height` (int): Height of the image in pixels.
/// - `buffer` (bytes): Immutable image buffer. It will be copied to a mutable bytearray internally.
/// - `transparent` (bool): Whether to make corners transparent.
///
/// Returns:
/// - `Py<PyByteArray>`: A *new* PyByteArray containing the modified image data.
///
/// Raises:
/// - `ValueError`: If buffer size is invalid or parameters are inconsistent.
/// - `IndexError`: If calculated pixel indices are out of bounds.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python<'_>,
    aa_enabled: u8,
    image_mode: &str,
    a_radius_raw: i32,
    b_radius_raw: i32,
    r: u8,
    g: u8,
    b: u8,
    width_raw: i32,
    height_raw: i32,
    buffer: Bound<'_, PyBytes>,
    transparent: bool,
) -> PyResult<Py<PyByteArray>> {
    let py_byte_array = PyByteArray::new(py, buffer.as_bytes());
    let buffer_slice: &mut [u8] = unsafe { py_byte_array.as_bytes_mut() };

    let aa_enabled_bool = aa_enabled != 0;

    let width = width_raw.max(0) as usize;
    let height = height_raw.max(0) as usize;
    let num_bytes = bytes_per_pixel(image_mode);
    let image_size = width * height * num_bytes;

    if buffer_slice.len() < image_size {
        return Err(PyValueError::new_err(format!(
            "Buffer length ({}) is less than expected image size ({})",
            buffer_slice.len(),
            image_size
        )));
    }

    let r_idx = rgb_order(image_mode, 'R');
    let g_idx = rgb_order(image_mode, 'G');
    let b_idx = rgb_order(image_mode, 'B');
    let a_idx = rgb_order(image_mode, 'A');

    if r_idx >= num_bytes
        || g_idx >= num_bytes
        || b_idx >= num_bytes
        || (transparent && a_idx >= num_bytes)
    {
        return Err(PyValueError::new_err(
            "Invalid image mode or color component indices out of expected pixel size.",
        ));
    }

    let a_radius = a_radius_raw.max(0).min(width_raw / 2);
    let b_radius = b_radius_raw.max(0).min(height_raw / 2);

    let a_rad = a_radius as f32;
    let b_rad = b_radius as f32;

    let aa_amount = 0.75_f32;

    for y_i32 in 0..=b_radius {
        let y_f32 = y_i32 as f32;

        let x_f32 = -(a_rad * ((b_rad * b_rad - y_f32 * y_f32).sqrt()) / b_rad);

        let y_top_usize = (b_radius - y_i32).max(0) as usize;
        let y_bottom_usize = (height_raw - b_radius + y_i32 - 1).max(0) as usize;

        let end_x_i32 = (x_f32 + a_rad) as i32;
        let end_x_usize = end_x_i32.max(0) as usize;

        for curr_x_i32 in 0..end_x_i32 {
            let curr_x_usize = curr_x_i32.max(0) as usize;

            let top_left_px_start = y_top_usize * width + curr_x_usize;
            let bottom_left_px_start = y_bottom_usize * width + curr_x_usize;
            let top_right_px_start =
                y_top_usize * width + (width_raw - 1 - curr_x_i32).max(0) as usize;
            let bottom_right_px_start =
                y_bottom_usize * width + (width_raw - 1 - curr_x_i32).max(0) as usize;

            let top_left_byte_idx = num_bytes * top_left_px_start;
            let bottom_left_byte_idx = num_bytes * bottom_left_px_start;
            let top_right_byte_idx = num_bytes * top_right_px_start;
            let bottom_right_byte_idx = num_bytes * bottom_right_px_start;

            if top_left_byte_idx + b_idx >= image_size
                || bottom_left_byte_idx + b_idx >= image_size
                || top_right_byte_idx + b_idx >= image_size
                || bottom_right_byte_idx + b_idx >= image_size
                || (transparent
                    && (top_left_byte_idx + a_idx >= image_size
                        || bottom_left_byte_idx + a_idx >= image_size
                        || top_right_byte_idx + a_idx >= image_size
                        || bottom_right_byte_idx + a_idx >= image_size))
            {
                return Err(PyIndexError::new_err(
                    format!("Calculated pixel index out of bounds during corner drawing. TL:{} BL:{} TR:{} BR:{}",
                        top_left_byte_idx, bottom_left_byte_idx, top_right_byte_idx, bottom_right_byte_idx)
                ));
            }

            buffer_slice[top_left_byte_idx + r_idx] = r;
            buffer_slice[top_left_byte_idx + g_idx] = g;
            buffer_slice[top_left_byte_idx + b_idx] = b;
            if transparent {
                buffer_slice[top_left_byte_idx + a_idx] = 0;
            }
            buffer_slice[bottom_left_byte_idx + r_idx] = r;
            buffer_slice[bottom_left_byte_idx + g_idx] = g;
            buffer_slice[bottom_left_byte_idx + b_idx] = b;
            if transparent {
                buffer_slice[bottom_left_byte_idx + a_idx] = 0;
            }

            buffer_slice[top_right_byte_idx + r_idx] = r;
            buffer_slice[top_right_byte_idx + g_idx] = g;
            buffer_slice[top_right_byte_idx + b_idx] = b;
            if transparent {
                buffer_slice[top_right_byte_idx + a_idx] = 0;
            }
            buffer_slice[bottom_right_byte_idx + r_idx] = r;
            buffer_slice[bottom_right_byte_idx + g_idx] = g;
            buffer_slice[bottom_right_byte_idx + b_idx] = b;
            if transparent {
                buffer_slice[bottom_right_byte_idx + a_idx] = 0;
            }
        }

        if !aa_enabled_bool {
            continue;
        }

        let mut idx = 1;
        let mut aa_x_i32 = (x_f32 - 1.0) as i32;

        let mut pixel_count_x = 0;

        while aa_x_i32 >= -a_radius {
            let aa_x_f32 = aa_x_i32 as f32;
            let aa_y_check =
                ((b_rad * ((a_rad * a_rad - aa_x_f32 * aa_x_f32).sqrt())) / a_rad) as i32;
            if aa_y_check != y_i32 {
                break;
            }
            pixel_count_x += 1;
            aa_x_i32 -= 1;
        }

        aa_x_i32 = (x_f32 - pixel_count_x as f32) as i32;
        if aa_x_i32 < -a_radius {
            aa_x_i32 += 1;
        }

        let last_top_left_px_start = y_top_usize * width + end_x_usize;
        let last_bottom_left_px_start = y_bottom_usize * width + end_x_usize;
        let last_top_right_px_start =
            y_top_usize * width + (width_raw - 1 - end_x_i32).max(0) as usize;
        let last_bottom_right_px_start =
            y_bottom_usize * width + (width_raw - 1 - end_x_i32).max(0) as usize;

        let last_top_left_byte_idx = num_bytes * last_top_left_px_start;
        let last_bottom_left_byte_idx = num_bytes * last_bottom_left_px_start;
        let last_top_right_byte_idx = num_bytes * last_top_right_px_start;
        let last_bottom_right_byte_idx = num_bytes * last_bottom_right_px_start;

        if last_top_left_byte_idx + num_bytes > image_size
            || last_bottom_left_byte_idx + num_bytes > image_size
            || last_top_right_byte_idx + num_bytes > image_size
            || last_bottom_right_byte_idx + num_bytes > image_size
        {
            return Err(PyIndexError::new_err(
                "Buffer index out of bounds during anti-aliasing color copying (start)",
            ));
        }

        let color_top_left =
            buffer_slice[last_top_left_byte_idx..last_top_left_byte_idx + num_bytes].to_owned();
        let color_bottom_left = buffer_slice
            [last_bottom_left_byte_idx..last_bottom_left_byte_idx + num_bytes]
            .to_owned();
        let color_top_right =
            buffer_slice[last_top_right_byte_idx..last_top_right_byte_idx + num_bytes].to_owned();
        let color_bottom_right = buffer_slice
            [last_bottom_right_byte_idx..last_bottom_right_byte_idx + num_bytes]
            .to_owned();

        while aa_x_i32 < x_f32 as i32 {
            // Compare with int x
            let aa_x_adj_i32 = aa_x_i32 + a_radius;
            let aa_x_adj_usize = aa_x_adj_i32.max(0) as usize;

            let top_left_byte_idx = num_bytes * (y_top_usize * width + aa_x_adj_usize);
            let bottom_left_byte_idx = num_bytes * (y_bottom_usize * width + aa_x_adj_usize);
            let top_right_byte_idx =
                num_bytes * (y_top_usize * width + (width_raw - 1 - aa_x_adj_i32).max(0) as usize);
            let bottom_right_byte_idx = num_bytes
                * (y_bottom_usize * width + (width_raw - 1 - aa_x_adj_i32).max(0) as usize);

            let aa = 1.0 - ((idx as f32 / pixel_count_x as f32) * aa_amount);

            if top_left_byte_idx + b_idx >= image_size
                || bottom_left_byte_idx + b_idx >= image_size
                || top_right_byte_idx + b_idx >= image_size
                || bottom_right_byte_idx + b_idx >= image_size
                || (transparent
                    && (top_left_byte_idx + a_idx >= image_size
                        || bottom_left_byte_idx + a_idx >= image_size
                        || top_right_byte_idx + a_idx >= image_size
                        || bottom_right_byte_idx + a_idx >= image_size))
            {
                return Err(PyIndexError::new_err(
                    "Buffer index out of bounds during anti-aliasing color application (x-axis)",
                ));
            }

            if transparent {
                buffer_slice[top_left_byte_idx + r_idx] =
                    (color_top_left[r_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_left_byte_idx + g_idx] =
                    (color_top_left[g_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_left_byte_idx + b_idx] =
                    (color_top_left[b_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_left_byte_idx + a_idx] =
                    (color_top_left[a_idx] as f32 * (1.0 - aa)) as u8;

                buffer_slice[bottom_left_byte_idx + r_idx] =
                    (color_bottom_left[r_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_left_byte_idx + g_idx] =
                    (color_bottom_left[g_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_left_byte_idx + b_idx] =
                    (color_bottom_left[b_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_left_byte_idx + a_idx] =
                    (color_bottom_left[a_idx] as f32 * (1.0 - aa)) as u8;

                buffer_slice[top_right_byte_idx + r_idx] =
                    (color_top_right[r_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_right_byte_idx + g_idx] =
                    (color_top_right[g_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_right_byte_idx + b_idx] =
                    (color_top_right[b_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[top_right_byte_idx + a_idx] =
                    (color_top_right[a_idx] as f32 * (1.0 - aa)) as u8;

                buffer_slice[bottom_right_byte_idx + r_idx] =
                    (color_bottom_right[r_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_right_byte_idx + g_idx] =
                    (color_bottom_right[g_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_right_byte_idx + b_idx] =
                    (color_bottom_right[b_idx] as f32 * (1.0 - aa)) as u8;
                buffer_slice[bottom_right_byte_idx + a_idx] =
                    (color_bottom_right[a_idx] as f32 * (1.0 - aa)) as u8;
            } else {
                buffer_slice[top_left_byte_idx + r_idx] =
                    ((color_top_left[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                buffer_slice[top_left_byte_idx + g_idx] =
                    ((color_top_left[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                buffer_slice[top_left_byte_idx + b_idx] =
                    ((color_top_left[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                buffer_slice[bottom_left_byte_idx + r_idx] =
                    ((color_bottom_left[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                buffer_slice[bottom_left_byte_idx + g_idx] =
                    ((color_bottom_left[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                buffer_slice[bottom_left_byte_idx + b_idx] =
                    ((color_bottom_left[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                buffer_slice[top_right_byte_idx + r_idx] =
                    ((color_top_right[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                buffer_slice[top_right_byte_idx + g_idx] =
                    ((color_top_right[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                buffer_slice[top_right_byte_idx + b_idx] =
                    ((color_top_right[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                buffer_slice[bottom_right_byte_idx + r_idx] =
                    ((color_bottom_right[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                buffer_slice[bottom_right_byte_idx + g_idx] =
                    ((color_bottom_right[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                buffer_slice[bottom_right_byte_idx + b_idx] =
                    ((color_bottom_right[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;
            }

            aa_x_i32 += 1;
            idx += 1;
        }
    }

    if aa_enabled_bool {
        // Anti-aliasing for y-axis
        for x_i32 in (-a_radius..=0).rev() {
            let x_f32 = x_i32 as f32;
            let y_f32 = b_rad * ((a_rad * a_rad - x_f32 * x_f32).sqrt()) / a_rad;
            let y_i32 = y_f32 as i32;

            let mut pixel_count_y = 0;
            let mut aa_y_check_i32 = y_i32 + 1;

            while aa_y_check_i32 < b_radius {
                let aa_y_check_f32 = aa_y_check_i32 as f32;
                let aa_x_check_f32 =
                    -((a_rad * ((b_rad * b_rad - aa_y_check_f32 * aa_y_check_f32).sqrt())) / b_rad)
                        - 1.0;

                if aa_x_check_f32 as i32 != x_i32 {
                    break;
                }
                pixel_count_y += 1;
                aa_y_check_i32 += 1;
            }

            let y_top_usize = (b_radius - y_i32).max(0) as usize;
            let y_bottom_usize = (height_raw - b_radius + y_i32 - 1).max(0) as usize;

            let left_x_i32 = x_i32 + a_radius;
            let left_x_usize = left_x_i32.max(0) as usize;

            let right_x_i32 = width_raw - a_radius - x_i32;
            let right_x_usize = right_x_i32.max(0) as usize;

            let last_top_left_byte_idx = num_bytes * (y_top_usize * width + left_x_usize);
            let last_bottom_left_byte_idx = num_bytes * (y_bottom_usize * width + left_x_usize);
            let last_top_right_byte_idx = num_bytes * (y_top_usize * width + right_x_usize);
            let last_bottom_right_byte_idx = num_bytes * (y_bottom_usize * width + right_x_usize);

            if last_top_left_byte_idx + num_bytes > image_size
                || last_bottom_left_byte_idx + num_bytes > image_size
                || last_top_right_byte_idx + num_bytes > image_size
                || last_bottom_right_byte_idx + num_bytes > image_size
            {
                return Err(PyIndexError::new_err(
                    "Buffer index out of bounds during anti-aliasing color copying (y-axis)",
                ));
            }

            let color_top_left =
                buffer_slice[last_top_left_byte_idx..last_top_left_byte_idx + num_bytes].to_owned();
            let color_bottom_left = buffer_slice
                [last_bottom_left_byte_idx..last_bottom_left_byte_idx + num_bytes]
                .to_owned();
            let color_top_right = buffer_slice
                [last_top_right_byte_idx..last_top_right_byte_idx + num_bytes]
                .to_owned();
            let color_bottom_right = buffer_slice
                [last_bottom_right_byte_idx..last_bottom_right_byte_idx + num_bytes]
                .to_owned();

            let mut idx = 1;
            let mut aa_y_loop_i32 = y_i32 + pixel_count_y;
            if aa_y_loop_i32 > b_radius {
                aa_y_loop_i32 -= 1;
            }

            while aa_y_loop_i32 > y_i32 {
                let top_left_byte_idx =
                    num_bytes * ((b_radius - aa_y_loop_i32).max(0) as usize * width + left_x_usize);
                let bottom_left_byte_idx = num_bytes
                    * ((height_raw - b_radius + aa_y_loop_i32 - 1).max(0) as usize * width
                        + left_x_usize);
                let top_right_byte_idx = num_bytes
                    * ((b_radius - aa_y_loop_i32).max(0) as usize * width + right_x_usize);
                let bottom_right_byte_idx = num_bytes
                    * ((height_raw - b_radius + aa_y_loop_i32 - 1).max(0) as usize * width
                        + right_x_usize);

                let aa = 1.0 - ((idx as f32 / pixel_count_y as f32) * aa_amount);

                if top_left_byte_idx + b_idx >= image_size
                    || bottom_left_byte_idx + b_idx >= image_size
                    || top_right_byte_idx + b_idx >= image_size
                    || bottom_right_byte_idx + b_idx >= image_size
                    || (transparent
                        && (top_left_byte_idx + a_idx >= image_size
                            || bottom_left_byte_idx + a_idx >= image_size
                            || top_right_byte_idx + a_idx >= image_size
                            || bottom_right_byte_idx + a_idx >= image_size))
                {
                    return Err(PyIndexError::new_err(
                        "Buffer index out of bounds during anti-aliasing color application (y-axis)",
                    ));
                }

                if transparent {
                    buffer_slice[top_left_byte_idx + r_idx] =
                        (color_top_left[r_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_left_byte_idx + g_idx] =
                        (color_top_left[g_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_left_byte_idx + b_idx] =
                        (color_top_left[b_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_left_byte_idx + a_idx] =
                        (color_top_left[a_idx] as f32 * (1.0 - aa)) as u8;

                    buffer_slice[bottom_left_byte_idx + r_idx] =
                        (color_bottom_left[r_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_left_byte_idx + g_idx] =
                        (color_bottom_left[g_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_left_byte_idx + b_idx] =
                        (color_bottom_left[b_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_left_byte_idx + a_idx] =
                        (color_bottom_left[a_idx] as f32 * (1.0 - aa)) as u8;

                    buffer_slice[top_right_byte_idx + r_idx] =
                        (color_top_right[r_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_right_byte_idx + g_idx] =
                        (color_top_right[g_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_right_byte_idx + b_idx] =
                        (color_top_right[b_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[top_right_byte_idx + a_idx] =
                        (color_top_right[a_idx] as f32 * (1.0 - aa)) as u8;

                    buffer_slice[bottom_right_byte_idx + r_idx] =
                        (color_bottom_right[r_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_right_byte_idx + g_idx] =
                        (color_bottom_right[g_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_right_byte_idx + b_idx] =
                        (color_bottom_right[b_idx] as f32 * (1.0 - aa)) as u8;
                    buffer_slice[bottom_right_byte_idx + a_idx] =
                        (color_bottom_right[a_idx] as f32 * (1.0 - aa)) as u8;
                } else {
                    buffer_slice[top_left_byte_idx + r_idx] =
                        ((color_top_left[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                    buffer_slice[top_left_byte_idx + g_idx] =
                        ((color_top_left[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                    buffer_slice[top_left_byte_idx + b_idx] =
                        ((color_top_left[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                    buffer_slice[bottom_left_byte_idx + r_idx] =
                        ((color_bottom_left[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                    buffer_slice[bottom_left_byte_idx + g_idx] =
                        ((color_bottom_left[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                    buffer_slice[bottom_left_byte_idx + b_idx] =
                        ((color_bottom_left[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                    buffer_slice[top_right_byte_idx + r_idx] =
                        ((color_top_right[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                    buffer_slice[top_right_byte_idx + g_idx] =
                        ((color_top_right[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                    buffer_slice[top_right_byte_idx + b_idx] =
                        ((color_top_right[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;

                    buffer_slice[bottom_right_byte_idx + r_idx] =
                        ((color_bottom_right[r_idx] as f32 * (1.0 - aa)) + (r as f32 * aa)) as u8;
                    buffer_slice[bottom_right_byte_idx + g_idx] =
                        ((color_bottom_right[g_idx] as f32 * (1.0 - aa)) + (g as f32 * aa)) as u8;
                    buffer_slice[bottom_right_byte_idx + b_idx] =
                        ((color_bottom_right[b_idx] as f32 * (1.0 - aa)) + (b as f32 * aa)) as u8;
                }

                aa_y_loop_i32 -= 1;
                idx += 1;
            }
        }
    }

    Ok(py_byte_array.into())
}

#[pymodule]
fn _round_corner(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
