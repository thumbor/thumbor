// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;

use utils_lib::bytes_per_pixel;

#[derive(Debug)]
struct BoxBounds {
    left: i32,
    top: i32,
    right: i32,
    bottom: i32,
}

struct Bitmap<'a> {
    width: i32,
    height: i32,
    stride: i32,
    image: &'a [u8],
}

fn color_distance(c1: &[u8], c2: &[u8], stride: usize) -> f64 {
    let mut sum = 0f64;
    for i in 0..stride {
        let diff = c1[i] as i32 - c2[i] as i32;
        sum += (diff * diff) as f64;
    }
    sum.sqrt()
}

fn find_bounding_box(image_data: &Bitmap, reference_mode: &str, tolerance: i32) -> BoxBounds {
    let mut b = BoxBounds {
        left: image_data.width,
        top: image_data.height,
        right: 0,
        bottom: 0,
    };

    let stride = image_data.stride as usize;

    let reference_pixel = if reference_mode == "top-left" {
        &image_data.image[0..stride]
    } else {
        let idx = ((image_data.height - 1) * image_data.width * image_data.stride
            + (image_data.width - 1) * image_data.stride) as usize;
        &image_data.image[idx..(idx + stride)]
    };

    for y in 0..image_data.height {
        let y_usize = y as usize;
        let mut x = 0usize;

        while x < image_data.width as usize {
            let idx = (y_usize * image_data.width as usize * stride) + (x * stride);
            let pixel = &image_data.image[idx..idx + stride];
            if color_distance(pixel, reference_pixel, stride) > tolerance as f64 {
                if (x as i32) < b.left {
                    b.left = x as i32;
                }
                if (y) < b.top {
                    b.top = y;
                }
                b.bottom = y;
                break;
            }
            x += 1;
        }

        let min_right = if (x as i32) > b.right {
            x as i32
        } else {
            b.right
        };
        let mut xi = image_data.width - 1;

        while xi > min_right {
            let idx = (y_usize * image_data.width as usize * stride) + (xi as usize * stride);
            let pixel = &image_data.image[idx..idx + stride];
            if color_distance(pixel, reference_pixel, stride) > tolerance as f64 {
                if xi > b.right {
                    b.right = xi;
                }
                break;
            }
            xi -= 1;
        }
    }

    b
}

/// Calculates the bounding box necessary to trim an image based on the color of
/// one of the corners and the euclidean distance between the colors within a
/// specified tolerance.
///
/// # Arguments
///
/// * `image_mode` - Image mode string (e.g., "RGBA").
/// * `width` - Width of the image.
/// * `height` - Height of the image.
/// * `reference_mode` - Reference corner ("top-left" or "bottom-right").
/// * `tolerance` - Color tolerance value.
/// * `buffer` - Raw image bytes.
///
/// # Returns
///
/// Tuple `(left, top, right, bottom)` representing the bounding box coordinates.
#[pyfunction]
fn apply(
    image_mode: &str,
    width: i32,
    height: i32,
    reference_mode: &str,
    tolerance: i32,
    buffer: &[u8],
) -> PyResult<(i32, i32, i32, i32)> {
    let num_bytes = bytes_per_pixel(image_mode);

    let bitmap = Bitmap {
        width,
        height,
        stride: num_bytes as i32,
        image: buffer,
    };

    let b = find_bounding_box(&bitmap, reference_mode, tolerance);

    Ok((b.left, b.top, b.right, b.bottom))
}

#[pymodule]
fn _bounding_box(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
