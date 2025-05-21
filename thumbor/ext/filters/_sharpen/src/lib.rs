// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color, bytes_per_pixel, rgb_order};

const CHANNELS: usize = 3;

pub struct SharpenInfo<'a> {
    pub amount: f64,
    pub radius: f64,
    pub luminance_only: bool,
    pub width: i32,
    pub height: i32,
    pub buffer: &'a mut [u8],
    pub color_offset: [usize; 3],
    pub bpp: usize,
}

fn rgb2ycbcr(r: &mut f32, g: &mut f32, b: &mut f32) {
    let rr = *r;
    let gg = *g;
    let bb = *b;

    *r = 0.299 * rr + 0.587 * gg + 0.114 * bb; // Y (luminance)
    *g = -0.168736 * rr - 0.331264 * gg + 0.5 * bb; // Cb (blue-difference)
    *b = 0.5 * rr - 0.418688 * gg - 0.081312 * bb; // Cr (red-difference)
}

fn ycbcr2rgb(r: &mut f32, g: &mut f32, b: &mut f32) {
    let y = *r;
    let cb = *g;
    let cr = *b;

    *r = y + 1.402 * cr;
    *g = y - 0.344136 * cb - 0.714136 * cr;
    *b = y + 1.772 * cb;
}

fn hat_transform(temp: &mut [f32], base: &[f32], st: usize, size: usize, sc: usize) {
    let mut i = 0;
    let mut offset = 0;

    while i < sc && i < size {
        temp[i] = 2.0 * base[offset] + base[st * (sc - i)] + base[st * (i + sc)];
        i += 1;
        offset += st;
    }

    while i + sc < size {
        temp[i] = 2.0 * base[offset] + base[offset - st * sc] + base[offset + st * sc];
        i += 1;
        offset += st;
    }

    let two_size_minus_2_val = if size > 0 { 2 * size - 2 } else { 0 };
    while i < size {
        let reflected_idx_component = two_size_minus_2_val - (i + sc);
        let reflected = st * reflected_idx_component;
        temp[i] = 2.0 * base[offset] + base[offset - st * sc] + base[reflected];
        i += 1;
        offset += st;
    }
}

fn wavelet_sharpen(
    fimg: &mut [&mut [f32]; CHANNELS],
    width: usize,
    height: usize,
    amount: f32,
    radius: f32,
) {
    let size = width * height;
    let mut temp = vec![0.0f32; std::cmp::max(width, height)];

    let mut hpass = 0;

    for lev in 0..5 {
        let lpass = ((lev & 1) + 1) as usize;

        for row in 0..height {
            let base = &fimg[hpass][row * width..(row + 1) * width];
            let temp_slice = &mut temp[..width];
            hat_transform(temp_slice, base, 1, width, 1 << lev);
            for (col, &value) in temp_slice.iter().enumerate().take(width) {
                fimg[lpass][row * width + col] = value * 0.25;
            }
        }

        for col in 0..width {
            // coleta coluna
            let col_vec: Vec<f32> = (0..height)
                .map(|row| fimg[lpass][row * width + col])
                .collect();

            hat_transform(&mut temp[..height], &col_vec, 1, height, 1 << lev);

            for (row, &value) in temp.iter().enumerate().take(height) {
                fimg[lpass][row * width + col] = value * 0.25;
            }
        }

        let amt = amount * (-((lev as f32 - radius) * (lev as f32 - radius)) / 1.5).exp() + 1.0;

        #[allow(clippy::needless_range_loop)]
        for i in 0..size {
            fimg[hpass][i] -= fimg[lpass][i];
            fimg[hpass][i] *= amt;

            if hpass != 0 {
                fimg[0][i] += fimg[hpass][i];
            }
        }

        hpass = lpass;
    }

    #[allow(clippy::needless_range_loop)]
    for i in 0..size {
        fimg[0][i] += fimg[hpass][i];
    }
}

