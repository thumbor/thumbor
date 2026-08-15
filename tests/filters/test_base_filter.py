# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import sys
from unittest.mock import MagicMock, patch

import pytest
from tornado.testing import gen_test

import thumbor.filters
from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context
from thumbor.filters import BaseFilter, FiltersFactory, filter_method
from thumbor.importer import Importer

FILTER_PARAMS_DATA = [
    {
        "type": BaseFilter.Number,
        "values": [
            ("1", 1),
            ("10", 10),
            ("99", 99),
            ("-1", -1),
            ("-10", -10),
            ("010", 10),
            ("  1 ", 1),
            ("0", 0),
        ],
        "invalid_values": ["x", "x10", "10x", "- 1", ""],
    },
    {
        "type": BaseFilter.PositiveNumber,
        "values": [
            ("1", 1),
            ("10", 10),
            ("99", 99),
            (" 1 ", 1),
            ("010", 10),
            ("0", 0),
        ],
        "invalid_values": ["-1", "x", "x10", "10x", ""],
    },
    {
        "type": BaseFilter.PositiveNonZeroNumber,
        "values": [("1", 1), ("10", 10), ("99", 99), (" 1 ", 1), ("010", 10)],
        "invalid_values": ["-1", "x", "x10", "10x", "0", ""],
    },
    {
        "type": BaseFilter.NegativeNumber,
        "values": [("-1", -1), ("-10", -10), (" -9 ", -9), ("-0", 0)],
        "invalid_values": ["x", "x10", "10x", "- 1", ""],
    },
    {
        "type": BaseFilter.DecimalNumber,
        "values": [
            ("1", 1.0),
            ("10", 10.0),
            ("99", 99.0),
            ("-1", -1.0),
            ("-10", -10.0),
            ("010", 10.0),
            ("  1 ", 1.0),
            ("1.0", 1.0),
            ("10.12", 10.12),
            ("9.9", 9.9),
            ("-1.1", -1.1),
            (" -10.2 ", -10.2),
            ("  1 ", 1.0),
            (".11", 0.11),
            ("0.111", 0.111),
            ("0", 0.0),
        ],
        "invalid_values": ["x", "x10", "10x", "- 1.1", "", "."],
    },
    {
        "type": BaseFilter.String,
        "values": [
            ("a", "a"),
            ("bbbb", "bbbb"),
            ("  cccc  ", "cccc"),
            ("  cc:cc  ", "cc:cc"),
            ("'a,b'", "a,b"),
        ],
        "invalid_values": ["", ",", ",,,,"],
    },
    {
        "type": BaseFilter.Boolean,
        "values": [
            ("1", True),
            ("True", True),
            ("true", True),
            ("0", False),
            ("False", False),
            ("false", False),
            (" True ", True),
        ],
        "invalid_values": ["", "x", "TRUE", "111"],
    },
    {
        "type": r"\dx\d",
        "values": [("1x1", "1x1"), (" 9x9   ", "9x9")],
        "invalid_values": ["a", ",", "9 x 9"],
    },
]


class FilterParamsTestCase(TestCase):
    def test_with_valid_values_should_correctly_parse_value(self):
        for params in FILTER_PARAMS_DATA:
            for test_data, expected_data in params["values"]:
                BaseFilter.compile_regex(
                    {"name": "x", "params": [params["type"]]}
                )
                filter_instance = BaseFilter(f"x({test_data})")
                assert filter_instance.params[0] == expected_data

    def test_with_invalid_values_should_correctly_parse_value(self):
        for params in FILTER_PARAMS_DATA:
            for test_data in params["invalid_values"]:
                BaseFilter.compile_regex(
                    {"name": "x", "params": [params["type"]]}
                )
                filter_instance = BaseFilter(f"x({test_data})")
                assert filter_instance.params is None


class MyFilter(BaseFilter):
    @filter_method(BaseFilter.Number, BaseFilter.DecimalNumber)
    async def my_filter(self, value1, value2):
        return (value1, value2)


class StringFilter(BaseFilter):
    @filter_method(BaseFilter.String)
    async def my_string_filter(self, value):
        return value


class EmptyFilter(BaseFilter):
    @filter_method()
    async def my_empty_filter(self):
        return "ok"


class InvalidFilter(BaseFilter):
    async def my_invalid_filter(self, value):
        return value


class DoubleStringFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    async def my_string_filter(self, value1, value2):
        return (value1, value2)


class OptionalParamFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    async def my_optional_filter(self, value1, value2="not provided"):
        return (value1, value2)


class PreLoadFilter(BaseFilter):
    phase = thumbor.filters.PHASE_PRE_LOAD

    @filter_method(BaseFilter.String)
    async def my_pre_load_filter(self, value):
        return value


class BaseFilterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.context = self.get_context()
        self.factory = FiltersFactory(
            [MyFilter, StringFilter, OptionalParamFilter, PreLoadFilter]
        )
        self.runner = self.get_runner()

    def get_runner(self):
        return None

    def get_context(self):
        def is_multiple():
            return False

        cfg = Config()
        importer = Importer(cfg)
        importer.import_modules()
        context = Context(config=cfg, importer=importer)
        context.modules.engine.is_multiple = is_multiple
        return context


class RunnerWithParametersFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            "my_string_filter(aaaa):my_string_filter(bbb):my_pre_load_filter(ccc)",
        )

    def test_runner_with_parameters_should_create_two_instances(self):
        post_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        pre_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_PRE_LOAD
        ]
        assert len(post_instances) == 2
        assert post_instances[0].__class__ == StringFilter
        assert post_instances[1].__class__ == StringFilter
        assert len(pre_instances) == 1
        assert pre_instances[0].__class__ == PreLoadFilter

    @gen_test
    async def test_running_post_filters_should_run_only_post_filters(self):
        await self.runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)
        post_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        pre_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_PRE_LOAD
        ]
        assert len(post_instances) == 0
        assert len(pre_instances) == 1

    @gen_test
    async def test_running_pre_filters_should_run_only_pre_filters(self):
        await self.runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)
        await self.runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD)
        post_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        pre_instances = self.runner.filter_instances[
            thumbor.filters.PHASE_PRE_LOAD
        ]
        assert len(post_instances) == 0
        assert len(pre_instances) == 0

    def test_invalid_filter(self):
        InvalidFilter.pre_compile()
        assert not hasattr(InvalidFilter, "runnable_method")

    def test_valid_filter_creates_a_runnable_method(self):
        MyFilter.pre_compile()
        assert MyFilter.runnable_method == MyFilter.my_filter

    @gen_test
    async def test_valid_filter_sets_correct_result_value(self):
        filter_instance = MyFilter("my_filter(1, -1.1)")
        result = await filter_instance.run()
        assert result == [(1, -1.1)]

    @gen_test
    async def test_invalid_number_throws_an_error(self):
        filter_instance = MyFilter("my_invalid_filter(x, 1)")
        result = await filter_instance.run()
        assert not hasattr(result, "result")

    @gen_test
    async def test_double_string_filter_sets_correct_values(self):
        DoubleStringFilter.pre_compile()
        filter_instance = DoubleStringFilter("my_string_filter(a, b)")
        result = await filter_instance.run()
        assert result == [("a", "b")]

    @gen_test
    async def test_with_strings_with_commas_sets_correct_values(self):
        DoubleStringFilter.pre_compile()
        tests = [
            ("my_string_filter(a,'b, c')", [("a", "b, c")]),
            ("my_string_filter('a,b', c)", [("a,b", "c")]),
            ("my_string_filter('ab', c)", [("ab", "c")]),
            ("my_string_filter('ab,', c)", [("ab,", "c")]),
            ("my_string_filter('ab,', ',c')", [("ab,", ",c")]),
            ("my_string_filter('ab, c)", [("'ab", "c")]),
            ("my_string_filter('ab, c',d)", [("ab, c", "d")]),
            ("my_string_filter('a,b, c)", None),
            ("my_string_filter('a,b, c')", None),
        ]
        for test, expected in tests:
            filter_instance = DoubleStringFilter(test)
            result = await filter_instance.run()
            assert result == expected

    @gen_test
    async def test_with_empty_filter_should_call_filter(self):
        EmptyFilter.pre_compile()
        filter_instance = EmptyFilter("my_empty_filter()")
        result = await filter_instance.run()
        assert result == ["ok"]

    @pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="python37 mock does not support async mocks, see https://bugs.python.org/issue26467",
    )
    @gen_test
    @patch.object(StringFilter, "run", autospec=True)
    async def test_apply_filters_respects_filter_params_order(self, run_mock):
        filter_order = []
        run_mock.side_effect = lambda self: filter_order.append(self.params[0])
        await self.runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)
        assert filter_order == ["aaaa", "bbb"]


class WithOneValidParamFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_filter(1, 0a):my_string_filter(aaaa)"
        )

    def test_should_create_one_instance(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 1
        assert instances[0].__class__ == StringFilter


class WithParameterContainingColonsFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_string_filter(aaaa):my_string_filter(aa:aa)"
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 2
        assert instances[0].__class__ == StringFilter
        assert instances[1].__class__ == StringFilter

    def test_should_understant_parameters(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert instances[0].params == ["aaaa"]
        assert instances[1].params == ["aa:aa"]


class WithValidParamsFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_filter(1, 0):my_string_filter(aaaa)"
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 2
        assert instances[0].__class__ == MyFilter
        assert instances[1].__class__ == StringFilter

    @gen_test
    async def test_when_running_should_create_two_instances(self):
        result = []
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        for instance in instances:
            result.append(await instance.run())
        assert result[0] == [(1, 0.0)]
        assert result[1] == ["aaaa"]


class WithOptionalParamFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_optional_filter(aa, bb)"
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 1
        assert instances[0].__class__ == OptionalParamFilter

    @gen_test
    async def test_should_understand_parameters(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert await instances[0].run() == [("aa", "bb")]


class WithOptionalParamsInOptionalFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_optional_filter(aa)"
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 1
        assert instances[0].__class__ == OptionalParamFilter

    @gen_test
    async def test_should_understand_parameters(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        result = await instances[0].run()
        assert result == [("aa", "not provided")]


class WithInvalidOptionalFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_optional_filter()"
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_POST_TRANSFORM
        ]
        assert len(instances) == 0


class WithPreLoadFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context, "my_pre_load_filter(aaaa)"
        )

    def should_create_two_instances(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_PRE_LOAD
        ]
        assert len(instances) == 1
        assert instances[0].__class__ == PreLoadFilter

    def should_understant_parameters(self):
        instances = self.runner.filter_instances[
            thumbor.filters.PHASE_PRE_LOAD
        ]
        assert instances[0].params == ["aaaa"]


class FilterMethodMetricsTestCase(TestCase):

    def _make_context(self, multiple=False, frame_count=3):
        cfg = Config()
        importer = Importer(cfg)
        importer.import_modules()
        context = Context(config=cfg, importer=importer)
        context.metrics = MagicMock()

        if multiple:
            context.modules.engine.is_multiple = lambda: True
            context.modules.engine.frame_engines = lambda: [
                MagicMock() for _ in range(frame_count)
            ]
        else:
            context.modules.engine.is_multiple = lambda: False

        return context

    def _make_success_filter(self, context):
        class _SuccessFilter(BaseFilter):
            @filter_method(BaseFilter.Number)
            async def success_filter(self, value):
                return value

        _SuccessFilter.__module__ = "thumbor.filters.success_filter"
        _SuccessFilter.pre_compile()
        return _SuccessFilter("success_filter(42)", context)

    def _make_error_filter(self, context):
        class _ErrorFilter(BaseFilter):
            @filter_method(BaseFilter.Number)
            async def error_filter(self, value):
                raise ValueError("boom")

        _ErrorFilter.__module__ = "thumbor.filters.error_filter"
        _ErrorFilter.pre_compile()
        return _ErrorFilter("error_filter(1)", context)

    @gen_test
    async def test_emits_count_and_timing_on_success(self):
        context = self._make_context()
        instance = self._make_success_filter(context)
        await instance.run()

        context.metrics.incr.assert_called_once_with(
            "filter.success_filter.count"
        )
        context.metrics.timing.assert_called_once()
        assert (
            context.metrics.timing.call_args[0][0]
            == "filter.success_filter.time"
        )

    @gen_test
    async def test_emits_metrics_once_for_multiple_engines(self):
        context = self._make_context(multiple=True)
        instance = self._make_success_filter(context)
        result = await instance.run()

        assert result == [42, 42, 42]
        context.metrics.incr.assert_called_once_with(
            "filter.success_filter.count"
        )
        context.metrics.timing.assert_called_once()
        assert (
            context.metrics.timing.call_args[0][0]
            == "filter.success_filter.time"
        )

    @gen_test
    async def test_uses_filter_name_instead_of_module_name_in_metrics(self):
        context = self._make_context()

        class _AliasedFilter(BaseFilter):
            @filter_method(BaseFilter.Number)
            async def public_name(self, value):
                return value

        _AliasedFilter.__module__ = "thumbor.filters.internal_module_name"
        factory = FiltersFactory([_AliasedFilter])
        runner = factory.create_instances(context, "public_name(42)")
        filters = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

        await filters[0].run()

        incr_calls = [c[0][0] for c in context.metrics.incr.call_args_list]
        timing_calls = [c[0][0] for c in context.metrics.timing.call_args_list]

        assert "filter.public_name.count" in incr_calls
        assert "filter.public_name.time" in timing_calls
        assert "filter.internal_module_name.count" not in incr_calls
        assert "filter.internal_module_name.time" not in timing_calls

    @gen_test
    async def test_timing_value_is_non_negative_integer(self):
        context = self._make_context()
        instance = self._make_success_filter(context)
        await instance.run()

        _, elapsed = context.metrics.timing.call_args[0]

        assert isinstance(elapsed, int)
        assert elapsed >= 0
        assert elapsed < 5000

    @gen_test
    async def test_emits_error_and_timing_on_exception(self):
        context = self._make_context()
        instance = self._make_error_filter(context)

        with pytest.raises(ValueError, match="boom"):
            await instance.run()

        context.metrics.incr.assert_called_once_with(
            "filter.error_filter.error"
        )
        context.metrics.timing.assert_called_once()
        assert (
            context.metrics.timing.call_args[0][0]
            == "filter.error_filter.time"
        )

    @gen_test
    async def test_does_not_fail_when_metrics_is_none(self):
        context = self._make_context()
        context.metrics = None

        class _SafeFilter(BaseFilter):
            @filter_method(BaseFilter.Number)
            async def safe_filter(self, value):
                return value

        _SafeFilter.__module__ = "thumbor.filters.safe_filter"
        _SafeFilter.pre_compile()

        instance = _SafeFilter("safe_filter(7)", context)

        await instance.run()
