# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 23:09:26 2018

@author: Court
"""
# import required modules
import pandas as pd
import numpy as np
from datetime import datetime as dt

# import bokeh modules
from bokeh.models import (ColumnDataSource, NumeralTickFormatter,Select)
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.io import curdoc

#start=dt(2017, 1, 1)
#end=dt.now()

# generator function
def compute(principal, rate, payment, additional_payment):
    """
    Generator that yields successive period payment details
    """
    amount = payment + additional_payment
    while principal > 0:
        period_interest = round(principal * rate, 2)
        principal_reduction = min(principal, amount - period_interest)
        principal = principal - principal_reduction
        yield principal_reduction, period_interest, principal

# iterative code to generate loan schedule
def amortization_table(interest_rate, years, payments_year, principal, addl_principal=0, start_date=dt.today()):
    """
    Calculate the amortization schedule given the loan details


    :param interest_rate: The annual interest rate for this loan
    :param years: Number of years for the loan
    :param payments_year: Number of payments in a year
    :parma principal: Amount borrowed
    :param addl_principal (optional): Additional payments to be made each period. Default 0.
    :param start_date (optional): Start date. Default first of next month if none provided

    :return: 
        schedule: Amortization schedule as a pandas dataframe
        summary: Pandas dataframe that summarizes the payoff information
    """
    #Calculate the fixed payment 
    period_rate = interest_rate/payments_year 
    payment = round(-1 * np.pmt(period_rate, years*payments_year, principal),2)
    
    #Generate the period details schedule
    df = pd.DataFrame(list(compute(principal, period_rate, payment, addl_principal)), columns=["Principal", "Interest", "Curr_Balance"])
    df["Additional Payment"] = addl_principal
    df["Total Payment"] = df["Principal"] + df["Interest"]
    df["Cummulative Principal"] = df["Principal"].cumsum()
    payment_dates = pd.date_range(start_date, periods=len(df.index), freq='MS')
    df.insert(0,'Payment_Date', payment_dates)
    df.index += 1
    df.index.name = "Period"
    
    #Create a summary statistics table
    payoff_date = df['Payment_Date'].iloc[-1]
    stats = pd.Series([payoff_date, interest_rate, years, principal, payment, addl_principal, df["Interest"].sum()],
                     index=["Payoff Date", "Interest Rate", "Years", "Principal", "Payment", "Additional Payment", "Total Interest"], )
    return df, stats      

# setup three scenarios
start=dt(2017, 1, 1)    

schedule1, stats1 = amortization_table(0.0325, 30, 12, 94000, addl_principal=0, start_date = start)
schedule2, stats2 = amortization_table(0.0325, 30, 12, 94000, addl_principal=75, start_date = start)
schedule3, stats3 = amortization_table(0.0325, 30, 12, 94000, addl_principal=200, start_date = start)

# define plot plot attributes and legends
colors_list = ['#1f77b4','#ff7f0e','#2ca02c']
legends_list = ['scenario 1', 'scenario 2','scenario 3']

src = ColumnDataSource(data={
        'x':schedule1['Payment_Date'],
        'y':schedule1['Curr_Balance']
})

# set up the first figure
p1 = figure(plot_width=600, plot_height=250,title='Payoff Timelines',
 x_axis_type='datetime', toolbar_location=None)

p1.xgrid.grid_line_color = None
p1.xaxis.axis_label = 'Date'
p1.yaxis.axis_label = 'Loan Balance'
p1.yaxis[0].formatter = NumeralTickFormatter(format='$0,0')

# make plot
p1.line(x='x', y='y', line_width = 2, source=src)

# Define a callback function: update_plot
def update_plot1(attr, old, new):
    # If the new Selection is 'female_literacy', update 'y' to female_literacy
    if new == 'scenario 1': 
        src.data = {
            'x' : schedule1['Payment_Date'],
            'y' : schedule1['Curr_Balance']
        }
    elif new == 'scenario 2':
            src.data = {
                    'x' : schedule2['Payment_Date'],
                    'y' : schedule2['Curr_Balance']
            }   
    # Else, update to scenario3
    else:
        src.data = {
            'x' : schedule3['Payment_Date'],
            'y' : schedule3['Curr_Balance']
        }

####################################################
## TOTAL INTEREST PAID
####################################################

# Map second chart source data
def GroupbyYear(y):
    y['Year'] = y['Payment_Date'].dt.year
    return y.groupby('Year', as_index=False).agg({'Interest': 'sum'})
        
t1 = GroupbyYear(schedule1)
t2 = GroupbyYear(schedule2)
t3 = GroupbyYear(schedule3)

src2 = ColumnDataSource(data={
        'x2':t1['Year'],
        'y2':t1['Interest']
})

# setup second figure
p2 = figure(plot_width=600, plot_height=250, title='Total Annual Interest',
          toolbar_location=None)

p2.xgrid.grid_line_color = None
p2.xaxis.axis_label = 'Year'
p2.yaxis.axis_label = 'Total Annual Amount'
p2.yaxis[0].formatter = NumeralTickFormatter(format='$0,0')

p2.vbar(x='x2', top='y2', width = 0.9, source=src2)

# Define a callback function: update_plot
def update_plot2(attr, old, new):
    # If the new Selection is 'female_literacy', update 'y' to female_literacy
    if new == 'scenario 1': 
        src2.data = {
            'x2' : t1['Year'],
            'y2' : t1['Interest']
        }
    elif new == 'scenario 2':
            src2.data = {
                    'x2' : t2['Year'],
                    'y2' : t2['Interest']
            }   
    # Else, update to scenario3
    else:
        src2.data = {
            'x2' : t3['Year'],
            'y2' : t3['Interest']
        }

# Create a dropdown Select widget: select    
select = Select(title="Select Scenario",
 options=legends_list, value='scenario 1')

 # Attach the update_plot callback to the 'value' property of select
select.on_change('value', update_plot1, update_plot2)

# Create layout and add to current document
layout = row(select,column(p1, p2))
curdoc().add_root(layout)