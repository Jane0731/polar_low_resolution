import numpy as np
from pyart.config import get_metadata
from pyart.core.radar import Radar
from .RadarDataProcessorClass import RadarDataProcessor
from typing import Tuple

 
def regrid_polar_data(radar_obj: "RadarDataProcessor", 
                      new_ngate: int = 459,
                      new_nray: int = 360,
                      new_gate_start: float = 1.0,
                      new_gate_sp: float = 1.0,
                      new_azm_start: float = 0.0,
                      new_azm_sp: float = 1.0) -> Tuple[np.ndarray, dict]:
    """
    將雷達資料重新網格化到新的解析度
    
    Parameters
    ----------
    radar_obj : RadarDataProcessor
        原始雷達資料物件
    new_ngate : int
        新的距離方向格點數
    new_nray : int
        新的方位角方向格點數
    new_gate_start : float
        新的起始距離(km)
    new_gate_sp : float
        新的距離間隔(km)
    new_azm_start : float
        新的起始方位角(度)
    new_azm_sp : float
        新的方位角間隔(度)
        
    Returns
    -------
    Tuple[np.ndarray, dict]
        重新網格化後的資料陣列和更新後的header資訊
    """
    # 獲取原始資料參數
    orig_data = radar_obj.data
    orig_gate_start = radar_obj.gate_start / 1000.0  # 轉換到km
    orig_gate_sp = radar_obj.gate_sp / 1000.0        # 轉換到km
    orig_azm_start = radar_obj.azm_start
    orig_azm_sp = radar_obj.azm_sp
    
    # 創建新的資料陣列
    new_data = np.zeros((new_nray, new_ngate), dtype=np.float32)
    
    # 對每個新的網格點進行插值
    for j in range(new_nray):
        for i in range(new_ngate):
            # 計算新網格點的實際距離和方位角
            range_val = new_gate_start + new_gate_sp * i
            azimuth = np.mod(new_azm_start + new_azm_sp * j, 360.0)
            
            # 計算對應的原始網格索引
            gate_idx = round((range_val - orig_gate_start) / orig_gate_sp)
            azm_idx = round((azimuth - orig_azm_start) / orig_azm_sp)
            azm_idx = np.mod(azm_idx, radar_obj.nray)
            
            # 檢查索引是否在有效範圍內
            if 0 <= gate_idx < radar_obj.ngate and 0 <= azm_idx < radar_obj.nray:
                new_data[j, i] = orig_data[azm_idx, gate_idx]
            else:
                new_data[j, i] = radar_obj.rf_miss  # 使用缺失值
    
    # 更新header資訊
    new_header = {
        'nray': new_nray,
        'ngate': new_ngate,
        'azm_start': new_azm_start,
        'azm_sp': new_azm_sp,
        'gate_start': new_gate_start * 1000,  # 轉回meters
        'gate_sp': new_gate_sp * 1000         # 轉回meters
    }
    
    return new_data, new_header
   
