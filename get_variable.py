import numpy as np
import netCDF4 as nc
import netCDF4 as nc
import numpy as np
from netCDF4 import Dataset

def get_variable(filename, var_name, time_step=None, depth=None, latSlice=None, lonSlice=None):
    """
    Retrieves a variable from a NetCDF file with flexibility for different dimensions.
    
    Args:
        filename (str): The path to the NetCDF file.
        var_name (str): The name of the variable to retrieve.
        time_step (int, optional): The time index to retrieve (if applicable).
        depth (int, optional): The depth index to retrieve (if applicable).
        latSlice (slice, optional): The latitude slice (if applicable).
        lonSlice (slice, optional): The longitude slice (if applicable).

    Returns:
        np.ndarray: The data for the specified variable and dimensions.
    """
    with Dataset(filename, 'r') as ds:
        var = ds.variables[var_name]
        dimensions = len(var.dimensions)
        
        # Handling based on dimensions
        if dimensions == 1:  # 1D variable (e.g., time)
            return var[:]
        elif dimensions == 3:  # time, lat, lon
            if time_step is not None:
                return var[time_step, latSlice, lonSlice]
            else:
                return var[:, latSlice, lonSlice]
        elif dimensions == 4:  # time, depth, lat, lon
            if time_step is not None and depth is not None:
                return var[time_step, depth, latSlice, lonSlice]
            elif time_step is not None:
                return var[time_step, :, latSlice, lonSlice]
            elif depth is not None:
                return var[:, depth, latSlice, lonSlice]
            else:
                return var[:, :, latSlice, lonSlice]
        else:
            raise ValueError(f"Unsupported variable dimensions: {dimensions}")
