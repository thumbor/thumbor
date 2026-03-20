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

#[derive(Copy, Clone, Default)]
struct Pixel {
    r: u8,
    g: u8,
    b: u8,
    a: u8,
}

impl Pixel {
    fn from_slice(
        slice: &[u8],
        r_idx: usize,
        g_idx: usize,
        b_idx: usize,
        a_idx: usize,
        has_alpha: bool,
    ) -> Self {
        Pixel {
            r: slice[r_idx],
            g: slice[g_idx],
            b: slice[b_idx],
            a: if has_alpha { slice[a_idx] } else { 255 },
        }
    }

    fn blend(self, corner_color: &Pixel, aa: f32, transparent: bool) -> Self {
        if transparent {
            let inv_aa = 1.0 - aa;
            Pixel {
                r: (self.r as f32 * inv_aa) as u8,
                g: (self.g as f32 * inv_aa) as u8,
                b: (self.b as f32 * inv_aa) as u8,
                a: (self.a as f32 * inv_aa) as u8,
            }
        } else {
            let inv_aa = 1.0 - aa;
            Pixel {
                r: ((self.r as f32 * inv_aa) + (corner_color.r as f32 * aa)) as u8,
                g: ((self.g as f32 * inv_aa) + (corner_color.g as f32 * aa)) as u8,
                b: ((self.b as f32 * inv_aa) + (corner_color.b as f32 * aa)) as u8,
                a: self.a,
            }
        }
    }

