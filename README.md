# 將極座標資料統一降解析度

## 檔案介紹
### configs 設定參數
### main 主程式
### radar_processing
#### RadarDataProcessorClass 極座標雷達物件
#### radar_polar_processor
1. regrid_polar_data 將雷達資料重新網格化到新的解析度
2. read_cwb_radar_sweep 讀取極座標雷達物件
3. create_radar_object_from_regridded 將重新網格化後的資料轉換為 pyart.core.radar.Radar 物件
#### visualization
1. 將可視化結果存成 png
2. 將各層 png 存成 GIF