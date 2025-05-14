import xarray as xr
import time 
import os
from netCDF4 import Dataset
import numpy as np

def process_bottom_layer_no_dask(
    file_path,
    variable_name,
    gridLons=None, #to calculate statistical northness and eastness
    #chunks={"time":-1, "zc": -1, "yc": 50, "xc": 50},
    output_path=None
):
    """
    Process bottom layer data for a specified variable in a NetCDF file.
    
    Parameters:
    - file_path (str): Path to the NetCDF file.
    - variable_name (str): Name of the variable to process.
    - output_path (str): Path to save the processed file (optional). If None, the result is not saved.
    
    Returns:
    - xarray.DataArray: The time-averaged bottom layer data.
    """

    if output_path is not None:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        elif not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Write permission denied for the directory: {output_dir}")

    time_start = time.time()

    ds = xr.open_dataset(file_path)

    print(f"\nAccessed the dataset after {time.time() - time_start:.2f} seconds")
    
    if variable_name == "current_speed":
        data_var = ds["u_velocity"]

    elif variable_name == "statistical_northness" or variable_name == "statistical_eastness":
        data_var = ds["u_velocity"]

    else:
        data_var = ds[variable_name]
    
    time_slice = data_var.isel(time=0)
    
    valid_mask = ~time_slice.isnull()
    
    bottom_layer_idx = valid_mask.argmin(dim="zc") - 1

    bottom_layer_idx = bottom_layer_idx.clip(min=0)

      if variable_name == "current_speed":
        bottom_layer_data = (data_var.isel(zc=bottom_layer_idx)**2 + ds["v_velocity"].isel(zc=bottom_layer_idx)**2)**0.5
        
    elif variable_name == "statistical_northness" or variable_name == "statistical_eastness":
        longitude_of_projection_origin = ds["grid_mapping"].attrs["longitude_of_projection_origin"]
        theta = gridLons - longitude_of_projection_origin
        
        eastward_velocity = data_var.isel(zc=bottom_layer_idx)* np.cos(np.deg2rad(theta)) - ds["v_velocity"].isel(zc=bottom_layer_idx)*np.sin(np.deg2rad(theta))
        northward_velocity = data_var.isel(zc=bottom_layer_idx)* np.sin(np.deg2rad(theta)) + ds["v_velocity"].isel(zc=bottom_layer_idx)* np.cos(np.deg2rad(theta))

        aspect = np.arctan2(eastward_velocity, northward_velocity)

        if variable_name == 'statistical_eastness':
            print("halloo")
            bottom_layer_data = np.sin(aspect)
        else:
            bottom_layer_data = np.cos(aspect)
        
    else:
        bottom_layer_data = data_var.isel(zc=bottom_layer_idx)
        
    ds.close()

    print(f"\nExtracted the bottom layer data after {time.time() - time_start:.2f} seconds.\n\nStarting computation of statistics...")

    time_avg_bottom_layer = bottom_layer_data.mean(dim="time", skipna=True)

    time_percentiles = bottom_layer_data.quantile([0.1, 0.9], dim="time", skipna=True)

    print(f"\nComputed statistics after {time.time() - time_start:.2f} seconds")

    stats_array = xr.concat([time_avg_bottom_layer, time_percentiles.sel(quantile=0.1).drop_vars("quantile"), time_percentiles.sel(quantile=0.9).drop_vars("quantile")], dim="stat").rename(f"{variable_name}_features")

    stats_array = stats_array.assign_coords(stat=["mean", "10th_percentile", "90th_percentile"])

    if output_path:
        stats_array.to_netcdf(output_path, mode='w')

    return stats_array

filename_physstates_2d = '/cluster/projects/itk-SINMOD/coral-mapping/midnor/samp_2D_jan_jun.nc'
physstates_2d = Dataset(filename_physstates_2d, 'r')
gridLons = physstates_2d.variables['gridLons']

#Run on statistical northness
process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "statistical_northness", gridLons, output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/statistical_northness_features.nc")

