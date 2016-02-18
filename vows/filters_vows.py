#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import functools

from pyvows import Vows, expect

from thumbor.filters import BaseFilter, FiltersFactory, filter_method
import thumbor.filters

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


@Vows.batch
class FilterParamsVows(Vows.Context):
    def topic(self):
        for test_data in FILTER_PARAMS_DATA:
            yield(test_data)

    class WithValidValues(Vows.Context):
        def topic(self, test_data):
            for value in test_data['values']:
                yield(test_data['type'], value[0], value[1])

        def should_correctly_parse_value(self, data):
            type, test_data, expected_data = data
            BaseFilter.compile_regex({'name': 'x', 'params': [type]})
            f = BaseFilter('x(%s)' % test_data)
            expect(f.params[0]).to_equal(expected_data)

    class WithInvalidValues(Vows.Context):
        def topic(self, test_data):
            for value in test_data['invalid_values']:
                yield(test_data['type'], value)

        def should_not_parse_invalid_value(self, data):
            type, test_data = data
            BaseFilter.compile_regex({'name': 'x', 'params': [type]})
            f = BaseFilter('x(%s)' % test_data)
            expect(f.params).to_be_null()


class MyFilter(BaseFilter):
    @filter_method(BaseFilter.Number, BaseFilter.DecimalNumber)
    def my_filter(self, value1, value2):
        return (value1, value2)


class StringFilter(BaseFilter):
    @filter_method(BaseFilter.String)
    def my_string_filter(self, value):
        return value


class EmptyFilter(BaseFilter):
    @filter_method()
    def my_empty_filter(self):
        return 'ok'


class AsyncFilter(BaseFilter):
    @filter_method(BaseFilter.String, async=True)
    def my_async_filter(self, callback, value):
        callback(value)


class InvalidFilter(BaseFilter):
    def my_invalid_filter(self, value):
        return value


class DoubleStringFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    def my_string_filter(self, value1, value2):
        return (value1, value2)


class OptionalParamFilter(BaseFilter):
    @filter_method(BaseFilter.String, BaseFilter.String)
    def my_optional_filter(self, value1, value2="not provided"):
        return (value1, value2)


class PreLoadFilter(BaseFilter):
    phase = thumbor.filters.PHASE_PRE_LOAD

    @filter_method(BaseFilter.String)
    def my_pre_load_filter(self, value):
        return value


