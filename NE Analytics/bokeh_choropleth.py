import json
from pyproj import Proj, transform

from bokeh.core.properties import Enum
from bokeh.models import GeoJSONDataSource, HoverTool, ColorBar, BasicTicker, BasicTickFormatter
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN

def bokeh_choropleth(data_df, geojson, key_on, data, tooltips, color_mapper):
    geojson2 = geojson.copy()
    in_proj = Proj(init='epsg:4326')
    out_proj = Proj(init='epsg:3857')
    
    for f in geojson2['features']:
        for col in data_df.columns:
            f['properties'][col] = str(data_df[data_df[key_on[0]] == f['properties'][key_on[1]]][col].values[0])
        if f['geometry']['type'] == 'MultiPolygon':
            f['geometry']['coordinates'] = [[[[x for x in transform(in_proj, out_proj, p[0], p[1])] for p in c]] for c in f['geometry']['coordinates']]
        else:
            f['geometry']['coordinates'] = [[[x for x in transform(in_proj, out_proj, p[0], p[1])] for p in c] for c in f['geometry']['coordinates']]
    geo_source = GeoJSONDataSource(geojson=json.dumps(geojson2, ensure_ascii=True))
    
    TOOLS = "pan,wheel_zoom,hover,save"
    choropleth = figure(tools=TOOLS,
                        x_axis_location=None, y_axis_location=None)
    choropleth.patches('xs', 'ys',
                       source=geo_source,
                       line_color="black",
                       line_width=0.2,
                       fill_color={'field': data, 'transform': color_mapper},
                       fill_alpha=1)

    choropleth.add_tile(STAMEN_TERRAIN)

    color_bar = ColorBar(color_mapper=color_mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(color_mapper.palette)),
                         formatter=BasicTickFormatter(precision=2, use_scientific=False),
                         label_standoff=6, border_line_color=None, location=(0,0),
                         scale_alpha=1,
                         orientation='horizontal')
    choropleth.add_layout(color_bar, 'above')
    
    hover = choropleth.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = tooltips
    
    return choropleth
