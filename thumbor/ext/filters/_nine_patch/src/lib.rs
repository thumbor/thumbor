// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use utils_lib::{adjust_color_double, bytes_per_pixel, rgb_order};

#[derive(Debug, Copy, Clone)]
struct Rect {
    x: usize,
    y: usize,
    w: usize,
    h: usize,
}

#[derive(Debug)]
struct Segment {
    start: usize,
    len: usize,
    is_stretchy: bool,
}

#[derive(Debug)]
struct NinePatchInfo {
    h_segments: Vec<Segment>,
    v_segments: Vec<Segment>,
    stretchy_w: usize,
    stretchy_h: usize,
    fixed_w: usize,
    fixed_h: usize,
    padding: (usize, usize, usize, usize),
}

struct Bitmap<'a> {
    width: usize,
    height: usize,
    stride: usize,
    alpha_idx: usize,
    buffer: &'a [u8],
}

struct BitmapMut<'a> {
    width: usize,
    height: usize,
    stride: usize,
    alpha_idx: usize,
    buffer: &'a mut [u8],
}

impl<'a> Bitmap<'a> {
    fn new(image_mode: &str, buffer: &'a [u8], width: usize, height: usize) -> Self {
        Self {
            width,
            height,
            stride: bytes_per_pixel(image_mode),
            alpha_idx: rgb_order(image_mode, 'A'),
            buffer,
        }
    }

    #[inline]
    fn get_pixel(&self, x: usize, y: usize) -> Option<&'a [u8]> {
        if x >= self.width || y >= self.height {
            return None;
        }
        let start = (y * self.width + x) * self.stride;
        self.buffer.get(start..start + self.stride)
    }

    #[inline]
    fn is_stretchy_at(&self, x: usize, y: usize) -> bool {
        if let Some(pixel) = self.get_pixel(x, y) {
            for (i, &val) in pixel.iter().enumerate() {
                let expected = if i == self.alpha_idx { 255 } else { 0 };
                if val != expected {
                    return false;
                }
            }
            return true;
        }
        false
    }
}

impl NinePatchInfo {
    fn new(nine_patch: &Bitmap) -> Self {
        let np_w = nine_patch.width;
        let np_h = nine_patch.height;

        let h_stretchy_map: Vec<bool> = (1..np_w.saturating_sub(1))
            .map(|x| nine_patch.is_stretchy_at(x, 0))
            .collect();
        let v_stretchy_map: Vec<bool> = (1..np_h.saturating_sub(1))
            .map(|y| nine_patch.is_stretchy_at(0, y))
            .collect();

        let h_segments = Self::compute_segments(&h_stretchy_map);
        let v_segments = Self::compute_segments(&v_stretchy_map);

        let stretchy_w = h_segments
            .iter()
            .filter(|s| s.is_stretchy)
            .map(|s| s.len)
            .sum();
        let stretchy_h = v_segments
            .iter()
            .filter(|s| s.is_stretchy)
            .map(|s| s.len)
            .sum();

        let fixed_w = np_w.saturating_sub(2).saturating_sub(stretchy_w);
        let fixed_h = np_h.saturating_sub(2).saturating_sub(stretchy_h);

        let padding = Self::compute_padding(nine_patch);

        Self {
            h_segments,
            v_segments,
            stretchy_w,
            stretchy_h,
            fixed_w,
            fixed_h,
            padding,
        }
    }

    fn compute_segments(stretchy_map: &[bool]) -> Vec<Segment> {
        if stretchy_map.is_empty() {
            return vec![];
        }
        let mut segments = Vec::new();
        let mut current_state = stretchy_map[0];
        let mut start = 1;

        for (i, &is_stretchy) in stretchy_map.iter().enumerate().skip(1) {
            if is_stretchy != current_state {
                segments.push(Segment {
                    start,
                    len: i + 1 - start,
                    is_stretchy: current_state,
                });
                current_state = is_stretchy;
                start = i + 1;
            }
        }
        segments.push(Segment {
            start,
            len: stretchy_map.len() + 1 - start,
            is_stretchy: current_state,
        });
        segments
    }

    fn compute_padding(nine_patch: &Bitmap) -> (usize, usize, usize, usize) {
        let w = nine_patch.width;
        let h = nine_patch.height;
        if w < 2 || h < 2 {
            return (0, 0, 0, 0);
        }

        let left = (1..w - 1)
            .position(|x| nine_patch.is_stretchy_at(x, h - 1))
            .unwrap_or(0);
        let right = (1..w - 1)
            .rposition(|x| nine_patch.is_stretchy_at(x, h - 1))
            .map_or(0, |p| w - 3 - p);
        let top = (1..h - 1)
            .position(|y| nine_patch.is_stretchy_at(w - 1, y))
            .unwrap_or(0);
        let bottom = (1..h - 1)
            .rposition(|y| nine_patch.is_stretchy_at(w - 1, y))
            .map_or(0, |p| h - 3 - p);

        (left, top, right, bottom)
    }
}

