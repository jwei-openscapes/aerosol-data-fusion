# Saving as NetCDF
# 
# There are several ways to save gridded data as netcdf:
# 
# 1. Translation from geoTIFF format to netcdf 
# - this is taken care of by gdal
# - does not support time dimension
# 2. Single file saving: gridNC_single(limit, gsize, indata, inlat, inlon, filename)
# - limit - [lat1, lat2, lon1, lon2]
# - gsize - pixel size
# - indata - raw satellite data from import in
# - inlat
# - inlon
# - filename (that we save to, including path)
# 3. Single time file saving: gridNC_time(limit, gsize, indata, inlat, inlon, filename)
# - limit - [lat1, lat2, lon1, lon2]
# - gsize - pixel size
# - indata - raw satellite data from import in (multiple file array)
# - inlat
# - inlon
# - filename (that we save to, including path)
# 4. Multi time file saving: 

from http.client import MOVED_PERMANENTLY
import netCDF4
import numpy as np
import numpy.ma as ma
import time

import gridding
import sat_data_input
import filter_data
import naming_conventions
import solar_zenith
import datetime
 
#filename - 'gridNet.nc'
# takes representation of a single file
# to make geo2D variable - add _CoordinateAxisType = "Lat";
def gridNC_single(limit, gsize, indata, inlat, inlon, filename):

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    #lat_dim= len(np.arange(minlat, maxlat, gsize)) #int(1+round(((maxlat-minlat)/gsize)))
    #lon_dim= len(np.arange(minlon, maxlon, gsize)) # int(1+round(((maxlon-minlon)/gsize)))
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon dimensions
    time = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('lat', 'f4', ('lat',)) #latitude is fatitude
    lons = ds.createVariable('lon', 'f4', ('lon',))
    
    value = ds.createVariable('value', 'f4', ('time', 'lat', 'lon', ))
    value.units = 'unknown'
    
    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,gsize,indata,inlat,inlon)
    
    rotated = list(zip(*mintau))[::-1]
    value[0, :, :] = (np.flipud(rotated))
    
    #close file
    ds.close()
    
# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
def gridNC_time(limit, gsize, indata, inlat, inlon, time_interval, phy_list, geo_list, sat_files, filename):

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    #lat_dim= len(np.arange(minlat, maxlat, gsize)) #int(1+round(((maxlat-minlat)/gsize)))
    #lon_dim= len(np.arange(minlon, maxlon, gsize)) # int(1+round(((maxlon-minlon)/gsize)))
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon dimensions
    time = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('lat', 'f4', ('lat',)) #latitude is fatitude
    lons = ds.createVariable('lon', 'f4', ('lon',))
    
    value = ds.createVariable('value', 'f4', ('time', 'lat', 'lon', ))
    value.units = 'unknown'
    
    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    #run through and assign gridded data to corresponding time interval    
    for i in range(0,len(sat_files),time_interval):
        satellites = sat_files[i: i+time_interval]
        print(satellites)
        avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau =  gridding.multi_sensor_grid(satellites, gsize, limit, phy_list, geo_list)
    
        rotated = list(zip(*mintau))[::-1]
        value[i, :, :] = (np.flipud(rotated))
        
    
    #close file
    ds.close()

# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
def grid_nc_mult_files_time(limit, gsize, indata, inlat, inlon, phy_list, geo_list, filelist, filename):

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon dimensions
    time = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('lat', 'f4', ('lat',)) #latitude is fatitude
    lons = ds.createVariable('lon', 'f4', ('lon',))
    
    value = ds.createVariable('value', 'f4', ('time', 'lat', 'lon', ))
    value.units = 'unknown'
    
    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    #run through and assign gridded data to corresponding time interval    
    for i in range(0,len(filelist)):
        avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau =  gridding.multi_sensor_grid(filelist[i], gsize, limit, phy_list, geo_list)
    
        rotated = list(zip(*mintau))[::-1]
        value[i, :, :] = (np.flipud(rotated))
        
    
    #close file
    ds.close()

# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
# saves all satellite sensor gridded data as separate variables
#def grid_nc_single_statistics(limit, gsize, inlat, inlon, geo_list, phy_list, filelist, filename):
def grid_nc_single_statistics(limit, gsize, geo_list, phy_list, filelist, filename):

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon dimensions
    timed = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('lat', 'f4', ('lat',)) #latitude is fatitude
    lons = ds.createVariable('lon', 'f4', ('lon',))

    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    # unknown number of sensors, save values to list
    values = []
    # instantiate empty arrays for summary statistics
    indata_stat = []
    inlat_stat = []
    inlon_stat = []
    
    #run through and assign gridded data to single sensor variable
    for i in range(0,len(filelist)):
        start_timer = time.time()
        name = str(filelist[i].split("/")[-1])
        values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', )))
        values[i].units = 'unknown'

        #print(filelist[i])
        
        L2FID,GeoID,PhyID = sat_data_input.open_file(filelist[i])
        # check for hdf files 
        if (filelist[i].split(".")[-1] == "hdf"):
            geo_list = ['Latitude', 'Longitude']
        else:
            geo_list = ['latitude', 'longitude']

        lat,lon,phy_vars, metadata = filter_data.filter_data(GeoID, PhyID, geo_list, phy_list, phy_nc=phy_list, phy_hdf=phy_list)


        L2FID.close()

        #summary statistics appending
        if len(indata_stat) == 0:
            indata_stat = phy_vars[0]
            inlat_stat = lat[0]
            inlon_stat = lon[0]
        else:
            inlat_stat = ma.concatenate([inlat_stat, lat[0]])
            # dictionary later on
            indata_stat = ma.concatenate([indata_stat, phy_vars[0]]) 
            inlon_stat = ma.concatenate([inlon_stat, lon[0]])

        #grid parameters
        #limit = [min(lat[0]), max(lat[0]), min(lon[0]),  max(lon[0])]
        gsize = 0.25
        indata = phy_vars[0]
        inlat=lat[0]
        inlon = lon[0]

        #dont need this
        avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,gsize,indata,inlat,inlon)

        rotated = list(zip(*avgtau))[::-1]
        #print(np.flipud(rotated))
        #print(i, ": ", filelist[i])
        #values[i][0, :, :] = np.nan_to_num(np.flipud(rotated))
        values[i][0, :, :] = np.flipud(rotated)

        end_timer = time.time()
        print("Sensor: ",name ," time: ", end_timer - start_timer)

    start_timer = time.time()

    # put in gridded statistics
    avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,gsize,indata_stat,inlat_stat,inlon_stat)

    avg = ds.createVariable("merge_avgtau", 'f4', ('time', 'lat', 'lon', ))
    avg.units = 'unknown' # pull from metadata
    avg[0, :, :] = np.flipud(list(zip(*avgtau))[::-1]) # make sure this is correct

    std = ds.createVariable("merge_stdtau", 'f4', ('time', 'lat', 'lon', ))
    std.units = 'unknown'
    std[0, :, :] = np.flipud(list(zip(*stdtau))[::-1])

    grdlatvar = ds.createVariable("merge_grdlat", 'f4', ('time', 'lat', 'lon', ))
    grdlatvar.units = 'unknown'
    grdlatvar[0, :, :] = np.flipud(list(zip(*grdlat))[::-1])

    grdlonvar = ds.createVariable("merge_grdlon", 'f4', ('time', 'lat', 'lon', ))
    grdlonvar.units = 'unknown'
    grdlonvar[0, :, :] = np.flipud(list(zip(*grdlon))[::-1])

    min = ds.createVariable("merge_mintau", 'f4', ('time', 'lat', 'lon', ))
    min.units = 'unknown'
    min[0, :, :] = np.flipud(list(zip(*mintau))[::-1])

    max = ds.createVariable("merge_maxtau", 'f4', ('time', 'lat', 'lon', ))
    max.units = 'unknown'
    max[0, :, :] = np.flipud(list(zip(*maxtau))[::-1])

    countvar = ds.createVariable("merge_count", 'f4', ('time', 'lat', 'lon', ))
    countvar.units = 'unknown'
    countvar[0, :, :] = np.flipud(list(zip(*count))[::-1])

    sum = ds.createVariable("merge_sumtau", 'f4', ('time', 'lat', 'lon', ))
    sum.units = 'unknown'
    sum[0, :, :] = np.flipud(list(zip(*sumtau))[::-1])

    end_timer = time.time()
    print("Statistics summary time: ", end_timer - start_timer)
    
    #close file
    ds.close()


# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
# saves all satellite sensor gridded data as separate variables
#def grid_nc_single_statistics(limit, gsize, inlat, inlon, geo_list, phy_list, filelist, filename):
def grid_nc_statistics(limit, gsize, geo_list, phy_list, filelist, filename):
    #start_timer = time.time()

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon dimensions
    timed = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('lat', 'f4', ('lat',)) #latitude is fatitude
    lons = ds.createVariable('lon', 'f4', ('lon',))

    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    # unknown number of sensors, save values to list
    values = []

    # instantiate empty arrays for summary statistics
    indata_stat = []
    inlat_stat = []
    inlon_stat = []
    indata_temp = []
    inlat_temp = []
    inlon_temp = []
    
    #run through and assign gridded data to sensor variable
    # filenames are in the form:
    # [[time0: [sat1], [sat2], ... ], ...[timek: [sat1], [sat2], ....]] 
    # we assume we receive a signle dict for a time interval though

    for i, s_name in enumerate(filelist.keys()): 
        start_timer = time.time()
        name = str(s_name)
        
        values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', )))
        values[i].units = 'unknown'

        for s in filelist.get(s_name):
            
            L2FID,GeoID,PhyID = sat_data_input.open_file(str(s))

            # check for hdf files 
            if (str(s).split(".")[-1] == "hdf"):
                geo_list = ['Latitude', 'Longitude']
            else:
                geo_list = ['latitude', 'longitude']

            lat,lon,phy_vars, metadata = filter_data.filter_data(GeoID, PhyID, geo_list, phy_list, phy_nc=phy_list, phy_hdf=phy_list)

            L2FID.close()

            # statistics appending for this sensor
            if len(indata_temp) == 0:
                indata_temp = phy_vars[0]
                inlat_temp = lat[0]
                inlon_temp = lon[0]
            else:
                inlat_temp = ma.concatenate([inlat_temp, lat[0]])
                indata_temp = ma.concatenate([indata_temp, phy_vars[0]]) 
                inlon_temp = ma.concatenate([inlon_temp, lon[0]])

            #summary statistics appending
            if len(indata_stat) == 0:
                indata_stat = phy_vars[0]
                inlat_stat = lat[0]
                inlon_stat = lon[0]
            else:
                inlat_stat = ma.concatenate([inlat_stat, lat[0]])
                indata_stat = ma.concatenate([indata_stat, phy_vars[0]]) 
                inlon_stat = ma.concatenate([inlon_stat, lon[0]])

        #grid parameters
        avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp,inlat_temp,inlon_temp)

        # reset
        indata_temp = []
        inlat_temp = []
        inlon_temp = []

        rotated = list(zip(*avgtau))[::-1]

        values[i][0, :, :] = np.flipud(rotated)

        end_timer = time.time()
        print("Sensor: ",s_name ," time: ", end_timer - start_timer)

    # put in gridded statistics
    avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_stat,inlat_stat,inlon_stat)

    avg = ds.createVariable("merge_avgtau", 'f4', ('time', 'lat', 'lon', ))
    avg.units = 'unknown'
    avg[0, :, :] = np.flipud(list(zip(*avgtau))[::-1])

    std = ds.createVariable("merge_stdtau", 'f4', ('time', 'lat', 'lon', ))
    std.units = 'unknown'
    std[0, :, :] = np.flipud(list(zip(*stdtau))[::-1])

    grdlatvar = ds.createVariable("merge_grdlat", 'f4', ('time', 'lat', 'lon', ))
    grdlatvar.units = 'unknown'
    grdlatvar[0, :, :] = np.flipud(list(zip(*grdlat))[::-1])

    grdlonvar = ds.createVariable("merge_grdlon", 'f4', ('time', 'lat', 'lon', ))
    grdlonvar.units = 'unknown'
    grdlonvar[0, :, :] = np.flipud(list(zip(*grdlon))[::-1])

    min = ds.createVariable("merge_mintau", 'f4', ('time', 'lat', 'lon', ))
    min.units = 'unknown'
    min[0, :, :] = np.flipud(list(zip(*mintau))[::-1])

    max = ds.createVariable("merge_maxtau", 'f4', ('time', 'lat', 'lon', ))
    max.units = 'unknown'
    max[0, :, :] = np.flipud(list(zip(*maxtau))[::-1])

    countvar = ds.createVariable("merge_count", 'f4', ('time', 'lat', 'lon', ))
    countvar.units = 'unknown'
    countvar[0, :, :] = np.flipud(list(zip(*count))[::-1])

    sum = ds.createVariable("merge_sumtau", 'f4', ('time', 'lat', 'lon', ))
    sum.units = 'unknown'
    sum[0, :, :] = np.flipud(list(zip(*sumtau))[::-1])
    
    #close file
    ds.close()
    # output = 1 netcdf with six variables (one for each sensor) 
    # merge = run two loops (lat lon) (xdim, ydim from grid) 
    # merge aod equal to average of six sensors making sure no nan
    # identify which sensors are availabe - sensor ID variable 0 or 1 (unavailable vs available)
    # byte type array, keep n-dimensional for now
    # minimum number of things to merge: in the future

    # future capabilities:
    # minimum number, flagging system, use higher quality data (prefiltered)


# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
# saves all satellite sensor gridded data as separate variables
#def grid_nc_single_statistics(limit, gsize, inlat, inlon, geo_list, phy_list, filelist, filename):
def grid_nc_sensor_statistics(limit, gsize, geo_list, phy_list, filelist, filename, phy_nc=None, phy_hdf=None):
    #start_timer = time.time()

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    # Create time, lat, lon, sensor dimensions
    timed = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    sensor = ds.createDimension('sensor', 6) #only used for SensorWeighting mask
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('latitude', np.short, ('lat',), fill_value=-9999.) #latitude is fatitude
    lons = ds.createVariable('longitude', np.short, ('lon',), fill_value=-9999.)
    sensor_var = ds.createVariable("sensors",)
    
    
    #latitude / longitude metadata
    lats.valid_range = [-90.0, 90.0]
    #lats._FillValue = -9999.
    lats.standard_name = "latitude"
    lats.long_name = "Geodectic Latitude"
    lats.units = "degree_north"
    lats.scale_factor = 1.
    lats.add_offset = 0.
    lats.Parameter_Type = "Equal angle grid center location"
    lats.Geolocation_Pointer = "Geolocation data not applicable" 
    lats._CoordinateAxisType = "Lat"
    
    lons.valid_range = [-180.0, 180.0]
    #lons._FillValue = -9999.
    lons.standard_name = "longitude"
    lons.long_name = "Geodectic Longitude"
    lons.units = "degree_east"
    lons.scale_factor = 1.
    lons.add_offset = 0.
    lons.Parameter_Type = "Equal angle grid center location"
    lons.Geolocation_Pointer = "Geolocation data not applicable" 
    lons._CoordinateAxisType = "Lon"

    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon

    #metadata for lat lon
    
    # unknown number of sensors, save values to list
    values = []
    sensors = {}

    # instantiate empty arrays for summary statistics
    indata_temp = []
    inlat_temp = []
    inlon_temp = []
    
    
    #run through and assign gridded data to sensor variable
    # filenames are in the form:
    # [[time0: [sat1], [sat2], ... ], ...[timek: [sat1], [sat2], ....]] 
    # we assume we receive a signle dict for a time interval though

    for i, s_name in enumerate(filelist.keys()): 
        start_timer = time.time()

        for s in filelist.get(s_name):
            print("WORK SENSOR: ", s_name)

            L2FID,GeoID,PhyID = sat_data_input.open_file(str(s))

            # check for hdf files 
            if (str(s).split(".")[-1] == "hdf"):
                geo_list = ['Latitude', 'Longitude']
            else:
                geo_list = ['latitude', 'longitude']

            lat,lon,phy_vars, meta = filter_data.filter_data(GeoID, PhyID, geo_list, phy_list, phy_nc, phy_hdf)
            
            #close/end the file
            try:#netcdf
                L2FID.close()
            except:#hdf
                L2FID.end()

            #print("latitude:" , lat)
            #print("Physical variables: ", phy_vars)

            for count, p_var in enumerate(phy_list):
                # statistics appending for this sensor
                if len(indata_temp) < count+1:
                    indata_temp.append([])
                    inlat_temp.append([])
                    inlon_temp.append([])
                    #print("sdf",indata_temp)
                
                indata_temp[count] = ma.concatenate([indata_temp[count], phy_vars[count]])
                inlat_temp[count] = ma.concatenate([inlat_temp[count], lat[count]])
                inlon_temp[count] = ma.concatenate([inlon_temp[count], lon[count]])

        #grid parameters
        for j, p_vars in enumerate(phy_list):

            #print("Indata: ", indata_temp[j])
            avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp[j],inlat_temp[j],inlon_temp[j])

            rotated = list(zip(*avgtau))[::-1]

            index = i * len(phy_list) + j
            name = str(s_name+"_"+p_vars)
            values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=meta[j]["_FillValue"]))
            
            # metadata
            values[index].units = meta[j]["units"]
            values[index].valid_range = meta[j]["valid_range"]
            #values[index]._FillValue = meta[j]["_FillValue"]
            values[index].long_name = meta[j]["long_name"]
            values[index].scale_factor = meta[j]["scale_factor"]
            values[index].add_offset = meta[j]["add_offset"]
            values[index].Parameter_Type = meta[j]["Parameter_Type"]

            #make sure key is in dict
            if not p_vars in sensors:
                sensors[p_vars] = []
            
            values[index][0, :, :] = np.flipud(rotated) # make it 2dimensional
            check = values[index][0, :, :].flatten()
            print("Final: ", check)
            sensors[p_vars].append(np.flipud(rotated))

            end_timer = time.time()
            print("Sensor: ",s_name ," time: ", end_timer - start_timer)
        
        # reset
        indata_temp = []
        inlat_temp = []
        inlon_temp = []

    # put in gridded statistics
    # avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_stat,inlat_stat,inlon_stat)
    sensor_id = []
    shape = (len(np.arange(0,lat_dim)*gsize+minlat), len(np.arange(0,lon_dim)*gsize+minlon))
    avg = []

    for k, p_vars in enumerate(phy_list):
        # averages
        try:
            avgtau = np.nanmean(np.array(sensors.get(p_vars)), axis=0 )
            # other statistics nan

            # sensor id x
            sensor_id_x = np.zeros(shape)
            for i in range(len(sensors[p_vars])):
                sensor_id_x = sensor_id_x + (np.array(sensors.get(p_vars)[i])*0+1)
                #print(np.nan_to_num(np.array(sensors.get(p_vars)[i])*0+1, -1))

            avg_name = str("merge_avgtau_" + p_vars)
            avg.append(ds.createVariable(avg_name, 'f4', ('time', 'lat', 'lon', )))
            avg[k][0, :, :] = avgtau

            # metadata
            # naming convention, units should be consistent
            # read from configuration file
            # follow netcdf conventions

            # avg[k].units = meta["units"]
            # avg[k].valid_range = meta["valid_range"]
            # avg[k]._FillValue = meta["_FillValue"]
            # avg[k].long_name = meta["long_name"]
            # avg[k].scale_factor = meta["scale_factor"]
            # avg[k].add_offset = meta["add_offset"]
            # avg[k].Parameter_Type = meta["Parameter_Type"]

            sensor_id_name = str("sensor_id_x_" + p_vars)
            sensor_id.append(ds.createVariable(sensor_id_name, 'f4', ('time', 'lat', 'lon', )))
            sensor_id[k].units = 'unknown'
            sensor_id[k][0, :, :] = sensor_id_x
        except:
            #print("There are: ", len(sensors.get(p_vars)), " sensors for the var")
            print(p_vars)
            print(sensors.get(p_vars))
        

    #close file
    ds.close()
    # output = 1 netcdf with six variables (one for each sensor) 
    # merge = run two loops (lat lon) (xdim, ydim from grid) 
    # merge aod equal to average of six sensors making sure no nan
    # identify which sensors are availabe - sensor ID variable 0 or 1 (unavailable vs available)
    # byte type array, keep n-dimensional for now
    # minimum number of things to merge: in the future

    # future capabilities:
    # minimum number, flagging system, use higher quality data (prefiltered)
    
    
