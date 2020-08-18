# Cyna Shirazinejad
# dear god, this needes a lot of documentation because things do not work always as expected (8/1/20)

import pickle
import napari 
import pims
import os
import sys
import numpy as np
from os import listdir
from os.path import isfile, join
from nd2reader import ND2Reader
from naparimovie import Movie

import dask.array as da
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import ipywidgets as widgets
plt.rcParams.update({'figure.max_open_warning': 0})
import subprocess
from skimage.filters import threshold_otsu
import scipy as sp
import scipy.optimize
sys.path.append(os.path.abspath(os.getcwd() + '/visualization_python_scripts_cyna'))
# from dask_to_napari import option_1_view, option_2_view, option_3_view, option_4_view, option_5_view, option_6_view, option_7_view, option_8_view
# from pims import ND2_Reader
from PIL import Image
from visualization_utilities import add_3d_axes
def create_image_dimensionality_array(file_to_process):
    print(f'The file being processed is: {file_to_process}')
    print()
#    image_frames = pims.open(file_to_process)
    image_frames = ND2Reader(file_to_process)

    print(f'The coordinates available in this file are: {image_frames.sizes.keys()}')
    print()
    image_dimensionality_array = np.array([1,1,1,1,1])
    axes_available = ''
    print(image_frames.sizes.keys())
    for key in list(image_frames.sizes.keys()):
        axes_available+=key
        if key=='t':
            image_dimensionality_array[0]=image_frames.sizes['t']
            print(f"The number of time points in the movie: {image_frames.sizes['t']}")
        elif key=='c':
            image_dimensionality_array[1]=image_frames.sizes['c']
            print(f"The number of channels in the movie: {image_frames.sizes['c']}")
        elif key=='x':
            image_dimensionality_array[4]=image_frames.sizes['x']
            print(f"The number of x positions in each frame of the movie: {image_frames.sizes['x']}")
        elif key=='y':
            image_dimensionality_array[3]=image_frames.sizes['y']
            print(f"The number of y positions in each frame of the movie: {image_frames.sizes['y']}")
        elif key=='z':
            image_dimensionality_array[2]=image_frames.sizes['z']
            print(f"The number of z positions in each frame of the movie: {image_frames.sizes['z']}")
    print(f'The dimensionality array of this file is: {image_dimensionality_array}')
    print(axes_available)
    return image_dimensionality_array, axes_available, image_frames
    

# modified from https://github.com/JohSchoeneberg/pyLattice/blob/master/src/jupyter/latticeMovie_correctBleaching.ipynb

def fit_exp_nonlinear(t, y):
    opt_parms, parm_cov = sp.optimize.curve_fit(model_func, t, y, maxfev=10000,p0=(0 ,-0.1, y[0]))

    return opt_parms
def model_func(t, A, K, C):
    return A * np.exp(K * t) + C





def return_widgets_for_display(file_to_process):
    
    image_dimensionality_array, axes_available, image_frames=create_image_dimensionality_array(file_to_process)
    num_channels=int(image_dimensionality_array[1])
    style = {'description_width': 'initial'}

    percentile_ranges=[widgets.FloatSlider(
        value=temp[2],
        min=0,
        max=100,
        step=0.1,
        description='percentile ch'+str(temp[0])+' '+ temp[1] + ':',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
        style=style
    ) for temp in [(int(i/2),'lower',0) if i%2==0 else (int(i/2),'upper',100) for i in range(num_channels*2)]]

    all_percentiles_entrybox_lower_upper = [widgets.FloatText(
        value=0,
        description='ch'+str(int(i/2))+' lower:',
        disabled=False,
        style=style
    ) if i%2==0 else widgets.FloatText(
        value=100,
        description='ch'+str(int(i/2))+' upper:',
        disabled=False,
        style=style
    ) for i in range(num_channels*2)]   

    linked_widgets=[widgets.link((percentile_ranges[i], 'value'), (all_percentiles_entrybox_lower_upper[i], 'value')) for i in range(num_channels*2)]
    
    options=['None', 'single-Otsu', 'percentile']
    all_options=['ch'+str(ch)+' '+str(method) for ch in range(num_channels) for method in options]

    threshold_options=widgets.SelectMultiple(options=all_options,
                                             description='threshold channels:',
                                             disabled=False)
    
    channels_to_view=widgets.SelectMultiple(options=[str(chan) for chan in range(num_channels)],
                                            value=[],
                                            description='view channels',
                                            disabled=False)

    channels_thresholded=widgets.SelectMultiple(options=[str(chan) for chan in range(num_channels)],
                                                value=[],
                                                #rows=10,
                                                description='threshold channels:',
                                                disabled=False)
    display_widget=widgets.Checkbox(
                value=False,
                description='display on',
                disabled=False)
    
    make_napari_movie=widgets.Checkbox(
                value=False,
                description='make naparimovie',
                disabled=False)
    
    return num_channels, channels_to_view, channels_thresholded, percentile_ranges, all_percentiles_entrybox_lower_upper, threshold_options, image_dimensionality_array, axes_available, image_frames, display_widget, make_napari_movie
    
    
