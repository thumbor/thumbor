#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.transformer import Transformer
from thumbor.point import FocalPoint as fp
from transform_helper import TestData

TESTITEMS = [
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=150, crop_right=800, crop_bottom=450
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=150, crop_top=0, crop_right=450, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=400,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=0, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=140,
        target_width=180, target_height=100,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=14, crop_right=200, crop_bottom=126
    ),
    
    # tests with focal points
    TestData(
        source_width=200, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(100, 100, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=150.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=75.0, crop_top=0, crop_right=175.0, crop_bottom=200
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=225.0, crop_top=0, crop_right=325.0, crop_bottom=200
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(300, 50, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 150, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(100, 50, 1), fp(100, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=200, source_height=400,
        target_width=100, target_height=200,
        halign="center", valign="middle",
        focal_points=[fp(300, 50, 1), fp(300, 150, 1)],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=400, source_height=200,
        target_width=100, target_height=100,
        halign="center", valign="middle",
        focal_points=[fp(50, 100, 1), fp(50, 300, 1), fp(150, 100, 1), fp(150, 300, 1)],
        crop_left=50.0, crop_top=0, crop_right=250.0, crop_bottom=200
    ),

    #Width maior

    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=100, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=600, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=150, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=550, crop_top=0, crop_right=700, crop_bottom=300
    ),

    ##/* Height maior */
    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=350, crop_right=300, crop_bottom=800
    ),

    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=350, crop_right=300, crop_bottom=800
    ),

    TestData(
        source_width=300, source_height=800,
        target_width=200, target_height=300,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=350, crop_right=300, crop_bottom=800
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=183, crop_right=500, crop_bottom=600
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=183, crop_right=500, crop_bottom=600
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=0, crop_top=183, crop_right=500, crop_bottom=600
    ),

    ##Height na proporçao#
    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=300, target_height=0,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=250, target_height=0,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    #Width na proporçao
    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=400,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="center", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="left", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=600, source_height=800,
        target_width=0, target_height=350,
        halign="right", valign="bottom",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=150, crop_right=800, crop_bottom=450
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=800, source_height=300,
        target_width=400, target_height=150,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=50, crop_top=0, crop_right=650, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=600, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=300, target_height=150,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=100, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=275, crop_top=0, crop_right=425, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=150, crop_bottom=300
    ),

    TestData(
        source_width=700, source_height=300,
        target_width=150, target_height=300,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=550, crop_top=0, crop_right=700, crop_bottom=300
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=234, crop_bottom=700
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=58, crop_top=0, crop_right=292, crop_bottom=700
    ),

    TestData(
        source_width=350, source_height=700,
        target_width=200, target_height=600,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=116, crop_top=0, crop_right=350, crop_bottom=700
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=91, crop_right=500, crop_bottom=508
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=91, crop_right=500, crop_bottom=508
    ),

    TestData(
        source_width=500, source_height=600,
        target_width=300, target_height=250,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=0, crop_top=91, crop_right=500, crop_bottom=508
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="center", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=1, source_height=1,
        target_width=0, target_height=0,
        halign="right", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=200, source_height=400,
        target_width=0, target_height=1,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    TestData(
        source_width=200, source_height=200,
        target_width=16, target_height=16,
        halign="left", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),

    #--------------------Normal---------------------------------------
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=150,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=300
    ),
    #---------------Normal Invertido---------------------------
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=300, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="center", valign="top",
        focal_points=[],
        crop_left=150, crop_top=0, crop_right=450, crop_bottom=800
    ),
    TestData(
        source_width=600, source_height=800,
        target_width=150, target_height=400,
        halign="right", valign="top",
        focal_points=[],
        crop_left=300, crop_top=0, crop_right=600, crop_bottom=800
    ),
    #-----------Largo e Baixo---------------------
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    TestData(
        source_width=800, source_height=60,
        target_width=400, target_height=15,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=800, crop_bottom=30
    ),
    #----------------Alto e Estreito--------------------------
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=30, crop_bottom=800
    ),
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="center", valign="top",
        focal_points=[],
        crop_left=15, crop_top=0, crop_right=45, crop_bottom=800
    ),
    TestData(
        source_width=60, source_height=800,
        target_width=15, target_height=400,
        halign="right", valign="top",
        focal_points=[],
        crop_left=30, crop_top=0, crop_right=60, crop_bottom=800
    ),
    #------------------Valores Pequenos--------------------------
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="center", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    TestData(
        source_width=8, source_height=6,
        target_width=4, target_height=2,
        halign="right", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=8, crop_bottom=4
    ),
    #----------------Valores Pequeno Invertido-------------
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="left", valign="top",
        focal_points=[],
        crop_left=0, crop_top=0, crop_right=4, crop_bottom=8
    ),
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="center", valign="top",
        focal_points=[],
        crop_left=1, crop_top=0, crop_right=5, crop_bottom=8
    ),
    TestData(
        source_width=6, source_height=8,
        target_width=2, target_height=4,
        halign="right", valign="top",
        focal_points=[],
        crop_left=2, crop_top=0, crop_right=6, crop_bottom=8
    ),
    #----------------Valores Proporcionais-------------
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="left", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="center", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=400, target_height=300,
        halign="right", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    #----------------Valores Iguais-----------------------
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="left", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="center", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    ),
    TestData(
        source_width=800, source_height=600,
        target_width=800, target_height=600,
        halign="right", valign="top",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None
    )
]

FIT_IN_CROP_DATA = [
    (TestData(
        source_width=800, source_height=400,
        target_width=400, target_height=100,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True
    ), (200, 100)),

    (TestData(
        source_width=1000, source_height=250,
        target_width=500, target_height=200,
        halign="middle", valign="middle",
        focal_points=[],
        crop_left=None, crop_top=None, crop_right=None, crop_bottom=None,
        fit_in=True
    ), (500, 125))

]

def test_transformer():
    for data in TESTITEMS:
        yield assert_proper_operations, data

def assert_proper_operations(data):
    trans = Transformer(data.to_context())
    trans.transform()

    assert data.has_cropped_properly(), data.crop_error_message
    assert data.has_resized_properly(), data.resize_error_message

def test_fit_in():
    for data in FIT_IN_CROP_DATA:
        yield assert_fit_in_resize, data

def assert_fit_in_resize(data):
    data, expectations = data

    trans = Transformer(data.to_context())
    trans.transform()

    assert not data.engine.calls['crop']

    assert data.engine.calls['resize']
    assert len(data.engine.calls['resize']) == 1

    assert data.engine.calls['resize'][0]['width'] == expectations[0]
    assert data.engine.calls['resize'][0]['height'] == expectations[1]