# filename - 'gridNet.nc' (this is what it saves to)
# sat_files - list of satellite files to pull data from
# saves all satellite sensor gridded data as separate variables
#def grid_nc_single_statistics(limit, gsize, inlat, inlon, geo_list, phy_list, filelist, filename):
def grid_nc_sensor_statistics_metadata2(limit, gsize, geo_list, phy_list, filelist, filename, time_start, time_diff, phy_nc=None, phy_hdf=None, static_file=None):
    
    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize))) #int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize))) #int(1+round(((maxlon-minlon)/gsize)))
    print("LAT:" ,lat_dim)
    print("LON:" ,lon_dim)
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    #start_timer = time.time()
    time_date = time_start.strftime('%Y-%m-%d')
    time_time = time_start.strftime('%H:%M:%S.%f')[:-4]
    time_end = time_start + datetime.timedelta(minutes=time_diff)
    time_end_date = time_end.strftime('%Y-%m-%d')
    time_end_time = time_end.strftime('%H:%M:%S.%f')[:-4]
    
    
    #set global attributes
    ds.title = "Level 3 gridded merged aerosol data from Dark Target Algorithm for MEASURES Project (2017-2023)"
    ds.history = "TBD"
    ds.institution = "NASA Goddard Space Flight Center, Climate and Radiation Laboratory"
    ds.source = "MODIS-Terra, MODIS-Aqua, VIIRS-SNPP, ABI-G16, ABI-G17, AHI-Himawari-08"
    ds.references = """- Levy, R. C., S. Mattoo, L. A. Munchak, et al. 2013. "The Collection 6 MODIS Aerosol Products over Land and Ocean." Atmos Meas Tech 6 2989-3034 [10.5194/amt-6-2989-2013]
                        - Gupta  et  al., Increasing aerosol optical depth spatial and temporal availability by merging geostationary and sun-synchronous satellite products using the Dark Target algorithm, in -prep
                        - Gupta, P.; Remer, L.A.; Patadia, F.; Levy, R.C.; Christopher, S.A. High-Resolution Gridded Level 3 Aerosol Optical Depth Data from MODIS. Remote Sens. 2020, 12, 2847. https://doi.org/10.3390/rs12172847"""
    ds.Conventions = "CF-1.8"
    ds.LongName = "Level 3 quarter degree gridded global  aerosol  data from six LEO and GEO sensors averaged for a 30 minute interval."
    ds.VersionID = 0
    ds.Format = "NetCDF-4"
    ds.DataSetQuality = "TBD"
    ds.IdentifierProductDOI = "TBD"
    ds.RangeBeginningDate = time_date
    ds.RangeBeginningTime = time_time
    ds.RangeEndingDate = time_end_date
    ds.RangeEndingTime = time_end_time
    ds.ProcessingLevel = "Level 3"
    
    ds.ShortName = "AERDT_L3_MEASURES_QD_HH"
    #ds.format_version = 1#VersionID = 1
    ds.LocalGranuleID = filename
    ds.product_version = "001"
    ds.IdentifierProductDOIAuthority  = "https://dx.doi.org/"
    """
    
    ds.GranuleID = None
    ds.Format = "netCDF4"
    ds.RangeBeginningDate = None
    ds.RangeBeginningTime  = None
    ds.RangeEndingDate = None
    ds.RangeEndingTime = None
    ds.IdentifierProductDOIAuthority = "https://dx.doi.org/ - product DOI authority "
    ds.IdentifierProductDOI = None
    ds.ProductionDateTime = None
    ds.ProcessingLevel = "Level 3"
    ds.Conventions = None
    ds.NorthernmostLatitude = limit[1]
    ds.SouthernmostLatitude = limit[0]
    ds.WesternmostLongitude = limit[2]
    ds.WesternmostLongitude = limit[3]
    """
    
    # Create time, lat, lon, sensor dimensions
    timed = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    sensor = ds.createDimension('sensor', 6) #only used for SensorWeighting mask
    
    #set time variable to filename parse
    times = ds.createVariable('time', np.short, ('time',))
    times.long_name = "time"
    time.calendar = "standard"
    #time.units = "minutes since "+str(time_start)
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('latitude', 'f4', ('lat',), fill_value=-9999.) #latitude is fatitude
    lons = ds.createVariable('longitude', 'f4', ('lon',), fill_value=-9999.)
    sensor_var = ds.createVariable("sensors", np.short, ('sensor', ))
    
    #sensors metadata
    sensor_var.long_name = "Sensors: 1- MODIS-T, 2 - MODIS-A, 3 - VIIRS-SNP, 4 - ABI-G16, 5 - ABI-G17, 6 - AHI-H08"
    sensor_var.units = "None"
    
    #latitude / longitude metadata
    lats.valid_range = [-90.0, 90.0]
    #lats._FillValue = -9999.
    lats.standard_name = "latitude"
    lats.long_name = "Geodectic Latitude"
    lats.units = "degrees_north"
    lats.scale_factor = 1.
    lats.add_offset = 0.
    lats.Parameter_Type = "Equal angle grid center location"
    lats.Geolocation_Pointer = "Geolocation data not applicable" 
    lats._CoordinateAxisType = "Lat"
    
    lons.valid_range = [-180.0, 180.0]
    #lons._FillValue = -9999.
    lons.standard_name = "longitude"
    lons.long_name = "Geodectic Longitude"
    lons.units = "degrees_east"
    lons.scale_factor = 1.
    lons.add_offset = 0.
    lons.Parameter_Type = "Equal angle grid center location"
    lons.Geolocation_Pointer = "Geolocation data not applicable" 
    lons._CoordinateAxisType = "Lon"

    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    # unknown number of sensors, save values to list
    values = []
    sensors = {}

    # instantiate empty arrays for summary statistics
    indata_temp = []
    inlat_temp = []
    inlon_temp = []
    
    # copy static file data into this file
    # Land_Sea_Mask, Topographic_Altitude
    if(static_file != None):
        static_vars = ["Land_Sea_Mask", "Topographic_Altitude"]
        
        #with netCDF4.Dataset(static_file) as src, ds as dst:
        src = netCDF4.Dataset(static_file)
        # copy dimensions
        """
        for name, dimension in src.dimensions.items():
            ds.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None))
        """
        # copy all file data in the specified variables
        for name, variable in src.variables.items():
            if name in static_vars:
                print(name)
                dimensions = ('time', 'lat', 'lon',)
                x = ds.createVariable(name, variable.datatype, dimensions) #variable.dimensions)
                #ds[name][:] = src[name][:]
                ds[name][0, :, :] = src[name][:]
                print(ds[name][:])
                # copy variable attributes all at once via dictionary
                ds[name].setncatts(src[name].__dict__)
                
                
        src.close()
        
    print("done with copy")
    
    # Solar zenith angle 
    name = "Solar_Zenith_Angle"
    solar_zenith_variable = ds.createVariable(name, np.short, ('time', 'lat', 'lon', ), fill_value=int(-9999))
    solar_zenith_variable.long_name = "Solar Zenith Angle at the center of grid calculated for central time of the file"
    solar_zenith_variable.units = "degree"
    solar_zenith_variable.valid_range = [ 0, 18000]
    solar_zenith_variable.scale_factor = 0.01
    #solar_zenith_variable.add_offset = float(0)
    #netCDF4.nc_put_att(ds, solar_zenith_variable, 'add_offset', 'f4', 1, 0)
    
    
    #solar_zenith_variable[0, :, :] = solar_zenith.get_SZA_vec(limit, gsize, time_start, time_diff)
    #copy solar_zenith
    """ 
    path = "/mnt/c/Users/bobgr/Desktop/Spring 2022 NASA/Gridtools Package (Code, README, inputs, outputs, examples, verification)/"
    fn = path + "SampleOutputs 0000-0059 01-01-2020/Old outputs/XAERDT_L3_MEASURES_QD_HH.20200101.0000.V0.20221108.nc"
    src = netCDF4.Dataset(fn)
    for name, variable in src.variables.items():
        if name == "Solar_Zenith_Angle":
            print("metadata: ", src[name].__dict__)
    #solar_zenith_variable[0, :, :] = src["Solar_Zenith_Angle"][:]
    src.close()
    
    print("solar zenith done")
    """
    
    
    # for calculating LEOGEO statistics
    # LEOGEO: Mean, STD, NumberOfSensors, SensorWeighting, TotalPixels
    # index of value corresponds to individual sensor
    #leogeo_stats = {"Mean": [], "STD": [], "TotalPixels":[]}
    leogeo_stats_arr = {} #contains leogeo_stats as value, geophys as key
    #sensor_idx_stats = {"NumberOfSensors":[], "SensorWeighting":[]}
    #sensor_idx = {} #key = sensor name, value = sensoridx
    sensor_idx_arr = {} #key = geophys value, value = sensor_idx
    
    #run through and assign gridded data to sensor variable
    # filenames are in the form:
    # [[time0: [sat1], [sat2], ... ], ...[timek: [sat1], [sat2], ....]] 
    # we assume we receive a signle dict for a time interval though
    for i, s_name in enumerate(filelist.keys()): 
        start_timer = time.time()

        for s in filelist.get(s_name):
            print("WORK SENSOR: ", s_name)

            L2FID,GeoID,PhyID = sat_data_input.open_file(str(s))

            # check for hdf files 
            if (str(s).split(".")[-1] == "hdf"):
                geo_list = ['Latitude', 'Longitude']
                lat,lon,phy_vars, meta = filter_data.filter_data_hdf(GeoID, PhyID, geo_list, phy_list, phy_hdf)
                L2FID.end()
                
            else: #netcdf
                geo_list = ['latitude', 'longitude']
                lat,lon,phy_vars, meta = filter_data.filter_data_nc(GeoID, PhyID, geo_list, phy_list, phy_nc)
                L2FID.close()
            
            # statistics appending for this sensor
            # index for arrays = geophysical variable indices
            for count, p_var in enumerate(phy_list):
                
                #create empty array for geophysical variable
                if len(indata_temp) < count+1:
                    indata_temp.append([])
                    inlat_temp.append([])
                    inlon_temp.append([])
                
                indata_temp[count] = ma.concatenate([indata_temp[count], phy_vars[count]])
                inlat_temp[count] = ma.concatenate([inlat_temp[count], lat[count]])
                inlon_temp[count] = ma.concatenate([inlon_temp[count], lon[count]])
        # end sensor concatenations
        # indata = [[geovar data 1], [geovar data 2], ... , [geovar data n]]
        
        # grid parameters
        # individual sensor statistics
        for j, p_vars in enumerate(phy_list):
            
            #special metadata and statistic calculations for AOD
            # values that need LEOGEO statistic calculations
            if not("Sensor_Zenith" in p_vars or "Scattering_Angle" in p_vars):#"Optical_Depth_Land_And_Ocean" in p_vars:
                aod_statistics = ["Mean", "STD", "Pixels"]
                avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp[j],inlat_temp[j],inlon_temp[j])
                #concatenate AOD data for leogeo stats later
                print("avgtau: x", len(avgtau), " y: ",len(avgtau[0]))
                
                for aod_stat in aod_statistics:
                    
                    index = len(values) #i * len(phy_list) + j
                    aod_long = meta[j]["long_name"]
                    name = naming_conventions.nc_var_name(p_vars, s_name, aod_stat) #str(s_name+"_"+p_vars)
                    values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=meta[j]["_FillValue"]))
                    
                    # metadata
                    values[index].units = "1"#meta[j]["units"]
                    values[index].valid_range = meta[j]["valid_range"]
                    values[index].long_name = naming_conventions.nc_long_name(p_vars, s_name, aod_stat, aod_long) + " for the grid" #meta[j]["long_name"]
                    values[index].Parameter_Type = meta[j]["Parameter_Type"]
                    
                    # check if pixels to add add_offset or scale_factor or not
                    if not(aod_stat in "Pixels"):
                        values[index].scale_factor = round(meta[j]["scale_factor"], 3)
                        values[index].add_offset = meta[j]["add_offset"]

                    
                    # instantiate the dictionary for statistics
                    if not p_vars in leogeo_stats_arr:
                        leogeo_stats_arr[p_vars] = {"Mean": [], "STD": [], "TotalPixels":[]}
                        
                        
                    # make sure key is in dict 
                    # instantiation
                    if not p_vars in sensors:
                        sensors[p_vars] = []
                    
                    if not p_vars in sensor_idx_arr:
                        sensor_idx_arr[p_vars] = {}
                    
                    #statistics to be added
                    if aod_stat== "Mean":
                        rotated = list(zip(*avgtau))[::-1]
                        leogeo_stats_arr[p_vars] ["Mean"].append(np.flipud(rotated)) #for leogeo calculation later
                        
                        #sensor idx (Sensor Weighting)
                        temp_a = np.flipud(rotated)
                        """
                        print("\nBEFORE SENSOR IDX \n")
                        print(temp_a)
                        print("Fill Value: ", meta[j]["_FillValue"])"""
                        temp_a[temp_a > -9999] = 1
                        temp_a[temp_a <= meta[j]["_FillValue"]] = 0
                        temp_a[np.isnan(temp_a)] = 0
                        #sensor_idx[naming_conventions.get_sensor(s_name)] = temp_a
                        sensor_idx_arr[p_vars][naming_conventions.get_sensor(s_name)] = temp_a
                        """
                        print("\nSENSOR IDX\n")
                        print(sensor_idx[naming_conventions.get_sensor(s_name)])
                        print("\n")
                        """
                    
                    
                        
                    elif aod_stat == "STD":
                        rotated = list(zip(*stdtau))[::-1]
                        
                        leogeo_stats_arr[p_vars]["STD"].append(np.flipud(rotated))
                        
                        #leogeo_stats["STD"].append(np.flipud(rotated)) #for leogeo calculation later
                    elif aod_stat == "Pixels":
                        rotated = list(zip(*count))[::-1]
                        
                        leogeo_stats_arr[p_vars]["TotalPixels"].append(np.flipud(rotated))
                        #leogeo_stats["TotalPixels"].append(np.flipud(rotated)) #for leogeo calculation later
                    else:
                        rotated = list(zip(*avgtau))[::-1]
                        
                        leogeo_stats_arr[p_vars]["Mean"].append(np.flipud(rotated))
                        #leogeo_stats["Mean"].append(np.flipud(rotated)) #for leogeo calculation later
                        print("STATISTIC ERROR")
                    
                    values[index][0, :, :] = np.flipud(rotated) # make it 2dimensional
                    sensors[p_vars].append(np.flipud(rotated)) #add it to complete dataset for LEOGEO calculations

                #time
                end_timer = time.time()
                print("Sensor: ",s_name ," time: ", end_timer - start_timer)
                
            else:  #phy_var is NOT AOD

                avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp[j],inlat_temp[j],inlon_temp[j])

                index = len(values) #i * len(phy_list) + j
                name = naming_conventions.nc_var_name(p_vars, s_name) #str(s_name+"_"+p_vars)
                values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=meta[j]["_FillValue"]))
                
                # metadata
                values[index].units = "degree"#meta[j]["units"]
                values[index].valid_range = meta[j]["valid_range"]
                values[index].long_name = naming_conventions.nc_long_name(p_vars, s_name)#meta[j]["long_name"]
                values[index].scale_factor = round(meta[j]["scale_factor"], 3)
                values[index].add_offset = meta[j]["add_offset"]
                values[index].Parameter_Type = meta[j]["Parameter_Type"]

                """
                # make sure key is in dict 
                # instantiation
                if not p_vars in sensors:
                    sensors[p_vars] = []
                """
                
                rotated = list(zip(*avgtau))[::-1]
                
                values[index][0, :, :] = np.flipud(rotated) # make it 2dimensional
                #sensors[p_vars].append(np.flipud(rotated)) #add it to complete dataset for LEOGEO calculations

                #time
                end_timer = time.time()
                print("Sensor: ",s_name ," time: ", end_timer - start_timer)
        
        # reset
        indata_temp = []
        inlat_temp = []
        inlon_temp = []
        
    # end individual sensor gridding and adding to nc
    
    # calculate LEOGEO statistics
    # LEOGEO: Mean, STD, NumberOfSensors, SensorWeighting, TotalPixels
    # index of value corresponds to individual sensor
    # leogeo_stats = {"Mean": [], "STD": [], "TotalPixels":[]}
    # sensor_idx = {} #key = sensor name, value = sensoridx
    leogeo_calculated_statistics = []
    number_of_sensors_variable = []
    sensor_idx_variable = []
    
    #print("\nLEOGEO STATS\n")
    #print(leogeo_stats)
    
    # FilteredQA_550
    # Mean, STD, and TotalPixels stat calculations
    j = 0
    leogeo_index = 0
    for p_var in phy_list:
        if p_var in leogeo_stats_arr: #go through each geophysical variable
        
            leogeo_stats = leogeo_stats_arr[p_var] #current dict 
            leogeo_calculated_statistics.append([])
            
            i=0
            # mean, std, pixel statistics
            for statistic in leogeo_stats:
                name = naming_conventions.nc_var_name(p_var, "LEOGEO", statistic)
                
                # avgtau = np.nanmean(np.array(sensors.get(p_vars)), axis=0 )
                stat_values = naming_conventions.calculate_statistic(statistic, 
                                                                    leogeo_stats["Mean"],
                                                                    leogeo_stats["STD"],
                                                                    leogeo_stats["TotalPixels"])
                
                leogeo_calculated_statistics[leogeo_index].append(ds.createVariable(name, np.short, ('time', 'lat', 'lon', )))
                leogeo_calculated_statistics[leogeo_index][i][0, :, :] = stat_values
                leogeo_long = meta[leogeo_index]["long_name"]
                leogeo_calculated_statistics[leogeo_index][i].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO", 
                                                                                            statistic, leogeo_long) + " for the grid"
                
                # metadata
                leogeo_calculated_statistics[leogeo_index][i].units = "1"#"degree"#meta[leogeo_index]["units"]
                leogeo_calculated_statistics[leogeo_index][i].valid_range = meta[leogeo_index]["valid_range"]
                if not("Pixels" in leogeo_stats):
                    leogeo_calculated_statistics[leogeo_index][i].scale_factor = round(meta[leogeo_index]["scale_factor"], 3)
                    leogeo_calculated_statistics[leogeo_index][i].add_offset = meta[leogeo_index]["add_offset"]
                
                i+=1
            
                
            # Sensor IDX calculations
            # SensorWeighting and NumberOfSensors
            # sensor_idx = {} #key = sensor name, value = sensoridx
            
            sensor_order = ["MODIS_T", "MODIS_A", "VIIRS_SNPP", "ABI_G16", "ABI_G17", "AHI_H08"]
            name = naming_conventions.nc_var_name(p_var,"LEOGEO", "SensorWeighting")
            sensor_idx_variable.append(ds.createVariable(name, np.short, ('sensor', 'lat', 'lon', ), fill_value=-9999))
            sensor_idx_variable[leogeo_index].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO",
                                                                            "SensorWeighting", meta[j]["long_name"]) + " for the grid"
            sensor_idx_variable[leogeo_index].units = "1"
            
            number_of_sensors = []
            
            i = 0
            for satellite in sensor_order:
                # check to make sure sensor is in there
                if satellite in sensor_idx_arr[p_var]:
                    
                    #add number of sensors together
                    if len(number_of_sensors)==0:
                        number_of_sensors = sensor_idx_arr[p_var][satellite]
                    else:
                        number_of_sensors = number_of_sensors + sensor_idx_arr[p_var][satellite]
                    
                    #save for sensor layer
                    sensor_idx_variable[leogeo_index][i, :, :] = sensor_idx_arr[p_var][satellite]
                # no files for this satellite
                else:
                    pass
                i += 1
            
            name = naming_conventions.nc_var_name(p_var, "LEOGEO", "NumberOfSensors")
            number_of_sensors_variable.append(ds.createVariable(name, np.short, ('time', 'lat', 'lon', ), fill_value=-9999))   
            number_of_sensors_variable[leogeo_index][0, :, :] = number_of_sensors
            number_of_sensors_variable[leogeo_index].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO",
                                                                              "NumberOfSensors", meta[j]["long_name"]) + " for the grid"
            number_of_sensors_variable[leogeo_index].units = "1"
            
            leogeo_index+=1    
        j += 1
    
    """
    # put in gridded statistics
    # avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_stat,inlat_stat,inlon_stat)
    sensor_id = []
    shape = (len(np.arange(0,lat_dim)*gsize+minlat), len(np.arange(0,lon_dim)*gsize+minlon))
    avg = []

    # all sensors combined statistics (LEOGEO)
    for k, p_vars in enumerate(phy_list):
        # averages
        try:
            avgtau = np.nanmean(np.array(sensors.get(p_vars)), axis=0 )
            # other statistics nan

            # Number of Sensors
            sensor_id_x = np.zeros(shape)
            for i in range(len(sensors[p_vars])):
                sensor_id_x = sensor_id_x + (np.array(sensors.get(p_vars)[i])*0+1)
                #print(np.nan_to_num(np.array(sensors.get(p_vars)[i])*0+1, -1))

            avg_name = str("merge_avgtau_" + p_vars)
            avg.append(ds.createVariable(avg_name, 'f4', ('time', 'lat', 'lon', )))
            avg[k][0, :, :] = avgtau

            # metadata
            # naming convention, units should be consistent
            # read from configuration file
            # follow netcdf conventions

            # avg[k].units = meta["units"]
            # avg[k].valid_range = meta["valid_range"]
            # avg[k]._FillValue = meta["_FillValue"]
            # avg[k].long_name = meta["long_name"]
            # avg[k].scale_factor = meta["scale_factor"]
            # avg[k].add_offset = meta["add_offset"]
            # avg[k].Parameter_Type = meta["Parameter_Type"]

            sensor_id_name = str("sensor_id_x_" + p_vars)
            sensor_id.append(ds.createVariable(sensor_id_name, 'f4', ('time', 'lat', 'lon', )))
            sensor_id[k].units = 'unknown'
            sensor_id[k][0, :, :] = sensor_id_x
        except:
            #print("There are: ", len(sensors.get(p_vars)), " sensors for the var")
            print(p_vars)
            print(sensors.get(p_vars))
    """

    #close file
    ds.close()
    # output = 1 netcdf with six variables (one for each sensor) 
    # merge = run two loops (lat lon) (xdim, ydim from grid) 
    # merge aod equal to average of six sensors making sure no nan
    # identify which sensors are availabe - sensor ID variable 0 or 1 (unavailable vs available)
    # byte type array, keep n-dimensional for now
    # minimum number of things to merge: in the future

    # future capabilities:
    # minimum number, flagging system, use higher quality data (prefiltered)
    
