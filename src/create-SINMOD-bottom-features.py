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

    # Check if output path is valid
    if output_path is not None:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        elif not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Write permission denied for the directory: {output_dir}")

    time_start = time.time()

    # Open the dataset
    ds = xr.open_dataset(file_path)

    print(f"\nAccessed the dataset after {time.time() - time_start:.2f} seconds")
    
    # Extract the variable
    if variable_name == "current_speed":
        data_var = ds["u_velocity"]
        #data_var = np.sqrt(ds["u_velocity"]**2 + ds["v_velocity"]**2)

    elif variable_name == "statistical_northness" or variable_name == "statistical_eastness":
        data_var = ds["u_velocity"]

    else:
        data_var = ds[variable_name]
    
    # Extract the first time step
    time_slice = data_var.isel(time=0)
    
    # Step 1: Create a mask for valid values in first time step
    valid_mask = ~time_slice.isnull()
    
    # Step 2: Find the index of the bottom-most valid layer for each (yc, xc)
    # Subtract 1 to get the correct index for the bottom layer
    bottom_layer_idx = valid_mask.argmin(dim="zc") - 1

    # Ensure bottom_layer_idx does not go negative (e.g., if all values are invalid in a column)
    bottom_layer_idx = bottom_layer_idx.clip(min=0)

    #try this
    #bottom_layer_idx_flat = bottom_layer_idx.values.flatten()
    #yc, xc = np.meshgrid(data_var.yc.values, data_var.xc.values, indexing='ij')
    #yc_flat = yc.flatten().astype(int)
    #xc_flat = xc.flatten().astype(int)
    #yc_flat = np.clip(yc_flat, 0, 554)  # because yc and xc have size 555
    #xc_flat = np.clip(xc_flat, 0, 554)

    # Step 3: Extract the bottom layer data across all time steps
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

    # Step 4: Calculate statistics across time
    time_avg_bottom_layer = bottom_layer_data.mean(dim="time", skipna=True)

    # Calculate both 10th and 90th percentiles
    time_percentiles = bottom_layer_data.quantile([0.1, 0.9], dim="time", skipna=True)

    print(f"\nComputed statistics after {time.time() - time_start:.2f} seconds")

    # Create a new DataArray with the (mean, 10th, 90th) percentiles and explicitly define the 'stat' dimension
    # Concatenate mean and percentiles in one line, drop 'quantile' and concatenate all together
    stats_array = xr.concat([time_avg_bottom_layer, time_percentiles.sel(quantile=0.1).drop_vars("quantile"), time_percentiles.sel(quantile=0.9).drop_vars("quantile")], dim="stat").rename(f"{variable_name}_features")

    # Name each value of the first dimension
    stats_array = stats_array.assign_coords(stat=["mean", "10th_percentile", "90th_percentile"])

    # Save to output file if specified
    if output_path:
        stats_array.to_netcdf(output_path, mode='w')

    return stats_array

# Run on temperature data
#process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "temperature", output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/temperature_bottom_features.nc")

#process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "salinity", output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/salinity_bottom_features.nc")

#process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "current_speed", output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/current_speed_bottom_features.nc")

filename_physstates_2d = '/cluster/projects/itk-SINMOD/coral-mapping/midnor/samp_2D_jan_jun.nc'
physstates_2d = Dataset(filename_physstates_2d, 'r')
gridLons = physstates_2d.variables['gridLons']

#Run on statistical northness
process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "statistical_northness", gridLons, output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/statistical_northness_features.nc")

# process_bottom_layer_no_dask("/cluster/projects/itk-SINMOD/coral-mapping/midnor/PhysStates_2019.nc", "statistical_eastness", gridLons, output_path="/cluster/home/haroldh/coral-mapping/processed_data/features/statistical_eastness_features.nc")
