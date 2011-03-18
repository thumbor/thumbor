import ctypes
from pythonmagickwand import api

# Pixel resolutions
PIXELS_PER_INCH = api.PixelsPerInchResolution
PIXELS_PER_CENTIMETER = api.PixelsPerCentimeterResolution

# Image filters
BESSEL_FILTER = api.BesselFilter
BLACKMAN_FILTER = api.BlackmanFilter
BOX_FILTER = api.BoxFilter
CATROM_FILTER = api.CatromFilter
CUBIC_FILTER = api.CubicFilter
GAUSSIAN_FILTER = api.GaussianFilter
HANNING_FILTER = api.HanningFilter
HERMITE_FILTER = api.HermiteFilter
LANCZOS_FILTER = api.LanczosFilter
MITCHELL_FILTER = api.MitchellFilter
POINT_FILTER = api.PointFilter
QUADRATIC_FILTER = api.QuadraticFilter
SINC_FILTER = api.SincFilter
TRIANGLE_FILTER = api.TriangleFilter

# Color spaces
CMYK_COLORSPACE = api.CMYKColorspace
CMY_COLORSPACE = api.CMYColorspace
OHTA_COLORSPACE = api.OHTAColorspace
LAB_COLORSPACE = api.LabColorspace
HWB_COLORSPACE = api.HWBColorspace
REC601YCBCR_COLORSPACE = api.Rec601YCbCrColorspace
REC709YCBCR_COLORSPACE = api.Rec709YCbCrColorspace
YIQ_COLORSPACE = api.YIQColorspace
TRANSPARENT_COLORSPACE = api.TransparentColorspace
YUV_COLORSPACE = api.YUVColorspace
YCC_COLORSPACE = api.YCCColorspace
SRGB_COLORSPACE = api.sRGBColorspace
HSL_COLORSPACE = api.HSLColorspace
REC601LUMA_COLORSPACE = api.Rec601LumaColorspace
HSB_COLORSPACE = api.HSBColorspace
REC709LUMA_COLORSPACE = api.Rec709LumaColorspace
GRAY_COLORSPACE = api.GRAYColorspace
LOG_COLORSPACE = api.LogColorspace
XYZ_COLORSPACE = api.XYZColorspace
YCBCR_COLORSPACE = api.YCbCrColorspace
RGB_COLORSPACE = api.RGBColorspace
YPBPR_COLORSPACE = api.YPbPrColorspace

# Channels
RED_CHANNEL = api.RedChannel
CYAN_CHANNEL = api.CyanChannel
GREEN_CHANNEL = api.GreenChannel
MAGENTA_CHANNEL = api.MagentaChannel
BLUE_CHANNEL = api.BlueChannel
YELLOW_CHANNEL = api.YellowChannel
ALPHA_CHANNEL = api.AlphaChannel
OPACITY_CHANNEL = api.OpacityChannel
BLACK_CHANNEL = api.BlackChannel
INDEX_CHANNEL = api.IndexChannel
ALL_CHANNELS = api.AllChannels

# Compression types
LOSSLESS_JPEG_COMPRESSION = api.LosslessJPEGCompression
JPEG_COMPRESSION = api.JPEGCompression
NO_COMPRESSION = api.NoCompression
JPEG2000_COMPRESSION = api.JPEG2000Compression
RLE_COMPRESSION = api.RLECompression
GROUP4_COMPRESSION = api.Group4Compression
FAX_COMPRESSION = api.FaxCompression
UNDEFINED_COMPRESSION = api.UndefinedCompression
BZIP_COMPRESSION = api.BZipCompression
LZW_COMPRESSION = api.LZWCompression
ZIP_COMPRESSION = api.ZipCompression

# Composite operations
MINUS_COMPOSITE_OP = api.MinusCompositeOp
ADD_COMPOSITE_OP = api.AddCompositeOp
IN_COMPOSITE_OP = api.InCompositeOp
DIFFERENCE_COMPOSITE_OP = api.DifferenceCompositeOp
PLUS_COMPOSITE_OP = api.PlusCompositeOp
BUMPMAP_COMPOSITE_OP = api.BumpmapCompositeOp
ATOP_COMPOSITE_OP = api.AtopCompositeOp
XOR_COMPOSITE_OP = api.XorCompositeOp
SUBTRACT_COMPOSITE_OP = api.SubtractCompositeOp
OUT_COMPOSITE_OP = api.OutCompositeOp
COPY_COMPOSITE_OP = api.CopyCompositeOp
DISPLACE_COMPOSITE_OP = api.DisplaceCompositeOp
OVER_COMPOSITE_OP = api.OverCompositeOp

# Evaluate operators
MAX_OPERATOR = api.MaxEvaluateOperator
MIN_OPERATOR = api.MinEvaluateOperator
MULTIPLY_OPERATOR = api.MultiplyEvaluateOperator
SET_OPERATOR = api.SetEvaluateOperator
XOR_OPERATOR = api.XorEvaluateOperator
AND_OPERATOR = api.AndEvaluateOperator
ADD_OPERATOR = api.AddEvaluateOperator
LEFT_SHIFT_OPERATOR = api.LeftShiftEvaluateOperator
RIGHT_SHIFT_OPERATOR = api.RightShiftEvaluateOperator
SUBTRACT_OPERATOR = api.SubtractEvaluateOperator
OR_OPERATOR = api.OrEvaluateOperator
DIVIDE_OPERATOR = api.DivideEvaluateOperator

def _check_wand_error(wand, func):
    if not func:
        severity = api.ExceptionType()
        description = api.MagickGetException(wand, severity)
        raise Exception(description)

class MagickWand(object):

    def __init__(self, image=None):
        self._wand = api.NewMagickWand()

        if hasattr(image, 'read'):
            c = image.read()
            self._check_wand_error(api.MagickReadImageBlob(self._wand, c, len(c)))

    def __del__(self):
        if self._wand:
            self._wand = api.DestroyMagickWand(self._wand)

    def _check_wand_error(self, func):
        _check_wand_error(self._wand, func)

    def _get_size(self):
        x = y = ctypes.c_ulong()
        self._check_wand_error(api.MagickGetSize(self._wand, x, y))
        return (x.value, y.value)

    def _set_size(self, value):
        self._check_wand_error(api.MagickSetSize(self._wand, value[0], value[1]))

    size = property(_get_size, _set_size, None, 'A tuple containing the size associated with the magick wand.')