fn run_sharpen(info: &mut SharpenInfo) {
    let width = info.width as usize;
    let height = info.height as usize;
    let image_area = width * height;
    let bpp = info.bpp;
    let channels = CHANNELS;

    let mut transform_buffer: Vec<Vec<f32>> = Vec::with_capacity(channels);
    let mut aux_buffer: Vec<Option<Vec<f32>>> = vec![None; channels];

    for _ in 0..channels {
        transform_buffer.push(vec![0.0f32; image_area]);
    }

    aux_buffer
        .iter_mut()
        .take(channels)
        .skip(1)
        .for_each(|slot| {
            *slot = Some(vec![0.0f32; image_area]);
        });

    #[allow(clippy::needless_range_loop)]
    for i in 0..image_area {
        let buffer_pos = i * bpp;
        let mut pixel = [0f32; CHANNELS];

        pixel
            .iter_mut()
            .enumerate()
            .take(channels)
            .for_each(|(c, val)| {
                *val = info.buffer[buffer_pos + c] as f32;
            });

        if info.luminance_only {
            let r_idx = info.color_offset[0];
            let g_idx = info.color_offset[1];
            let b_idx = info.color_offset[2];

            let mut r = pixel[r_idx];
            let mut g = pixel[g_idx];
            let mut b = pixel[b_idx];

            rgb2ycbcr(&mut r, &mut g, &mut b);

            pixel[r_idx] = r;
            pixel[g_idx] = g;
            pixel[b_idx] = b;
        }

        for c in 0..channels {
            transform_buffer[c][i] = pixel[c] / 255.0;
        }
    }

    for (c, buffer) in transform_buffer.iter_mut().enumerate().take(channels) {
        if info.luminance_only && c != info.color_offset[0] {
            continue;
        }

        aux_buffer[0] = Some(buffer.clone());
        aux_buffer[1] = Some(vec![0.0f32; image_area]);
        aux_buffer[2] = Some(vec![0.0f32; image_area]);

        let (left, right) = aux_buffer.split_at_mut(1);
        let (mid, right) = right.split_at_mut(1);

        let mut fimg: [&mut [f32]; CHANNELS] = [
            left[0].as_mut().unwrap().as_mut_slice(),
            mid[0].as_mut().unwrap().as_mut_slice(),
            right[0].as_mut().unwrap().as_mut_slice(),
        ];

        wavelet_sharpen(
            &mut fimg,
            width,
            height,
            info.amount as f32,
            info.radius as f32,
        );

        *buffer = aux_buffer[0].take().unwrap();
    }

    #[allow(clippy::needless_range_loop)]
    for i in 0..image_area {
        let mut pixel = [0f32; CHANNELS];
        for c in 0..channels {
            pixel[c] = transform_buffer[c][i] * 255.0;
        }

        if info.luminance_only {
            let r_idx = info.color_offset[0];
            let g_idx = info.color_offset[1];
            let b_idx = info.color_offset[2];

            let mut r_val = pixel[r_idx];
            let mut g_val = pixel[g_idx];
            let mut b_val = pixel[b_idx];

            ycbcr2rgb(&mut r_val, &mut g_val, &mut b_val);

            pixel[r_idx] = r_val;
            pixel[g_idx] = g_val;
            pixel[b_idx] = b_val;
        }

        let buffer_pos = i * bpp;
        for (c, &val) in pixel.iter().enumerate().take(channels) {
            let val_i32 = val.round() as i32;
            info.buffer[buffer_pos + c] = adjust_color(val_i32);
        }
    }
}

/// Applies the sharpen filter to an image.
///
/// # Parameters
/// - `image_mode`: The image mode (e.g., RGB, RGBA, etc.).
/// - `width`: The width of the image in pixels.
/// - `height`: The height of the image in pixels.
/// - `amount`: The intensity of the sharpening effect.
/// - `radius`: The radius of the sharpening effect.
/// - `luminance_only`: If `true`, applies the filter only on luminance.
/// - `buffer`: The buffer containing the image data.
///
/// # Returns
/// Returns a `string` indicating the result or status of the filter application.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn apply<'py>(
    py: Python<'py>,
    image_mode_str: String,
    width: i32,
    height: i32,
    amount: f64,
    radius: f64,
    luminance_only: bool,
    buffer_py: &[u8],
) -> PyResult<Py<PyBytes>> {
    let mut buffer = buffer_py.to_vec();
    let num_bytes = bytes_per_pixel(&image_mode_str);
    let r_idx = rgb_order(&image_mode_str, 'R');
    let g_idx = rgb_order(&image_mode_str, 'G');
    let b_idx = rgb_order(&image_mode_str, 'B');

    let mut info = SharpenInfo {
        amount,
        radius,
        luminance_only,
        width,
        height,
        buffer: buffer.as_mut_slice(),
        color_offset: [r_idx, g_idx, b_idx],
        bpp: num_bytes,
    };

    run_sharpen(&mut info);

    Ok(PyBytes::new(py, &buffer).into())
}

#[pymodule]
fn _sharpen(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    Ok(())
}