def make_movie(file_to_process,
               image_dimensionality_array,
               axes_available, 
               image_frames,
               channels_to_display,
               channels_to_threshold,
               percentile_values,
               threshold_methods,
               display_on,
               make_naparimovie):
    global viewer
    global movie
#     print(movie, viewer)
#     print('test')
#     print(threshold_methods)
    channels_view_enabled = channels_to_display
    temp_view = []
    for i in range(len(channels_view_enabled)):
        temp_view.append(int(channels_view_enabled[i]))
    channels_view_enabled = temp_view
    
    channels_thresholded = []
    for i in range(len(channels_to_threshold)):
        if channels_to_threshold[i]!='None':
            channels_thresholded.append(int(channels_to_threshold[i]))
    print('channels to threshold:' + str(channels_thresholded))
    
    image_dimensionality_array, axes_available, image_frames=create_image_dimensionality_array(file_to_process)
    
    
    raw_metadata = image_frames.metadata
    raw_metadata

    axes_to_bundle = ''
    if 'c' in axes_available:
        axes_to_bundle+='c'
    if 'z' in axes_available:
        axes_to_bundle+='z'
    if 'y' in axes_available:
        axes_to_bundle+='y'
    if 'x' in axes_available:
        axes_to_bundle+='x'
    print(axes_to_bundle)
    image_frames.bundle_axes = axes_to_bundle

    da_stack = da.stack(image_frames)
    print('dimensions of dask stack: ' + str(da_stack.shape))

    colors=['magenta','cyan','yellow']
    raw_metadata = ND2Reader(file_to_process).metadata
    print(raw_metadata)
    micron_per_px = raw_metadata['pixel_microns']
    print('Microns per pixel: ' + str(micron_per_px))
    print(image_dimensionality_array)

    # option #1 - 2d: t=1, c=1
    # option #2 - 2d: t=1, c>1
    # option #3 - 2d: t>1, c=1
    # option #4 - 2d: t>1, c>1
    # option #5 - 3d: t=1, c=1
    # option #6 - 3d: t=1, c>1
    # option #7 - 3d: t>1, c=1
    # option #8 - 3d: t>1, c>1

    # coordinates in "image_dimensionality_array" -> (t,c,z,y,x)
    # the first three (t,c,z) constrain how napari is fed the dask array of variable sizes


    # option #1 - 2d: t=1, c=1
    if image_dimensionality_array[2]==1 and image_dimensionality_array[0]==1 and image_dimensionality_array[1]==1:
        
        option_1_view(da_stack,colors)

    # option #2 - 2d: t=1, c>1 (NEED EXAMPLE BEFORE HARDCODING IN COORDINATES)
    elif image_dimensionality_array[2]==0 and image_dimensionality_array[0]==1 and image_dimensionality_array[1]>1:
        print('Executing option 2')
    #     viewer = napari.Viewer(ndisplay=2)
    # #     for time_point in range(image_dimensionality_array[0]):
    #     channel_stack = da_stack[:,:,:]
    #     viewer.add_image(channel_stack,blending='additive',colormap=colors[0])

    # option #3 - 2d: t>1, c=1 
    elif image_dimensionality_array[2]==1 and image_dimensionality_array[0]>1 and image_dimensionality_array[1]==1:
        print('Executing option 3')
        viewer = napari.Viewer(ndisplay=2)
        viewer.add_image(da_stack, colormap=colors[0])

    # option #4 - 2d: t>1, c>1
    elif image_dimensionality_array[2]==1 and image_dimensionality_array[0]>1 and image_dimensionality_array[1]>1:
        print('Executing option 4')
        viewer = napari.Viewer(ndisplay=2)
        for channel in range(image_dimensionality_array[1]):
            channel_stack = da_stack[:,channel,...]
            viewer.add_image(channel_stack, blending='additive', colormap=colors[channel])


    # option #5 - 3d: t=1, c=1
    elif image_dimensionality_array[2]>1 and image_dimensionality_array[0]==1 and image_dimensionality_array[1] == 1:
        print('Executing option 5')
        viewer = napari.Viewer(ndisplay=3)

        viewer.add_image(da_stack,colormap=colors[0])



    # option #6 - 3d: t=1, c>1
    elif image_dimensionality_array[2]>1 and image_dimensionality_array[0]==1 and image_dimensionality_array[1]>1:
        print('Executing option 6')
        
