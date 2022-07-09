import plotly.graph_objects as go
import numpy as np

MAX = 2
MIN = 0
npstuff = np.linspace(MIN, MAX, 201)

nums = [2 ** (1 + n) for n in npstuff]

nums2 = list(set([2 ** (1 + int(n)) for n in npstuff]))
nums2.sort()

fig = go.Figure()
fig.add_trace(go.Scatter(x=npstuff, y=nums, mode='lines+markers'))
fig.add_trace(go.Line(x=np.linspace(MIN, MAX, len(nums2)), y=nums2))
fig.show()

