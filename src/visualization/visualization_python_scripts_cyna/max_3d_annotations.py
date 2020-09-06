# Max Ferrin 9/4/20

import numpy as np

# origin: [z,y,x] in µm
# scale_size: [z,y,x] in µm
def add_scale_3d(viewer, origin=[0,0,0], scale_size=[5,5,5], scale_width=0.2, color='white'):
    scale_size_z, scale_size_y, scale_size_x = scale_size
    origin_z, origin_y, origin_x = origin
    
    scale_bar_z = [[origin_z,origin_y,origin_x],[origin_z+scale_size_z,origin_y,origin_x]]
    scale_bar_y = [[origin_z,origin_y,origin_x],[origin_z,origin_y+scale_size_y,origin_x]]
    scale_bar_x = [[origin_z,origin_y,origin_x],[origin_z,origin_y,origin_x+scale_size_x]]
    
    viewer.add_shapes(scale_bar_x, shape_type='path', edge_width=scale_width,
                      face_color=color, edge_color=color)
    viewer.add_shapes(scale_bar_y, shape_type='path', edge_width=scale_width,
                      face_color=color, edge_color=color)
    viewer.add_shapes(scale_bar_z, shape_type='path', edge_width=scale_width,
                      face_color=color, edge_color=color)
    

def add_timestamp_3d(viewer, s_timestamps, origin=[0,0,0]):
    time_labels = np.full((len(s_timestamps),4),0.)
    time_labels[:,0] = np.arange(len(s_timestamps))
    time_labels[:,1:] = origin

    properties = {'minutes':s_timestamps//60,
                 'seconds':np.round((s_timestamps/60-s_timestamps//60)*60)}
    text = {'text': '{minutes:n}:{seconds:n} (min:sec)', 
            'color':'white',
    #        'translation': [[0,-40,-40]],
            'size': 20
           }
    viewer.add_points(time_labels, properties=properties, text=text, 
                      face_color='transparent', edge_color='transparent',
                     blending='additive')