# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 22:17:39 2018

@author: Court
"""

from bokeh.layouts import widgetbox
from bokeh.models import Slider
from bokeh.io import curdoc

# create slider widget
slider_widget = Slider(start = 0, end = 100, step = 10,
                       title = 'Single Slider')

# create a layout for the widget
slider_layout = widgetbox(slider_widget)

# add slider widget to the app
curdoc().add_root(slider_layout)
