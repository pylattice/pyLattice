# Cyna Shirazinejad 8/4/20 

from operator import add
import numpy as np

def add_3d_axes(viewer, 
                shape_of_file, 
                line_width=1, 
                marker_width = 1, 
                offset= [0,0,0], 
                extension = [0,0,0], 
                points_on_axes = [10,10,10]):
    """Displays a 3d scale bar
    Parameters
    ----------
    viewer: napari.Viewer()
        a napari Viewer() instance
    shape_of_file: list or tuple of integers
        the dimensions of the largest image in the viewer
    line_width: int
        width of the lines of the scale bars
    marker_width: int
        width of the markers on the scale bars
    offset: list of 
        offset of origin away from (shape_of_file[0], 0, 0) 
    extension: list of integers
        extension or reduction of length of scale bars from shape_of_file
    points_in_axes: list of integers
        number of scale markers along each axis
      
    Returns
    -------
    none
    """
    
    # set colors of scale bars and markers
    bar_colors=['white','white','white']
    marker_colors=['white','white','white']
    
    origin = [shape_of_file[1]+offset[0],0+offset[1],0+offset[2]] # origin of scaled axes

    # end-point along each axis
    end_z = [0-extension[0]+offset[0],0+offset[1],0+offset[2]] 
    end_y = [shape_of_file[1]+offset[0],shape_of_file[2]+extension[1]+offset[1],0+offset[2]]
    end_x = [shape_of_file[1]+offset[0],0+offset[1],shape_of_file[2]+extension[2]+offset[2]]
    ends = [end_z, end_y, end_x]
    
    # lengths of each scale bar dimension
    length_z = np.abs(origin[0]-end_z[0])
    length_y = np.abs(origin[1]-end_y[1])
    length_x = np.abs(origin[2]-end_x[2])
    lengths = [length_z, length_y, length_x]
    
    # spacing between each scale marker on each axis
    spacings = [lengths[i]/points_on_axes[i] for i,_ in enumerate(lengths)]
#     print(spacings)
    # add lines for scale bar
    viewer.add_shapes(np.array([origin,ends[0]]), shape_type='path', edge_width=line_width, face_color=bar_colors[0])
    viewer.add_shapes(np.array([origin,ends[1]]), shape_type='path', edge_width=line_width, face_color=bar_colors[0])
    viewer.add_shapes(np.array([origin,ends[2]]), shape_type='path', edge_width=line_width, face_color=bar_colors[0])
    
    # basis for incremental change in position of each scale marker on each axis
    spacer_templates = [[-1,0,0], [0,1,0], [0,0,1]]
    
    # add a polygon at origin
    shape_vertices = []
    new_shape_center=origin
    for z_shift in [-marker_width/2,marker_width/2]:
        for y_shift in [-marker_width/2,marker_width/2]:
            for x_shift in [-marker_width/2,marker_width/2]:

                shape_vertices.append(list(map(add, new_shape_center, [z_shift, y_shift, x_shift])))
    viewer.add_shapes(np.array(shape_vertices), shape_type='polygon', edge_width=0.5, face_color='white')
    
    # for each scale bar, get the number of points that belongs on the scale bar
    for i, num_points_in_axis in enumerate(points_on_axes):
        for j in range(1,num_points_in_axis+1):
            # get center of each marker on scale bar
            new_shape_center = list(map(np.add,(j*spacings[i])*np.array(spacer_templates[i]), origin))
            shape_vertices = []
            # gather all corners of a cube
            for z_shift in [-marker_width/2,marker_width/2]:
                for y_shift in [-marker_width/2,marker_width/2]:
                    for x_shift in [-marker_width/2,marker_width/2]:

                        shape_vertices.append(list(map(add, new_shape_center, [z_shift, y_shift, x_shift])))
            # plot a cube as the marker along scale bar
            viewer.add_shapes(np.array(shape_vertices), shape_type='polygon', edge_width=0.5, face_color=marker_colors[i])
#          