import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4]))
fig.add_trace(go.Bar(y=[1, 4, 3, 2]))
fig.update_layout(title='Hello Figure')
fig.show()
