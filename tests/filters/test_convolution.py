# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2022 globo.com thumbor@googlegroups.com

import signal

from preggy import expect
from tornado.testing import gen_test

from tests.base import FilterTestCase
from thumbor.ext.filters import _convolution
from thumbor.filters.convolution import Filter


class ConvolutionFilterTestCase(FilterTestCase):
    @gen_test
    async def test_convolution_filter_true(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.convolution",
            "convolution(1;2;1;2;4;2;1;2;1,3,true)",
        )
        expected = self.get_fixture("convolution-true.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    @gen_test
    async def test_convolution_filter_false(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.convolution",
            "convolution(-1;-1;-1;-1;8;-1;-1;-1;-1,3,false)",
        )
        expected = self.get_fixture("convolution-false.png")

        ssim = self.get_ssim(image, expected)
        expect(ssim).to_be_greater_than(0.99)

    def test_zero_columns_is_rejected_by_regex(self):
        """columns=0 must not match the filter regex (DoS prevention)."""
        Filter.pre_compile()
        match = Filter.regex.match("convolution(1;2;1;2;4;2;1;2;1,0,true)")
        expect(match).to_be_null()

    def test_c_extension_raises_on_zero_columns(self):
        """The C extension must raise ValueError for columns=0, not crash."""
        width, height = 2, 2
        img_bytes = bytes([128, 128, 128] * width * height)
        err = None
        try:
            _convolution.apply(
                "RGB",
                img_bytes,
                width,
                height,
                ("1",),
                0,
                False,
            )
        except Exception as exc:  # pylint: disable=broad-except
            err = exc
        expect(err).to_be_an_error_like(ValueError)

    def test_convolution_redos_does_not_hang(self):
        Filter.pre_compile()

        # PoC payload: 30 repeated elements with no trailing column count;
        # the old `(A;)*A` pattern would backtrack exponentially here.
        malicious = "convolution(" + ";".join(["-11"] * 30) + ")"

        def _timeout_handler(signum, frame):
            raise AssertionError(
                "ReDoS: convolution regex did not complete within 1 second"
            )

        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(1)
        try:
            result = Filter.regex.match(malicious)
        finally:
            signal.alarm(0)

        # The input is intentionally malformed (missing column count), so the
        # regex must not match. What matters is that it returns promptly.
        expect(result).to_be_null()
