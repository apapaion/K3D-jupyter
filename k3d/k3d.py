# optional dependency
try:
    import vtk
    from vtk.util import numpy_support
except ImportError:
    vtk = None
    numpy_support = None

import numpy as np
import six
from .colormaps.basic_color_maps import basic_color_maps
from .plot import Plot
from .helpers import get_model_matrix, get_dimensions, validate_vectors_size
from .objects import Line, Points, Text, Text2d, Surface, Mesh, MarchingCubes, Voxels, VectorFields, Vectors, Texture, \
    STL

_default_color = 0x0000FF


def vtk_poly_data(poly_data, model_matrix=np.identity(4), color=_default_color, color_attribute=None,
                  color_map=basic_color_maps.Rainbow):
    if poly_data.GetPolys().GetMaxCellSize() > 3:
        cut_triangles = vtk.vtkTriangleFilter()
        cut_triangles.SetInputData(poly_data)
        cut_triangles.Update()
        poly_data = cut_triangles.GetOutput()

    if color_attribute is not None:
        attribute = numpy_support.vtk_to_numpy(poly_data.GetPointData().GetArray(color_attribute[0]))
        color_range = color_attribute[1:3]
    else:
        attribute = []
        color_range = []

    vertices = numpy_support.vtk_to_numpy(poly_data.GetPoints().GetData())
    indices = numpy_support.vtk_to_numpy(poly_data.GetPolys().GetData()).reshape(-1, 4)[:, 1:4]

    return Mesh(**{
        'model_matrix': model_matrix,
        'vertices': np.array(vertices, np.float32),
        'indices': np.array(indices, np.uint32),
        'color': color,
        'attribute': np.array(attribute, np.float32),
        'color_range': color_range,
        'color_map': np.array(color_map, np.float32)
    })


def stl(stl, model_matrix=np.identity(4), color=_default_color):
    return STL(**{
        'model_matrix': model_matrix,
        'color': color,
        'text': stl if isinstance(stl, six.string_types) else None,
        'binary': np.array(stl) if not isinstance(stl, six.string_types) else np.array([])
    })


def texture(binary, file_format, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5, zmax=.5, model_matrix=np.identity(4)):
    return Texture(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'binary': binary,
        'file_format': file_format
    })


def vectors(origins, vectors, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5, zmax=.5,
            model_matrix=np.identity(4), use_head=True, labels=[], colors=[], color=_default_color, line_width=1,
            label_size=1.0, head_size=1.0, head_color=None, origin_color=None):
    return Vectors(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'use_head': use_head,
        'origins': np.array(origins, np.float32),
        'vectors': np.array(vectors, np.float32),
        'line_width': line_width,
        'labels': labels,
        'label_size': label_size,
        'head_size': head_size,
        'colors': np.array(colors, np.uint32),
        'head_color': head_color if head_color is not None else color,
        'origin_color': origin_color if origin_color is not None else color,
    })


def vector_fields(vectors, colors=[], color=_default_color, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5,
                  zmax=.5, model_matrix=np.identity(4), width=None, height=None, length=None, use_head=True,
                  head_color=None, head_size=1.0, origin_color=None):
    shape = np.shape(vectors)

    if len(shape[:-1]) < 3:
        shape = (None,) + shape

    length, height, width = get_dimensions(shape[:-1], length, height, width)

    validate_vectors_size(length, vector_size=shape[-1])

    return VectorFields(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'use_head': use_head,
        'vectors': np.array(vectors, np.float32),
        'width': width,
        'height': height,
        'length': length,
        'head_size': head_size,
        'colors': np.array(colors, np.uint32),
        'head_color': head_color if head_color is not None else color,
        'origin_color': origin_color if head_color is not None else color
    })


def voxels(voxels, color_map, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5, zmax=.5,
           model_matrix=np.identity(4), width=None, height=None, length=None):
    length, height, width = get_dimensions(np.shape(voxels), length, height, width)

    return Voxels(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'width': width,
        'height': height,
        'length': length,
        'color_map': np.array(color_map, np.float32),
        'voxels': np.array(voxels, np.uint8)
    })


def marching_cubes(scalar_field, level, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5, zmax=.5,
                   model_matrix=np.identity(4), width=None, height=None, length=None, color=_default_color):
    length, height, width = get_dimensions(np.shape(scalar_field), length, height, width)

    return MarchingCubes(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'width': width,
        'height': height,
        'length': length,
        'color': color,
        'level': level,
        'scalar_field': np.array(scalar_field, np.float32)
    })


def mesh(vertices, indices, attribute=[], color_range=[], color_map=[], model_matrix=np.identity(4),
         color=_default_color):
    return Mesh(**{
        'model_matrix': model_matrix,
        'vertices': np.array(vertices, np.float32),
        'indices': np.array(indices, np.uint32),
        'color': color,
        'attribute': np.array(attribute, np.float32),
        'color_range': color_range,
        'color_map': np.array(color_map, np.float32)
    })


def surface(heights, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, model_matrix=np.identity(4), width=None,
            height=None, color=_default_color):
    height, width = get_dimensions(np.shape(heights), height, width)

    return Surface(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax),
        'color': color,
        'width': width,
        'height': height,
        'heights': np.array(heights, np.float32),
    })


def text(text, position=[0, 0, 0], color=_default_color, font_weight=400, font_face='Courier New',
         font_size=68, size=1.0):
    return Text(**{
        'position': position,
        'text': text,
        'color': color,
        'size': size,
        'font_face': font_face,
        'font_size': font_size,
        'font_weight': font_weight
    })


def text2d(text, position=[0, 0, 0], color=_default_color, size=1.0, reference_point='lb'):
    return Text2d(**{
        'position': position,
        'reference_point': reference_point,
        'text': text,
        'size': size,
        'color': color,
    })


def points(positions, colors=[], color=_default_color, model_matrix=np.identity(4), point_size=1.0,
           shader='3dSpecular'):
    return Points(**{
        'model_matrix': get_model_matrix(model_matrix),
        'point_size': point_size,
        'point_positions': np.array(positions, np.float32),
        'point_colors': np.array(colors, np.float32),
        'color': color,
        'shader': shader
    })


def line(positions, xmin=-.5, xmax=.5, ymin=-.5, ymax=.5, zmin=-.5, zmax=.5, model_matrix=np.identity(4),
         width=1, color=_default_color):
    return Line(**{
        'model_matrix': get_model_matrix(model_matrix, xmin, xmax, ymin, ymax, zmin, zmax),
        'color': color,
        'line_width': width,
        'point_positions': np.array(positions, np.float32)
    })


def plot(*args, **kwargs):
    return Plot(*args, **kwargs)