#         print(display_on)
        viewer = napari.Viewer(ndisplay=3)
        for channel in channels_view_enabled:
            channel_stack = np.array(da_stack[:,channel,...][0])

                
#                 channel_stack = interact(threshold_channel(channel_stack)
            if channel in channels_thresholded:
                print('loop')
#                 viewer.add_image(channel_stack,blending='additive',colormap=colors[channel])
                num_channels = image_dimensionality_array[1]
                print(threshold_methods)
                threshold_method_selected=threshold_methods
                num_selected=0
                
                for method in threshold_method_selected:
                    str_temp='ch'+str(channel)
                    if str_temp in method:
                        num_selected+=1
                        current_method = method
                if num_selected==0:
                    raise Exception('no selection made for channel'+str(channel))
                if num_selected>1:
                    raise Exception('more than 1 selection made for channel'+str(channel))
                if 'Otsu' in current_method:
                    threshold = threshold_otsu(np.ndarray.flatten(channel_stack))
                    ind_below_threshold = channel_stack<threshold
                    channel_stack[ind_below_threshold]=0
                    plt.hist(np.ndarray.flatten(channel_stack),log=True, label='raw counts')
                    plt.axvline(threshold,color='r', label = 'threshold')
                    plt.ylabel('counts')
                    plt.xlabel('intensity')
                    plt.title('ch'+str(channel))
                    plt.legend()
                    plt.show()
                if 'percentile' in current_method:
                    print(f'lower percentile {int(percentile_values[channel*2].value)}')
                    print(f'upper percentile {int(percentile_values[channel*2+1].value)}')
                    lower_percentile = np.percentile(np.ndarray.flatten(channel_stack),int(percentile_values[channel*2].value))
                    upper_percentile = np.percentile(np.ndarray.flatten(channel_stack),int(percentile_values[channel*2+1].value))
                    plt.hist(np.ndarray.flatten(channel_stack),log=True)
                    plt.axvline(lower_percentile,color='r')
                    plt.axvline(upper_percentile,color='g')
                    plt.ylabel('counts')
                    plt.xlabel('intensity')
                    plt.title('ch'+str(channel))
                    plt.legend(['raw counts','lower percentile','upper percentile'])
                    plt.show()
                    print('The upper and lower percentile for this channel is: ' + str(upper_percentile) + ', ' + str(lower_percentile))
                    ind_above_threshold = channel_stack > upper_percentile
                    ind_below_threshold = channel_stack < lower_percentile
                    channel_stack[ind_above_threshold]=0
                    channel_stack[ind_below_threshold]=0
                if display_on:
                    viewer.add_image(channel_stack,blending='additive',colormap=colors[channel])
                print(method)
            else:
                
                if display_on:
                    viewer.add_image(channel_stack,blending='additive',colormap=colors[channel])

     
    # option #7 - 3d: t>1, c=1
    elif image_dimensionality_array[2]>1 and image_dimensionality_array[0]>1 and image_dimensionality_array[1]==1:

#         frame_sum = []
#         print(da_stack.shape)
#         for i in range(da_stack.shape[0]):

