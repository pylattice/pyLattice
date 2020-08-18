# Cyna Shirazinejad 7/21/20

import pickle
import napari 
import os
import pims
import sys
import numpy as np
from os import listdir
from os.path import isfile, join
from naparimovie import Movie
from skimage.filters import threshold_otsu
import dask.array as da 
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import subprocess
import scipy as sp
import scipy.optimize
import dask
import imageio
from skimage.io import imread
from dask import delayed
import dask.array as da
from PIL import Image
from pims import ImageSequence
from glob import glob
import tifffile


    

def convert_tiffs_to_dask_arrays(path_to_directory, 
                                 channel_identifiers=None,
                                 is_MIP=False,
                                 verbose=True):
    """"returns a dask array of the data in the provided directory"""""
    
    # get all files in provided directory
    all_files = os.listdir(path_to_directory)
    
    # get files that are images, ignore random folders and junk
    files_images=[]
    if channel_identifiers==None:
        # identifiers for different channels to search for
        channel_designation_flags = []

        # indentifiers for stack numbers
        stack_ind = []

        # search for index of 'CamN', 'chN', 'stack' in files if split by '_'
        cam_index = [-1]
        ch_index = [-1]
        stack_index = [-1]
        for file in all_files:
            file_split = file.split('_')
            for i,sub_file in enumerate(file_split):
                if 'Cam' in sub_file:
                    if i not in cam_index:
                        cam_index.append(i)
                elif 'ch' in sub_file:
                    if i not in ch_index:
                        ch_index.append(i)
                elif 'stack' in sub_file:
                    if i not in stack_index:
                        stack_index.append(i)
            if 'Cam' and 'ch' in file:
                files_images.append(file)

        # make sure indices exist
        if cam_index == [-1] or ch_index == [-1] or stack_index == [-1]:
            raise Exception('Houston, we got a problem')

        # make sure indices are unique
        if len(cam_index)>2 or len(ch_index)>2 or len(stack_index)>2:
            raise Exception('Houston, we got a bigger problem')

        cam_index = cam_index[1]
        ch_index = ch_index[1]
        stack_index=stack_index[1]
        if verbose: print(f'Index of camera designation is {cam_index}\nIndex of channel designation is {ch_index}\nIndex of stack designation is {stack_index}')

        # find number of stacks
        stacks_present = []

        # find all designations of unique identifiers for channels from 'ch' and 'Cam'
        for file in files_images:

            file_split = file.split('_')
            camera=file_split[cam_index]
            ch=file_split[ch_index]

            if [camera,ch] not in channel_designation_flags:
                channel_designation_flags.append([camera,ch])

            if file_split[stack_index][5:] not in stacks_present:
                stacks_present.append(file_split[stack_index][5:])

        stacks_present.sort()
        if verbose: print(f'The stacks present in this file are: {stacks_present}')

        channel_order_designation = [[i,(tag[0],tag[1])] for i,tag in enumerate(channel_designation_flags)]
        print(f'The channels will be returned in the following order linked to the detected identifiers: {channel_order_designation}')
    
    # a list of lists. each nested list contains all files that belong to the 
    # unique channel identifiers in the same order as channel_designation_flags
        channels_sorted = []



        for designation in channel_designation_flags:

            designation_assigned_files=[]
            for file in files_images:

                channel_of_interest = designation[1]
                camera_of_interest = designation[0]

                if channel_of_interest in file and camera_of_interest in file:

                    designation_assigned_files.append(file)
            channels_sorted.append(sorted(designation_assigned_files))
    
    else:
        
        channels_sorted = []
        
        for identifier in channel_identifier:
            for file in all_files:
                print('none')
                
            
#     return channels_sorted
    
        
        

    sample = tifffile.imread(path_to_directory+channels_sorted[0][0])
   # test if there is MIP in filename to designate Z=1
    if 'MIP' in path_to_directory+channels_sorted[0][0] or is_MIP:
        is_mip=True
    else:
        is_mip=False

    channels_dask=[]
    lazy_imread=delayed(tifffile.imread)

    for channel in channels_sorted:
        channel.sort()
