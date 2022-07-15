# Plotly tips and tricks (and other stuff i forget often)
## links:
* [https://plotly.com/python/axes/](https://plotly.com/python/axes/)
* [https://plotly.com/python/legend/](https://plotly.com/python/legend/)
* [https://plotly.com/python/](https://plotly.com/python/)
* [https://plotly.com/python/figure-labels/](https://plotly.com/python/figure-labels/)
* [https://plotly.com/python/bubble-charts/](https://plotly.com/python/bubble-charts/)
* [Is Plotly The Better Matplotlib? [YOUTUBE]](https://www.youtube.com/watch?v=GzUVacnrgFc)

## disabling/enabling lines/markers with scatter plots:
* note, this refers to using this import : `import plotly.graph_objects as go`


* markers only: `mode='markers`
* lines only: `mode='lines'`
* both (default): `mode='lines+markers'`

## legends for `import plotly.graph_objects as go`
* setting legend names: 
  * specify `name='DATA NAME'` in the call creating the actual graph object


* forcing plot to show legend:
    * `fig.update_layout(showlegend=True)`


* setting legend title text:
    * `fig.update_layout(legend_title_text='...')`


* disabling legend for a specific graph object:
    * specify `showlegend=False` in the graph object 


* hiding trace until legend is clicked:
    * specify `visible='legendonly'` in the graph object


* setting color/size of traces:
    * `(marker OR line, ect)=dict(color="MediumPurple", size=10)`

# code examples:
(from: [https://plotly.com/python/legend/](https://plotly.com/python/legend/))

## trace marker sizing:
```py
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[1, 2, 3, 4, 5],
    mode='markers',
    marker={'size':10}
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[5, 4, 3, 2, 1],
    mode='markers',
    marker={'size':100}
))

fig.update_layout(legend= {'itemsizing': 'constant'})

fig.show()
```

## grouped legend items:
```py
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 1, 3],
    legendgroup="group",  # this can be any string, not just "group"
    legendgrouptitle_text="First Group Title",
    name="first legend group",
    mode="markers",
    marker=dict(color="Crimson", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[2, 2, 2],
    legendgroup="group",
    name="first legend group - average",
    mode="lines",
    line=dict(color="Crimson")
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[4, 9, 2],
    legendgroup="group2",
    legendgrouptitle_text="Second Group Title",
    name="second legend group",
    mode="markers",
    marker=dict(color="MediumPurple", size=10)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[5, 5, 5],
    legendgroup="group2",
    name="second legend group - average",
    mode="lines",
    line=dict(color="MediumPurple")
))

fig.update_layout(title="Try Clicking on the Legend Items!")

fig.show()
```

### set axis labels (and extra fig configs)
```py
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    y=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    name="Name of Trace 1"       # this sets its legend entry
))


fig.add_trace(go.Scatter(
    x=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    y=[1, 0, 3, 2, 5, 4, 7, 6, 8],
    name="Name of Trace 2"
))

fig.update_layout(
    title="Plot Title",
    xaxis_title="X Axis Title",
    yaxis_title="Y Axis Title",
    legend_title="Legend Title",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)

fig.show()
```


### full label example
```py
import plotly.graph_objects as go
import numpy as np

MAX = 2
MIN = 0
npstuff = np.linspace(MIN, MAX, 201)

nums = [2 ** (1 + n) for n in npstuff]

nums2 = list(set([2 ** (1 + int(n)) for n in npstuff]))
nums2.sort()

fig = go.Figure()
fig.update_layout(
    title='two to the power of fractions vs whole numbers',
    xaxis_title='power',
    yaxis_title='two power result',
)
fig.add_trace(go.Scatter(name='fractional powers', x=npstuff, y=nums, mode='lines+markers', legendrank=2))
fig.add_trace(go.Scatter(name='integer powers', x=np.linspace(MIN, MAX, len(nums2)), y=nums2, legendrank=1))
fig.show()
```