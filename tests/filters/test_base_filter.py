#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import tornado

from preggy import expect
from tornado.testing import AsyncTestCase

from thumbor.filters import BaseFilter, FiltersFactory, filter_method
import thumbor.filters

from tests.base import PythonTestCase

FILTER_PARAMS_DATA = [
    {
        'type': BaseFilter.Number,
        'values': [
            ('1', 1), ('10', 10), ('99', 99), ('-1', -1), ('-10', -10), ('010', 10), ('  1 ', 1), ('0', 0)
        ],
        'invalid_values': ['x', 'x10', '10x', '- 1', '']
    },
    {
        'type': BaseFilter.PositiveNumber,
        'values': [
            ('1', 1), ('10', 10), ('99', 99), (' 1 ', 1), ('010', 10), ('0', 0)
        ],
        'invalid_values': ['-1', 'x', 'x10', '10x', '']
    },
    {
        'type': BaseFilter.PositiveNonZeroNumber,
        'values': [
            ('1', 1), ('10', 10), ('99', 99), (' 1 ', 1), ('010', 10)
        ],
        'invalid_values': ['-1', 'x', 'x10', '10x', '0', '']
    },
    {
        'type': BaseFilter.NegativeNumber,
        'values': [
            ('-1', -1), ('-10', -10), (' -9 ', -9), ('-0', 0)
        ],
        'invalid_values': ['x', 'x10', '10x', '- 1', '']
    },
    {
        'type': BaseFilter.DecimalNumber,
        'values': [
            ('1', 1.0), ('10', 10.0), ('99', 99.0), ('-1', -1.0), ('-10', -10.0), ('010', 10.0), ('  1 ', 1.0),
            ('1.0', 1.0), ('10.12', 10.12), ('9.9', 9.9), ('-1.1', -1.1), (' -10.2 ', -10.2), ('  1 ', 1.0),
            ('.11', 0.11), ('0.111', 0.111), ('0', 0.0)
        ],
        'invalid_values': ['x', 'x10', '10x', '- 1.1', '', '.']
    },
    {
        'type': BaseFilter.String,
        'values': [
            ('a', 'a'), ('bbbb', 'bbbb'), ('  cccc  ', 'cccc'), ('  cc:cc  ', 'cc:cc'), ('\'a,b\'', 'a,b')
        ],
        'invalid_values': ['', ',', ',,,,']
    },
    {
        'type': BaseFilter.Boolean,
        'values': [
            ('1', True), ('True', True), ('true', True), ('0', False), ('False', False), ('false', False), (' True ', True)
        ],
        'invalid_values': ['', 'x', 'TRUE', '111']
    },
    {
        'type': r'\dx\d',
        'values': [
            ('1x1', '1x1'), (' 9x9   ', '9x9')
        ],
        'invalid_values': ['a', ',', '9 x 9']
    }
]


class FilterParamsTestCase(PythonTestCase):
    def test_with_valid_values_should_correctly_parse_value(self):
        for params in FILTER_PARAMS_DATA:
            for test_data, expected_data in params['values']:
                BaseFilter.compile_regex({'name': 'x', 'params': [params['type']]})
                f = BaseFilter('x(%s)' % test_data)
                expect(f.params[0]).to_equal(expected_data)

    def test_with_invalid_values_should_correctly_parse_value(self):
        for params in FILTER_PARAMS_DATA:
            for test_data in params['invalid_values']:
                BaseFilter.compile_regex({'name': 'x', 'params': [params['type']]})
                f = BaseFilter('x(%s)' % test_data)
                expect(f.params).to_be_null()


class MyFilter(BaseFilter):
    @filter_method(BaseFilter.Number, BaseFilter.DecimalNumber)
    def my_filter(self, value1, value2):
        self.context.result_value = (value1, value2)


class StringFilter(BaseFilter):
    @filter_method(BaseFilter.String)
    def my_string_filter(self, value):
        self.context.result_value = value


class EmptyFilter(BaseFilter):
    @filter_method()
    def my_empty_filter(self):
        self.context.result_value = 'ok'


class AsyncFilter(BaseFilter):
    @filter_method(BaseFilter.String, async=True)
    @tornado.gen.coroutine
    def my_async_filter(self, value):
        self.context.result_value = value


class InvalidFilter(BaseFilter):
    def my_invalid_filter(self, value):
        return


class DoubleStringFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    def my_string_filter(self, value1, value2):
        self.context.result_value = (value1, value2)


class OptionalParamFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    def my_optional_filter(self, value1, value2="not provided"):
        self.context.result_value = (value1, value2)


class PreLoadFilter(BaseFilter):
    phase = thumbor.filters.PHASE_PRE_LOAD

    @filter_method(BaseFilter.String)
    def my_pre_load_filter(self, value):
        self.context.result_value = value


class BaseFilterTestCase(AsyncTestCase):
    def setUp(self, *args, **kwargs):
        super(BaseFilterTestCase, self).setUp(*args, **kwargs)
        self.context = self.get_context()
        self.factory = FiltersFactory([MyFilter, StringFilter, OptionalParamFilter, PreLoadFilter])
        self.runner = self.get_runner()

    def get_runner(self):
        return None

    def get_context(self):
        class Any:
            pass

        def is_multiple():
            return False

        context = Any()
        context.modules = Any()
        engine = Any()
        engine.is_multiple = is_multiple
        context.modules.engine = engine
        return context


class RunnerWithParametersFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_string_filter(aaaa):my_string_filter(bbb):my_pre_load_filter(ccc)'
        )

    def test_runner_with_parameters_should_create_two_instances(self):
        post_instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        pre_instances = self.runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
        expect(len(post_instances)).to_equal(2)
        expect(post_instances[0].__class__).to_equal(StringFilter)
        expect(post_instances[1].__class__).to_equal(StringFilter)
        expect(len(pre_instances)).to_equal(1)
        expect(pre_instances[0].__class__).to_equal(PreLoadFilter)

    @tornado.testing.gen_test
    def test_running_post_filters_should_run_only_post_filters(self):
        yield self.runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)
        post_instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        pre_instances = self.runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
        expect(len(post_instances)).to_equal(0)
        expect(len(pre_instances)).to_equal(1)

    @tornado.testing.gen_test
    def test_running_pre_filters_should_run_only_pre_filters(self):
        yield self.runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM)
        yield self.runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD)
        post_instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        pre_instances = self.runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
        expect(len(post_instances)).to_equal(0)
        expect(len(pre_instances)).to_equal(0)

    def test_invalid_filter(self):
        InvalidFilter.pre_compile()
        expect(hasattr(InvalidFilter, 'runnable_method')).to_be_false()

    def test_valid_filter_creates_a_runnable_method(self):
        MyFilter.pre_compile()
        expect(MyFilter.runnable_method).to_equal(MyFilter.my_filter)

    @tornado.testing.gen_test
    def test_valid_filter_sets_correct_result_value(self):
        f = MyFilter("my_filter(1, -1.1)", self.context)
        yield f.run()
        expect(self.context.result_value).to_equal((1, -1.1))

    @tornado.testing.gen_test
    def test_invalid_number_throws_an_error(self):
        f = MyFilter("my_invalid_filter(x, 1)", self.context)
        yield f.run()
        expect(hasattr(self.context, 'result_value')).to_be_false()

    @tornado.testing.gen_test
    def test_double_string_filter_sets_correct_values(self):
        DoubleStringFilter.pre_compile()
        f = DoubleStringFilter("my_string_filter(a, b)", self.context)
        yield f.run()
        expect(self.context.result_value).to_equal(('a', 'b'))

    @tornado.testing.gen_test
    def test_WithStringsWithCommas_sets_correct_values(self):
        DoubleStringFilter.pre_compile()
        tests = [
            ("my_string_filter(a,'b, c')", ('a', 'b, c')),
            ("my_string_filter('a,b', c)", ('a,b', 'c')),
            ("my_string_filter('ab', c)", ('ab', 'c')),
            ("my_string_filter('ab,', c)", ('ab,', 'c')),
            ("my_string_filter('ab,', ',c')", ('ab,', ',c')),
            ("my_string_filter('ab, c)", ('\'ab', 'c')),
            ("my_string_filter('ab, c',d)", ('ab, c', 'd')),
            ("my_string_filter('a,b, c)", None),
            ("my_string_filter('a,b, c')", None),
        ]
        for test, expected in tests:
            self.context.result_value = None
            f = DoubleStringFilter(test, self.context)
            yield f.run()
            expect(self.context.result_value).to_equal(expected)

    @tornado.testing.gen_test
    def test_with_empty_filter_should_call_filter(self):
        EmptyFilter.pre_compile()
        f = EmptyFilter('my_empty_filter()', self.context)
        yield f.run()
        expect(self.context.result_value).to_equal('ok')

    @tornado.testing.gen_test
    def test_with_async_filter_should_run(self):
        AsyncFilter.pre_compile()
        f = AsyncFilter("my_async_filter(yyy)", self.context)
        yield f.run()
        expect(self.context.result_value).to_equal('yyy')


class WithOneValidParamFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_filter(1, 0a):my_string_filter(aaaa)'
        )

    def test_should_create_one_instance(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(1)
        expect(instances[0].__class__).to_equal(StringFilter)


class WithParameterContainingColonsFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_string_filter(aaaa):my_string_filter(aa:aa)'
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(2)
        expect(instances[0].__class__).to_equal(StringFilter)
        expect(instances[1].__class__).to_equal(StringFilter)

    def test_should_understant_parameters(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(instances[0].params).to_equal(["aaaa"])
        expect(instances[1].params).to_equal(["aa:aa"])


class WithValidParamsFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_filter(1, 0):my_string_filter(aaaa)'
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(2)
        expect(instances[0].__class__).to_equal(MyFilter)
        expect(instances[1].__class__).to_equal(StringFilter)

    @tornado.testing.gen_test
    def test_when_running_should_create_two_instances(self):
        result = []
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        for instance in instances:
            yield instance.run()
            result.append(self.context.result_value)

        expect(result[0]).to_equal((1, 0.0))
        expect(result[1]).to_equal('aaaa')


class WithOptionalParamFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_optional_filter(aa, bb)'
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(1)
        expect(instances[0].__class__).to_equal(OptionalParamFilter)

    @tornado.testing.gen_test
    def test_should_understand_parameters(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        yield instances[0].run()
        expect(self.context.result_value).to_equal(("aa", "bb"))


class WithOptionalParamsInOptionalFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_optional_filter(aa)'
        )

    def test_should_create_one_instance(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(1)
        expect(instances[0].__class__).to_equal(OptionalParamFilter)

    @tornado.testing.gen_test
    def test_should_understand_parameters(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        yield instances[0].run()
        expect(self.context.result_value).to_equal(("aa", "not provided"))


class WithInvalidOptionalFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_optional_filter()'
        )

    def test_should_create_two_instances(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
        expect(len(instances)).to_equal(0)


class WithPreLoadFilterTestCase(BaseFilterTestCase):
    def get_runner(self):
        return self.factory.create_instances(
            self.context,
            'my_pre_load_filter(aaaa)'
        )

    def should_create_two_instances(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
        expect(len(instances)).to_equal(1)
        expect(instances[0].__class__).to_equal(PreLoadFilter)

    def should_understant_parameters(self):
        instances = self.runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
        expect(instances[0].params).to_equal(["aaaa"])
