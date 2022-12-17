import os
import folium
import pandas as pd
import geopandas as gpd
from IPython.display import display


stop_gdf = gpd.read_file(
    "/Users/Licious/Downloads/Project Data-20221102/2109_STIB_MIVB_Network/ACTU_STOPS.shp"
)
lines_gdf = gpd.read_file(
    "/Users/Licious/Downloads/Project Data-20221102/2109_STIB_MIVB_Network/ACTU_LINES.shp"
)
color_select = {
    "T": {1: "black", 2: "red"},
    "B": {1: "blue", 2: "lightgreen"},
    "M": {1: "yellow", 2: "pink"},
}
icon_select = {"T": "plane", "B": "bus", "M": "dribbble"}
stop_col = [
    "Code_Ligne",
    "Variante",
    "succession",
    "stop_id",
    "descr_fr",
    "descr_nl",
    "alpha_fr",
    "alpha_nl",
    "coord_x",
    "coord_y",
    "mode",
    "numero_lig",
    "terminus",
]


def map_maker(mode, line, direction, stop_name):
    map = folium.Map(
        location=[50.8260, 4.3802], tiles="CartoDB positron", zoom_start=15
    )
    filtered_data = stop_gdf.loc[
        (stop_gdf["mode"] == mode)
        & (stop_gdf["Variante"] == direction + 1)
        & (stop_gdf["numero_lig"] == line)
    ]
    layer1 = folium.GeoJson(
        data=filtered_data,
        popup=folium.GeoJsonPopup(stop_col),
        zoom_on_click=True,
        name=f"{mode} {direction+1}",
        marker=folium.Marker(
            icon=folium.Icon(
                icon=icon_select[mode],
                prefix="fa",
                color=color_select[mode][direction + 1],
                icon_color="white",
            )
        ),
    )
    layer1.add_to(map)
    # str(data[i]).rjust(3, "0")
    line_e = f"{line}{mode.lower()}".rjust(4, "0")
    print(line_e)
    # print(f"{line}{mode}")
    # df[df.name.str.match(regex)]
    # print(lines_gdf['LIGNE'].drop_duplicates())
    # print(lines_gdf.LIGNE.str.match(f"[0]*{line}{mode}"))
    # filtered_line= lines_gdf[lines_gdf.LIGNE.str.match(f"[0]*{line}{mode}")]
    filtered_line = lines_gdf.loc[
        (lines_gdf["VARIANTE"] == direction + 1)
     & 
     (lines_gdf["LIGNE"] == line_e)
     ]
    print(filtered_line.head())
    layer2 = folium.GeoJson(
        data=filtered_line,
        popup=folium.GeoJsonPopup(["LIGNE"]),
        name=f"line {mode}",
        style_function=lambda x: {
            "color": "red",
            # x['properties']['COLOR_HEX'],
            "weight": 10,
            "opacity": 1,
        },
    )
    layer2.add_to(map)
    folium.LayerControl().add_to(map)

    from folium.plugins import Search
    servicesearch = Search(
            layer=layer1,
            search_label="descr_fr",
            placeholder='Search for a service',
            collapsed=False,
        ).add_to(map)
    map.save(f"data/test_{mode}_{line}_{direction}.html")
    return f"data/test_{mode}_{line}_{direction}.html"


# map_maker("T", 7, 0, "GOSSART")
