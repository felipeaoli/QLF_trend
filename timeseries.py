# app.py
#        bokeh serve --show timeseries.py
import numpy as np

from numpy.random import random

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import ColumnDataSource, Figure
from bokeh.models.widgets import Select, TextInput
from bokeh.models import HoverTool

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, Spacer
from bokeh.models.widgets import Div, Select, RangeSlider
from bokeh.plotting import Figure
from bokeh.io import output_notebook, show
from scipy.stats import pearsonr

import json

try:
    data_json = json.load(open('QLFmock_trend_data-b0.json'))
except Exception as err:
    print(err)
noise = data_json['noise']
bias =  data_json['bias']
fidsnr = data_json['fidsnr']
peakcount = data_json['peakcount']
time = data_json['time']


data_model=dict(
        noise1 = noise[0], noise2=noise[1], noise3=noise[2], noise4=noise[3],
        bias1 = bias[0], bias2=bias[1], bias3=bias[2], bias4=bias[3], 
        peak = peakcount, time=time)

for i in list(range(len(fidsnr))):
    data_model['snr%s'%(i+1)] = fidsnr[i]

source = ColumnDataSource(data=dict(
        x=data_model['time'],
        y=data_model['noise1']
        ))

def style(p):
    # Title 
    p.title.align = 'center'
    p.title.text_font_size = '20pt'
    p.title.text_font = 'serif'

    # Axis titles
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_style = 'bold'

    # Tick labels
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'

    return p



fiber_tooltip = """
            <div>
                <div>
                    <span style="font-size: 12px; font-weight: bold; color: #303030;">time (time_scale): </span>
                    <span style="font-size: 13px; color: #515151">@x</span>
                </div>
                <div>
                    <span style="font-size: 12px; font-weight: bold; color: #303030;">y: </span>
                    <span style="font-size: 13px; color: #515151;">@y</span>
                </div>
            </div>
        """

hover = HoverTool(tooltips=fiber_tooltip)


plot = Figure(title='', plot_width=900, plot_height=300,
            toolbar_location='above',
            x_axis_label='Time (time scale)', y_axis_label='Noise (AMP 1)',
            #x_axis_type = "datetime",
            tools=[hover,'pan,wheel_zoom,box_select,reset'])

q = plot.line('x', 'y', source=source, #size= 8,
             line_color='dodgerblue')
            #hover_fill_color='blue', line_color='black')

qa_options =  ["noise%s"%i for i in list(range(1,5)) ]\
            + ["bias%s"%i for i in list(range(1,5)) ]\
            + ["snr%s"%(i+1) for i in list(range(len(fidsnr))) ]\
            + ['peak']

label_dict =  dict( zip( qa_options,
            ["Noise (AMP %s)"%i for i in list(range(1,5)) ]\
            + ["Bias (AMP %s)"%i for i in list(range(1,5)) ]\
            + ["SNR %s"%(i+1) for i in list(range(len(fidsnr))) ]\
            + ['Peak Count']            
            ))

# select_x = Select(title="x", value="noise1", options= qa_options)
select_y = Select(title="", value="noise1", options= qa_options) 

plot = style(plot)
plot.xaxis.major_label_overrides = {
    date: "{} {}".format(str(date)[4:-6], str(date)[:-4]) for i, date in enumerate(data_model['time'])
}


hhist, hedges = np.histogram(source.data['x'], bins='sqrt')
hzeros = np.zeros(len(hedges)-1)
hmax = max(hhist)*1.1


# 
def update_y(attrname, old, new):
    source.data['y'] = data_model[select_y.value]
    plot.yaxis.axis_label = label_dict[select_y.value]
    # vhist1, vedges1 = np.histogram( data_model[select_y.value], bins='sqrt')
    # vmax = max(vhist1)*1.1

    # pv.x_range.end= vmax
    # qv.data_source.data["right"] = vhist1
    # qv.data_source.data["bottom"] = vedges1[:-1]
    # qv.data_source.data["top"] = vedges1[1:]
    
    # corr = pearsonr(data_model[select_x.value], data_model[select_y.value])
    # plot.title.text =  'r: {:3.2f}'.format(corr[0])


    #pv.y_range = plot.y_range 

select_y.on_change('value', update_y)


# RangeSlider to change the maximum and minimum values on histogram
range_select = RangeSlider(start = 0, end = len(time), value = (0, 999),
                           step = 1, title = 'Time')


# Update function that accounts for all 3 controls
def update(attr, old, new):
    
    # Find the selected carriers
    #carriers_to_plot = [carrier_selection.labels[i] for i in carrier_selection.active]
    
    # Change binwidth to selected value
    #bin_width = binwidth_select.value

    # Value for the range slider is a tuple (start, end)
    rng_st = int(range_select.value[0])
    rng_end = int(range_select.value[1])
    print('\n' , rng_st)
    st = rng_st
    end = rng_end
    # Create new ColumnDataSource
    # new_src = make_dataset(range_start = range_start,
    #                        range_end = range_end,
    #                        bin_width = bin_width)

    # Update the data on the plot
    source.data['x'] = data_model['time'][st:end]
    print(select_y.value)
    source.data['y'] = data_model[select_y.value][st:end]
        

# Update the plot when the value is changed
range_select.on_change('value', update)



# start = Slider(title="start", value=data_model['time'][0], start=data_model['time'][0], 
#                 end=data_model['time'][-1], step=data_model['time'][1]-data_model['time'][0])

# end = Slider(title="end", value=data_model['time'][-1], start=data_model['time'][0], 
#                 end=data_model['time'][-1], step=data_model['time'][1]-data_model['time'][0])


# def update_range(attrname, old, new):

#     # Get the current slider values
#     a = start.value
#     b = end.value
#     ai = np.where(data_model['time']== a)
#     bi = np.where(data_model['time']== b)
#     # Generate the new ranges
#     source.data['time'] = data_model['time'][ai:bi]
#     source.data['y'] = data_model['y'][ai:bi]

#     #source.data = dict(x=x, y=y)



# for w in [start, end ]:
#     w.on_change('value', update_range)


        

# title = PreText("cam: b0")
# layout = column(
#      row( column(widgetbox(select_y)), column( row(plot, pv), 
#     row(ph, Spacer(width= pv.width, height=ph.height))  )))
frame_title ="""<div><p align="center" style="font-size: 40px;">Selected arm: b</p></div>"""
layout = column(widgetbox(Div(text=frame_title), width=1000, height=100),
    row(  column(widgetbox(select_y), widgetbox(range_select)),  plot) )
# column(
#      row( column(widgetbox(select_y)), column( row(plot, pv), 
#     row(ph, Spacer(width= pv.width, height=ph.height))  )))


curdoc().add_root(layout)




# def get_data(N):
#     return dict(x=random(size=N), y=random(size=N), r=random(size=N) * 0.03)

# source = ColumnDataSource(data=get_data(200))

# p = Figure(tools="", toolbar_location=None)
# r = p.circle(x='x', y='y', radius='r', source=source,
#              color="navy", alpha=0.6, line_color="white")

# COLORS = ["black", "firebrick", "navy", "olive", "goldenrod"]
# select = Select(title="Color", value="navy", options=COLORS)
# input_txt = TextInput(title="Number of points", value="200")

# def update_color(attrname, old, new):
#     r.glyph.fill_color = select.value
# select.on_change('value', update_color)

# def update_points(attrname, old, new):
#     N = int(input.value)
#     source.data = get_data(N)
# input_txt.on_change('value', update_points)

# layout = column(row(select, input_txt, width=400), row(p))

# curdoc().add_root(layout)