fn validate_bitmap(
    image_mode: &str,
    buffer: &[u8],
    width: usize,
    height: usize,
    is_nine_patch: bool,
) -> PyResult<()> {
    if image_mode != "RGBA" {
        return Err(PyValueError::new_err(
            "Nine-patch processing requires an RGBA image.",
        ));
    }
    if width == 0 || height == 0 || (is_nine_patch && (width < 3 || height < 3)) {
        return Err(PyValueError::new_err(if is_nine_patch {
            "Nine-patch images must be at least 3x3 pixels."
        } else {
            "Target images must have positive dimensions."
        }));
    }

    let expected_size = width
        .checked_mul(height)
        .and_then(|area| area.checked_mul(4))
        .ok_or_else(|| PyValueError::new_err("Image dimensions are too large."))?;
    if buffer.len() != expected_size {
        return Err(PyValueError::new_err(
            "Image buffer size does not match its dimensions.",
        ));
    }
    Ok(())
}

impl<'a> BitmapMut<'a> {
    fn new(image_mode: &str, buffer: &'a mut [u8], width: usize, height: usize) -> Self {
        Self {
            width,
            height,
            stride: bytes_per_pixel(image_mode),
            alpha_idx: rgb_order(image_mode, 'A'),
            buffer,
        }
    }

    #[inline]
    fn get_subpixel(&self, x: usize, y: usize, s: usize) -> u8 {
        self.buffer[(y * self.width + x) * self.stride + s]
    }

    #[inline]
    fn set_subpixel(&mut self, x: usize, y: usize, s: usize, value: f64) {
        let offset = (y * self.width + x) * self.stride + s;
        self.buffer[offset] = adjust_color_double(value);
    }

    fn paste_rectangle(&mut self, source: &Bitmap, src_rect: Rect, tgt_rect: Rect) -> PyResult<()> {
        if tgt_rect.w == 0 || tgt_rect.h == 0 || src_rect.w == 0 || src_rect.h == 0 {
            return Ok(());
        }
        if tgt_rect.x + tgt_rect.w > self.width || tgt_rect.y + tgt_rect.h > self.height {
            return Err(PyValueError::new_err("Target rectangle is out of bounds."));
        }

        let x_ratio = if tgt_rect.w > 1 {
            (src_rect.w - 1) as f64 / (tgt_rect.w - 1) as f64
        } else {
            0.0
        };
        let y_ratio = if tgt_rect.h > 1 {
            (src_rect.h - 1) as f64 / (tgt_rect.h - 1) as f64
        } else {
            0.0
        };

        for y in 0..tgt_rect.h {
            let y_pos = y as f64 * y_ratio;
            let src_y = y_pos.floor() as usize;
            let y_frac = y_pos - src_y as f64;

            for x in 0..tgt_rect.w {
                let x_pos = x as f64 * x_ratio;
                let src_x = x_pos.floor() as usize;
                let x_frac = x_pos - src_x as f64;

                let mut blended_pixel: [f64; 4] = [0.0; 4];

                let src_a = Self::interpolate_subpixel(
                    source,
                    src_rect.x + src_x,
                    src_rect.y + src_y,
                    x_frac,
                    y_frac,
                    source.alpha_idx,
                )? / 255.0;
                if src_a < 1e-6 {
                    continue;
                }

                let tgt_a = self.get_subpixel(tgt_rect.x + x, tgt_rect.y + y, self.alpha_idx)
                    as f64
                    / 255.0;

                for (s, value) in blended_pixel.iter_mut().enumerate().take(self.stride) {
                    if s == self.alpha_idx {
                        continue;
                    }
                    let src_val = Self::interpolate_subpixel(
                        source,
                        src_rect.x + src_x,
                        src_rect.y + src_y,
                        x_frac,
                        y_frac,
                        s,
                    )?;
                    let tgt_val = self.get_subpixel(tgt_rect.x + x, tgt_rect.y + y, s) as f64;
                    *value = src_val * src_a + tgt_val * tgt_a * (1.0 - src_a);
                }

                let out_a = src_a + tgt_a * (1.0 - src_a);
                if out_a > 1e-6 {
                    let inv_out_a = 1.0 / out_a;
                    for (s, &value) in blended_pixel.iter().enumerate().take(self.stride) {
                        if s != self.alpha_idx {
                            self.set_subpixel(tgt_rect.x + x, tgt_rect.y + y, s, value * inv_out_a);
                        }
                    }
                }
                self.set_subpixel(
                    tgt_rect.x + x,
                    tgt_rect.y + y,
                    self.alpha_idx,
                    out_a * 255.0,
                );
            }
        }
        Ok(())
    }