@Vows.batch
class FilterVows(Vows.Context):

    class CreatingFilterInstances(Vows.Context):
        def topic(self):
            class Any:
                pass
            ctx = Any()
            ctx.modules = Any()
            engine = Any()

            def is_multiple():
                return False

            engine.is_multiple = is_multiple
            ctx.modules.engine = engine
            fact = FiltersFactory([MyFilter, StringFilter, OptionalParamFilter, PreLoadFilter])
            return (fact, ctx)

        class RunnerWithParameters(Vows.Context):

            def topic(self, parent_topic):
                factory, context = parent_topic
                return factory.create_instances(context, 'my_string_filter(aaaa):my_string_filter(bbb):my_pre_load_filter(ccc)')

            def should_create_two_instances(self, runner):
                post_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
                pre_instances = runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
                expect(len(post_instances)).to_equal(2)
                expect(post_instances[0].__class__).to_equal(StringFilter)
                expect(post_instances[1].__class__).to_equal(StringFilter)
                expect(len(pre_instances)).to_equal(1)
                expect(pre_instances[0].__class__).to_equal(PreLoadFilter)

            class RunningPostFilters(Vows.Context):
                @Vows.async_topic
                def topic(self, callback, runner):
                    runner.apply_filters(thumbor.filters.PHASE_POST_TRANSFORM, functools.partial(callback, runner))

                def should_run_only_post_filters(self, args):
                    runner = args.args[0]
                    post_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
                    pre_instances = runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
                    expect(len(post_instances)).to_equal(0)
                    expect(len(pre_instances)).to_equal(1)

                class RunningPreFilters(Vows.Context):
                    @Vows.async_topic
                    def topic(self, callback, args):
                        runner = args.args[0]
                        runner.apply_filters(thumbor.filters.PHASE_PRE_LOAD, functools.partial(callback, runner))

                    def should_run_only_pre_filters(self, args):
                        runner = args.args[0]
                        post_instances = runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]
                        pre_instances = runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]
                        expect(len(post_instances)).to_equal(0)
                        expect(len(pre_instances)).to_equal(0)

        class WithOneValidParam(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_filter(1, 0a):my_string_filter(aaaa)')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_one_instance(self, instances):
                expect(len(instances)).to_equal(1)
                expect(instances[0].__class__).to_equal(StringFilter)

        class WithParameterContainingColons(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_string_filter(aaaa):my_string_filter(aa:aa)')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(2)
                expect(instances[0].__class__).to_equal(StringFilter)
                expect(instances[1].__class__).to_equal(StringFilter)

            def should_understant_parameters(self, instances):
                expect(instances[0].params).to_equal(["aaaa"])
                expect(instances[1].params).to_equal(["aa:aa"])

        class WithValidParams(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_filter(1, 0):my_string_filter(aaaa)')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(2)
                expect(instances[0].__class__).to_equal(MyFilter)
                expect(instances[1].__class__).to_equal(StringFilter)

            class WhenRunning(Vows.Context):
                def topic(self, instances):
                    result = []
                    for instance in instances:
                        result.append(instance.run())
                    return result

                def should_create_two_instances(self, result):
                    expect(result[0]).to_equal([(1, 0.0)])
                    expect(result[1]).to_equal(['aaaa'])

        class WithOptionalParamFilter(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_optional_filter(aa, bb)')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(1)
                expect(instances[0].__class__).to_equal(OptionalParamFilter)

            def should_understand_parameters(self, instances):
                expect(instances[0].run()).to_equal([("aa", "bb")])

        class WithOptionalParamsInOptionalFilter(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_optional_filter(aa)')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(1)
                expect(instances[0].__class__).to_equal(OptionalParamFilter)

            def should_understand_parameters(self, instances):
                expect(instances[0].run()).to_equal([("aa", "not provided")])

        class WithInvalidOptionalFilter(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_optional_filter()')
                return runner.filter_instances[thumbor.filters.PHASE_POST_TRANSFORM]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(0)

        class WithPreLoadFilter(Vows.Context):
            def topic(self, parent_topic):
                factory, context = parent_topic
                runner = factory.create_instances(context, 'my_pre_load_filter(aaaa)')
                return runner.filter_instances[thumbor.filters.PHASE_PRE_LOAD]

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(1)
                expect(instances[0].__class__).to_equal(PreLoadFilter)

            def should_understant_parameters(self, instances):
                expect(instances[0].params).to_equal(["aaaa"])

    class WithInvalidFilter(Vows.Context):
        def topic(self):
            InvalidFilter.pre_compile()
            return InvalidFilter

        def doesnt_create_a_runnable_method(self, cls):
            expect(hasattr(cls, 'runnable_method')).to_be_false()

    class WithValidFilter(Vows.Context):
        def topic(self):
            MyFilter.pre_compile()
            return MyFilter

        def creates_a_runnable_method(self, cls):
            expect(cls.runnable_method).to_equal(MyFilter.my_filter)

        class WithValidNumber:
            def topic(self, cls):
                f = cls("my_filter(1, -1.1)")
                return f.run()

            def sets_correct_result_value(self, topic):
                expect(topic).to_equal([(1, -1.1)])

        class WithInvalidNumber:
            def topic(self, cls):
                f = cls("my_invalid_filter(x, 1)")
                return f.run()

            def throws_an_error(self, topic):
                expect(hasattr(topic, 'result')).to_be_false()

        class WhenPassedCallback:
            @Vows.async_topic
            def topic(self, callback, cls):
                f = cls("my_filter(1, -1.1)")
                f.run(callback)

            def calls_callback(self, topic):
                expect(topic.args).to_equal(())

    class DoubleStringFilter(Vows.Context):
        def topic(self):
            DoubleStringFilter.pre_compile()
            return DoubleStringFilter

        class WithTwoNormalStrings:
            def topic(self, cls):
                f = cls("my_string_filter(a, b)")
                return f.run()

            def sets_correct_values(self, topic):
                expect(topic).to_equal([('a', 'b')])

        class WithStringsWithCommas:
            def topic(self, cls):
                tests = [
                    ("my_string_filter(a,'b, c')", [('a', 'b, c')]),
                    ("my_string_filter('a,b', c)", [('a,b', 'c')]),
                    ("my_string_filter('ab', c)", [('ab', 'c')]),
                    ("my_string_filter('ab,', c)", [('ab,', 'c')]),
                    ("my_string_filter('ab,', ',c')", [('ab,', ',c')]),
                    ("my_string_filter('ab, c)", [('\'ab', 'c')]),
                    ("my_string_filter('ab, c',d)", [('ab, c', 'd')]),
                    ("my_string_filter('a,b, c)", None),
                    ("my_string_filter('a,b, c')", None),
                ]
                for (test, expected) in tests:
                    f = cls(test)
                    yield f.run(), expected

            def sets_correct_values(self, test_data):
                result, expected = test_data
                expect(result).to_equal(expected)

    class WithEmptyFilter(Vows.Context):
        def topic(self):
            EmptyFilter.pre_compile()
            f = EmptyFilter('my_empty_filter()')
            return f.run()

        def should_call_filter(self, value):
            expect(value).to_equal(['ok'])

    class WithAsyncFilter(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            AsyncFilter.pre_compile()
            f = AsyncFilter("my_async_filter(yyy)")
            f.run(callback)

        def should_call_callback(self, topic):
            expect(topic.args[0]).to_equal('yyy')
