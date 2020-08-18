# Cyna Shirazinejad
# 7/29/20

# utilities for gif generation in naparimovie
# the following functions are wrappers for naparimovie to automate the line by line construction of text commands to make a movie

class MovieBuilder:
    """Builds a movie script through a movie object"""
    x_axis='(1,0,0)' # x axis rotation vector
    z_axis='(0,1,0)' # z axis rotation vector
    def __init__(self, frame_start=0): # initialize a MovieBuilder object, default start from is 0
        self._commands = [] # commands compiled for a complete movie through operations
        self._frame_in_movie = frame_start # current frame of movie 

    def _make_rotation(frame_start, frame_end, degrees, rotation_vector):
        """Make a rotation from the designated start and end frames by the specified degrees around an axis"""
        return f'From frame {frame_start} to frame {frame_end}\n-rotate by {degrees} degrees around {rotation_vector}'
        
    def _make_layer_visible(frame_number, layer_number):
        """Make a layer visible"""
        return f'At frame {frame_number} make layer {layer_number} visible'

    def _make_layer_invisible(frame_number, layer_number):
        """Make a layer invisible"""
        return f'At frame {frame_number} make layer {layer_number} invisible'

    def make_all_layers_invisible(self,
                                num_channels):
        """Iterate through the number of specified channels and make them invisible"""
        for channel in range(num_channels):
            self._frame_in_movie = self.make_one_layer_invisible( channel)
        return self._frame_in_movie

    def make_all_layers_visible(self,
                                num_channels):
        """Iterate through the number of specified channels and make them visible"""
        for channel in range(num_channels):
            self._frame_in_movie = self.make_one_layer_visible(channel)
        return self._frame_in_movie

    def rotate(self,
               number_frames_per_unit_rotation,
               number_of_unit_rotations,
               unit_rotation_amount,
               rotation_vector):
        """Rotate the field of view and update the current movie frame"""
        rotation_command = MovieBuilder._make_rotation(self._frame_in_movie,
                                                       self._frame_in_movie + number_frames_per_unit_rotation * number_of_unit_rotations,
                                                       number_of_unit_rotations * unit_rotation_amount,
                                                       rotation_vector)
        
        self._commands.append(rotation_command)
        
        self._frame_in_movie += number_frames_per_unit_rotation * number_of_unit_rotations + 1
        
        return self._frame_in_movie

    def make_one_layer_visible(self,
                            channel):
        """Make one layer visible and update the current movie frame"""
        layer_invisible_command = MovieBuilder._make_layer_visible(self._frame_in_movie, channel)
        self._commands.append(layer_invisible_command)
        self._frame_in_movie += 1
        return self._frame_in_movie

    def make_one_layer_invisible(self,
                                channel):
        """Make one layer invisible and update hte current movie frame"""
        layer_invisible_command = MovieBuilder._make_layer_invisible(self._frame_in_movie, channel)
        self._commands.append(layer_invisible_command)
        self._frame_in_movie += 1
        return self._frame_in_movie
    
    def wait(self, duration):
        """Update the number of frames to reflect a pause"""
        self._frame_in_movie += duration

    def build_movie(self, file_path):
        """Assemble the movie commands and build a human-readable text file at the specified path"""
        with open(file_path, 'w') as file:
            print('\n'.join(self._commands), file=file, end='')
    
    def zoom(self,
               number_of_frames,
               zoom_amount):
        """Zoom by the specified amount over the number of frames provided"""
        self._commands.append(f'From frame {self._frame_in_movie} to frame {self._frame_in_movie+number_of_frames}\n-zoom by a factor of {zoom_amount}')

        self._frame_in_movie += number_of_frames+1
        
        return self._frame_in_movie
    
    
    def shift_time(self,
               number_of_frames,
               number_of_time_points):
        """Shift time by the specified amount over the number of frames provided"""
        self._commands.append(f'From frame {self._frame_in_movie} to frame {self._frame_in_movie+number_of_frames}\n-shift time by {number_of_time_points}')

        self._frame_in_movie += number_of_frames+1
        
        return self._frame_in_movie