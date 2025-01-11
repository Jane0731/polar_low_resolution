from configs import config
from radar_processing.visualization import visualize_and_save,create_gif
import os
import numpy as np
from radar_processing.radar_polar_processor import regrid_polar_data,create_radar_object_from_regridded
from radar_processing.RadarDataProcessorClass import RadarDataProcessor

def main(config):
    input_dir = os.path.normpath(os.path.abspath(config['input_dir']))
    output_dir = os.path.normpath(os.path.abspath(config['output_dir']))
    dates = config['dates']
    times = config['times']
    param_types = config['param_types']

    for date in dates:
        date_output_dir = os.path.join(output_dir, date)  # 為每個日期創建資料夾
        os.makedirs(date_output_dir, exist_ok=True)

    for time in times:            
        time_output_dir = os.path.join(date_output_dir, time)  # 為每個時間創建資料夾
        os.makedirs(time_output_dir, exist_ok=True)

        for param_type in param_types:
            print(f"Processing {date} - {time} - {param_type}")

            param_output_dir = os.path.join(time_output_dir, param_type)
            os.makedirs(param_output_dir, exist_ok=True)

            gif_path = os.path.join(param_output_dir, f"radar_animation_{param_type}.gif")
            radar_matrix = []

            # 處理 1-15 層
            for layer_num in range(1, 16):
                filename = os.path.join(input_dir, f"RCWF.{date}.{time}.{param_type}.{layer_num:02d}.gz")
                if not os.path.exists(filename):
                    print(f"File not found: {filename}")
                    continue

                radar_obj = RadarDataProcessor(filename)
                new_data, new_header = regrid_polar_data(radar_obj)
                radar, distances = create_radar_object_from_regridded(filename, new_data, radar_obj, new_header)

                # 可視化並保存圖片
                visualize_and_save(radar,layer_num, param_output_dir, date, time, param_type)

                # 添加到三維矩陣
                radar_matrix.append(new_data)

            # 保存三維矩陣
            if radar_matrix:
                radar_matrix = np.stack(radar_matrix)
                np.save(os.path.join(param_output_dir, f"radar_matrix_{param_type}.npy"), radar_matrix)

                # 創建GIF
                create_gif(param_output_dir, gif_path, date, time, param_type)

if __name__ == "__main__":
    main(config)
