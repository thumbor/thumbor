// thumbor imaging service
// https://github.com/thumbor/thumbor/wiki
//
// Licensed under the MIT license:
// http://www.opensource.org/licenses/mit-license
// Copyright (c) 2011 globo.com thumbor@googlegroups.com

pub fn bytes_per_pixel(image_mode: &str) -> usize {
    image_mode.len()
}

pub fn rgb_order(image_mode: &str, channel: char) -> usize {
    image_mode.find(channel).unwrap_or(image_mode.len())
}

pub fn colorize(value: u8, percent: i32, fill: i32) -> i32 {
    let diff = fill - value as i32;
    value as i32 + (diff * percent / 100)
}

pub fn adjust_color(value: i32) -> u8 {
    value.clamp(0, 255) as u8
}

pub fn adjust_color_double(value: f64) -> u8 {
    value.clamp(0.0, 255.0) as u8
}
