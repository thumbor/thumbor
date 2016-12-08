#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import logging

try:
    import cv
except ImportError:
    import cv2.cv as cv
import math

import tornado.gen
from PIL import Image, ImageDraw, ImageFont
from numpy import array

from thumbor.ext.filters import _alpha
from thumbor.filters import BaseFilter, filter_method

FONT_COLOUR = 'white'  # 字颜色
FONT_SIZE = 20  # 字体大小
FONT_X = 10  # 字体开始的X轴坐标
FONT_LINE_Y = 24  # 字体每行用24
HALF_WIDTH = 10  # 半角像素数
FULL_WIDTH = 20  # 全角像素数
TOTAL = 540  # 每行总像素数
ONE_LINE_TOTAL = 10  # 每行初始化像素数
WIDTH = 560  # 生成图片的默认宽度
HIGH = 24  # 生成图片的默认高度
EVERY_LINE_HIGH = 28  # 每行的高度
PIC_TYPE = '.png'  # 默认生成的图片是png


class Filter(BaseFilter):
    regex = r'(?:text_watermark\((?P<name>.*?),(?P<date>.*?),(?P<address>.*?),(?P<x>(?:-?\d+)|center|repeat),(?P<y>(?:-?\d+)|center|repeat))'

    # regex = r'(?:watermark\((?P<url>.*?),(?P<x>(?:-?\d+)|center|repeat),(?P<y>(?:-?\d+)|center|repeat),(?P<alpha>[\d]*?)\))'
    def on_image_ready(self, buffer):
        self.watermark_engine.load(buffer, self.extension)
        self.watermark_engine.enable_alpha()

        mode, data = self.watermark_engine.image_data_as_rgb()
        imgdata = _alpha.apply(mode,
                               self.alpha,
                               data)

        self.watermark_engine.set_image_data(imgdata)

        mos_x = self.x == 'repeat'
        mos_y = self.y == 'repeat'
        center_x = self.x == 'center'
        center_y = self.y == 'center'
        if not center_x and not mos_x:
            inv_x = self.x[0] == '-'
            x = int(self.x)
        if not center_y and not mos_y:
            inv_y = self.y[0] == '-'
            y = int(self.y)

        sz = self.engine.size
        watermark_sz = self.watermark_engine.size

        if not mos_x:
            repeat_x = (1, 0)
            if center_x:
                x = (sz[0] - watermark_sz[0]) / 2
            elif inv_x:
                x = (sz[0] - watermark_sz[0]) + x
        else:
            repeat_x = divmod(sz[0], watermark_sz[0])
            if sz[0] * 1.0 / watermark_sz[0] < 2:
                repeat_x = (math.ceil(sz[0] * 1.0 / watermark_sz[0]), 10)
                space_x = 10
        if not mos_y:
            repeat_y = (1, 0)
            if center_y:
                y = (sz[1] - watermark_sz[1]) / 2
            elif inv_y:
                y = (sz[1] - watermark_sz[1]) + y
        else:
            repeat_y = divmod(sz[1], watermark_sz[1])
            if sz[1] * 1.0 / watermark_sz[1] < 2:
                repeat_y = (math.ceil(sz[1] * 1.0 / watermark_sz[1]), 10)
                space_y = 10

        if not mos_x and not mos_y:
            self.engine.paste(self.watermark_engine, (x, y), merge=True)
        elif mos_x and mos_y:
            if (repeat_x[0] * repeat_y[0]) > 100:
                tmpRepeatX = min(6, repeat_x[0])
                tmpRepeatY = min(6, repeat_y[0])
                repeat_x = (tmpRepeatX, sz[0] - tmpRepeatX * watermark_sz[0])
                repeat_y = (tmpRepeatY, sz[1] - tmpRepeatY * watermark_sz[1])
            space_x = repeat_x[1] / (max(repeat_x[0], 2) - 1)
            space_y = repeat_y[1] / (max(repeat_y[0], 2) - 1)
            for i in range(int(repeat_x[0])):
                x = i * space_x + i * watermark_sz[0]
                for j in range(int(repeat_y[0])):
                    y = j * space_y + j * watermark_sz[1]
                    self.engine.paste(self.watermark_engine, (x, y), merge=True)
        elif mos_x:
            space_x = repeat_x[1] / (max(repeat_x[0], 2) - 1)
            for i in range(int(repeat_x[0])):
                x = i * space_x + i * watermark_sz[0]
                self.engine.paste(self.watermark_engine, (x, y), merge=True)
        else:
            space_y = repeat_y[1] / (max(repeat_y[0], 2) - 1)
            for j in range(int(repeat_y[0])):
                y = j * space_y + j * watermark_sz[1]
                self.engine.paste(self.watermark_engine, (x, y), merge=True)

        self.callback()

    @filter_method(
        BaseFilter.String,
        BaseFilter.String,
        BaseFilter.String,
        r'(?:-?\d+)|center|repeat',
        r'(?:-?\d+)|center|repeat',
        async=True
    )
    @tornado.gen.coroutine
    def text_watermark(self, callback, name, date, address, x, y):
        logging.error('name is: %s', name)
        self.name = name
        self.date = date
        self.address = address
        contents = [self.name, self.date, self.address]
        self.x = x
        self.y = y
        self.alpha = u'0'
        self.callback = callback
        self.extension = PIC_TYPE
        self.watermark_engine = self.context.modules.engine.__class__(self.context)
        try:
            fontFile = self.context.config.WATER_MARK_FONT_FILE_PATH
        except Exception, err:
            logging.error(err)
        buffer = yield tornado.gen.maybe_future(self.watermark(contents, fontFile))
        self.on_image_ready(buffer)

    def cal_lines(self, content, total=TOTAL, f_width=FULL_WIDTH, h_width=HALF_WIDTH):
        '''
            计算一段文本需要的行数
            total   =>  每行像素数
            f_width =>  全角像素数
            h_width =>  半角像素数
            返回:
                lines    总行数(int)
                split_points 需要换行的索引列表(list)
        '''
        lines = 1
        split_points = []

        one_line_total = ONE_LINE_TOTAL  # 初始化每行的像素数
        for index, word in enumerate(content):
            # 判断是否是半角
            if 0x001F < ord(word) < 0x0080:
                one_line_total += h_width
            else:
                one_line_total += f_width
            # 判断是否满行
            if one_line_total >= total:
                lines += 1
                split_points.append(index)
                one_line_total = ONE_LINE_TOTAL

        return lines, split_points, content

    def watermark(self, contents, fontFile):
        try:
            sz = self.engine.size
            self.watermark_width = sz[0]
            line_num = 0  # 总行数
            content_infos = []
            for item in contents:  # 对换行之后的内容逐行判断继续分割的行数
                result = self.cal_lines(item, self.watermark_width - ONE_LINE_TOTAL)
                line_num += result[0]
                content_infos.append(result)
            self.watermark_high = line_num * EVERY_LINE_HIGH + HIGH
            watermark = Image.new('RGBA', (self.watermark_width, self.watermark_high),
                                  (255, 255, 255, 0))
            font = ImageFont.truetype(fontFile, FONT_SIZE)
            draw = ImageDraw.Draw(watermark, 'RGBA')
            cur_line = 0  # 当前行数
            for _, split_points, text in content_infos:
                start = 0
                for end in split_points:  # 如果存在分割点(即当前内容需要换行)
                    draw.text(
                        (FONT_X, FONT_LINE_Y + cur_line * FONT_LINE_Y),  # 每行开始坐标
                        text[start:end],  # 内容
                        FONT_COLOUR,
                        font=font,
                    )
                    start = end
                    cur_line += 1
                remain = text[start:]
                if remain:
                    draw.text(
                        (FONT_X, FONT_LINE_Y + cur_line * FONT_LINE_Y),
                        remain,
                        FONT_COLOUR,
                        font=font,
                    )
                    cur_line += 1
            buffer = cv.EncodeImage(PIC_TYPE, cv.fromarray(array(watermark))).tostring()
            return buffer
        except Exception, err:
            logging.error(err)
