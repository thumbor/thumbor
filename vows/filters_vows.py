#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from pyvows import Vows, expect

from thumbor.filters import BaseFilter, FiltersFactory, filter_method

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
            ('a', 'a'), ('bbbb', 'bbbb'), ('  cccc  ', 'cccc'), ('  cc:cc  ', 'cc:cc')
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

        def should_correctly_parse_value(self, (type, test_data, expected_data)):
            BaseFilter.compile_regex({'name': 'x', 'params': [type]})
            f = BaseFilter('x(%s)' % test_data)
            expect(f.params[0]).to_equal(expected_data)

    class WithInvalidValues(Vows.Context):
        def topic(self, test_data):
            for value in test_data['invalid_values']:
                yield(test_data['type'], value)

        def should_not_parse_invalid_value(self, (type, test_data)):
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
    @filter_method(BaseFilter.String, async = True)
    def my_async_filter(self, callback, value):
        callback(value)

class InvalidFilter(BaseFilter):
    def my_invalid_filter(self, value):
        return value


@Vows.batch
class FilterVows(Vows.Context):

    class CreatingFilterInstances(Vows.Context):
        def topic(self):
            class Any: pass
            ctx = Any()
            ctx.modules = Any()
            ctx.modules.engine = Any()
            fact = FiltersFactory([MyFilter, StringFilter])
            return (fact, ctx)

        class WithOneValidParam(Vows.Context):
            def topic(self, (factory, context)):
                return factory.create_instances(context, 'my_filter(1, 0a):my_string_filter(aaaa)')

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(1)
                expect(instances[0].__class__).to_equal(StringFilter)

        class WithParameterContainingColons(Vows.Context):
            def topic(self, (factory, context)):
                return factory.create_instances(context, 'my_string_filter(aaaa):my_string_filter(aa:aa)')

            def should_create_two_instances(self, instances):
                expect(len(instances)).to_equal(2)
                expect(instances[0].__class__).to_equal(StringFilter)
                expect(instances[1].__class__).to_equal(StringFilter)

            def should_understant_parameters(self, instances):
                expect(instances[0].params).to_equal(["aaaa"])
                expect(instances[1].params).to_equal(["aa:aa"])

        class WithValidParams(Vows.Context):
            def topic(self, (factory, context)):
                return factory.create_instances(context, 'my_filter(1, 0):my_string_filter(aaaa)')

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
                    expect(result[0]).to_equal((1, 0.0))
                    expect(result[1]).to_equal('aaaa')


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
                expect(topic).to_equal((1, -1.1))

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

    class WithEmptyFilter(Vows.Context):
        def topic(self):
            EmptyFilter.pre_compile()
            f = EmptyFilter('my_empty_filter()')
            return f.run()

        def should_call_filter(self, value):
            expect(value).to_equal('ok')

    class WithAsyncFilter(Vows.Context):
        @Vows.async_topic
        def topic(self, callback):
            AsyncFilter.pre_compile()
            f = AsyncFilter("my_async_filter(yyy)")
            f.run(callback)

        def should_call_callback(self, topic):
            expect(topic.args[0]).to_equal('yyy')