def grid_nc_sensor_statistics_metadata(limit, gsize, geo_list, phy_list, filelist, filename, time_start, time_diff, phy_nc=None, phy_hdf=None):
    #start_timer = time.time()

    # define boundary coordinates
    minlat=float(limit[0])
    maxlat=float(limit[1])
    minlon=float(limit[2])
    maxlon=float(limit[3])
    
    # pixel dimensions
    lat_dim = int(1+round(((maxlat-minlat)/gsize)))
    lon_dim = int(1+round(((maxlon-minlon)/gsize)))
    
    #set target netcdf file
    ds = netCDF4.Dataset(filename, 'w',format='NETCDF4')
    
    #set global attributes
    ds.ShortName = "AERDT_L3_MEASURES_QD_HH"
    #ds.LongName = None
    """
    ds.VersionID = None
    ds.GranuleID = None
    ds.Format = "netCDF4"
    ds.RangeBeginningDate = None
    ds.RangeBeginningTime  = None
    ds.RangeEndingDate = None
    ds.RangeEndingTime = None
    ds.IdentifierProductDOIAuthority = "https://dx.doi.org/ - product DOI authority "
    ds.IdentifierProductDOI = None
    ds.ProductionDateTime = None
    ds.ProcessingLevel = "Level 3"
    ds.Conventions = None
    ds.NorthernmostLatitude = limit[1]
    ds.SouthernmostLatitude = limit[0]
    ds.WesternmostLongitude = limit[2]
    ds.WesternmostLongitude = limit[3]
    """
    
    # Create time, lat, lon, sensor dimensions
    timed = ds.createDimension('time', None)
    lat = ds.createDimension('lat', lat_dim) #latitude is fatitude (y)
    lon = ds.createDimension('lon', lon_dim) # x
    sensor = ds.createDimension('sensor', 6) #only used for SensorWeighting mask
    
    #set time variable to filename parse
    times = ds.createVariable('time', 'f4', ('time',))
    
    #set lats and lons  (or rather y and x)
    lats = ds.createVariable('latitude', 'f4', ('lat',), fill_value=-9999.) #latitude is fatitude
    lons = ds.createVariable('longitude', 'f4', ('lon',), fill_value=-9999.)
    sensor_var = ds.createVariable("sensors",'f4', ('sensor', ))
    
    #sensors metadata
    sensor_var.long_name = "Sensors: MODIS-T, MODIS-A, VIIRS-SNP, ABI-G16, ABI-G17, AHI-H08"
    
    #latitude / longitude metadata
    lats.valid_range = [-90.0, 90.0]
    #lats._FillValue = -9999.
    lats.standard_name = "latitude"
    lats.long_name = "Geodectic Latitude"
    lats.units = "degree_north"
    lats.scale_factor = 1.
    lats.add_offset = 0.
    lats.Parameter_Type = "Equal angle grid center location"
    lats.Geolocation_Pointer = "Geolocation data not applicable" 
    lats._CoordinateAxisType = "Lat"
    
    lons.valid_range = [-180.0, 180.0]
    #lons._FillValue = -9999.
    lons.standard_name = "longitude"
    lons.long_name = "Geodectic Longitude"
    lons.units = "degree_east"
    lons.scale_factor = 1.
    lons.add_offset = 0.
    lons.Parameter_Type = "Equal angle grid center location"
    lons.Geolocation_Pointer = "Geolocation data not applicable" 
    lons._CoordinateAxisType = "Lon"

    #bounds for lats and lons
    lats[:] = np.arange(0,lat_dim)*gsize+minlat
    lons[:] = np.arange(0,lon_dim)*gsize+minlon
    
    # unknown number of sensors, save values to list
    values = []
    sensors = {}

    # instantiate empty arrays for summary statistics
    indata_temp = []
    inlat_temp = []
    inlon_temp = []
    
    # Solar zenith angle 
    name = "Solar_Zenith_Angle"
    solar_zenith_variable = ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=-9999)
    solar_zenith_variable.long_name = "Solar Zenith Angle at the center of grid calculated for central time of the file"
    solar_zenith_variable.units = "degree"
    solar_zenith_variable.valid_range = [ 0, 18000]
    solar_zenith_variable.scale_factor = 0.01
    solar_zenith_variable.add_offset = 0
    
    solar_zenith_variable[0, :, :] = solar_zenith.get_SZA_array(limit, gsize, time_start, time_diff)
    
    # for calculating LEOGEO statistics
    # LEOGEO: Mean, STD, NumberOfSensors, SensorWeighting, TotalPixels
    # index of value corresponds to individual sensor
    #leogeo_stats = {"Mean": [], "STD": [], "TotalPixels":[]}
    leogeo_stats_arr = {} #contains leogeo_stats as value, geophys as key
    #sensor_idx_stats = {"NumberOfSensors":[], "SensorWeighting":[]}
    #sensor_idx = {} #key = sensor name, value = sensoridx
    sensor_idx_arr = {} #key = geophys value, value = sensor_idx
    
    #run through and assign gridded data to sensor variable
    # filenames are in the form:
    # [[time0: [sat1], [sat2], ... ], ...[timek: [sat1], [sat2], ....]] 
    # we assume we receive a signle dict for a time interval though
    for i, s_name in enumerate(filelist.keys()): 
        start_timer = time.time()

        for s in filelist.get(s_name):
            print("WORK SENSOR: ", s_name)

            L2FID,GeoID,PhyID = sat_data_input.open_file(str(s))

            # check for hdf files 
            if (str(s).split(".")[-1] == "hdf"):
                geo_list = ['Latitude', 'Longitude']
                lat,lon,phy_vars, meta = filter_data.filter_data_hdf(GeoID, PhyID, geo_list, phy_list, phy_hdf)
                L2FID.end()
                
            else: #netcdf
                geo_list = ['latitude', 'longitude']
                lat,lon,phy_vars, meta = filter_data.filter_data_nc(GeoID, PhyID, geo_list, phy_list, phy_nc)
                L2FID.close()
            
            # statistics appending for this sensor
            # index for arrays = geophysical variable indices
            for count, p_var in enumerate(phy_list):
                
                #create empty array for geophysical variable
                if len(indata_temp) < count+1:
                    indata_temp.append([])
                    inlat_temp.append([])
                    inlon_temp.append([])
                
                indata_temp[count] = ma.concatenate([indata_temp[count], phy_vars[count]])
                inlat_temp[count] = ma.concatenate([inlat_temp[count], lat[count]])
                inlon_temp[count] = ma.concatenate([inlon_temp[count], lon[count]])
        # end sensor concatenations
        # indata = [[geovar data 1], [geovar data 2], ... , [geovar data n]]
        
        # grid parameters
        # individual sensor statistics
        for j, p_vars in enumerate(phy_list):
            
            #special metadata and statistic calculations for AOD
            # values that need LEOGEO statistic calculations
            if not("Sensor_Zenith" in p_vars or "Scattering_Angle" in p_vars):#"Optical_Depth_Land_And_Ocean" in p_vars:
                aod_statistics = ["Mean", "STD", "Pixels"]
                avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp[j],inlat_temp[j],inlon_temp[j])
                #concatenate AOD data for leogeo stats later
                
                for aod_stat in aod_statistics:
                    
                    index = len(values) #i * len(phy_list) + j
                    aod_long = meta[j]["long_name"]
                    name = naming_conventions.nc_var_name(p_vars, s_name, aod_stat) #str(s_name+"_"+p_vars)
                    values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=meta[j]["_FillValue"]))
                    
                    # metadata
                    values[index].units = meta[j]["units"]
                    values[index].valid_range = meta[j]["valid_range"]
                    values[index].long_name = naming_conventions.nc_long_name(p_vars, s_name, aod_stat, aod_long)#meta[j]["long_name"]
                    values[index].scale_factor = meta[j]["scale_factor"]
                    values[index].add_offset = meta[j]["add_offset"]
                    values[index].Parameter_Type = meta[j]["Parameter_Type"]

                    
                    # instantiate the dictionary for statistics
                    if not p_vars in leogeo_stats_arr:
                        leogeo_stats_arr[p_vars] = {"Mean": [], "STD": [], "TotalPixels":[]}
                        
                        
                    # make sure key is in dict 
                    # instantiation
                    if not p_vars in sensors:
                        sensors[p_vars] = []
                    
                    if not p_vars in sensor_idx_arr:
                        sensor_idx_arr[p_vars] = {}
                    
                    #statistics to be added
                    if aod_stat== "Mean":
                        rotated = list(zip(*avgtau))[::-1]
                        leogeo_stats_arr[p_vars] ["Mean"].append(np.flipud(rotated)) #for leogeo calculation later
                        
                        #sensor idx (Sensor Weighting)
                        temp_a = np.flipud(rotated)
                        """
                        print("\nBEFORE SENSOR IDX \n")
                        print(temp_a)
                        print("Fill Value: ", meta[j]["_FillValue"])"""
                        temp_a[temp_a > -9999] = 1
                        temp_a[temp_a <= meta[j]["_FillValue"]] = 0
                        temp_a[np.isnan(temp_a)] = 0
                        #sensor_idx[naming_conventions.get_sensor(s_name)] = temp_a
                        sensor_idx_arr[p_vars][naming_conventions.get_sensor(s_name)] = temp_a
                        """
                        print("\nSENSOR IDX\n")
                        print(sensor_idx[naming_conventions.get_sensor(s_name)])
                        print("\n")
                        """
                    
                    
                        
                    elif aod_stat == "STD":
                        rotated = list(zip(*stdtau))[::-1]
                        
                        leogeo_stats_arr[p_vars]["STD"].append(np.flipud(rotated))
                        
                        #leogeo_stats["STD"].append(np.flipud(rotated)) #for leogeo calculation later
                    elif aod_stat == "Pixels":
                        rotated = list(zip(*count))[::-1]
                        
                        leogeo_stats_arr[p_vars]["TotalPixels"].append(np.flipud(rotated))
                        #leogeo_stats["TotalPixels"].append(np.flipud(rotated)) #for leogeo calculation later
                    else:
                        rotated = list(zip(*avgtau))[::-1]
                        
                        leogeo_stats_arr[p_vars]["Mean"].append(np.flipud(rotated))
                        #leogeo_stats["Mean"].append(np.flipud(rotated)) #for leogeo calculation later
                        print("STATISTIC ERROR")
                    
                    values[index][0, :, :] = np.flipud(rotated) # make it 2dimensional
                    sensors[p_vars].append(np.flipud(rotated)) #add it to complete dataset for LEOGEO calculations

                #time
                end_timer = time.time()
                print("Sensor: ",s_name ," time: ", end_timer - start_timer)
                
            else:  #phy_var is NOT AOD

                avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_temp[j],inlat_temp[j],inlon_temp[j])

                index = len(values) #i * len(phy_list) + j
                name = naming_conventions.nc_var_name(p_vars, s_name) #str(s_name+"_"+p_vars)
                values.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', ), fill_value=meta[j]["_FillValue"]))
                
                # metadata
                values[index].units = meta[j]["units"]
                values[index].valid_range = meta[j]["valid_range"]
                values[index].long_name = naming_conventions.nc_long_name(p_vars, s_name)#meta[j]["long_name"]
                values[index].scale_factor = meta[j]["scale_factor"]
                values[index].add_offset = meta[j]["add_offset"]
                values[index].Parameter_Type = meta[j]["Parameter_Type"]

                """
                # make sure key is in dict 
                # instantiation
                if not p_vars in sensors:
                    sensors[p_vars] = []
                """
                
                rotated = list(zip(*avgtau))[::-1]
                
                values[index][0, :, :] = np.flipud(rotated) # make it 2dimensional
                #sensors[p_vars].append(np.flipud(rotated)) #add it to complete dataset for LEOGEO calculations

                #time
                end_timer = time.time()
                print("Sensor: ",s_name ," time: ", end_timer - start_timer)
        
        # reset
        indata_temp = []
        inlat_temp = []
        inlon_temp = []
        
    # end individual sensor gridding and adding to nc
    
    # calculate LEOGEO statistics
    # LEOGEO: Mean, STD, NumberOfSensors, SensorWeighting, TotalPixels
    # index of value corresponds to individual sensor
    # leogeo_stats = {"Mean": [], "STD": [], "TotalPixels":[]}
    # sensor_idx = {} #key = sensor name, value = sensoridx
    leogeo_calculated_statistics = []
    number_of_sensors_variable = []
    sensor_idx_variable = []
    
    #print("\nLEOGEO STATS\n")
    #print(leogeo_stats)
    
    # FilteredQA_550
    # Mean, STD, and TotalPixels stat calculations
    j = 0
    leogeo_index = 0
    for p_var in phy_list:
        if p_var in leogeo_stats_arr: #go through each geophysical variable
        
            leogeo_stats = leogeo_stats_arr[p_var] #current dict 
            leogeo_calculated_statistics.append([])
            
            i=0
            # mean, std, pixel statistics
            for statistic in leogeo_stats:
                name = naming_conventions.nc_var_name(p_var, "LEOGEO", statistic)
                
                # avgtau = np.nanmean(np.array(sensors.get(p_vars)), axis=0 )
                stat_values = naming_conventions.calculate_statistic(statistic, 
                                                                    leogeo_stats["Mean"],
                                                                    leogeo_stats["STD"],
                                                                    leogeo_stats["TotalPixels"])
                
                leogeo_calculated_statistics[leogeo_index].append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', )))
                leogeo_calculated_statistics[leogeo_index][i][0, :, :] = stat_values
                leogeo_long = meta[leogeo_index]["long_name"]
                leogeo_calculated_statistics[leogeo_index][i].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO", 
                                                                                            statistic, leogeo_long)
                
                i+=1
            
                
            # Sensor IDX calculations
            # SensorWeighting and NumberOfSensors
            # sensor_idx = {} #key = sensor name, value = sensoridx
            
            sensor_order = ["MODIS_T", "MODIS_A", "VIIRS_SNPP", "ABI_G16", "ABI_G17", "AHI_H08"]
            name = naming_conventions.nc_var_name(p_var,"LEOGEO", "SensorWeighting")
            sensor_idx_variable.append(ds.createVariable(name, 'f4', ('sensor', 'lat', 'lon', )))
            sensor_idx_variable[leogeo_index].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO",
                                                                            "SensorWeighting", meta[j]["long_name"])
            
            number_of_sensors = []
            
            i = 0
            for satellite in sensor_order:
                #add number of sensors together
                if len(number_of_sensors)==0:
                    number_of_sensors = sensor_idx_arr[p_var][satellite]
                else:
                    number_of_sensors = number_of_sensors + sensor_idx_arr[p_var][satellite]
                
                #save for sensor layer
                sensor_idx_variable[leogeo_index][i, :, :] = sensor_idx_arr[p_var][satellite]
                i += 1
            
            name = naming_conventions.nc_var_name(p_var, "LEOGEO", "NumberOfSensors")
            number_of_sensors_variable.append(ds.createVariable(name, 'f4', ('time', 'lat', 'lon', )))   
            number_of_sensors_variable[leogeo_index][0, :, :] = number_of_sensors
            number_of_sensors_variable[leogeo_index].long_name = naming_conventions.nc_long_name(p_var, "LEOGEO",
                                                                              "NumberOfSensors", meta[j]["long_name"])
            leogeo_index+=1    
        j += 1
    
    """
    # put in gridded statistics
    # avgtau,stdtau,grdlat,grdlon,mintau,maxtau,count,sumtau = gridding.grid(limit,float(gsize),indata_stat,inlat_stat,inlon_stat)
    sensor_id = []
    shape = (len(np.arange(0,lat_dim)*gsize+minlat), len(np.arange(0,lon_dim)*gsize+minlon))
    avg = []
    # all sensors combined statistics (LEOGEO)
    for k, p_vars in enumerate(phy_list):
        # averages
        try:
            avgtau = np.nanmean(np.array(sensors.get(p_vars)), axis=0 )
            # other statistics nan
            # Number of Sensors
            sensor_id_x = np.zeros(shape)
            for i in range(len(sensors[p_vars])):
                sensor_id_x = sensor_id_x + (np.array(sensors.get(p_vars)[i])*0+1)
                #print(np.nan_to_num(np.array(sensors.get(p_vars)[i])*0+1, -1))
            avg_name = str("merge_avgtau_" + p_vars)
            avg.append(ds.createVariable(avg_name, 'f4', ('time', 'lat', 'lon', )))
            avg[k][0, :, :] = avgtau
            # metadata
            # naming convention, units should be consistent
            # read from configuration file
            # follow netcdf conventions
            # avg[k].units = meta["units"]
            # avg[k].valid_range = meta["valid_range"]
            # avg[k]._FillValue = meta["_FillValue"]
            # avg[k].long_name = meta["long_name"]
            # avg[k].scale_factor = meta["scale_factor"]
            # avg[k].add_offset = meta["add_offset"]
            # avg[k].Parameter_Type = meta["Parameter_Type"]
            sensor_id_name = str("sensor_id_x_" + p_vars)
            sensor_id.append(ds.createVariable(sensor_id_name, 'f4', ('time', 'lat', 'lon', )))
            sensor_id[k].units = 'unknown'
            sensor_id[k][0, :, :] = sensor_id_x
        except:
            #print("There are: ", len(sensors.get(p_vars)), " sensors for the var")
            print(p_vars)
            print(sensors.get(p_vars))
    """

    #close file
    ds.close()
    # output = 1 netcdf with six variables (one for each sensor) 
    # merge = run two loops (lat lon) (xdim, ydim from grid) 
    # merge aod equal to average of six sensors making sure no nan
    # identify which sensors are availabe - sensor ID variable 0 or 1 (unavailable vs available)
    # byte type array, keep n-dimensional for now
    # minimum number of things to merge: in the future

    # future capabilities:
    # minimum number, flagging system, use higher quality data (prefiltered)
    