    #[inline]
    fn interpolate_subpixel(
        b: &Bitmap,
        x: usize,
        y: usize,
        x_frac: f64,
        y_frac: f64,
        s: usize,
    ) -> PyResult<f64> {
        let get = |dx, dy| {
            b.get_pixel(x + dx, y + dy)
                .and_then(|p| p.get(s).map(|&v| v as f64))
                .ok_or_else(|| {
                    PyValueError::new_err(format!(
                        "Pixel access out of bounds at ({}, {})",
                        x + dx,
                        y + dy
                    ))
                })
        };

        let p00 = get(0, 0)?;
        let p10 = get(1, 0)?;
        let p01 = get(0, 1)?;
        let p11 = get(1, 1)?;

        let interp_x1 = p00 * (1.0 - x_frac) + p10 * x_frac;
        let interp_x2 = p01 * (1.0 - x_frac) + p11 * x_frac;

        Ok(interp_x1 * (1.0 - y_frac) + interp_x2 * y_frac)
    }
}

#[pyfunction]
fn get_padding(
    image_mode: &str,
    nine_patch_buffer: &[u8],
    nine_patch_w: usize,
    nine_patch_h: usize,
) -> PyResult<(usize, usize, usize, usize)> {
    validate_bitmap(
        image_mode,
        nine_patch_buffer,
        nine_patch_w,
        nine_patch_h,
        true,
    )?;
    let nine_patch = Bitmap::new(image_mode, nine_patch_buffer, nine_patch_w, nine_patch_h);
    let info = NinePatchInfo::new(&nine_patch);
    Ok(info.padding)
}

#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn apply(
    py: Python,
    image_mode: &str,
    target_buffer: &[u8],
    target_w: usize,
    target_h: usize,
    nine_patch_buffer: &[u8],
    nine_patch_w: usize,
    nine_patch_h: usize,
) -> PyResult<Py<PyBytes>> {
    validate_bitmap(image_mode, target_buffer, target_w, target_h, false)?;
    validate_bitmap(
        image_mode,
        nine_patch_buffer,
        nine_patch_w,
        nine_patch_h,
        true,
    )?;

    let nine_patch = Bitmap::new(image_mode, nine_patch_buffer, nine_patch_w, nine_patch_h);
    let info = NinePatchInfo::new(&nine_patch);

    let target_stretchy_w = target_w.saturating_sub(info.fixed_w);
    let target_stretchy_h = target_h.saturating_sub(info.fixed_h);

    PyBytes::new_with(py, target_buffer.len(), |out| {
        out.copy_from_slice(target_buffer);
        let mut target = BitmapMut::new(image_mode, out, target_w, target_h);

        let mut target_y = 0;
        for v_seg in &info.v_segments {
            let target_h = if v_seg.is_stretchy && info.stretchy_h > 0 {
                (v_seg.len as f64 / info.stretchy_h as f64 * target_stretchy_h as f64).round()
                    as usize
            } else {
                v_seg.len
            };

            let mut target_x = 0;
            for h_seg in &info.h_segments {
                let target_w = if h_seg.is_stretchy && info.stretchy_w > 0 {
                    (h_seg.len as f64 / info.stretchy_w as f64 * target_stretchy_w as f64).round()
                        as usize
                } else {
                    h_seg.len
                };

                let src_rect = Rect {
                    x: h_seg.start,
                    y: v_seg.start,
                    w: h_seg.len,
                    h: v_seg.len,
                };
                let tgt_rect = Rect {
                    x: target_x,
                    y: target_y,
                    w: target_w,
                    h: target_h,
                };

                target.paste_rectangle(&nine_patch, src_rect, tgt_rect)?;

                target_x += target_w;
            }
            target_y += target_h;
        }

        Ok(())
    })
    .map(Into::into)
}

#[pymodule]
fn _nine_patch(_py: Python<'_>, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(apply, &m)?)?;
    m.add_function(wrap_pyfunction!(get_padding, &m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{Bitmap, NinePatchInfo};

    fn rgba_bitmap(buffer: &[u8], width: usize, height: usize) -> Bitmap<'_> {
        Bitmap::new("RGBA", buffer, width, height)
    }

    #[test]
    fn black_content_markers_have_no_padding() {
        let pixels = [0, 0, 0, 255].repeat(16);
        let bitmap = rgba_bitmap(&pixels, 4, 4);

        assert_eq!(NinePatchInfo::compute_padding(&bitmap), (0, 0, 0, 0));
    }

    #[test]
    fn missing_content_markers_have_no_padding() {
        let pixels = [0, 0, 0, 0].repeat(16);
        let bitmap = rgba_bitmap(&pixels, 4, 4);

        assert_eq!(NinePatchInfo::compute_padding(&bitmap), (0, 0, 0, 0));
    }

    #[test]
    fn content_markers_define_each_padding_edge() {
        let mut pixels = [0, 0, 0, 0].repeat(36);
        let mut mark = |x: usize, y: usize| {
            let offset = (y * 6 + x) * 4;
            pixels[offset..offset + 4].copy_from_slice(&[0, 0, 0, 255]);
        };
        mark(2, 5);
        mark(3, 5);
        mark(5, 2);
        mark(5, 3);
        let bitmap = rgba_bitmap(&pixels, 6, 6);

        assert_eq!(NinePatchInfo::compute_padding(&bitmap), (1, 1, 1, 1));
    }
}
