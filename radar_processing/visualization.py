import numpy as np
import os
import numpy as np
import math
from pyart.graph import RadarMapDisplayBasemap
import matplotlib.pyplot as plt
from visualize.colormap import nws_precip_colors
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import Basemap
from PIL import Image

def plot_taiwan_basemap(radius_km,degree_per_km,center_lat,center_lon):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 獲取當前檔案的目錄
    shape_path = os.path.join(base_dir, "../visualize/mapdata201805310314/COUNTY_MOI_1070516")
    m = Basemap(projection='merc', resolution='i', fix_aspect=True,
                llcrnrlon=center_lon - radius_km * degree_per_km,
                llcrnrlat=center_lat - radius_km * degree_per_km,
                urcrnrlon=center_lon + radius_km * degree_per_km,
                urcrnrlat=center_lat + radius_km * degree_per_km,
                lat_ts=center_lat)
    m.readshapefile(shape_path, linewidth=0.25, drawbounds=True, name='Taiwan')
    m.drawcoastlines(linewidth=1)
    return m

def visualize_and_save(radar_obj,layer_num, output_dir,date, time,param_type):
    cmap = mcolors.ListedColormap(nws_precip_colors())
    degree_per_km = 1 / 111  # 每公里對應的緯度或經度（粗略近似）
    margin = 5  # 給予額外的公里邊界

    # 中間點
    center_lat = radar_obj.latitude['data'][0]
    center_lon = radar_obj.longitude['data'][0]
    
    # 半徑 150 公里
    radius_km = 150

    # 計算經緯度範圍
    lat_range = radius_km / 111  # 每緯度約為 111 公里
    lon_range = radius_km / (111 * math.cos(math.radians(center_lat)))  # 每經度距離依緯度變化

    # 設定雷達站的經緯度範圍
    LAT_MIN = center_lat - lat_range
    LAT_MAX = center_lat + lat_range
    LON_MIN = center_lon - lon_range
    LON_MAX = center_lon + lon_range
    m = plot_taiwan_basemap(radius_km+margin,degree_per_km,center_lat,center_lon)

    # 繪製圖形
    plt.figure(figsize=(12, 10))  # 每次創建新的圖像，避免重疊
    display = RadarMapDisplayBasemap(radar_obj)
    display.plot_ppi_map(
        list(radar_obj.fields.keys())[0],
        sweep=0,
        resolution='h',
        vmin=0,
        vmax=65,
        cmap=cmap,  # 使用自定義顏色表
        min_lon=LON_MIN, max_lon=LON_MAX,
        min_lat=LAT_MIN, max_lat=LAT_MAX,
        mask_outside=True,
        projection='aeqd',
        basemap=m
    )
    plt.title(f'{date}{time}_layer_{layer_num:02d}_{param_type}')
    plt.savefig(os.path.join(output_dir, f'{date}{time}_layer_{layer_num:02d}_{param_type}.png'))
    plt.close()
    
def create_gif(image_dir, output_gif,date, time,param_type):
    """
    創建GIF
    """
    images = []
    for layer_num in range(1, 16):
        img_path = os.path.join(image_dir, f'{date}{time}_layer_{layer_num:02d}_{param_type}.png')
        img = Image.open(img_path)
        images.append(img)
    images[0].save(output_gif, save_all=True, append_images=images[1:], loop=0, duration=500)