def read_cwb_radar_sweep(fname):
    """
    Return an Radar object, representing a PPI scan.

    Parameters
    ----------
    ngates : int
        Number of gates per ray.
    rays_per_sweep : int
        Number of rays in each PPI sweep.
    nsweeps : int
        Number of sweeps.

    Returns
    -------
    radar : Radar
        Radar object with no fields, other parameters are set to default
        values.
    transforming CWB data into object	

    """
    cwb_radar_object = RadarDataProcessor(fname)

    ngates = cwb_radar_object.ngate
    rays_per_sweep = cwb_radar_object.nray
    nsweeps = 1

    nrays = rays_per_sweep * nsweeps

    time = get_metadata('time')
    _range = get_metadata('range')
    latitude = get_metadata('latitude')
    longitude = get_metadata('longitude')
    altitude = get_metadata('altitude')
    sweep_number = get_metadata('sweep_number')
    sweep_mode = get_metadata('sweep_mode')
    fixed_angle = get_metadata('fixed_angle')
    sweep_start_ray_index = get_metadata('sweep_start_ray_index')
    sweep_end_ray_index = get_metadata('sweep_end_ray_index')
    azimuth = get_metadata('azimuth')
    elevation = get_metadata('elevation')
    if ("ref_qc" in fname):
        varname = 'corrected_reflectivity'
    elif ("ref_raw" in fname):
        varname = 'reflectivity'
    elif ("vel" in fname):
        varname = 'velocity'
    elif ("phi" in fname):
        varname = 'differential_phase'
    elif ("zdr" in fname):
        varname = 'differential_reflectivity'
    elif ("rho" in fname):
        varname = 'cross_correlation_ratio'
    elif ('cref' in fname):
        varname = 'composite_reflectivity'
    elif ('spw' in fname):
        varname = 'spectrum_width'

    data_dict = get_metadata(varname)
    data_dict['data'] = np.array(cwb_radar_object.data, dtype='float32')
    fields = {varname: data_dict}
    scan_type = 'ppi'
    metadata = {'instrument_name': cwb_radar_object.name}

    time['data'] = np.arange(nrays, dtype='float64')
#    time['units'] = 'seconds since 1989-01-01T00:00:01Z'
    time['units'] = 'seconds since '+str(cwb_radar_object.yyyy) +\
        '-'+format(cwb_radar_object.mm, '02d') +\
        '-'+format(cwb_radar_object.dd, '02d') +\
        'T'+format(cwb_radar_object.hh, '02d') +\
        ':'+format(cwb_radar_object.mn, '02d') +\
        ':'+format(cwb_radar_object.ss, '02d')+'Z'
    _range['data'] = np.linspace(cwb_radar_object.gate_start, cwb_radar_object.gate_start +
                                 cwb_radar_object.gate_sp*(ngates-1), ngates).astype('float32')

    latitude['data'] = np.array([cwb_radar_object.rlat], dtype='float64')
    longitude['data'] = np.array([cwb_radar_object.rlon], dtype='float64')
    altitude['data'] = np.array([cwb_radar_object.radar_elev], dtype='float64')
    
    sweep_number['data'] = np.arange(nsweeps, dtype='int32')
    sweep_mode['data'] = np.array(['azimuth_surveillance'] * nsweeps)
    fixed_angle['data'] = np.array(
        [cwb_radar_object.theta] * nsweeps, dtype='float32')
    sweep_start_ray_index['data'] = np.arange(0, nrays, rays_per_sweep,
                                              dtype='int32')
    sweep_end_ray_index['data'] = np.arange(rays_per_sweep - 1, nrays,
                                            rays_per_sweep, dtype='int32')

  #  azimuth['data'] = np.arange(nrays, dtype='float32')
    azimuth['data'] = np.linspace(cwb_radar_object.azm_start, cwb_radar_object.azm_start +
                                  cwb_radar_object.azm_sp*(nrays-1), nrays, dtype='float32')
#    azimuth['data'] = np.linspace(cwb_radar_object.azm_start,cwb_radar_object.azm_start+0.5*(nrays-1),nrays, dtype='float32')
    elevation['data'] = np.array(
        [cwb_radar_object.theta] * nrays, dtype='float32')
    
    return Radar(time, _range, fields, metadata, scan_type,
                 latitude, longitude, altitude,
                 sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
                 sweep_end_ray_index,
                 azimuth, elevation,
                 instrument_parameters=None)

