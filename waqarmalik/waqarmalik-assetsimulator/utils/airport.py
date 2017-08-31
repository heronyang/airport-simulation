#!/opt/local/bin/python
from collections import OrderedDict

import pandas as pd
import bokeh.plotting as plt
from bokeh.objects import HoverTool


def main():
    nodes = pd.read_table('../data/KDFW/nodes.txt', comment='#', header=None)
    nodes.columns = ['x', 'y', 'ind', 'name', 'type', 'to', 'from']
    nodes.reset_index('ind', inplace=True)
    nodes.dropna(inplace=True)
    nodes[['x', 'y']] = nodes[['x', 'y']].astype(float).astype(int)
    nodes['color'] = 'teal'
    links = pd.read_table('../data/KDFW/links.txt', comment='#', header=None)
    links.dropna(inplace=True)
    links[[0, 1, 2]] = links[[0, 1, 2]].astype(int)

    # initialize plot
    plt.output_file("KDFW_Map_Viewer.html")
    tools = "pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    plt.figure(title='', tools=tools, x_range=[-1000, 1000], y_range=[-500, 1500], plot_width=1200, plot_height=1200)
    plt.hold()

    lx, ly = [], []
    for i in range(len(links)):
        n1 = nodes.loc[links.iloc[i, 1], :]
        n2 = nodes.loc[links.iloc[i, 2], :]
        lx.append([n1.x, n2.x])
        ly.append([n1.y, n2.y])

    source = plt.ColumnDataSource(data=nodes)
    plt.multi_line(lx, ly, line_width=1.0, color='darkgrey')
    plt.scatter('x', 'y', color='color', source=source, fill_alpha=0.5, radius=5)
    a = nodes.to_dict('list')
    plt.text(a['x'], a['y'], text=a['ind'], angle=0, text_font_size='8pt')
    hover = [t for t in plt.curplot().tools if isinstance(t, HoverTool)][0]
    hover.tooltips = OrderedDict([("(x,y)", "@x, @y"), ("Name", "@ind @name"), ("type", "@type")])
    plt.show()


if __name__ == '__main__':
    main()
    