    fn write_to_slice(
        &self,
        slice: &mut [u8],
        r_idx: usize,
        g_idx: usize,
        b_idx: usize,
        a_idx: usize,
        has_alpha: bool,
    ) {
        slice[r_idx] = self.r;
        slice[g_idx] = self.g;
        slice[b_idx] = self.b;
        if has_alpha {
            slice[a_idx] = self.a;
        }
    }
}

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
    let has_alpha = image_mode.contains('A');

    if r_idx >= num_bytes
        || g_idx >= num_bytes
        || b_idx >= num_bytes
        || (has_alpha && a_idx >= num_bytes)
    {
        return Err(PyValueError::new_err(
            "Invalid image mode or color component indices out of expected pixel size.",
        ));
    }
    if transparent && !has_alpha {
        return Err(PyValueError::new_err(
            "Cannot make corners transparent on an image without an alpha channel.",
        ));
    }

    let a_radius = a_radius_raw.max(0).min(width_raw / 2);
    let b_radius = b_radius_raw.max(0).min(height_raw / 2);

    let a_rad = a_radius as f32;
    let b_rad = b_radius as f32;

    // Optimization: Define corner color once
    let corner_color = Pixel {
        r,
        g,
        b,
        a: if transparent { 0 } else { 255 },
    };

    for y_i32 in 0..=b_radius {
        let y_f32 = y_i32 as f32;
        let x_f32 = -(a_rad * ((b_rad * b_rad - y_f32 * y_f32).sqrt()) / b_rad);
        let end_x_i32 = (x_f32 + a_rad) as i32;

        for curr_x_i32 in 0..end_x_i32 {
            let y_top_usize = (b_radius - y_i32) as usize;
            let y_bottom_usize = (height_raw - b_radius + y_i32 - 1) as usize;
            let x_left_usize = curr_x_i32 as usize;
            let x_right_usize = (width_raw - 1 - curr_x_i32) as usize;

            let indices = [
                (y_top_usize * width + x_left_usize) * num_bytes, // Top-left
                (y_bottom_usize * width + x_left_usize) * num_bytes, // Bottom-left
                (y_top_usize * width + x_right_usize) * num_bytes, // Top-right
                (y_bottom_usize * width + x_right_usize) * num_bytes, // Bottom-right
            ];

            for &idx in &indices {
                if idx + num_bytes > image_size {
                    return Err(PyIndexError::new_err("Index out of bounds"));
                }
                corner_color.write_to_slice(
                    &mut buffer_slice[idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                );
            }
        }
    }

    if !aa_enabled_bool {
        return Ok(py_byte_array.into());
    }

    let aa_amount = 0.75_f32;

    for y_i32 in 0..=b_radius {
        let y_f32 = y_i32 as f32;
        let x_f32 = -(a_rad * ((b_rad * b_rad - y_f32 * y_f32).sqrt()) / b_rad);

        let mut pixel_count_x = 0;
        let mut aa_x_i32 = (x_f32 - 1.0) as i32;
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

        if pixel_count_x == 0 {
            continue;
        }

        let end_x_i32 = (x_f32 + a_rad) as i32;
        let y_top_usize = (b_radius - y_i32) as usize;
        let y_bottom_usize = (height_raw - b_radius + y_i32 - 1) as usize;

        let orig_pixels = {
            let tl_idx = (y_top_usize * width + end_x_i32 as usize) * num_bytes;
            let bl_idx = (y_bottom_usize * width + end_x_i32 as usize) * num_bytes;
            let tr_idx = (y_top_usize * width + (width_raw - 1 - end_x_i32) as usize) * num_bytes;
            let br_idx =
                (y_bottom_usize * width + (width_raw - 1 - end_x_i32) as usize) * num_bytes;
            if br_idx + num_bytes > image_size {
                return Err(PyIndexError::new_err(
                    "Index out of bounds for AA source pixel",
                ));
            }
            [
                Pixel::from_slice(
                    &buffer_slice[tl_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[bl_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[tr_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[br_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
            ]
        };

        let mut idx_aa = 1;
        for i in 0..pixel_count_x {
            let aa_x_adj_i32 = (x_f32 as i32) - (pixel_count_x - i) + a_radius;

            let aa = 1.0 - ((idx_aa as f32 / pixel_count_x as f32) * aa_amount);

            let x_left_usize = aa_x_adj_i32 as usize;
            let x_right_usize = (width_raw - 1 - aa_x_adj_i32) as usize;

            let indices = [
                (y_top_usize * width + x_left_usize) * num_bytes,
                (y_bottom_usize * width + x_left_usize) * num_bytes,
                (y_top_usize * width + x_right_usize) * num_bytes,
                (y_bottom_usize * width + x_right_usize) * num_bytes,
            ];

            for (i, &byte_idx) in indices.iter().enumerate() {
                if byte_idx + num_bytes > image_size {
                    return Err(PyIndexError::new_err(
                        "Index out of bounds during AA (horizontal)",
                    ));
                }
                let blended_pixel = orig_pixels[i].blend(&corner_color, aa, transparent);
                blended_pixel.write_to_slice(
                    &mut buffer_slice[byte_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                );
            }
            idx_aa += 1;
        }
    }

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

        if pixel_count_y == 0 {
            continue;
        }

        let x_left_usize = (x_i32 + a_radius) as usize;
        let x_right_usize = (width_raw - 1 - (x_i32 + a_radius)) as usize;
        let y_top_usize = (b_radius - y_i32) as usize;
        let y_bottom_usize = (height_raw - b_radius + y_i32 - 1) as usize;

        let orig_pixels = {
            let tl_idx = (y_top_usize * width + x_left_usize) * num_bytes;
            let bl_idx = (y_bottom_usize * width + x_left_usize) * num_bytes;
            let tr_idx = (y_top_usize * width + x_right_usize) * num_bytes;
            let br_idx = (y_bottom_usize * width + x_right_usize) * num_bytes;
            if br_idx + num_bytes > image_size {
                return Err(PyIndexError::new_err(
                    "Index out of bounds for AA source pixel (vertical)",
                ));
            }
            [
                Pixel::from_slice(
                    &buffer_slice[tl_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[bl_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[tr_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
                Pixel::from_slice(
                    &buffer_slice[br_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                ),
            ]
        };

        let mut idx_aa = 1;
        for i in 0..pixel_count_y {
            let aa_y_loop_i32 = y_i32 + pixel_count_y - i;
            let aa = 1.0 - ((idx_aa as f32 / pixel_count_y as f32) * aa_amount);

            let y_top_loop_usize = (b_radius - aa_y_loop_i32) as usize;
            let y_bottom_loop_usize = (height_raw - b_radius + aa_y_loop_i32 - 1) as usize;

            let indices = [
                (y_top_loop_usize * width + x_left_usize) * num_bytes,
                (y_bottom_loop_usize * width + x_left_usize) * num_bytes,
                (y_top_loop_usize * width + x_right_usize) * num_bytes,
                (y_bottom_loop_usize * width + x_right_usize) * num_bytes,
            ];

            for (i, &byte_idx) in indices.iter().enumerate() {
                if byte_idx + num_bytes > image_size {
                    return Err(PyIndexError::new_err(
                        "Index out of bounds during AA (vertical)",
                    ));
                }
                let blended_pixel = orig_pixels[i].blend(&corner_color, aa, transparent);
                blended_pixel.write_to_slice(
                    &mut buffer_slice[byte_idx..],
                    r_idx,
                    g_idx,
                    b_idx,
                    a_idx,
                    has_alpha,
                );
            }
            idx_aa += 1;
        }
    }

    Ok(py_byte_array.into())
}

#[pymodule]
fn _round_corner(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