#             time_frame_stack = da_stack[i,...]
#             frame_sum.append(np.mean(time_frame_stack))
#         y=np.array(frame_sum)
#         t=np.array(range(len(frame_sum)))
#     #     plt.plot(frame_sum)
#         A, K, C = fit_exp_nonlinear(t, y)
#         print(A,K,C)
#         fit_y = model_func(t, A, K, C)
#         plt.plot(t, y, 'rx', t, fit_y)
#         print('Executing option 7')
#         ratio_decay = fit_y/fit_y[0]
#         print(ratio_decay)
#         new_stack = []
#         for i in range(da_stack.shape[0]):
#             print(ratio_decay[i])
#             corrected_stack = np.divide(da_stack[i,...],ratio_decay[i])
#             new_stack.append(corrected_stack)

#         new_da_stack = da.stack(new_stack)
#     #         da_stack[i,...] = da.stack(corrected_stack)

        viewer = napari.Viewer(ndisplay=3)
#         viewer.add_image(da_stack,colormap=colors[0])

#     # option #8 - 3d: t>1, c>1
    elif image_dimensionality_array[2]>1 and image_dimensionality_array[0]>1 and image_dimensionality_array[1]>1:

# #         frame_sum = []

# #         for channel in range(image_dimensionality_array[1]):

# #             channel_temp=[]
# #             for time_point in range(image_dimensionality_array[0]):


# #                 temp_stack = np.array(da_stack[time_point,channel,...])

# #                 thresh = threshold_otsu(temp_stack)

# #                 indices_below_threshold = temp_stack<thresh
# #                 temp_stack[indices_below_threshold]=0
# #                 indices_nonzero = np.nonzero(temp_stack)
# #                 average = temp_stack[np.nonzero(temp_stack)].mean()
# #                 channel_temp.append(average)

# #             frame_sum.append(channel_temp)

# #         ch_decay = []
# #         new_stack = []
        
#         for channel in range(len(frame_sum)):
# #             if channel in channels_to_bleach_correct:

# #                 print(f'channel processing',channel)
# #                 channel_stack = []    
# #                 y = np.array(frame_sum[channel])
# #                 t = np.array(range(len(frame_sum[channel])))
# #                 print('starting fit')
# #                 A,K,C = fit_exp_nonlinear(t,y)
# #                 fit_y = model_func(t,A,K,C)
# #                 print('finished fit')
# #                 plt.plot(t,y,'rx',t,fit_y)
# #                 plt.show()
# #                 print(fit_y)
# #                 ratio_decay = fit_y/fit_y[0]
# #                 print(ratio_decay)

# #                 print('bleach correcint this channel')
# #                 for time_point in range(len(frame_sum[channel])):
# #                     print(time_point)
# #                     corrected_stack = np.divide(da_stack[time_point,channel,...],ratio_decay[time_point])
# #                     channel_stack.append(channel_stack)
# #                 print()
# #                 new_stack.append(channel_stack)
# #             else:
#             for time_point in range(len(frame_sum[channel])):
#                 print(time_point)
#                 new_stack.append(da_stack[time_point,channel,...])
# #             print('finished a channel')
# #         print('making an empty array')
# #         new_array = np.zeros((image_dimensionality_array[0],image_dimensionality_array[1],image_dimensionality_array[2],image_dimensionality_array[3],image_dimensionality_array[4]))
# #         print('finished making an empty array')
# #         for channel in range(len(new_stack)):
# #             print('making new channel')
# #             for time_point in range(len(new_stack[channel])):
# #                 print('adding a time_point')
#                 new_array[channel,time_point,...]=new_stack[channel][time_point]
#         print('making a dask array')
#         new_da_stack = da.stack(new_array)


        if display_on:
            print('Executing option 8')
            viewer = napari.Viewer(ndisplay=3)
            for channel in range(image_dimensionality_array[1]):
                viewer.add_image(da_stack[:,channel,...],blending='additive',colormap=colors[channel],scale=[1,micron_per_px*2,micron_per_px,micron_per_px])
            add_3d_axes(viewer, 
                (512,512,3), 
                line_width=.1, 
                marker_width = .1, 
                offset= [0,0,0], 
                extension = [0,0,0], 
                points_on_axes = [3,10,10])
    print('made it to the end ')
    if make_naparimovie:
        print('making naparimovie object')
        movie = Movie(myviewer=viewer) 
        print(movie)
        return movie