def create_radar_object_from_regridded(filename: str, 
                                     new_data: np.ndarray,
                                     radar_obj: "RadarDataProcessor",
                                     new_header: dict) -> Radar:
    """
    將重新網格化後的資料轉換為 pyart.core.radar.Radar 物件
    
    Parameters
    ----------
    filename : str
        原始檔案名稱(用於判斷資料類型)
    new_data : np.ndarray
        重新網格化後的資料
    radar_obj : RadarDataProcessor
        原始雷達資料物件
    new_header : dict
        新的header資訊
    
    Returns
    -------
    Radar
        可供pyart使用的Radar物件
    """
    # 設定基本參數
    nsweeps = 1
    nrays = new_header['nray']
    ngates = new_header['ngate']
    
    # 準備metadata
    time = get_metadata('time')
    _range = get_metadata('range')
    latitude = get_metadata('latitude')
    longitude = get_metadata('longitude')
    altitude = get_metadata('altitude')
    sweep_number = get_metadata('sweep_number')
    sweep_mode = get_metadata('sweep_mode')
    fixed_angle = get_metadata('fixed_angle')
    sweep_start_ray_index = get_metadata('sweep_start_ray_index')
    sweep_end_ray_index = get_metadata('sweep_end_ray_index')
    azimuth = get_metadata('azimuth')
    elevation = get_metadata('elevation')

    # 判斷資料類型
    if "ref_qc" in filename:
        varname = 'corrected_reflectivity'
    elif "ref_raw" in filename:
        varname = 'reflectivity'
    elif "vel" in filename:
        varname = 'velocity'
    elif "phi" in filename:
        varname = 'differential_phase'
    elif "zdr" in filename:
        varname = 'differential_reflectivity'
    elif "rho" in filename:
        varname = 'cross_correlation_ratio'
    elif 'cref' in filename:
        varname = 'composite_reflectivity'
    elif 'spw' in filename:
        varname = 'spectrum_width'

    # 設定資料欄位
    data_dict = get_metadata(varname)
    data_dict['data'] = new_data
    fields = {varname: data_dict}
    
    # 設定時間
    time['data'] = np.arange(nrays, dtype='float64')
    time['units'] = (f'seconds since {radar_obj.yyyy:04d}-{radar_obj.mm:02d}-{radar_obj.dd:02d}'
                    f'T{radar_obj.hh:02d}:{radar_obj.mn:02d}:{radar_obj.ss:02d}Z')

    # 設定距離
    _range['data'] = np.linspace(new_header['gate_start'], 
                                new_header['gate_start'] + new_header['gate_sp'] * (ngates-1),
                                ngates).astype('float32')

    # 設定位置資訊
    latitude['data'] = np.array([radar_obj.rlat], dtype='float64')
    longitude['data'] = np.array([radar_obj.rlon], dtype='float64')
    altitude['data'] = np.array([radar_obj.radar_elev], dtype='float64')

    # 設定掃描資訊
    sweep_number['data'] = np.arange(nsweeps, dtype='int32')
    sweep_mode['data'] = np.array(['azimuth_surveillance'] * nsweeps)
    fixed_angle['data'] = np.array([radar_obj.theta] * nsweeps, dtype='float32')
    sweep_start_ray_index['data'] = np.arange(0, nrays, nrays, dtype='int32')
    sweep_end_ray_index['data'] = np.arange(nrays-1, nrays, nrays, dtype='int32')

    # 設定方位角和仰角
    azimuth['data'] = np.linspace(new_header['azm_start'],
                                 new_header['azm_start'] + new_header['azm_sp'] * (nrays-1),
                                 nrays, dtype='float32')
    elevation['data'] = np.array([radar_obj.theta] * nrays, dtype='float32')

    # 建立metadata
    metadata = {'instrument_name': radar_obj.name}
    scan_type = 'ppi'
    distances = np.linspace(
        new_header['gate_start']/1000,
        new_header['gate_start']/1000 + new_header['gate_sp']/1000 * (ngates),
        ngates
    )
    return Radar(time, _range, fields, metadata, scan_type,
                latitude, longitude, altitude,
                sweep_number, sweep_mode, fixed_angle,
                sweep_start_ray_index, sweep_end_ray_index,
                azimuth, elevation,
                instrument_parameters=None),distances
    