#         print(channel)
        if is_mip:
            
            x_y_shape = sample.shape
            new_shape=(1,x_y_shape[0],x_y_shape[1])
            dask_arrays=[]
            for fn in channel:
                old_array=tifffile.imread(path_to_directory+fn)
#                 print(old_array.shape)
                place_holder_array = np.zeros(new_shape)
                place_holder_array[0,...]=old_array
                dask_arrays.append(da.from_array(place_holder_array))
            
            

        else:
            # if not a MIP, make a full array of the data with lazy loading
            lazy_arrays = [lazy_imread(path_to_directory+fn) for fn in channel]
            dask_arrays = [da.from_delayed(delayed_reader, shape = sample.shape, dtype=sample.dtype) for delayed_reader in lazy_arrays]


    
        channels_dask.append(dask_arrays)
    # create the full output array
    output_array = np.empty((len(channels_sorted), len(channels_sorted[0]), sample.shape[0],sample.shape[1],sample.shape[2]), dtype=np.float32)
    
    # add each channel's stacks into the final array
    for i,channel in enumerate(channels_dask):
        if verbose: print(f'Adding channel {i} to an output array')
        for j,channel_stack in enumerate(channel):
            if verbose: print(f'Adding stack {j} within channel {i} to an output array')
            output_array[i,j,:] = channel_stack
    if verbose: print('Converting array to dask array')
    return da.asarray(output_array)


# def dask_to


def view_one_time_one_channel(dask_channel_list,channel,time_point):
    
    with napari.gui_qt():
#     for channel in range(len(channels_dask)):
        
    # specify contrast_limits and is_pyramid=False with big data
    # to avoid unnecessary computations
        napari.view_image(dask_channel_list[channel][time_point,...],contrast_limits=[0,200], multiscale=False)
    
def view_one_channel(dask_channel_list,channel):
    
    with napari.gui_qt():
    #     for channel in range(len(channels_dask)):

        # specify contrast_limits and is_pyramid=False with big data
        # to avoid unnecessary computations
        napari.view_image(dask_channel_list[channel],contrast_limits=[0,200], multiscale=False)
        
def view_specified_channels_one_time(dask_channel_list,channels_list,time_point,colors):
    
    viewer = napari.Viewer(ndisplay=len(channels_list))
    
    for channel in channels_list:
        
        viewer.add_image(dask_channel_list[channel][time_point],colormap=colors[channel])
        
        
        



def populate_grid(viewer, height, width, images, dummy=None):
    """
    generates a napari image grid with the given size and images in the given positions
    viewer -- napart viewer object
    width, height -- grid dimensions
    images -- a list of images
    positions -- a list of positions for images
    dummy -- the image to show in empty cells
    """

    if dummy is None:
        dummy = np.zeros((1,1))

    # check preconditions
    if width < 1 or height < 1:
        raise ValueError('improper dimensions')
    if len(images) == 0:
        raise ValueError('no images provided')

    # create a matrix to hold image indices
    grid = []
    for j in range(height):
        grid.append([])
        for _ in range(width):
            grid[j].append([])
    
    # populate the matrix
    for image, positions, color, name in images:
        for pos in positions:
            grid[pos[0]][pos[1]].append((image,color,name))
#     print(grid)
    # build the image
    empty = False
    while not empty:
        empty = True
        for j in range(height):
            for i in range(width):
                image_queue = grid[height - j - 1][width - i - 1]
#                 print(image_queue)
                # add the image
                if len(image_queue) > 0:
                    image_data,color,name_channel=image_queue.pop(0)
                    name_channel=name_channel+'_'+str(height - j - 1)+','+str(width - i - 1)
                    viewer.add_image(image_data,colormap=color,name=name_channel, multiscale=False, contrast_limits = [0,2000]) 
                else:
                    viewer.add_image(dummy, name='dummy')

                # check if data is remaining
                if len(image_queue) > 0:
                    empty = False
    
    # show image
    viewer.grid_view(n_row=height, n_column=width, stride=1)
