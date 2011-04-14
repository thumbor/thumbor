#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

#from ctypes import *
from ctypes import c_char_p, CDLL, c_wchar_p, c_int, Structure, POINTER
from ctypes import c_uint, c_double, c_ulong, c_long, c_ubyte, c_ushort
from ctypes import c_void_p, c_char, CFUNCTYPE, c_ulonglong, c_longlong
from ctypes.util import find_library

from tornado.options import options

STRING = c_char_p

def find_wand(path):
    try:
        return find_library(path)
    except:
        pass

# Mac OS user may have installed ImageMagick via Fink
wand_lib = None
for path in options.MAGICKWAND_PATH + ['Wand', '/usr/local/lib/libWand', '/sw/lib/libWand', '/opt/local/lib/libWand', '/usr/local/lib/libMagickWand']:
    wand_lib = find_library(path)
    if wand_lib:
        break

if not wand_lib:
    raise ImportError('Cannot find ImageMagick MagickWand library.')

_lib = CDLL(wand_lib)

WSTRING = c_wchar_p


BesselFilter = 14
CompareAnyLayer = 2
OverlayCompositeOp = 41
X11Event = 32768
MagickQuantumFormatOptions = 37
AllValues = 2147483647
OpacityQuantum = 13
UndefinedTransmitType = 0
CMYKColorspace = 12
LosslessJPEGCompression = 7
__GCONV_NOCONV = 1
ActivateAlphaChannel = 1
MagickStorageOptions = 40
DstInCompositeOp = 23
RoundJoin = 2
RollPreview = 3
OpacityChannel = 8
TopLeftOrientation = 1
LongPixel = 5
MaxEvaluateOperator = 5
UndefinedDistortion = 0
__GCONV_NOMEM = 3
LeftBottomOrientation = 8
UndefinedQuantumFormat = 0
NonZeroRule = 2
__GCONV_FULL_OUTPUT = 5
BicubicInterpolatePixel = 2
QuadraticFilter = 9
DiskResource = 2
MagickVirtualPixelOptions = 44
UndefinedColorspace = 0
StreamFatalError = 740
IndexAlphaQuantum = 10
ReplaceCompositeOp = 43
ChangeMaskCompositeOp = 6
OHTAColorspace = 4
HeightValue = 8
ImageFatalError = 765
LabColorspace = 5
UltraExpandedStretch = 9
EdgeVirtualPixelMethod = 4
NormalStretch = 1
ShortPixel = 7
SetAlphaChannel = 4
ArcDistortion = 3
AffineProjectionDistortion = 2
__codecvt_partial = 1
MultiplicativeGaussianNoise = 3
UndefinedSpread = 0
EncoderThreadSupport = 2
UndefinedStretch = 0
DstAtopCompositeOp = 21
TypeFatalError = 705
WarningException = 300
MagickImageFilterModule = 1
MinEvaluateOperator = 6
TrueColorType = 6
UndefinedTimerState = 0
MagickDelegateOptions = 48
UndefinedGravity = 0
SaturationIntent = 1
OptimizePlusLayer = 8
RoundRectanglePrimitive = 4
OptionFatalError = 710
ResourceLimitWarning = 300
ConcatenateMode = 3
MagickMetricOptions = 29
FileTransmitType = 1
MagentaQuantum = 12
ScreenCompositeOp = 45
UndefinedClass = 0
UndefinedRule = 0
UserEvent = 8192
SemiExpandedStretch = 6
UndefinedPixel = 0
HWBColorspace = 16
EvenOddRule = 1
UndefinedJoin = 0
AnnotateEvent = 2
TailPath = 4
PixelsPerCentimeterResolution = 2
AnyStretch = 10
ImpulseNoise = 4
MagickComposeOptions = 8
TopRightOrientation = 2
IntegerPixel = 4
MagickMimeOptions = 51
GrayscaleMatteType = 3
ImplodePreview = 25
CopyGreenCompositeOp = 15
PathPrimitive = 15
PeakSignalToNoiseRatioMetric = 6
UndefinedCompliance = 0
TriangleFilter = 3
LineInterlace = 2
GaussianFilter = 8
StaticGravity = 10
ShadePreview = 21
MosaicLayer = 15
CMYKAQuantum = 4
UndefinedPrimitive = 0
FilterInterpolatePixel = 4
PolygonPrimitive = 9
RGBAQuantum = 15
ResourceEvent = 2048
FloatingPointQuantumFormat = 1
MagickLineJoinOptions = 26
DisposeLayer = 5
RedQuantum = 14
MissingDelegateWarning = 320
XServerError = 480
CopyCyanCompositeOp = 14
MagickChannelOptions = 3
Rec601YCbCrColorspace = 18
JPEGCompression = 5
MultiplyEvaluateOperator = 7
DefaultChannels = 247
BlobError = 435
ForgetGravity = 0
__codecvt_ok = 0
SquareCap = 3
SubimagePath = 7
MagickPreviewOptions = 35
RandomNoise = 7
__codecvt_error = 2
UndefinedChannel = 0
MeanSquaredErrorMetric = 4
UndefinedInterpolatePixel = 0
CubicFilter = 10
CorruptImageFatalError = 725
RemoveDupsLayer = 10
ObliqueStyle = 3
MagickResourceOptions = 39
CatromFilter = 11
CompareClearLayer = 3
ResetMethod = 5
UniformNoise = 1
UndefinedOrientation = 0
RGBOQuantum = 16
SrcInCompositeOp = 49
ExceptionEvent = 256
MagickLayerOptions = 24
FileResource = 3
FloatPixel = 3
UndefinedQuantum = 0
EastGravity = 6
UndefinedResolution = 0
DullPreview = 9
OverlineDecoration = 3
CoderWarning = 350
MagickDisposeOptions = 13
Rec709YCbCrColorspace = 20
ConstantVirtualPixelMethod = 2
DstOutCompositeOp = 24
SetEvaluateOperator = 10
AbsoluteIntent = 3
AddNoisePreview = 14
DitherVirtualPixelMethod = 3
ParzenFilter = 18
AllCompliance = 2147483647
MagickLocaleOptions = 52
HuePreview = 4
HardLightCompositeOp = 30
__GCONV_EMPTY_INPUT = 4
BlobTransmitType = 2
ImageInfoRegistryType = 2
UndefinedInterlace = 0
LSBEndian = 1
ItalicStyle = 2
UserSpace = 1
BlendCompositeOp = 4
GrayAlphaQuantum = 7
__GCONV_IS_LAST = 1
FlattenLayer = 14
PNGInterlace = 7
DirectClass = 1
XValue = 1
MagickMethodOptions = 30
BoxFilter = 2
PercentValue = 4096
AreaResource = 1
WidthValue = 4
UndefinedEvents = 0
DeactivateAlphaChannel = 2
UltraCondensedStretch = 2
ModuleError = 455
CacheWarning = 345
XNegative = 32
UnsignedQuantumFormat = 3
MagickInterpolateOptions = 23
YIQColorspace = 9
YellowQuantum = 18
SrcOverCompositeOp = 51
DoublePixel = 2
WavePreview = 26
RedChannel = 1
MagickClassOptions = 4
ExclusionCompositeOp = 29
GaussianNoise = 2
ReadMode = 0
QuantumPixel = 6
MonitorError = 485
PointPrimitive = 1
MagickDecorateOptions = 12
CMYColorspace = 22
CopyRedCompositeOp = 18
XorEvaluateOperator = 12
LeftAlign = 1
UndefinedIntent = 0
MinusCompositeOp = 36
MagickLogOptions = 53
MatteChannel = 8
AverageInterpolatePixel = 1
AddCompositeOp = 2
__GCONV_OK = 0
BlurPreview = 16
CyanChannel = 1
PeakAbsoluteErrorMetric = 5
TrueColorMatteType = 7
AndEvaluateOperator = 2
FileOpenFatalError = 730
HeadPath = 3
InCompositeOp = 32
HanningFilter = 5
AlphaQuantum = 1
PlaneInterlace = 3
MagickNoiseOptions = 33
SincFilter = 15
CyanQuantum = 6
DifferenceCompositeOp = 26
MagickStyleOptions = 42
YValue = 2
DrawEvent = 128
MagickMogrifyOptions = 32
LessValue = 16384
ColorPrimitive = 11
UndefinedMagickLayerMethod = 0
RaisePreview = 22
ChiValue = 16
NoCompression = 1
BartlettFilter = 21
CenterGravity = 5
ColorBurnCompositeOp = 8
JPEG2000Compression = 6
ModuleFatalError = 755
ThresholdCompositeOp = 53
UndefinedCap = 0
NoInterlace = 1
MissingDelegateFatalError = 720
SplineInterpolatePixel = 8
MagickThresholdOptions = 56
MaskVirtualPixelMethod = 9
YellowChannel = 4
DecoderThreadSupport = 1
LaplacianNoise = 5
ImagePrimitive = 14
MagickTrue = 1
AreaValue = 131072
UndefinedRegistryType = 0
MagickResolutionOptions = 38
RelativeIntent = 4
CopyBlueCompositeOp = 12
LinearLightCompositeOp = 34
EllipsePrimitive = 6
BilinearInterpolatePixel = 3
MergeLayer = 13
PointMethod = 1
SouthWestGravity = 7
UnrecognizedDispose = 0
PolylinePrimitive = 8
GreenQuantum = 9
DissolveCompositeOp = 28
__GCONV_INCOMPLETE_INPUT = 7
TransparentColorspace = 3
MinimumValue = 65536
TextPrimitive = 13
WandFatalError = 770
WandError = 470
RLECompression = 9
XServerFatalError = 780
DivideCompositeOp = 55
AddEvaluateOperator = 1
PaletteBilevelMatteType = 11
MagickDataTypeOptions = 10
SouthGravity = 8
ThresholdPreview = 17
ClearCompositeOp = 7
AllChannels = 255
LuminizeCompositeOp = 35
NoCompositeOp = 1
QuantizePreview = 11
OptionError = 410
ColorSeparationType = 8
MeanErrorPerPixelMetric = 3
OptimizeTransLayer = 9
WandEvent = 16384
MagickIntentOptions = 21
UndefinedMode = 0
ObjectBoundingBox = 3
UndefinedPreview = 0
KaiserFilter = 16
PartitionInterlace = 4
BohmanFilter = 20
DecimalValue = 262144
PreviousDispose = 3
MagickEvaluateOptions = 16
MemoryResource = 5
YUVColorspace = 11
YNegative = 64
MagickFillRuleOptions = 17
MagickPath = 1
ExtraExpandedStretch = 8
RegistryError = 490
ScaleRotateTranslateDistortion = 7
MiterJoin = 1
BrightnessPreview = 6
SharpenPreview = 15
MagickUndefinedOptions = -1
ColorDodgeCompositeOp = 9
BasePath = 5
RightAlign = 3
MagickAlignOptions = 0
ExtensionPath = 6
CacheError = 445
UndefinedFilter = 0
StreamError = 440
CanonicalPath = 8
BackgroundDispose = 2
ResourceLimitFatalError = 700
StoppedTimerState = 1
NoValue = 0
LeftShiftEvaluateOperator = 4
SentinelFilter = 22
BlueQuantum = 3
PoissonNoise = 6
MagentaChannel = 2
PlusCompositeOp = 42
SwirlPreview = 24
MagickListOptions = 27
BackgroundVirtualPixelMethod = 1
YCCColorspace = 8
MonitorFatalError = 785
MitchellFilter = 12
DelegateWarning = 315
sRGBColorspace = 13
PseudoClass = 2
RegistryWarning = 390
CoderEvent = 16
MagickCompressOptions = 9
UndefinedPath = 0
EdgeDetectPreview = 18
DrawWarning = 360
GrayChannel = 1
MagickDebugOptions = 11
BilinearDistortion = 4
OptimizeLayer = 6
WandWarning = 370
MagickModuleOptions = 55
RunningTimerState = 2
CompositeLayer = 12
FatalErrorException = 700
ModuleWarning = 355
BlackChannel = 32
XPMCompliance = 4
OptionWarning = 310
AbsoluteErrorMetric = 1
DelegateError = 415
CorruptImageWarning = 325
Group4Compression = 4
JPEGInterlace = 6
MagickColorOptions = 46
__GCONV_ILLEGAL_DESCRIPTOR = 8
RightTopOrientation = 6
PerceptualIntent = 2
LagrangeFilter = 19
WestGravity = 4
UndefinedType = 0
UnderlineDecoration = 2
AnyStyle = 4
FaxCompression = 3
CacheFatalError = 745
CoderError = 450
ColorSeparationMatteType = 9
IOMode = 2
BumpmapCompositeOp = 5
CacheEvent = 8
DrawFatalError = 760
IndexQuantum = 11
SaturateCompositeOp = 44
SignedQuantumFormat = 2
MeanAbsoluteErrorMetric = 2
RepeatSpread = 3
RegistryFatalError = 790
BottomRightOrientation = 3
NoDecoration = 1
ConfigureWarning = 395
UndefinedNoise = 0
MagickFilterOptions = 18
HSLColorspace = 15
RadialGradient = 2
MagickConfigureOptions = 47
GreenChannel = 2
MagickEndianOptions = 15
PerspectiveProjectionDistortion = 6
PixelsPerInchResolution = 1
RightShiftEvaluateOperator = 9
RectanglePrimitive = 3
AlphaChannel = 8
MagickPrimitiveOptions = 36
MagickLogEventOptions = 28
ImageRegistryType = 1
ButtCap = 1
BlackmanFilter = 7
PointFilter = 1
GrayVirtualPixelMethod = 11
AtopCompositeOp = 3
__GCONV_IGNORE_ERRORS = 2
CompareOverlayLayer = 4
GrayQuantum = 8
MagickStretchOptions = 41
StreamWarning = 340
ColorizeCompositeOp = 10
TypeWarning = 305
SoftLightCompositeOp = 46
StreamTransmitType = 3
MagickFalse = 0
LightenCompositeOp = 33
ErrorException = 400
XorCompositeOp = 54
MagickColorspaceOptions = 6
Rec601LumaColorspace = 17
PerspectiveDistortion = 5
BevelJoin = 3
ConfigureFatalError = 795
ArcPrimitive = 5
CorruptImageError = 425
BottomLeftOrientation = 4
BlackVirtualPixelMethod = 10
CopyBlackCompositeOp = 11
TransformEvent = 4096
SpreadPreview = 19
TileVirtualPixelMethod = 7
__GCONV_ILLEGAL_INPUT = 6
SrcCompositeOp = 48
CMYKQuantum = 5
FileOpenWarning = 330
DstCompositeOp = 22
ModuleEvent = 1024
MagickImageCoderModule = 0
PaletteType = 4
SrcAtopCompositeOp = 47
CondensedStretch = 4
RightBottomOrientation = 7
MagickFontsOptions = 19
HSBColorspace = 14
ResetAlphaChannel = 3
Rec709LumaColorspace = 19
ReduceNoisePreview = 13
ReflectSpread = 2
CopyMagentaCompositeOp = 16
SpiffPreview = 8
NormalStyle = 1
ShearPreview = 2
MagickClipPathOptions = 5
__GCONV_INTERNAL_ERROR = 9
UndefinedCompositeOp = 0
IndexChannel = 32
ChiNegative = 128
CirclePrimitive = 7
UndefinedLayer = 0
UndefinedDecoration = 0
DrawError = 460
RhoValue = 4
GRAYColorspace = 2
UndefinedReference = 0
WriteMode = 1
XiValue = 2
XiNegative = 32
MirrorVirtualPixelMethod = 5
UndefinedStyle = 0
RGBQuantum = 17
SrcOutCompositeOp = 50
MagickModeOptions = 31
OilPaintPreview = 27
TraceEvent = 1
SubtractCompositeOp = 52
LogColorspace = 21
SubtractEvaluateOperator = 11
ResourceLimitError = 400
FileOpenError = 430
NoneDispose = 1
LeftTopOrientation = 5
RoundCap = 2
PaletteMatteType = 5
RotatePreview = 1
GrayscalePreview = 10
NoCompliance = 0
HueCompositeOp = 31
MagickCoderOptions = 45
UndefinedEndian = 0
CharPixel = 1
GrayscaleType = 2
HermiteFilter = 4
CoderFatalError = 750
StringRegistryType = 3
CopyYellowCompositeOp = 19
MSBEndian = 2
UserSpaceOnUse = 2
WelshFilter = 17
ImageError = 465
RandomVirtualPixelMethod = 6
AspectValue = 8192
BezierPrimitive = 10
ExtraCondensedStretch = 3
XYZColorspace = 6
UndefinedException = 0
MonitorWarning = 385
UndefinedMetric = 0
PsiNegative = 64
JPEGPreview = 29
MagickInterlaceOptions = 22
CopyOpacityCompositeOp = 17
ExpandedStretch = 7
OrEvaluateOperator = 8
SegmentPreview = 23
OutCompositeOp = 39
MagickCommandOptions = 7
NoEvents = 0
UndefinedGradient = 0
MagickBooleanOptions = 2
ReplaceMethod = 2
CenterAlign = 2
MeshInterpolatePixel = 6
MultiplyCompositeOp = 38
MagickAlphaOptions = 1
__codecvt_noconv = 3
SVGCompliance = 1
BlobFatalError = 735
MagickFormatOptions = 50
TypeError = 405
ConfigureEvent = 32
GammaPreview = 7
LocaleEvent = 512
NorthWestGravity = 1
CopyCompositeOp = 13
UndefinedAlign = 0
UndefinedEvaluateOperator = 0
ModulateCompositeOp = 37
DelegateFatalError = 715
DivideEvaluateOperator = 3
RemoveZeroLayer = 11
BlackQuantum = 2
BlueChannel = 4
PsiValue = 1
LanczosFilter = 13
CoalesceLayer = 1
DisplaceCompositeOp = 27
GIFInterlace = 5
MapResource = 4
GreaterValue = 32768
UndefinedCompression = 0
MattePrimitive = 12
XServerWarning = 380
MagickLineCapOptions = 25
YCbCrColorspace = 7
BZipCompression = 2
MagickDistortOptions = 14
DeprecateEvent = 64
SemiCondensedStretch = 5
WhiteVirtualPixelMethod = 12
CharcoalDrawingPreview = 28
ImageTransmitType = 4
RGBColorspace = 1
BlobWarning = 335
UndefinedVirtualPixelMethod = 0
BlobEvent = 4
LineThroughDecoration = 4
SolarizePreview = 20
PadSpread = 1
DarkenCompositeOp = 20
RootPath = 2
NearestNeighborInterpolatePixel = 7
UndefinedMethod = 0
LZWCompression = 8
BilevelType = 1
SaturationPreview = 5
__GCONV_NODB = 2
FillToBorderMethod = 4
RootMeanSquaredErrorMetric = 7
UndefinedResource = 0
NorthGravity = 2
FloodfillMethod = 3
MagickOrientationOptions = 34
X11Compliance = 2
AllEvents = 2147483647
MagickTypeOptions = 43
FrameMode = 1
NorthEastGravity = 3
UndefinedPathUnits = 0
SigmaValue = 8
UndefinedAlphaChannel = 0
GradientReference = 1
MissingDelegateError = 420
YPbPrColorspace = 10
MagickGravityOptions = 20
LinearGradient = 1
DespecklePreview = 12
ConfigureError = 495
DstOverCompositeOp = 25
AffineDistortion = 1
LinePrimitive = 2
UnframeMode = 2
MagickMagicOptions = 54
TransparentVirtualPixelMethod = 8
NoThreadSupport = 0
OverCompositeOp = 40
OptimizeType = 10
UndefinedDispose = 0
MagickFontOptions = 49
ZipCompression = 10
SouthEastGravity = 9
IntegerInterpolatePixel = 5
ImageWarning = 365
HammingFilter = 6
OptimizeImageLayer = 7

# values for enumeration 'MagickBooleanType'
MagickBooleanType = c_int # enum
class _ImageInfo(Structure):
    pass
ImageInfo = _ImageInfo
class _Image(Structure):
    pass
Image = _Image
AnimateImages = _lib.AnimateImages
AnimateImages.restype = MagickBooleanType
AnimateImages.argtypes = [POINTER(ImageInfo), POINTER(Image)]
class _DrawInfo(Structure):
    pass
DrawInfo = _DrawInfo
AnnotateImage = _lib.AnnotateImage
AnnotateImage.restype = MagickBooleanType
AnnotateImage.argtypes = [POINTER(Image), POINTER(DrawInfo)]
class _TypeMetric(Structure):
    pass
TypeMetric = _TypeMetric
GetMultilineTypeMetrics = _lib.GetMultilineTypeMetrics
GetMultilineTypeMetrics.restype = MagickBooleanType
GetMultilineTypeMetrics.argtypes = [POINTER(Image), POINTER(DrawInfo), POINTER(TypeMetric)]
GetTypeMetrics = _lib.GetTypeMetrics
GetTypeMetrics.restype = MagickBooleanType
GetTypeMetrics.argtypes = [POINTER(Image), POINTER(DrawInfo), POINTER(TypeMetric)]

# values for enumeration 'MapMode'
MapMode = c_int # enum
class _IO_FILE(Structure):
    pass
FILE = _IO_FILE
GetBlobFileHandle = _lib.GetBlobFileHandle
GetBlobFileHandle.restype = POINTER(FILE)
GetBlobFileHandle.argtypes = [POINTER(Image)]
size_t = c_uint
class _ExceptionInfo(Structure):
    pass
ExceptionInfo = _ExceptionInfo
BlobToImage = _lib.BlobToImage
BlobToImage.restype = POINTER(Image)
BlobToImage.argtypes = [POINTER(ImageInfo), c_void_p, size_t, POINTER(ExceptionInfo)]
PingBlob = _lib.PingBlob
PingBlob.restype = POINTER(Image)
PingBlob.argtypes = [POINTER(ImageInfo), c_void_p, size_t, POINTER(ExceptionInfo)]
BlobToFile = _lib.BlobToFile
BlobToFile.restype = MagickBooleanType
BlobToFile.argtypes = [STRING, c_void_p, size_t, POINTER(ExceptionInfo)]
GetBlobError = _lib.GetBlobError
GetBlobError.restype = MagickBooleanType
GetBlobError.argtypes = [POINTER(Image)]
ImageToFile = _lib.ImageToFile
ImageToFile.restype = MagickBooleanType
ImageToFile.argtypes = [POINTER(Image), STRING, POINTER(ExceptionInfo)]
IsBlobExempt = _lib.IsBlobExempt
IsBlobExempt.restype = MagickBooleanType
IsBlobExempt.argtypes = [POINTER(Image)]
IsBlobSeekable = _lib.IsBlobSeekable
IsBlobSeekable.restype = MagickBooleanType
IsBlobSeekable.argtypes = [POINTER(Image)]
IsBlobTemporary = _lib.IsBlobTemporary
IsBlobTemporary.restype = MagickBooleanType
IsBlobTemporary.argtypes = [POINTER(Image)]
MagickSizeType = c_ulonglong
GetBlobSize = _lib.GetBlobSize
GetBlobSize.restype = MagickSizeType
GetBlobSize.argtypes = [POINTER(Image)]
StreamHandler = CFUNCTYPE(size_t, POINTER(Image), c_void_p, size_t)
GetBlobStreamHandler = _lib.GetBlobStreamHandler
GetBlobStreamHandler.restype = StreamHandler
GetBlobStreamHandler.argtypes = [POINTER(Image)]
FileToBlob = _lib.FileToBlob
FileToBlob.restype = POINTER(c_ubyte)
FileToBlob.argtypes = [STRING, size_t, POINTER(size_t), POINTER(ExceptionInfo)]
GetBlobStreamData = _lib.GetBlobStreamData
GetBlobStreamData.restype = POINTER(c_ubyte)
GetBlobStreamData.argtypes = [POINTER(Image)]
ImageToBlob = _lib.ImageToBlob
ImageToBlob.restype = POINTER(c_ubyte)
ImageToBlob.argtypes = [POINTER(ImageInfo), POINTER(Image), POINTER(size_t), POINTER(ExceptionInfo)]
ImagesToBlob = _lib.ImagesToBlob
ImagesToBlob.restype = POINTER(c_ubyte)
ImagesToBlob.argtypes = [POINTER(ImageInfo), POINTER(Image), POINTER(size_t), POINTER(ExceptionInfo)]
DestroyBlob = _lib.DestroyBlob
DestroyBlob.restype = None
DestroyBlob.argtypes = [POINTER(Image)]
SetBlobExempt = _lib.SetBlobExempt
SetBlobExempt.restype = None
SetBlobExempt.argtypes = [POINTER(Image), MagickBooleanType]

# values for enumeration 'VirtualPixelMethod'
VirtualPixelMethod = c_int # enum
class _ViewInfo(Structure):
    pass
_ViewInfo._fields_ = [
]
ViewInfo = _ViewInfo
Quantum = c_ushort
IndexPacket = Quantum
GetCacheViewIndexes = _lib.GetCacheViewIndexes
GetCacheViewIndexes.restype = POINTER(IndexPacket)
GetCacheViewIndexes.argtypes = [POINTER(ViewInfo)]
SyncCacheView = _lib.SyncCacheView
SyncCacheView.restype = MagickBooleanType
SyncCacheView.argtypes = [POINTER(ViewInfo)]
class _PixelPacket(Structure):
    pass
PixelPacket = _PixelPacket
GetCacheViewPixels = _lib.GetCacheViewPixels
GetCacheViewPixels.restype = POINTER(PixelPacket)
GetCacheViewPixels.argtypes = [POINTER(ViewInfo), c_long, c_long, c_ulong, c_ulong]
#SetCacheView = _lib.SetCacheView
#SetCacheView.restype = POINTER(PixelPacket)
#SetCacheView.argtypes = [POINTER(ViewInfo), c_long, c_long, c_ulong, c_ulong]
CloseCacheView = _lib.CloseCacheView
CloseCacheView.restype = POINTER(ViewInfo)
CloseCacheView.argtypes = [POINTER(ViewInfo)]
OpenCacheView = _lib.OpenCacheView
OpenCacheView.restype = POINTER(ViewInfo)
OpenCacheView.argtypes = [POINTER(Image)]
#AcquireCacheNexus = _lib.AcquireCacheNexus
#AcquireCacheNexus.restype = POINTER(PixelPacket)
#AcquireCacheNexus.argtypes = [POINTER(Image), VirtualPixelMethod, c_long, c_long, c_ulong, c_ulong, c_ulong, POINTER(ExceptionInfo)]
#GetPixelCacheArea = _lib.GetPixelCacheArea
#GetPixelCacheArea.restype = MagickSizeType
#GetPixelCacheArea.argtypes = [POINTER(Image)]
MagickOffsetType = c_longlong
#PersistCache = _lib.PersistCache
#PersistCache.restype = MagickBooleanType
#PersistCache.argtypes = [POINTER(Image), STRING, MagickBooleanType, POINTER(MagickOffsetType), POINTER(ExceptionInfo)]
#SyncCacheNexus = _lib.SyncCacheNexus
#SyncCacheNexus.restype = MagickBooleanType
#SyncCacheNexus.argtypes = [POINTER(Image), c_ulong]
#GetCacheNexus = _lib.GetCacheNexus
#GetCacheNexus.restype = POINTER(PixelPacket)
#GetCacheNexus.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, c_ulong]
#SetCacheNexus = _lib.SetCacheNexus
#SetCacheNexus.restype = POINTER(PixelPacket)
#SetCacheNexus.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, c_ulong]
GetClientPath = _lib.GetClientPath
GetClientPath.restype = STRING
GetClientPath.argtypes = []
GetClientName = _lib.GetClientName
GetClientName.restype = STRING
GetClientName.argtypes = []
SetClientName = _lib.SetClientName
SetClientName.restype = STRING
SetClientName.argtypes = [STRING]
SetClientPath = _lib.SetClientPath
SetClientPath.restype = STRING
SetClientPath.argtypes = [STRING]
class _CoderInfo(Structure):
    pass
_CoderInfo._fields_ = [
    ('path', STRING),
    ('magick', STRING),
    ('name', STRING),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_CoderInfo)),
    ('next', POINTER(_CoderInfo)),
    ('signature', c_ulong),
]
CoderInfo = _CoderInfo
GetCoderList = _lib.GetCoderList
GetCoderList.restype = POINTER(STRING)
GetCoderList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetCoderInfo = _lib.GetCoderInfo
GetCoderInfo.restype = POINTER(CoderInfo)
GetCoderInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetCoderInfoList = _lib.GetCoderInfoList
GetCoderInfoList.restype = POINTER(POINTER(CoderInfo))
GetCoderInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
ListCoderInfo = _lib.ListCoderInfo
ListCoderInfo.restype = MagickBooleanType
ListCoderInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
#DestroyCoderList = _lib.DestroyCoderList
#DestroyCoderList.restype = None
#DestroyCoderList.argtypes = []

# values for enumeration 'ComplianceType'
ComplianceType = c_int # enum
class _ColorInfo(Structure):
    pass
class _MagickPixelPacket(Structure):
    pass

# values for enumeration 'ClassType'
ClassType = c_int # enum

# values for enumeration 'ColorspaceType'
ColorspaceType = c_int # enum
MagickRealType = c_double
_MagickPixelPacket._pack_ = 4
_MagickPixelPacket._fields_ = [
    ('storage_class', ClassType),
    ('colorspace', ColorspaceType),
    ('matte', MagickBooleanType),
    ('fuzz', c_double),
    ('depth', c_ulong),
    ('red', MagickRealType),
    ('green', MagickRealType),
    ('blue', MagickRealType),
    ('opacity', MagickRealType),
    ('index', MagickRealType),
]
MagickPixelPacket = _MagickPixelPacket
_ColorInfo._fields_ = [
    ('path', STRING),
    ('name', STRING),
    ('compliance', ComplianceType),
    ('color', MagickPixelPacket),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_ColorInfo)),
    ('next', POINTER(_ColorInfo)),
    ('signature', c_ulong),
]
ColorInfo = _ColorInfo
class _ColorPacket(Structure):
    pass
_PixelPacket._fields_ = [
    ('blue', Quantum),
    ('green', Quantum),
    ('red', Quantum),
    ('opacity', Quantum),
]
_ColorPacket._pack_ = 4
_ColorPacket._fields_ = [
    ('pixel', PixelPacket),
    ('index', IndexPacket),
    ('count', MagickSizeType),
]
ColorPacket = _ColorPacket
class _ErrorInfo(Structure):
    pass
_ErrorInfo._pack_ = 4
_ErrorInfo._fields_ = [
    ('mean_error_per_pixel', c_double),
    ('normalized_mean_error', c_double),
    ('normalized_maximum_error', c_double),
]
ErrorInfo = _ErrorInfo
GetColorList = _lib.GetColorList
GetColorList.restype = POINTER(STRING)
GetColorList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetColorInfo = _lib.GetColorInfo
GetColorInfo.restype = POINTER(ColorInfo)
GetColorInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetColorInfoList = _lib.GetColorInfoList
GetColorInfoList.restype = POINTER(POINTER(ColorInfo))
GetColorInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetImageHistogram = _lib.GetImageHistogram
GetImageHistogram.restype = POINTER(ColorPacket)
GetImageHistogram.argtypes = [POINTER(Image), POINTER(c_ulong), POINTER(ExceptionInfo)]
IsGrayImage = _lib.IsGrayImage
IsGrayImage.restype = MagickBooleanType
IsGrayImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
IsMagickColorSimilar = _lib.IsMagickColorSimilar
IsMagickColorSimilar.restype = MagickBooleanType
IsMagickColorSimilar.argtypes = [POINTER(MagickPixelPacket), POINTER(MagickPixelPacket)]
IsMonochromeImage = _lib.IsMonochromeImage
IsMonochromeImage.restype = MagickBooleanType
IsMonochromeImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
IsOpaqueImage = _lib.IsOpaqueImage
IsOpaqueImage.restype = MagickBooleanType
IsOpaqueImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
IsPaletteImage = _lib.IsPaletteImage
IsPaletteImage.restype = MagickBooleanType
IsPaletteImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
ListColorInfo = _lib.ListColorInfo
ListColorInfo.restype = MagickBooleanType
ListColorInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
QueryColorDatabase = _lib.QueryColorDatabase
QueryColorDatabase.restype = MagickBooleanType
QueryColorDatabase.argtypes = [STRING, POINTER(PixelPacket), POINTER(ExceptionInfo)]
QueryColorname = _lib.QueryColorname
QueryColorname.restype = MagickBooleanType
QueryColorname.argtypes = [POINTER(Image), POINTER(PixelPacket), ComplianceType, STRING, POINTER(ExceptionInfo)]
QueryMagickColor = _lib.QueryMagickColor
QueryMagickColor.restype = MagickBooleanType
QueryMagickColor.argtypes = [STRING, POINTER(MagickPixelPacket), POINTER(ExceptionInfo)]
GetNumberColors = _lib.GetNumberColors
GetNumberColors.restype = c_ulong
GetNumberColors.argtypes = [POINTER(Image), POINTER(FILE), POINTER(ExceptionInfo)]
#DestroyColorList = _lib.DestroyColorList
#DestroyColorList.restype = None
#DestroyColorList.argtypes = []
GetColorTuple = _lib.GetColorTuple
GetColorTuple.restype = None
GetColorTuple.argtypes = [POINTER(MagickPixelPacket), MagickBooleanType, STRING]
RGBTransformImage = _lib.RGBTransformImage
RGBTransformImage.restype = MagickBooleanType
RGBTransformImage.argtypes = [POINTER(Image), ColorspaceType]
SetImageColorspace = _lib.SetImageColorspace
SetImageColorspace.restype = MagickBooleanType
SetImageColorspace.argtypes = [POINTER(Image), ColorspaceType]
TransformRGBImage = _lib.TransformRGBImage
TransformRGBImage.restype = MagickBooleanType
TransformRGBImage.argtypes = [POINTER(Image), ColorspaceType]

# values for enumeration 'MetricType'
MetricType = c_int # enum

# values for enumeration 'ChannelType'
ChannelType = c_int # enum
CompareImageChannels = _lib.CompareImageChannels
CompareImageChannels.restype = POINTER(Image)
CompareImageChannels.argtypes = [POINTER(Image), POINTER(Image), ChannelType, MetricType, POINTER(c_double), POINTER(ExceptionInfo)]
CompareImages = _lib.CompareImages
CompareImages.restype = POINTER(Image)
CompareImages.argtypes = [POINTER(Image), POINTER(Image), MetricType, POINTER(c_double), POINTER(ExceptionInfo)]
GetImageChannelDistortion = _lib.GetImageChannelDistortion
GetImageChannelDistortion.restype = MagickBooleanType
GetImageChannelDistortion.argtypes = [POINTER(Image), POINTER(Image), ChannelType, MetricType, POINTER(c_double), POINTER(ExceptionInfo)]
GetImageDistortion = _lib.GetImageDistortion
GetImageDistortion.restype = MagickBooleanType
GetImageDistortion.argtypes = [POINTER(Image), POINTER(Image), MetricType, POINTER(c_double), POINTER(ExceptionInfo)]
IsImagesEqual = _lib.IsImagesEqual
IsImagesEqual.restype = MagickBooleanType
IsImagesEqual.argtypes = [POINTER(Image), POINTER(Image)]

# values for enumeration 'CompositeOperator'
CompositeOperator = c_int # enum
CompositeImage = _lib.CompositeImage
CompositeImage.restype = MagickBooleanType
CompositeImage.argtypes = [POINTER(Image), CompositeOperator, POINTER(Image), c_long, c_long]

# values for enumeration 'CompressionType'
CompressionType = c_int # enum
class _Ascii85Info(Structure):
    pass
_Ascii85Info._fields_ = [
]
Ascii85Info = _Ascii85Info
HuffmanDecodeImage = _lib.HuffmanDecodeImage
HuffmanDecodeImage.restype = MagickBooleanType
HuffmanDecodeImage.argtypes = [POINTER(Image)]
HuffmanEncodeImage = _lib.HuffmanEncodeImage
HuffmanEncodeImage.restype = MagickBooleanType
HuffmanEncodeImage.argtypes = [POINTER(ImageInfo), POINTER(Image)]
#Huffman2DEncodeImage = _lib.Huffman2DEncodeImage
#Huffman2DEncodeImage.restype = MagickBooleanType
#Huffman2DEncodeImage.argtypes = [POINTER(ImageInfo), POINTER(Image)]
LZWEncodeImage = _lib.LZWEncodeImage
LZWEncodeImage.restype = MagickBooleanType
LZWEncodeImage.argtypes = [POINTER(Image), size_t, POINTER(c_ubyte)]
PackbitsEncodeImage = _lib.PackbitsEncodeImage
PackbitsEncodeImage.restype = MagickBooleanType
PackbitsEncodeImage.argtypes = [POINTER(Image), size_t, POINTER(c_ubyte)]
ZLIBEncodeImage = _lib.ZLIBEncodeImage
ZLIBEncodeImage.restype = MagickBooleanType
ZLIBEncodeImage.argtypes = [POINTER(Image), size_t, POINTER(c_ubyte)]
Ascii85Encode = _lib.Ascii85Encode
Ascii85Encode.restype = None
Ascii85Encode.argtypes = [POINTER(Image), c_ubyte]
Ascii85Flush = _lib.Ascii85Flush
Ascii85Flush.restype = None
Ascii85Flush.argtypes = [POINTER(Image)]
Ascii85Initialize = _lib.Ascii85Initialize
Ascii85Initialize.restype = None
Ascii85Initialize.argtypes = [POINTER(Image)]
class _ConfigureInfo(Structure):
    pass
_ConfigureInfo._fields_ = [
    ('path', STRING),
    ('name', STRING),
    ('value', STRING),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_ConfigureInfo)),
    ('next', POINTER(_ConfigureInfo)),
    ('signature', c_ulong),
]
ConfigureInfo = _ConfigureInfo
GetConfigureList = _lib.GetConfigureList
GetConfigureList.restype = POINTER(STRING)
GetConfigureList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetConfigureValue = _lib.GetConfigureValue
GetConfigureValue.restype = STRING
GetConfigureValue.argtypes = [POINTER(ConfigureInfo)]
GetConfigureInfo = _lib.GetConfigureInfo
GetConfigureInfo.restype = POINTER(ConfigureInfo)
GetConfigureInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetConfigureInfoList = _lib.GetConfigureInfoList
GetConfigureInfoList.restype = POINTER(POINTER(ConfigureInfo))
GetConfigureInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
class _LinkedListInfo(Structure):
    pass
LinkedListInfo = _LinkedListInfo
DestroyConfigureOptions = _lib.DestroyConfigureOptions
DestroyConfigureOptions.restype = POINTER(LinkedListInfo)
DestroyConfigureOptions.argtypes = [POINTER(LinkedListInfo)]
GetConfigurePaths = _lib.GetConfigurePaths
GetConfigurePaths.restype = POINTER(LinkedListInfo)
GetConfigurePaths.argtypes = [STRING, POINTER(ExceptionInfo)]
GetConfigureOptions = _lib.GetConfigureOptions
GetConfigureOptions.restype = POINTER(LinkedListInfo)
GetConfigureOptions.argtypes = [STRING, POINTER(ExceptionInfo)]
ListConfigureInfo = _lib.ListConfigureInfo
ListConfigureInfo.restype = MagickBooleanType
ListConfigureInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
#DestroyConfigureList = _lib.DestroyConfigureList
#DestroyConfigureList.restype = None
#DestroyConfigureList.argtypes = []

# values for enumeration 'StorageType'
StorageType = c_int # enum
ConstituteImage = _lib.ConstituteImage
ConstituteImage.restype = POINTER(Image)
ConstituteImage.argtypes = [c_ulong, c_ulong, STRING, StorageType, c_void_p, POINTER(ExceptionInfo)]
PingImage = _lib.PingImage
PingImage.restype = POINTER(Image)
PingImage.argtypes = [POINTER(ImageInfo), POINTER(ExceptionInfo)]
ReadImage = _lib.ReadImage
ReadImage.restype = POINTER(Image)
ReadImage.argtypes = [POINTER(ImageInfo), POINTER(ExceptionInfo)]
ReadInlineImage = _lib.ReadInlineImage
ReadInlineImage.restype = POINTER(Image)
ReadInlineImage.argtypes = [POINTER(ImageInfo), STRING, POINTER(ExceptionInfo)]
WriteImage = _lib.WriteImage
WriteImage.restype = MagickBooleanType
WriteImage.argtypes = [POINTER(ImageInfo), POINTER(Image)]
WriteImages = _lib.WriteImages
WriteImages.restype = MagickBooleanType
WriteImages.argtypes = [POINTER(ImageInfo), POINTER(Image), STRING, POINTER(ExceptionInfo)]
DestroyConstitute = _lib.DestroyConstitute
DestroyConstitute.restype = None
DestroyConstitute.argtypes = []
class _FrameInfo(Structure):
    pass
_FrameInfo._fields_ = [
    ('width', c_ulong),
    ('height', c_ulong),
    ('x', c_long),
    ('y', c_long),
    ('inner_bevel', c_long),
    ('outer_bevel', c_long),
]
FrameInfo = _FrameInfo
class _RectangleInfo(Structure):
    pass
RectangleInfo = _RectangleInfo
BorderImage = _lib.BorderImage
BorderImage.restype = POINTER(Image)
BorderImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), POINTER(ExceptionInfo)]
FrameImage = _lib.FrameImage
FrameImage.restype = POINTER(Image)
FrameImage.argtypes = [POINTER(Image), POINTER(FrameInfo), POINTER(ExceptionInfo)]
RaiseImage = _lib.RaiseImage
RaiseImage.restype = MagickBooleanType
RaiseImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), MagickBooleanType]
class _DelegateInfo(Structure):
    pass
_DelegateInfo._fields_ = [
    ('path', STRING),
    ('decode', STRING),
    ('encode', STRING),
    ('commands', STRING),
    ('mode', c_long),
    ('thread_support', MagickBooleanType),
    ('spawn', MagickBooleanType),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_DelegateInfo)),
    ('next', POINTER(_DelegateInfo)),
    ('signature', c_ulong),
]
DelegateInfo = _DelegateInfo
GetDelegateCommand = _lib.GetDelegateCommand
GetDelegateCommand.restype = STRING
GetDelegateCommand.argtypes = [POINTER(ImageInfo), POINTER(Image), STRING, STRING, POINTER(ExceptionInfo)]
GetDelegateList = _lib.GetDelegateList
GetDelegateList.restype = POINTER(STRING)
GetDelegateList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetDelegateCommands = _lib.GetDelegateCommands
GetDelegateCommands.restype = STRING
GetDelegateCommands.argtypes = [POINTER(DelegateInfo)]
GetDelegateInfo = _lib.GetDelegateInfo
GetDelegateInfo.restype = POINTER(DelegateInfo)
GetDelegateInfo.argtypes = [STRING, STRING, POINTER(ExceptionInfo)]
GetDelegateInfoList = _lib.GetDelegateInfoList
GetDelegateInfoList.restype = POINTER(POINTER(DelegateInfo))
GetDelegateInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetDelegateMode = _lib.GetDelegateMode
GetDelegateMode.restype = c_long
GetDelegateMode.argtypes = [POINTER(DelegateInfo)]
InvokeDelegate = _lib.InvokeDelegate
InvokeDelegate.restype = MagickBooleanType
InvokeDelegate.argtypes = [POINTER(ImageInfo), POINTER(Image), STRING, STRING, POINTER(ExceptionInfo)]
ListDelegateInfo = _lib.ListDelegateInfo
ListDelegateInfo.restype = MagickBooleanType
ListDelegateInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
#DestroyDelegateList = _lib.DestroyDelegateList
#DestroyDelegateList.restype = None
#DestroyDelegateList.argtypes = []
class _DoublePixelPacket(Structure):
    pass
_DoublePixelPacket._pack_ = 4
_DoublePixelPacket._fields_ = [
    ('red', c_double),
    ('green', c_double),
    ('blue', c_double),
    ('opacity', c_double),
    ('index', c_double),
]
DoublePixelPacket = _DoublePixelPacket

# values for enumeration 'MagickLayerMethod'
MagickLayerMethod = c_int # enum
ExtendedSignedIntegralType = c_longlong
ExtendedUnsignedIntegralType = c_ulonglong
MonitorHandler = CFUNCTYPE(MagickBooleanType, STRING, MagickOffsetType, MagickSizeType, POINTER(ExceptionInfo))
class _ImageAttribute(Structure):
    pass
_ImageAttribute._fields_ = [
    ('key', STRING),
    ('value', STRING),
    ('compression', MagickBooleanType),
    ('previous', POINTER(_ImageAttribute)),
    ('next', POINTER(_ImageAttribute)),
]
ImageAttribute = _ImageAttribute
AllocateString = _lib.AllocateString
AllocateString.restype = STRING
AllocateString.argtypes = [STRING]
PostscriptGeometry = _lib.PostscriptGeometry
PostscriptGeometry.restype = STRING
PostscriptGeometry.argtypes = [STRING]
TranslateText = _lib.TranslateText
TranslateText.restype = STRING
TranslateText.argtypes = [POINTER(ImageInfo), POINTER(Image), STRING]
GetImageAttribute = _lib.GetImageAttribute
GetImageAttribute.restype = POINTER(ImageAttribute)
GetImageAttribute.argtypes = [POINTER(Image), STRING]
GetImageClippingPathAttribute = _lib.GetImageClippingPathAttribute
GetImageClippingPathAttribute.restype = POINTER(ImageAttribute)
GetImageClippingPathAttribute.argtypes = [POINTER(Image)]
GetNextImageAttribute = _lib.GetNextImageAttribute
GetNextImageAttribute.restype = POINTER(ImageAttribute)
GetNextImageAttribute.argtypes = [POINTER(Image)]
GetImageFromMagickRegistry = _lib.GetImageFromMagickRegistry
GetImageFromMagickRegistry.restype = POINTER(Image)
GetImageFromMagickRegistry.argtypes = [STRING, POINTER(c_long), POINTER(ExceptionInfo)]
GetImageList = _lib.GetImageList
GetImageList.restype = POINTER(Image)
GetImageList.argtypes = [POINTER(Image), c_long, POINTER(ExceptionInfo)]
GetNextImage = _lib.GetNextImage
GetNextImage.restype = POINTER(Image)
GetNextImage.argtypes = [POINTER(Image)]
GetPreviousImage = _lib.GetPreviousImage
GetPreviousImage.restype = POINTER(Image)
GetPreviousImage.argtypes = [POINTER(Image)]
FlattenImages = _lib.FlattenImages
FlattenImages.restype = POINTER(Image)
FlattenImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
MosaicImages = _lib.MosaicImages
MosaicImages.restype = POINTER(Image)
MosaicImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
PopImageList = _lib.PopImageList
PopImageList.restype = POINTER(Image)
PopImageList.argtypes = [POINTER(POINTER(Image))]
ShiftImageList = _lib.ShiftImageList
ShiftImageList.restype = POINTER(Image)
ShiftImageList.argtypes = [POINTER(POINTER(Image))]
SpliceImageList = _lib.SpliceImageList
SpliceImageList.restype = POINTER(Image)
SpliceImageList.argtypes = [POINTER(Image), c_long, c_ulong, POINTER(Image), POINTER(ExceptionInfo)]
ValidateColormapIndex = _lib.ValidateColormapIndex
ValidateColormapIndex.restype = IndexPacket
ValidateColormapIndex.argtypes = [POINTER(Image), c_ulong]
GetImageGeometry = _lib.GetImageGeometry
GetImageGeometry.restype = c_int
GetImageGeometry.argtypes = [POINTER(Image), STRING, c_uint, POINTER(RectangleInfo)]
ParseImageGeometry = _lib.ParseImageGeometry
ParseImageGeometry.restype = c_int
ParseImageGeometry.argtypes = [STRING, POINTER(c_long), POINTER(c_long), POINTER(c_ulong), POINTER(c_ulong)]
GetImageListIndex = _lib.GetImageListIndex
GetImageListIndex.restype = c_long
GetImageListIndex.argtypes = [POINTER(Image)]

# values for enumeration 'RegistryType'
RegistryType = c_int # enum
SetMagickRegistry = _lib.SetMagickRegistry
SetMagickRegistry.restype = c_long
SetMagickRegistry.argtypes = [RegistryType, c_void_p, size_t, POINTER(ExceptionInfo)]
ClipPathImage = _lib.ClipPathImage
ClipPathImage.restype = MagickBooleanType
ClipPathImage.argtypes = [POINTER(Image), STRING, MagickBooleanType]
CloneImageAttributes = _lib.CloneImageAttributes
CloneImageAttributes.restype = MagickBooleanType
CloneImageAttributes.argtypes = [POINTER(Image), POINTER(Image)]

# values for enumeration 'PaintMethod'
PaintMethod = c_int # enum
ColorFloodfillImage = _lib.ColorFloodfillImage
ColorFloodfillImage.restype = MagickBooleanType
ColorFloodfillImage.argtypes = [POINTER(Image), POINTER(DrawInfo), PixelPacket, c_long, c_long, PaintMethod]
DeleteImageAttribute = _lib.DeleteImageAttribute
DeleteImageAttribute.restype = MagickBooleanType
DeleteImageAttribute.argtypes = [POINTER(Image), STRING]
DeleteMagickRegistry = _lib.DeleteMagickRegistry
DeleteMagickRegistry.restype = MagickBooleanType
DeleteMagickRegistry.argtypes = [c_long]
DescribeImage = _lib.DescribeImage
DescribeImage.restype = MagickBooleanType
DescribeImage.argtypes = [POINTER(Image), POINTER(FILE), MagickBooleanType]
FormatImageAttribute = _lib.FormatImageAttribute
FormatImageAttribute.restype = MagickBooleanType
FormatImageAttribute.argtypes = [POINTER(Image), STRING, STRING]
__gnuc_va_list = STRING
va_list = __gnuc_va_list
FormatImageAttributeList = _lib.FormatImageAttributeList
FormatImageAttributeList.restype = MagickBooleanType
FormatImageAttributeList.argtypes = [POINTER(Image), STRING, STRING, va_list]
FuzzyColorCompare = _lib.FuzzyColorCompare
FuzzyColorCompare.restype = MagickBooleanType
FuzzyColorCompare.argtypes = [POINTER(Image), POINTER(PixelPacket), POINTER(PixelPacket)]
FuzzyOpacityCompare = _lib.FuzzyOpacityCompare
FuzzyOpacityCompare.restype = MagickBooleanType
FuzzyOpacityCompare.argtypes = [POINTER(Image), POINTER(PixelPacket), POINTER(PixelPacket)]
MagickMonitor = _lib.MagickMonitor
MagickMonitor.restype = MagickBooleanType
MagickMonitor.argtypes = [STRING, MagickOffsetType, MagickSizeType, c_void_p]
MatteFloodfillImage = _lib.MatteFloodfillImage
MatteFloodfillImage.restype = MagickBooleanType
MatteFloodfillImage.argtypes = [POINTER(Image), PixelPacket, Quantum, c_long, c_long, PaintMethod]
OpaqueImage = _lib.OpaqueImage
OpaqueImage.restype = MagickBooleanType
OpaqueImage.argtypes = [POINTER(Image), PixelPacket, PixelPacket]
PaintOpaqueImage = _lib.PaintOpaqueImage
PaintOpaqueImage.restype = MagickBooleanType
PaintOpaqueImage.argtypes = [POINTER(Image), POINTER(MagickPixelPacket), POINTER(MagickPixelPacket)]
PaintTransparentImage = _lib.PaintTransparentImage
PaintTransparentImage.restype = MagickBooleanType
PaintTransparentImage.argtypes = [POINTER(Image), POINTER(MagickPixelPacket), Quantum]

# values for enumeration 'QuantumType'
QuantumType = c_int # enum
PopImagePixels = _lib.PopImagePixels
PopImagePixels.restype = MagickBooleanType
PopImagePixels.argtypes = [POINTER(Image), QuantumType, POINTER(c_ubyte)]
PushImagePixels = _lib.PushImagePixels
PushImagePixels.restype = MagickBooleanType
PushImagePixels.argtypes = [POINTER(Image), QuantumType, POINTER(c_ubyte)]

# values for enumeration 'ExceptionType'
ExceptionType = c_int # enum
SetExceptionInfo = _lib.SetExceptionInfo
SetExceptionInfo.restype = MagickBooleanType
SetExceptionInfo.argtypes = [POINTER(ExceptionInfo), ExceptionType]
SetImageAttribute = _lib.SetImageAttribute
SetImageAttribute.restype = MagickBooleanType
SetImageAttribute.argtypes = [POINTER(Image), STRING, STRING]
TransparentImage = _lib.TransparentImage
TransparentImage.restype = MagickBooleanType
TransparentImage.argtypes = [POINTER(Image), PixelPacket, Quantum]
GetMonitorHandler = _lib.GetMonitorHandler
GetMonitorHandler.restype = MonitorHandler
GetMonitorHandler.argtypes = []
SetMonitorHandler = _lib.SetMonitorHandler
SetMonitorHandler.restype = MonitorHandler
SetMonitorHandler.argtypes = [MonitorHandler]
SizeBlob = _lib.SizeBlob
SizeBlob.restype = MagickOffsetType
SizeBlob.argtypes = [POINTER(Image)]
GetCacheView = _lib.GetCacheView
GetCacheView.restype = POINTER(PixelPacket)
GetCacheView.argtypes = [POINTER(ViewInfo), c_long, c_long, c_ulong, c_ulong]
ChannelImage = _lib.ChannelImage
ChannelImage.restype = c_uint
ChannelImage.argtypes = [POINTER(Image), ChannelType]
ChannelThresholdImage = _lib.ChannelThresholdImage
ChannelThresholdImage.restype = c_uint
ChannelThresholdImage.argtypes = [POINTER(Image), STRING]
DispatchImage = _lib.DispatchImage
DispatchImage.restype = c_uint
DispatchImage.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, STRING, StorageType, c_void_p, POINTER(ExceptionInfo)]
FuzzyColorMatch = _lib.FuzzyColorMatch
FuzzyColorMatch.restype = c_uint
FuzzyColorMatch.argtypes = [POINTER(PixelPacket), POINTER(PixelPacket), c_double]
GetNumberScenes = _lib.GetNumberScenes
GetNumberScenes.restype = c_uint
GetNumberScenes.argtypes = [POINTER(Image)]
GetMagickGeometry = _lib.GetMagickGeometry
GetMagickGeometry.restype = c_uint
GetMagickGeometry.argtypes = [STRING, POINTER(c_long), POINTER(c_long), POINTER(c_ulong), POINTER(c_ulong)]
IsSubimage = _lib.IsSubimage
IsSubimage.restype = c_uint
IsSubimage.argtypes = [STRING, c_uint]
PushImageList = _lib.PushImageList
PushImageList.restype = c_uint
PushImageList.argtypes = [POINTER(POINTER(Image)), POINTER(Image), POINTER(ExceptionInfo)]
QuantizationError = _lib.QuantizationError
QuantizationError.restype = c_uint
QuantizationError.argtypes = [POINTER(Image)]
RandomChannelThresholdImage = _lib.RandomChannelThresholdImage
RandomChannelThresholdImage.restype = c_uint
RandomChannelThresholdImage.argtypes = [POINTER(Image), STRING, STRING, POINTER(ExceptionInfo)]
SetImageList = _lib.SetImageList
SetImageList.restype = c_uint
SetImageList.argtypes = [POINTER(POINTER(Image)), POINTER(Image), c_long, POINTER(ExceptionInfo)]
TransformColorspace = _lib.TransformColorspace
TransformColorspace.restype = c_uint
TransformColorspace.argtypes = [POINTER(Image), ColorspaceType]
ThresholdImage = _lib.ThresholdImage
ThresholdImage.restype = c_uint
ThresholdImage.argtypes = [POINTER(Image), c_double]
ThresholdImageChannel = _lib.ThresholdImageChannel
ThresholdImageChannel.restype = c_uint
ThresholdImageChannel.argtypes = [POINTER(Image), STRING]
UnshiftImageList = _lib.UnshiftImageList
UnshiftImageList.restype = c_uint
UnshiftImageList.argtypes = [POINTER(POINTER(Image)), POINTER(Image), POINTER(ExceptionInfo)]
GetImageListSize = _lib.GetImageListSize
GetImageListSize.restype = c_ulong
GetImageListSize.argtypes = [POINTER(Image)]
AcquireMemory = _lib.AcquireMemory
AcquireMemory.restype = c_void_p
AcquireMemory.argtypes = [size_t]
CloneMemory = _lib.CloneMemory
CloneMemory.restype = c_void_p
CloneMemory.argtypes = [c_void_p, c_void_p, size_t]
DestroyImageAttributes = _lib.DestroyImageAttributes
DestroyImageAttributes.restype = None
DestroyImageAttributes.argtypes = [POINTER(Image)]
DestroyImages = _lib.DestroyImages
DestroyImages.restype = None
DestroyImages.argtypes = [POINTER(Image)]
DestroyMagick = _lib.DestroyMagick
DestroyMagick.restype = None
DestroyMagick.argtypes = []
DestroyMagickRegistry = _lib.DestroyMagickRegistry
DestroyMagickRegistry.restype = None
DestroyMagickRegistry.argtypes = []
GetConfigureBlob = _lib.GetConfigureBlob
GetConfigureBlob.restype = c_void_p
GetConfigureBlob.argtypes = [STRING, STRING, POINTER(size_t), POINTER(ExceptionInfo)]
GetMagickRegistry = _lib.GetMagickRegistry
GetMagickRegistry.restype = c_void_p
GetMagickRegistry.argtypes = [c_long, POINTER(RegistryType), POINTER(size_t), POINTER(ExceptionInfo)]
class _AffineMatrix(Structure):
    pass
AffineMatrix = _AffineMatrix
IdentityAffine = _lib.IdentityAffine
IdentityAffine.restype = None
IdentityAffine.argtypes = [POINTER(AffineMatrix)]
LiberateMemory = _lib.LiberateMemory
LiberateMemory.restype = None
LiberateMemory.argtypes = [POINTER(c_void_p)]
class SemaphoreInfo(Structure):
    pass
LiberateSemaphoreInfo = _lib.LiberateSemaphoreInfo
LiberateSemaphoreInfo.restype = None
LiberateSemaphoreInfo.argtypes = [POINTER(POINTER(SemaphoreInfo))]
FormatString = _lib.FormatString
FormatString.restype = None
FormatString.argtypes = [STRING, STRING]
FormatStringList = _lib.FormatStringList
FormatStringList.restype = None
FormatStringList.argtypes = [STRING, STRING, va_list]
InitializeMagick = _lib.InitializeMagick
InitializeMagick.restype = None
InitializeMagick.argtypes = [STRING]
ReacquireMemory = _lib.ReacquireMemory
ReacquireMemory.restype = None
ReacquireMemory.argtypes = [POINTER(c_void_p), size_t]
ResetImageAttributeIterator = _lib.ResetImageAttributeIterator
ResetImageAttributeIterator.restype = None
ResetImageAttributeIterator.argtypes = [POINTER(Image)]
SetCacheThreshold = _lib.SetCacheThreshold
SetCacheThreshold.restype = None
SetCacheThreshold.argtypes = [c_ulong]
SetImage = _lib.SetImage
SetImage.restype = None
SetImage.argtypes = [POINTER(Image), Quantum]
Strip = _lib.Strip
Strip.restype = None
Strip.argtypes = [STRING]
TemporaryFilename = _lib.TemporaryFilename
TemporaryFilename.restype = None
TemporaryFilename.argtypes = [STRING]
DisplayImages = _lib.DisplayImages
DisplayImages.restype = MagickBooleanType
DisplayImages.argtypes = [POINTER(ImageInfo), POINTER(Image)]
RemoteDisplayCommand = _lib.RemoteDisplayCommand
RemoteDisplayCommand.restype = MagickBooleanType
RemoteDisplayCommand.argtypes = [POINTER(ImageInfo), STRING, STRING, POINTER(ExceptionInfo)]

# values for enumeration 'DistortImageMethod'
DistortImageMethod = c_int # enum

# values for enumeration 'AlignType'
AlignType = c_int # enum

# values for enumeration 'ClipPathUnits'
ClipPathUnits = c_int # enum

# values for enumeration 'DecorationType'
DecorationType = c_int # enum

# values for enumeration 'FillRule'
FillRule = c_int # enum

# values for enumeration 'GradientType'
GradientType = c_int # enum

# values for enumeration 'LineCap'
LineCap = c_int # enum

# values for enumeration 'LineJoin'
LineJoin = c_int # enum

# values for enumeration 'PrimitiveType'
PrimitiveType = c_int # enum

# values for enumeration 'ReferenceType'
ReferenceType = c_int # enum

# values for enumeration 'SpreadMethod'
SpreadMethod = c_int # enum
class _StopInfo(Structure):
    pass
_StopInfo._pack_ = 4
_StopInfo._fields_ = [
    ('color', MagickPixelPacket),
    ('offset', MagickRealType),
]
StopInfo = _StopInfo
class _GradientInfo(Structure):
    pass
_RectangleInfo._fields_ = [
    ('width', c_ulong),
    ('height', c_ulong),
    ('x', c_long),
    ('y', c_long),
]
class _SegmentInfo(Structure):
    pass
_SegmentInfo._pack_ = 4
_SegmentInfo._fields_ = [
    ('x1', c_double),
    ('y1', c_double),
    ('x2', c_double),
    ('y2', c_double),
]
SegmentInfo = _SegmentInfo
_GradientInfo._fields_ = [
    ('type', GradientType),
    ('bounding_box', RectangleInfo),
    ('gradient_vector', SegmentInfo),
    ('stops', POINTER(StopInfo)),
    ('number_stops', c_ulong),
    ('spread', SpreadMethod),
    ('debug', MagickBooleanType),
    ('signature', c_ulong),
]
GradientInfo = _GradientInfo
class _ElementReference(Structure):
    pass
_ElementReference._fields_ = [
    ('id', STRING),
    ('type', ReferenceType),
    ('gradient', GradientInfo),
    ('signature', c_ulong),
    ('previous', POINTER(_ElementReference)),
    ('next', POINTER(_ElementReference)),
]
ElementReference = _ElementReference
_AffineMatrix._pack_ = 4
_AffineMatrix._fields_ = [
    ('sx', c_double),
    ('rx', c_double),
    ('ry', c_double),
    ('sy', c_double),
    ('tx', c_double),
    ('ty', c_double),
]

# values for enumeration 'GravityType'
GravityType = c_int # enum

# values for enumeration 'StyleType'
StyleType = c_int # enum

# values for enumeration 'StretchType'
StretchType = c_int # enum
_DrawInfo._pack_ = 4
_DrawInfo._fields_ = [
    ('primitive', STRING),
    ('geometry', STRING),
    ('viewbox', RectangleInfo),
    ('affine', AffineMatrix),
    ('gravity', GravityType),
    ('fill', PixelPacket),
    ('stroke', PixelPacket),
    ('stroke_width', c_double),
    ('gradient', GradientInfo),
    ('fill_pattern', POINTER(Image)),
    ('tile', POINTER(Image)),
    ('stroke_pattern', POINTER(Image)),
    ('stroke_antialias', MagickBooleanType),
    ('text_antialias', MagickBooleanType),
    ('fill_rule', FillRule),
    ('linecap', LineCap),
    ('linejoin', LineJoin),
    ('miterlimit', c_ulong),
    ('dash_offset', c_double),
    ('decorate', DecorationType),
    ('compose', CompositeOperator),
    ('text', STRING),
    ('face', c_ulong),
    ('font', STRING),
    ('metrics', STRING),
    ('family', STRING),
    ('style', StyleType),
    ('stretch', StretchType),
    ('weight', c_ulong),
    ('encoding', STRING),
    ('pointsize', c_double),
    ('density', STRING),
    ('align', AlignType),
    ('undercolor', PixelPacket),
    ('border_color', PixelPacket),
    ('server_name', STRING),
    ('dash_pattern', POINTER(c_double)),
    ('clip_mask', STRING),
    ('bounds', SegmentInfo),
    ('clip_units', ClipPathUnits),
    ('opacity', Quantum),
    ('render', MagickBooleanType),
    ('element_reference', ElementReference),
    ('debug', MagickBooleanType),
    ('signature', c_ulong),
]
class _PointInfo(Structure):
    pass
_PointInfo._pack_ = 4
_PointInfo._fields_ = [
    ('x', c_double),
    ('y', c_double),
]
PointInfo = _PointInfo
class _PrimitiveInfo(Structure):
    pass
_PrimitiveInfo._fields_ = [
    ('point', PointInfo),
    ('coordinates', c_ulong),
    ('primitive', PrimitiveType),
    ('method', PaintMethod),
    ('text', STRING),
]
PrimitiveInfo = _PrimitiveInfo
_TypeMetric._pack_ = 4
_TypeMetric._fields_ = [
    ('pixels_per_em', PointInfo),
    ('ascent', c_double),
    ('descent', c_double),
    ('width', c_double),
    ('height', c_double),
    ('max_advance', c_double),
    ('underline_position', c_double),
    ('underline_thickness', c_double),
    ('bounds', SegmentInfo),
    ('origin', PointInfo),
]
CloneDrawInfo = _lib.CloneDrawInfo
CloneDrawInfo.restype = POINTER(DrawInfo)
CloneDrawInfo.argtypes = [POINTER(ImageInfo), POINTER(DrawInfo)]
DestroyDrawInfo = _lib.DestroyDrawInfo
DestroyDrawInfo.restype = POINTER(DrawInfo)
DestroyDrawInfo.argtypes = [POINTER(DrawInfo)]
DrawAffineImage = _lib.DrawAffineImage
DrawAffineImage.restype = MagickBooleanType
DrawAffineImage.argtypes = [POINTER(Image), POINTER(Image), POINTER(AffineMatrix)]
DrawClipPath = _lib.DrawClipPath
DrawClipPath.restype = MagickBooleanType
DrawClipPath.argtypes = [POINTER(Image), POINTER(DrawInfo), STRING]
DrawImage = _lib.DrawImage
DrawImage.restype = MagickBooleanType
DrawImage.argtypes = [POINTER(Image), POINTER(DrawInfo)]
DrawPatternPath = _lib.DrawPatternPath
DrawPatternPath.restype = MagickBooleanType
DrawPatternPath.argtypes = [POINTER(Image), POINTER(DrawInfo), STRING, POINTER(POINTER(Image))]
DrawPrimitive = _lib.DrawPrimitive
DrawPrimitive.restype = MagickBooleanType
DrawPrimitive.argtypes = [POINTER(Image), POINTER(DrawInfo), POINTER(PrimitiveInfo)]
GetAffineMatrix = _lib.GetAffineMatrix
GetAffineMatrix.restype = None
GetAffineMatrix.argtypes = [POINTER(AffineMatrix)]
GetDrawInfo = _lib.GetDrawInfo
GetDrawInfo.restype = None
GetDrawInfo.argtypes = [POINTER(ImageInfo), POINTER(DrawInfo)]

# values for enumeration 'NoiseType'
NoiseType = c_int # enum

# values for enumeration 'PreviewType'
PreviewType = c_int # enum
AddNoiseImage = _lib.AddNoiseImage
AddNoiseImage.restype = POINTER(Image)
AddNoiseImage.argtypes = [POINTER(Image), NoiseType, POINTER(ExceptionInfo)]
BlurImage = _lib.BlurImage
BlurImage.restype = POINTER(Image)
BlurImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
BlurImageChannel = _lib.BlurImageChannel
BlurImageChannel.restype = POINTER(Image)
BlurImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, c_double, POINTER(ExceptionInfo)]
DespeckleImage = _lib.DespeckleImage
DespeckleImage.restype = POINTER(Image)
DespeckleImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
EdgeImage = _lib.EdgeImage
EdgeImage.restype = POINTER(Image)
EdgeImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
EmbossImage = _lib.EmbossImage
EmbossImage.restype = POINTER(Image)
EmbossImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
GaussianBlurImage = _lib.GaussianBlurImage
GaussianBlurImage.restype = POINTER(Image)
GaussianBlurImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
GaussianBlurImageChannel = _lib.GaussianBlurImageChannel
GaussianBlurImageChannel.restype = POINTER(Image)
GaussianBlurImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, c_double, POINTER(ExceptionInfo)]
MedianFilterImage = _lib.MedianFilterImage
MedianFilterImage.restype = POINTER(Image)
MedianFilterImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
MotionBlurImage = _lib.MotionBlurImage
MotionBlurImage.restype = POINTER(Image)
MotionBlurImage.argtypes = [POINTER(Image), c_double, c_double, c_double, POINTER(ExceptionInfo)]
PreviewImage = _lib.PreviewImage
PreviewImage.restype = POINTER(Image)
PreviewImage.argtypes = [POINTER(Image), PreviewType, POINTER(ExceptionInfo)]
RadialBlurImage = _lib.RadialBlurImage
RadialBlurImage.restype = POINTER(Image)
RadialBlurImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
RadialBlurImageChannel = _lib.RadialBlurImageChannel
RadialBlurImageChannel.restype = POINTER(Image)
RadialBlurImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, POINTER(ExceptionInfo)]
ReduceNoiseImage = _lib.ReduceNoiseImage
ReduceNoiseImage.restype = POINTER(Image)
ReduceNoiseImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
ShadeImage = _lib.ShadeImage
ShadeImage.restype = POINTER(Image)
ShadeImage.argtypes = [POINTER(Image), MagickBooleanType, c_double, c_double, POINTER(ExceptionInfo)]
SharpenImage = _lib.SharpenImage
SharpenImage.restype = POINTER(Image)
SharpenImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
SharpenImageChannel = _lib.SharpenImageChannel
SharpenImageChannel.restype = POINTER(Image)
SharpenImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, c_double, POINTER(ExceptionInfo)]
SpreadImage = _lib.SpreadImage
SpreadImage.restype = POINTER(Image)
SpreadImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
UnsharpMaskImage = _lib.UnsharpMaskImage
UnsharpMaskImage.restype = POINTER(Image)
UnsharpMaskImage.argtypes = [POINTER(Image), c_double, c_double, c_double, c_double, POINTER(ExceptionInfo)]
UnsharpMaskImageChannel = _lib.UnsharpMaskImageChannel
UnsharpMaskImageChannel.restype = POINTER(Image)
UnsharpMaskImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, c_double, c_double, c_double, POINTER(ExceptionInfo)]
ContrastImage = _lib.ContrastImage
ContrastImage.restype = MagickBooleanType
ContrastImage.argtypes = [POINTER(Image), MagickBooleanType]
EqualizeImage = _lib.EqualizeImage
EqualizeImage.restype = MagickBooleanType
EqualizeImage.argtypes = [POINTER(Image)]
GammaImage = _lib.GammaImage
GammaImage.restype = MagickBooleanType
GammaImage.argtypes = [POINTER(Image), STRING]
GammaImageChannel = _lib.GammaImageChannel
GammaImageChannel.restype = MagickBooleanType
GammaImageChannel.argtypes = [POINTER(Image), ChannelType, c_double]
LevelImage = _lib.LevelImage
LevelImage.restype = MagickBooleanType
LevelImage.argtypes = [POINTER(Image), STRING]
LevelImageChannel = _lib.LevelImageChannel
LevelImageChannel.restype = MagickBooleanType
LevelImageChannel.argtypes = [POINTER(Image), ChannelType, c_double, c_double, c_double]
ModulateImage = _lib.ModulateImage
ModulateImage.restype = MagickBooleanType
ModulateImage.argtypes = [POINTER(Image), STRING]
NegateImage = _lib.NegateImage
NegateImage.restype = MagickBooleanType
NegateImage.argtypes = [POINTER(Image), MagickBooleanType]
NegateImageChannel = _lib.NegateImageChannel
NegateImageChannel.restype = MagickBooleanType
NegateImageChannel.argtypes = [POINTER(Image), ChannelType, MagickBooleanType]
NormalizeImage = _lib.NormalizeImage
NormalizeImage.restype = MagickBooleanType
NormalizeImage.argtypes = [POINTER(Image)]
NormalizeImageChannel = _lib.NormalizeImageChannel
NormalizeImageChannel.restype = MagickBooleanType
NormalizeImageChannel.argtypes = [POINTER(Image), ChannelType]
SigmoidalContrastImage = _lib.SigmoidalContrastImage
SigmoidalContrastImage.restype = MagickBooleanType
SigmoidalContrastImage.argtypes = [POINTER(Image), MagickBooleanType, STRING]
SigmoidalContrastImageChannel = _lib.SigmoidalContrastImageChannel
SigmoidalContrastImageChannel.restype = MagickBooleanType
SigmoidalContrastImageChannel.argtypes = [POINTER(Image), ChannelType, MagickBooleanType, c_double, c_double]
EnhanceImage = _lib.EnhanceImage
EnhanceImage.restype = POINTER(Image)
EnhanceImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
_ExceptionInfo._fields_ = [
    ('severity', ExceptionType),
    ('error_number', c_int),
    ('reason', STRING),
    ('description', STRING),
    ('exceptions', c_void_p),
    ('relinquish', MagickBooleanType),
    ('semaphore', POINTER(SemaphoreInfo)),
    ('signature', c_ulong),
]
ErrorHandler = CFUNCTYPE(None, ExceptionType, STRING, STRING)
FatalErrorHandler = CFUNCTYPE(None, ExceptionType, STRING, STRING)
WarningHandler = CFUNCTYPE(None, ExceptionType, STRING, STRING)
GetLocaleExceptionMessage = _lib.GetLocaleExceptionMessage
GetLocaleExceptionMessage.restype = STRING
GetLocaleExceptionMessage.argtypes = [ExceptionType, STRING]
SetErrorHandler = _lib.SetErrorHandler
SetErrorHandler.restype = ErrorHandler
SetErrorHandler.argtypes = [ErrorHandler]
DestroyExceptionInfo = _lib.DestroyExceptionInfo
DestroyExceptionInfo.restype = POINTER(ExceptionInfo)
DestroyExceptionInfo.argtypes = [POINTER(ExceptionInfo)]
SetFatalErrorHandler = _lib.SetFatalErrorHandler
SetFatalErrorHandler.restype = FatalErrorHandler
SetFatalErrorHandler.argtypes = [FatalErrorHandler]
ThrowException = _lib.ThrowException
ThrowException.restype = MagickBooleanType
ThrowException.argtypes = [POINTER(ExceptionInfo), ExceptionType, STRING, STRING]
ThrowMagickException = _lib.ThrowMagickException
ThrowMagickException.restype = MagickBooleanType
ThrowMagickException.argtypes = [POINTER(ExceptionInfo), STRING, STRING, c_ulong, ExceptionType, STRING, STRING]
ThrowMagickExceptionList = _lib.ThrowMagickExceptionList
ThrowMagickExceptionList.restype = MagickBooleanType
ThrowMagickExceptionList.argtypes = [POINTER(ExceptionInfo), STRING, STRING, c_ulong, ExceptionType, STRING, STRING, va_list]
CatchException = _lib.CatchException
CatchException.restype = None
CatchException.argtypes = [POINTER(ExceptionInfo)]
GetExceptionInfo = _lib.GetExceptionInfo
GetExceptionInfo.restype = None
GetExceptionInfo.argtypes = [POINTER(ExceptionInfo)]
InheritException = _lib.InheritException
InheritException.restype = None
InheritException.argtypes = [POINTER(ExceptionInfo), POINTER(ExceptionInfo)]
MagickError = _lib.MagickError
MagickError.restype = None
MagickError.argtypes = [ExceptionType, STRING, STRING]
MagickFatalError = _lib.MagickFatalError
MagickFatalError.restype = None
MagickFatalError.argtypes = [ExceptionType, STRING, STRING]
MagickWarning = _lib.MagickWarning
MagickWarning.restype = None
MagickWarning.argtypes = [ExceptionType, STRING, STRING]
SetWarningHandler = _lib.SetWarningHandler
SetWarningHandler.restype = WarningHandler
SetWarningHandler.argtypes = [WarningHandler]

# values for enumeration 'MagickEvaluateOperator'
MagickEvaluateOperator = c_int # enum
CharcoalImage = _lib.CharcoalImage
CharcoalImage.restype = POINTER(Image)
CharcoalImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
ColorizeImage = _lib.ColorizeImage
ColorizeImage.restype = POINTER(Image)
ColorizeImage.argtypes = [POINTER(Image), STRING, PixelPacket, POINTER(ExceptionInfo)]
ConvolveImage = _lib.ConvolveImage
ConvolveImage.restype = POINTER(Image)
ConvolveImage.argtypes = [POINTER(Image), c_ulong, POINTER(c_double), POINTER(ExceptionInfo)]
ConvolveImageChannel = _lib.ConvolveImageChannel
ConvolveImageChannel.restype = POINTER(Image)
ConvolveImageChannel.argtypes = [POINTER(Image), ChannelType, c_ulong, POINTER(c_double), POINTER(ExceptionInfo)]
FxImage = _lib.FxImage
FxImage.restype = POINTER(Image)
FxImage.argtypes = [POINTER(Image), STRING, POINTER(ExceptionInfo)]
FxImageChannel = _lib.FxImageChannel
FxImageChannel.restype = POINTER(Image)
FxImageChannel.argtypes = [POINTER(Image), ChannelType, STRING, POINTER(ExceptionInfo)]
ImplodeImage = _lib.ImplodeImage
ImplodeImage.restype = POINTER(Image)
ImplodeImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
MorphImages = _lib.MorphImages
MorphImages.restype = POINTER(Image)
MorphImages.argtypes = [POINTER(Image), c_ulong, POINTER(ExceptionInfo)]
SepiaToneImage = _lib.SepiaToneImage
SepiaToneImage.restype = POINTER(Image)
SepiaToneImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
ShadowImage = _lib.ShadowImage
ShadowImage.restype = POINTER(Image)
ShadowImage.argtypes = [POINTER(Image), c_double, c_double, c_long, c_long, POINTER(ExceptionInfo)]
SteganoImage = _lib.SteganoImage
SteganoImage.restype = POINTER(Image)
SteganoImage.argtypes = [POINTER(Image), POINTER(Image), POINTER(ExceptionInfo)]
StereoImage = _lib.StereoImage
StereoImage.restype = POINTER(Image)
StereoImage.argtypes = [POINTER(Image), POINTER(Image), POINTER(ExceptionInfo)]
SwirlImage = _lib.SwirlImage
SwirlImage.restype = POINTER(Image)
SwirlImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
TintImage = _lib.TintImage
TintImage.restype = POINTER(Image)
TintImage.argtypes = [POINTER(Image), STRING, PixelPacket, POINTER(ExceptionInfo)]
WaveImage = _lib.WaveImage
WaveImage.restype = POINTER(Image)
WaveImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
EvaluateImage = _lib.EvaluateImage
EvaluateImage.restype = MagickBooleanType
EvaluateImage.argtypes = [POINTER(Image), MagickEvaluateOperator, c_double, POINTER(ExceptionInfo)]
EvaluateImageChannel = _lib.EvaluateImageChannel
EvaluateImageChannel.restype = MagickBooleanType
EvaluateImageChannel.argtypes = [POINTER(Image), ChannelType, MagickEvaluateOperator, c_double, POINTER(ExceptionInfo)]
SolarizeImage = _lib.SolarizeImage
SolarizeImage.restype = MagickBooleanType
SolarizeImage.argtypes = [POINTER(Image), c_double]
ExpandAffine = _lib.ExpandAffine
ExpandAffine.restype = c_double
ExpandAffine.argtypes = [POINTER(AffineMatrix)]
GetOptimalKernelWidth = _lib.GetOptimalKernelWidth
GetOptimalKernelWidth.restype = c_ulong
GetOptimalKernelWidth.argtypes = [c_double, c_double]
GetOptimalKernelWidth1D = _lib.GetOptimalKernelWidth1D
GetOptimalKernelWidth1D.restype = c_ulong
GetOptimalKernelWidth1D.argtypes = [c_double, c_double]
GetOptimalKernelWidth2D = _lib.GetOptimalKernelWidth2D
GetOptimalKernelWidth2D.restype = c_ulong
GetOptimalKernelWidth2D.argtypes = [c_double, c_double]

# values for enumeration 'GeometryFlags'
GeometryFlags = c_int # enum
class _GeometryInfo(Structure):
    pass
_GeometryInfo._pack_ = 4
_GeometryInfo._fields_ = [
    ('rho', c_double),
    ('sigma', c_double),
    ('xi', c_double),
    ('psi', c_double),
    ('chi', c_double),
]
GeometryInfo = _GeometryInfo
GetPageGeometry = _lib.GetPageGeometry
GetPageGeometry.restype = STRING
GetPageGeometry.argtypes = [STRING]
IsGeometry = _lib.IsGeometry
IsGeometry.restype = MagickBooleanType
IsGeometry.argtypes = [STRING]
IsSceneGeometry = _lib.IsSceneGeometry
IsSceneGeometry.restype = MagickBooleanType
IsSceneGeometry.argtypes = [STRING, MagickBooleanType]
MagickStatusType = c_uint
GetGeometry = _lib.GetGeometry
GetGeometry.restype = MagickStatusType
GetGeometry.argtypes = [STRING, POINTER(c_long), POINTER(c_long), POINTER(c_ulong), POINTER(c_ulong)]
ParseAbsoluteGeometry = _lib.ParseAbsoluteGeometry
ParseAbsoluteGeometry.restype = MagickStatusType
ParseAbsoluteGeometry.argtypes = [STRING, POINTER(RectangleInfo)]
ParseGeometry = _lib.ParseGeometry
ParseGeometry.restype = MagickStatusType
ParseGeometry.argtypes = [STRING, POINTER(GeometryInfo)]
ParseGravityGeometry = _lib.ParseGravityGeometry
ParseGravityGeometry.restype = MagickStatusType
ParseGravityGeometry.argtypes = [POINTER(Image), STRING, POINTER(RectangleInfo)]
ParseMetaGeometry = _lib.ParseMetaGeometry
ParseMetaGeometry.restype = MagickStatusType
ParseMetaGeometry.argtypes = [STRING, POINTER(c_long), POINTER(c_long), POINTER(c_ulong), POINTER(c_ulong)]
ParsePageGeometry = _lib.ParsePageGeometry
ParsePageGeometry.restype = MagickStatusType
ParsePageGeometry.argtypes = [POINTER(Image), STRING, POINTER(RectangleInfo)]
ParseSizeGeometry = _lib.ParseSizeGeometry
ParseSizeGeometry.restype = MagickStatusType
ParseSizeGeometry.argtypes = [POINTER(Image), STRING, POINTER(RectangleInfo)]
SetGeometry = _lib.SetGeometry
SetGeometry.restype = None
SetGeometry.argtypes = [POINTER(Image), POINTER(RectangleInfo)]
SetGeometryInfo = _lib.SetGeometryInfo
SetGeometryInfo.restype = None
SetGeometryInfo.argtypes = [POINTER(GeometryInfo)]
class _HashmapInfo(Structure):
    pass
_HashmapInfo._fields_ = [
]
HashmapInfo = _HashmapInfo
_LinkedListInfo._fields_ = [
]
DestroyHashmap = _lib.DestroyHashmap
DestroyHashmap.restype = POINTER(HashmapInfo)
DestroyHashmap.argtypes = [POINTER(HashmapInfo)]
NewHashmap = _lib.NewHashmap
NewHashmap.restype = POINTER(HashmapInfo)
NewHashmap.argtypes = [c_ulong, CFUNCTYPE(size_t, c_void_p), CFUNCTYPE(MagickBooleanType, c_void_p, c_void_p), CFUNCTYPE(c_void_p, c_void_p), CFUNCTYPE(c_void_p, c_void_p)]
DestroyLinkedList = _lib.DestroyLinkedList
DestroyLinkedList.restype = POINTER(LinkedListInfo)
DestroyLinkedList.argtypes = [POINTER(LinkedListInfo), CFUNCTYPE(c_void_p, c_void_p)]
NewLinkedList = _lib.NewLinkedList
NewLinkedList.restype = POINTER(LinkedListInfo)
NewLinkedList.argtypes = [c_ulong]
AppendValueToLinkedList = _lib.AppendValueToLinkedList
AppendValueToLinkedList.restype = MagickBooleanType
AppendValueToLinkedList.argtypes = [POINTER(LinkedListInfo), c_void_p]
CompareHashmapString = _lib.CompareHashmapString
CompareHashmapString.restype = MagickBooleanType
CompareHashmapString.argtypes = [c_void_p, c_void_p]
CompareHashmapStringInfo = _lib.CompareHashmapStringInfo
CompareHashmapStringInfo.restype = MagickBooleanType
CompareHashmapStringInfo.argtypes = [c_void_p, c_void_p]
InsertValueInLinkedList = _lib.InsertValueInLinkedList
InsertValueInLinkedList.restype = MagickBooleanType
InsertValueInLinkedList.argtypes = [POINTER(LinkedListInfo), c_ulong, c_void_p]
InsertValueInSortedLinkedList = _lib.InsertValueInSortedLinkedList
InsertValueInSortedLinkedList.restype = MagickBooleanType
InsertValueInSortedLinkedList.argtypes = [POINTER(LinkedListInfo), CFUNCTYPE(c_int, c_void_p, c_void_p), POINTER(c_void_p), c_void_p]
IsHashmapEmpty = _lib.IsHashmapEmpty
IsHashmapEmpty.restype = MagickBooleanType
IsHashmapEmpty.argtypes = [POINTER(HashmapInfo)]
IsLinkedListEmpty = _lib.IsLinkedListEmpty
IsLinkedListEmpty.restype = MagickBooleanType
IsLinkedListEmpty.argtypes = [POINTER(LinkedListInfo)]
LinkedListToArray = _lib.LinkedListToArray
LinkedListToArray.restype = MagickBooleanType
LinkedListToArray.argtypes = [POINTER(LinkedListInfo), POINTER(c_void_p)]
PutEntryInHashmap = _lib.PutEntryInHashmap
PutEntryInHashmap.restype = MagickBooleanType
PutEntryInHashmap.argtypes = [POINTER(HashmapInfo), c_void_p, c_void_p]
HashPointerType = _lib.HashPointerType
HashPointerType.restype = size_t
HashPointerType.argtypes = [c_void_p]
HashStringType = _lib.HashStringType
HashStringType.restype = size_t
HashStringType.argtypes = [c_void_p]
HashStringInfoType = _lib.HashStringInfoType
HashStringInfoType.restype = size_t
HashStringInfoType.argtypes = [c_void_p]
GetNumberOfElementsInLinkedList = _lib.GetNumberOfElementsInLinkedList
GetNumberOfElementsInLinkedList.restype = c_ulong
GetNumberOfElementsInLinkedList.argtypes = [POINTER(LinkedListInfo)]
GetNumberOfEntriesInHashmap = _lib.GetNumberOfEntriesInHashmap
GetNumberOfEntriesInHashmap.restype = c_ulong
GetNumberOfEntriesInHashmap.argtypes = [POINTER(HashmapInfo)]
ClearLinkedList = _lib.ClearLinkedList
ClearLinkedList.restype = None
ClearLinkedList.argtypes = [POINTER(LinkedListInfo), CFUNCTYPE(c_void_p, c_void_p)]
GetLastValueInLinkedList = _lib.GetLastValueInLinkedList
GetLastValueInLinkedList.restype = c_void_p
GetLastValueInLinkedList.argtypes = [POINTER(LinkedListInfo)]
GetNextKeyInHashmap = _lib.GetNextKeyInHashmap
GetNextKeyInHashmap.restype = c_void_p
GetNextKeyInHashmap.argtypes = [POINTER(HashmapInfo)]
GetNextValueInHashmap = _lib.GetNextValueInHashmap
GetNextValueInHashmap.restype = c_void_p
GetNextValueInHashmap.argtypes = [POINTER(HashmapInfo)]
GetNextValueInLinkedList = _lib.GetNextValueInLinkedList
GetNextValueInLinkedList.restype = c_void_p
GetNextValueInLinkedList.argtypes = [POINTER(LinkedListInfo)]
GetValueFromHashmap = _lib.GetValueFromHashmap
GetValueFromHashmap.restype = c_void_p
GetValueFromHashmap.argtypes = [POINTER(HashmapInfo), c_void_p]
GetValueFromLinkedList = _lib.GetValueFromLinkedList
GetValueFromLinkedList.restype = c_void_p
GetValueFromLinkedList.argtypes = [POINTER(LinkedListInfo), c_ulong]
RemoveElementByValueFromLinkedList = _lib.RemoveElementByValueFromLinkedList
RemoveElementByValueFromLinkedList.restype = c_void_p
RemoveElementByValueFromLinkedList.argtypes = [POINTER(LinkedListInfo), c_void_p]
RemoveElementFromLinkedList = _lib.RemoveElementFromLinkedList
RemoveElementFromLinkedList.restype = c_void_p
RemoveElementFromLinkedList.argtypes = [POINTER(LinkedListInfo), c_ulong]
RemoveEntryFromHashmap = _lib.RemoveEntryFromHashmap
RemoveEntryFromHashmap.restype = c_void_p
RemoveEntryFromHashmap.argtypes = [POINTER(HashmapInfo), c_void_p]
RemoveLastElementFromLinkedList = _lib.RemoveLastElementFromLinkedList
RemoveLastElementFromLinkedList.restype = c_void_p
RemoveLastElementFromLinkedList.argtypes = [POINTER(LinkedListInfo)]
ResetHashmapIterator = _lib.ResetHashmapIterator
ResetHashmapIterator.restype = None
ResetHashmapIterator.argtypes = [POINTER(HashmapInfo)]
ResetLinkedListIterator = _lib.ResetLinkedListIterator
ResetLinkedListIterator.restype = None
ResetLinkedListIterator.argtypes = [POINTER(LinkedListInfo)]
IdentifyImage = _lib.IdentifyImage
IdentifyImage.restype = MagickBooleanType
IdentifyImage.argtypes = [POINTER(Image), POINTER(FILE), MagickBooleanType]

# values for enumeration 'AlphaChannelType'
AlphaChannelType = c_int # enum

# values for enumeration 'ImageType'
ImageType = c_int # enum

# values for enumeration 'InterlaceType'
InterlaceType = c_int # enum

# values for enumeration 'OrientationType'
OrientationType = c_int # enum

# values for enumeration 'ResolutionType'
ResolutionType = c_int # enum
class _PrimaryInfo(Structure):
    pass
_PrimaryInfo._pack_ = 4
_PrimaryInfo._fields_ = [
    ('x', c_double),
    ('y', c_double),
    ('z', c_double),
]
PrimaryInfo = _PrimaryInfo

# values for enumeration 'TransmitType'
TransmitType = c_int # enum
class _ChromaticityInfo(Structure):
    pass
_ChromaticityInfo._fields_ = [
    ('red_primary', PrimaryInfo),
    ('green_primary', PrimaryInfo),
    ('blue_primary', PrimaryInfo),
    ('white_point', PrimaryInfo),
]
ChromaticityInfo = _ChromaticityInfo

# values for enumeration 'RenderingIntent'
RenderingIntent = c_int # enum

# values for enumeration 'FilterTypes'
FilterTypes = c_int # enum

# values for enumeration 'EndianType'
EndianType = c_int # enum

# values for enumeration 'DisposeType'
DisposeType = c_int # enum
class _TimerInfo(Structure):
    pass
class _Timer(Structure):
    pass
_Timer._pack_ = 4
_Timer._fields_ = [
    ('start', c_double),
    ('stop', c_double),
    ('total', c_double),
]
Timer = _Timer

# values for enumeration 'TimerState'
TimerState = c_int # enum
_TimerInfo._fields_ = [
    ('user', Timer),
    ('elapsed', Timer),
    ('state', TimerState),
    ('signature', c_ulong),
]
TimerInfo = _TimerInfo
MagickProgressMonitor = CFUNCTYPE(MagickBooleanType, STRING, MagickOffsetType, MagickSizeType, c_void_p)
class _BlobInfo(Structure):
    pass
BlobInfo = _BlobInfo
class _ProfileInfo(Structure):
    pass
_ProfileInfo._fields_ = [
    ('name', STRING),
    ('length', size_t),
    ('info', POINTER(c_ubyte)),
    ('signature', c_ulong),
]
ProfileInfo = _ProfileInfo

# values for enumeration 'InterpolatePixelMethod'
InterpolatePixelMethod = c_int # enum
_Image._pack_ = 4
_Image._fields_ = [
    ('storage_class', ClassType),
    ('colorspace', ColorspaceType),
    ('compression', CompressionType),
    ('quality', c_ulong),
    ('orientation', OrientationType),
    ('taint', MagickBooleanType),
    ('matte', MagickBooleanType),
    ('columns', c_ulong),
    ('rows', c_ulong),
    ('depth', c_ulong),
    ('colors', c_ulong),
    ('colormap', POINTER(PixelPacket)),
    ('background_color', PixelPacket),
    ('border_color', PixelPacket),
    ('matte_color', PixelPacket),
    ('gamma', c_double),
    ('chromaticity', ChromaticityInfo),
    ('rendering_intent', RenderingIntent),
    ('profiles', c_void_p),
    ('units', ResolutionType),
    ('montage', STRING),
    ('directory', STRING),
    ('geometry', STRING),
    ('offset', c_long),
    ('x_resolution', c_double),
    ('y_resolution', c_double),
    ('page', RectangleInfo),
    ('extract_info', RectangleInfo),
    ('tile_info', RectangleInfo),
    ('bias', c_double),
    ('blur', c_double),
    ('fuzz', c_double),
    ('filter', FilterTypes),
    ('interlace', InterlaceType),
    ('endian', EndianType),
    ('gravity', GravityType),
    ('compose', CompositeOperator),
    ('dispose', DisposeType),
    ('clip_mask', POINTER(_Image)),
    ('scene', c_ulong),
    ('delay', c_ulong),
    ('ticks_per_second', c_long),
    ('iterations', c_ulong),
    ('total_colors', c_ulong),
    ('start_loop', c_long),
    ('error', ErrorInfo),
    ('timer', TimerInfo),
    ('progress_monitor', MagickProgressMonitor),
    ('client_data', c_void_p),
    ('cache', c_void_p),
    ('attributes', c_void_p),
    ('ascii85', POINTER(Ascii85Info)),
    ('blob', POINTER(BlobInfo)),
    ('filename', c_char * 4096),
    ('magick_filename', c_char * 4096),
    ('magick', c_char * 4096),
    ('magick_columns', c_ulong),
    ('magick_rows', c_ulong),
    ('exception', ExceptionInfo),
    ('debug', MagickBooleanType),
    ('reference_count', c_long),
    ('semaphore', POINTER(SemaphoreInfo)),
    ('color_profile', ProfileInfo),
    ('iptc_profile', ProfileInfo),
    ('generic_profile', POINTER(ProfileInfo)),
    ('generic_profiles', c_ulong),
    ('signature', c_ulong),
    ('previous', POINTER(_Image)),
    ('list', POINTER(_Image)),
    ('next', POINTER(_Image)),
    ('interpolate', InterpolatePixelMethod),
    ('black_point_compensation', MagickBooleanType),
    ('transparent_color', PixelPacket),
    ('mask', POINTER(_Image)),
    ('tile_offset', RectangleInfo),
    ('properties', c_void_p),
    ('artifacts', c_void_p),
]
_ImageInfo._pack_ = 4
_ImageInfo._fields_ = [
    ('compression', CompressionType),
    ('orientation', OrientationType),
    ('temporary', MagickBooleanType),
    ('adjoin', MagickBooleanType),
    ('affirm', MagickBooleanType),
    ('antialias', MagickBooleanType),
    ('size', STRING),
    ('extract', STRING),
    ('page', STRING),
    ('scenes', STRING),
    ('scene', c_ulong),
    ('number_scenes', c_ulong),
    ('depth', c_ulong),
    ('interlace', InterlaceType),
    ('endian', EndianType),
    ('units', ResolutionType),
    ('quality', c_ulong),
    ('sampling_factor', STRING),
    ('server_name', STRING),
    ('font', STRING),
    ('texture', STRING),
    ('density', STRING),
    ('pointsize', c_double),
    ('fuzz', c_double),
    ('background_color', PixelPacket),
    ('border_color', PixelPacket),
    ('matte_color', PixelPacket),
    ('dither', MagickBooleanType),
    ('monochrome', MagickBooleanType),
    ('colors', c_ulong),
    ('colorspace', ColorspaceType),
    ('type', ImageType),
    ('preview_type', PreviewType),
    ('group', c_long),
    ('ping', MagickBooleanType),
    ('verbose', MagickBooleanType),
    ('view', STRING),
    ('authenticate', STRING),
    ('channel', ChannelType),
    ('attributes', POINTER(Image)),
    ('options', c_void_p),
    ('progress_monitor', MagickProgressMonitor),
    ('client_data', c_void_p),
    ('cache', c_void_p),
    ('stream', StreamHandler),
    ('file', POINTER(FILE)),
    ('blob', c_void_p),
    ('length', size_t),
    ('magick', c_char * 4096),
    ('unique', c_char * 4096),
    ('zero', c_char * 4096),
    ('filename', c_char * 4096),
    ('debug', MagickBooleanType),
    ('tile', STRING),
    ('subimage', c_ulong),
    ('subrange', c_ulong),
    ('pen', PixelPacket),
    ('signature', c_ulong),
    ('virtual_pixel_method', VirtualPixelMethod),
    ('transparent_color', PixelPacket),
    ('profile', c_void_p),
]
AcquireImagePixels = _lib.AcquireImagePixels
AcquireImagePixels.restype = POINTER(PixelPacket)
AcquireImagePixels.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, POINTER(ExceptionInfo)]
CatchImageException = _lib.CatchImageException
CatchImageException.restype = ExceptionType
CatchImageException.argtypes = [POINTER(Image)]
AllocateImage = _lib.AllocateImage
AllocateImage.restype = POINTER(Image)
AllocateImage.argtypes = [POINTER(ImageInfo)]
AppendImages = _lib.AppendImages
AppendImages.restype = POINTER(Image)
AppendImages.argtypes = [POINTER(Image), MagickBooleanType, POINTER(ExceptionInfo)]
AverageImages = _lib.AverageImages
AverageImages.restype = POINTER(Image)
AverageImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
CloneImage = _lib.CloneImage
CloneImage.restype = POINTER(Image)
CloneImage.argtypes = [POINTER(Image), c_ulong, c_ulong, MagickBooleanType, POINTER(ExceptionInfo)]
CombineImages = _lib.CombineImages
CombineImages.restype = POINTER(Image)
CombineImages.argtypes = [POINTER(Image), ChannelType, POINTER(ExceptionInfo)]
DestroyImage = _lib.DestroyImage
DestroyImage.restype = POINTER(Image)
DestroyImage.argtypes = [POINTER(Image)]
GetImageClipMask = _lib.GetImageClipMask
GetImageClipMask.restype = POINTER(Image)
GetImageClipMask.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
NewMagickImage = _lib.NewMagickImage
NewMagickImage.restype = POINTER(Image)
NewMagickImage.argtypes = [POINTER(ImageInfo), c_ulong, c_ulong, POINTER(MagickPixelPacket)]
ReferenceImage = _lib.ReferenceImage
ReferenceImage.restype = POINTER(Image)
ReferenceImage.argtypes = [POINTER(Image)]
CloneImageInfo = _lib.CloneImageInfo
CloneImageInfo.restype = POINTER(ImageInfo)
CloneImageInfo.argtypes = [POINTER(ImageInfo)]
DestroyImageInfo = _lib.DestroyImageInfo
DestroyImageInfo.restype = POINTER(ImageInfo)
DestroyImageInfo.argtypes = [POINTER(ImageInfo)]
GetImageType = _lib.GetImageType
GetImageType.restype = ImageType
GetImageType.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
GetIndexes = _lib.GetIndexes
GetIndexes.restype = POINTER(IndexPacket)
GetIndexes.argtypes = [POINTER(Image)]
AllocateImageColormap = _lib.AllocateImageColormap
AllocateImageColormap.restype = MagickBooleanType
AllocateImageColormap.argtypes = [POINTER(Image), c_ulong]
ClipImage = _lib.ClipImage
ClipImage.restype = MagickBooleanType
ClipImage.argtypes = [POINTER(Image)]
CycleColormapImage = _lib.CycleColormapImage
CycleColormapImage.restype = MagickBooleanType
CycleColormapImage.argtypes = [POINTER(Image), c_long]
GradientImage = _lib.GradientImage
GradientImage.restype = MagickBooleanType
GradientImage.argtypes = [POINTER(Image), POINTER(PixelPacket), POINTER(PixelPacket)]
IsTaintImage = _lib.IsTaintImage
IsTaintImage.restype = MagickBooleanType
IsTaintImage.argtypes = [POINTER(Image)]
IsMagickConflict = _lib.IsMagickConflict
IsMagickConflict.restype = MagickBooleanType
IsMagickConflict.argtypes = [STRING]
ListMagickInfo = _lib.ListMagickInfo
ListMagickInfo.restype = MagickBooleanType
ListMagickInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
ModifyImage = _lib.ModifyImage
ModifyImage.restype = MagickBooleanType
ModifyImage.argtypes = [POINTER(POINTER(Image)), POINTER(ExceptionInfo)]
PlasmaImage = _lib.PlasmaImage
PlasmaImage.restype = MagickBooleanType
PlasmaImage.argtypes = [POINTER(Image), POINTER(SegmentInfo), c_ulong, c_ulong]
SeparateImageChannel = _lib.SeparateImageChannel
SeparateImageChannel.restype = MagickBooleanType
SeparateImageChannel.argtypes = [POINTER(Image), ChannelType]
SetImageBackgroundColor = _lib.SetImageBackgroundColor
SetImageBackgroundColor.restype = MagickBooleanType
SetImageBackgroundColor.argtypes = [POINTER(Image)]
SetImageClipMask = _lib.SetImageClipMask
SetImageClipMask.restype = MagickBooleanType
SetImageClipMask.argtypes = [POINTER(Image), POINTER(Image)]
SetImageExtent = _lib.SetImageExtent
SetImageExtent.restype = MagickBooleanType
SetImageExtent.argtypes = [POINTER(Image), c_ulong, c_ulong]
SetImageInfo = _lib.SetImageInfo
SetImageInfo.restype = MagickBooleanType
SetImageInfo.argtypes = [POINTER(ImageInfo), MagickBooleanType, POINTER(ExceptionInfo)]
SetImageOpacity = _lib.SetImageOpacity
SetImageOpacity.restype = MagickBooleanType
SetImageOpacity.argtypes = [POINTER(Image), Quantum]
SetImageType = _lib.SetImageType
SetImageType.restype = MagickBooleanType
SetImageType.argtypes = [POINTER(Image), ImageType]
SortColormapByIntensity = _lib.SortColormapByIntensity
SortColormapByIntensity.restype = MagickBooleanType
SortColormapByIntensity.argtypes = [POINTER(Image)]
StripImage = _lib.StripImage
StripImage.restype = MagickBooleanType
StripImage.argtypes = [POINTER(Image)]
SyncImage = _lib.SyncImage
SyncImage.restype = MagickBooleanType
SyncImage.argtypes = [POINTER(Image)]
SyncImagePixels = _lib.SyncImagePixels
SyncImagePixels.restype = MagickBooleanType
SyncImagePixels.argtypes = [POINTER(Image)]
TextureImage = _lib.TextureImage
TextureImage.restype = MagickBooleanType
TextureImage.argtypes = [POINTER(Image), POINTER(Image)]
AcquireOnePixel = _lib.AcquireOnePixel
AcquireOnePixel.restype = PixelPacket
AcquireOnePixel.argtypes = [POINTER(Image), c_long, c_long, POINTER(ExceptionInfo)]
GetImagePixels = _lib.GetImagePixels
GetImagePixels.restype = POINTER(PixelPacket)
GetImagePixels.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong]
GetOnePixel = _lib.GetOnePixel
GetOnePixel.restype = PixelPacket
GetOnePixel.argtypes = [POINTER(Image), c_long, c_long]
GetPixels = _lib.GetPixels
GetPixels.restype = POINTER(PixelPacket)
GetPixels.argtypes = [POINTER(Image)]
SetImagePixels = _lib.SetImagePixels
SetImagePixels.restype = POINTER(PixelPacket)
SetImagePixels.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong]
GetImageVirtualPixelMethod = _lib.GetImageVirtualPixelMethod
GetImageVirtualPixelMethod.restype = VirtualPixelMethod
GetImageVirtualPixelMethod.argtypes = [POINTER(Image)]
SetImageVirtualPixelMethod = _lib.SetImageVirtualPixelMethod
SetImageVirtualPixelMethod.restype = VirtualPixelMethod
SetImageVirtualPixelMethod.argtypes = [POINTER(Image), VirtualPixelMethod]
AllocateNextImage = _lib.AllocateNextImage
AllocateNextImage.restype = None
AllocateNextImage.argtypes = [POINTER(ImageInfo), POINTER(Image)]
DestroyImagePixels = _lib.DestroyImagePixels
DestroyImagePixels.restype = None
DestroyImagePixels.argtypes = [POINTER(Image)]
GetImageException = _lib.GetImageException
GetImageException.restype = None
GetImageException.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
GetImageInfo = _lib.GetImageInfo
GetImageInfo.restype = None
GetImageInfo.argtypes = [POINTER(ImageInfo)]
SetImageInfoBlob = _lib.SetImageInfoBlob
SetImageInfoBlob.restype = None
SetImageInfoBlob.argtypes = [POINTER(ImageInfo), c_void_p, size_t]
SetImageInfoFile = _lib.SetImageInfoFile
SetImageInfoFile.restype = None
SetImageInfoFile.argtypes = [POINTER(ImageInfo), POINTER(FILE)]

# values for enumeration 'ImageLayerMethod'
ImageLayerMethod = c_int # enum
CoalesceImages = _lib.CoalesceImages
CoalesceImages.restype = POINTER(Image)
CoalesceImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
DeconstructImages = _lib.DeconstructImages
DeconstructImages.restype = POINTER(Image)
DeconstructImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
CloneImageList = _lib.CloneImageList
CloneImageList.restype = POINTER(Image)
CloneImageList.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
CloneImages = _lib.CloneImages
CloneImages.restype = POINTER(Image)
CloneImages.argtypes = [POINTER(Image), STRING, POINTER(ExceptionInfo)]
DestroyImageList = _lib.DestroyImageList
DestroyImageList.restype = POINTER(Image)
DestroyImageList.argtypes = [POINTER(Image)]
GetFirstImageInList = _lib.GetFirstImageInList
GetFirstImageInList.restype = POINTER(Image)
GetFirstImageInList.argtypes = [POINTER(Image)]
GetImageFromList = _lib.GetImageFromList
GetImageFromList.restype = POINTER(Image)
GetImageFromList.argtypes = [POINTER(Image), c_long]
GetLastImageInList = _lib.GetLastImageInList
GetLastImageInList.restype = POINTER(Image)
GetLastImageInList.argtypes = [POINTER(Image)]
GetNextImageInList = _lib.GetNextImageInList
GetNextImageInList.restype = POINTER(Image)
GetNextImageInList.argtypes = [POINTER(Image)]
GetPreviousImageInList = _lib.GetPreviousImageInList
GetPreviousImageInList.restype = POINTER(Image)
GetPreviousImageInList.argtypes = [POINTER(Image)]
ImageListToArray = _lib.ImageListToArray
ImageListToArray.restype = POINTER(POINTER(Image))
ImageListToArray.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
NewImageList = _lib.NewImageList
NewImageList.restype = POINTER(Image)
NewImageList.argtypes = []
RemoveImageFromList = _lib.RemoveImageFromList
RemoveImageFromList.restype = POINTER(Image)
RemoveImageFromList.argtypes = [POINTER(POINTER(Image))]
RemoveLastImageFromList = _lib.RemoveLastImageFromList
RemoveLastImageFromList.restype = POINTER(Image)
RemoveLastImageFromList.argtypes = [POINTER(POINTER(Image))]
RemoveFirstImageFromList = _lib.RemoveFirstImageFromList
RemoveFirstImageFromList.restype = POINTER(Image)
RemoveFirstImageFromList.argtypes = [POINTER(POINTER(Image))]
SpliceImageIntoList = _lib.SpliceImageIntoList
SpliceImageIntoList.restype = POINTER(Image)
SpliceImageIntoList.argtypes = [POINTER(POINTER(Image)), c_ulong, POINTER(Image)]
SplitImageList = _lib.SplitImageList
SplitImageList.restype = POINTER(Image)
SplitImageList.argtypes = [POINTER(Image)]
SyncNextImageInList = _lib.SyncNextImageInList
SyncNextImageInList.restype = POINTER(Image)
SyncNextImageInList.argtypes = [POINTER(Image)]
GetImageIndexInList = _lib.GetImageIndexInList
GetImageIndexInList.restype = c_long
GetImageIndexInList.argtypes = [POINTER(Image)]
GetImageListLength = _lib.GetImageListLength
GetImageListLength.restype = c_ulong
GetImageListLength.argtypes = [POINTER(Image)]
AppendImageToList = _lib.AppendImageToList
AppendImageToList.restype = None
AppendImageToList.argtypes = [POINTER(POINTER(Image)), POINTER(Image)]
DeleteImageFromList = _lib.DeleteImageFromList
DeleteImageFromList.restype = None
DeleteImageFromList.argtypes = [POINTER(POINTER(Image))]
InsertImageInList = _lib.InsertImageInList
InsertImageInList.restype = None
InsertImageInList.argtypes = [POINTER(POINTER(Image)), POINTER(Image)]
PrependImageToList = _lib.PrependImageToList
PrependImageToList.restype = None
PrependImageToList.argtypes = [POINTER(POINTER(Image)), POINTER(Image)]
ReplaceImageInList = _lib.ReplaceImageInList
ReplaceImageInList.restype = None
ReplaceImageInList.argtypes = [POINTER(POINTER(Image)), POINTER(Image)]
ReverseImageList = _lib.ReverseImageList
ReverseImageList.restype = None
ReverseImageList.argtypes = [POINTER(POINTER(Image))]
SyncImageList = _lib.SyncImageList
SyncImageList.restype = None
SyncImageList.argtypes = [POINTER(Image)]
class _LocaleInfo(Structure):
    pass
_LocaleInfo._fields_ = [
    ('path', STRING),
    ('tag', STRING),
    ('message', STRING),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_LocaleInfo)),
    ('next', POINTER(_LocaleInfo)),
    ('signature', c_ulong),
]
LocaleInfo = _LocaleInfo
GetLocaleList = _lib.GetLocaleList
GetLocaleList.restype = POINTER(STRING)
GetLocaleList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetLocaleMessage = _lib.GetLocaleMessage
GetLocaleMessage.restype = STRING
GetLocaleMessage.argtypes = [STRING]
GetLocaleInfo_ = _lib.GetLocaleInfo_
GetLocaleInfo_.restype = POINTER(LocaleInfo)
GetLocaleInfo_.argtypes = [STRING, POINTER(ExceptionInfo)]
GetLocaleInfoList = _lib.GetLocaleInfoList
GetLocaleInfoList.restype = POINTER(POINTER(LocaleInfo))
GetLocaleInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
DestroyLocaleOptions = _lib.DestroyLocaleOptions
DestroyLocaleOptions.restype = POINTER(LinkedListInfo)
DestroyLocaleOptions.argtypes = [POINTER(LinkedListInfo)]
GetLocaleOptions = _lib.GetLocaleOptions
GetLocaleOptions.restype = POINTER(LinkedListInfo)
GetLocaleOptions.argtypes = [STRING, POINTER(ExceptionInfo)]
ListLocaleInfo = _lib.ListLocaleInfo
ListLocaleInfo.restype = MagickBooleanType
ListLocaleInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
#DestroyLocaleList = _lib.DestroyLocaleList
#DestroyLocaleList.restype = None
#DestroyLocaleList.argtypes = []

# values for enumeration 'LogEventType'
LogEventType = c_int # enum
class _LogInfo(Structure):
    pass
_LogInfo._fields_ = [
]
LogInfo = _LogInfo
GetLogList = _lib.GetLogList
GetLogList.restype = POINTER(STRING)
GetLogList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
#GetLogInfo = _lib.GetLogInfo
#GetLogInfo.restype = POINTER(LogInfo)
#GetLogInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetLogInfoList = _lib.GetLogInfoList
GetLogInfoList.restype = POINTER(POINTER(LogInfo))
GetLogInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
SetLogEventMask = _lib.SetLogEventMask
SetLogEventMask.restype = LogEventType
SetLogEventMask.argtypes = [STRING]
IsEventLogging = _lib.IsEventLogging
IsEventLogging.restype = MagickBooleanType
IsEventLogging.argtypes = []
ListLogInfo = _lib.ListLogInfo
ListLogInfo.restype = MagickBooleanType
ListLogInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
LogMagickEvent = _lib.LogMagickEvent
LogMagickEvent.restype = MagickBooleanType
LogMagickEvent.argtypes = [LogEventType, STRING, STRING, c_ulong, STRING]
LogMagickEventList = _lib.LogMagickEventList
LogMagickEventList.restype = MagickBooleanType
LogMagickEventList.argtypes = [LogEventType, STRING, STRING, c_ulong, STRING, va_list]
#DestroyLogList = _lib.DestroyLogList
#DestroyLogList.restype = None
#DestroyLogList.argtypes = []
SetLogFormat = _lib.SetLogFormat
SetLogFormat.restype = None
SetLogFormat.argtypes = [STRING]
class _MagicInfo(Structure):
    pass
_MagicInfo._pack_ = 4
_MagicInfo._fields_ = [
    ('path', STRING),
    ('name', STRING),
    ('target', STRING),
    ('magic', POINTER(c_ubyte)),
    ('length', size_t),
    ('offset', MagickOffsetType),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_MagicInfo)),
    ('next', POINTER(_MagicInfo)),
    ('signature', c_ulong),
]
MagicInfo = _MagicInfo
GetMagicList = _lib.GetMagicList
GetMagicList.restype = POINTER(STRING)
GetMagicList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetMagicName = _lib.GetMagicName
GetMagicName.restype = STRING
GetMagicName.argtypes = [POINTER(MagicInfo)]
ListMagicInfo = _lib.ListMagicInfo
ListMagicInfo.restype = MagickBooleanType
ListMagicInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
GetMagicInfo = _lib.GetMagicInfo
GetMagicInfo.restype = POINTER(MagicInfo)
GetMagicInfo.argtypes = [POINTER(c_ubyte), size_t, POINTER(ExceptionInfo)]
GetMagicInfoList = _lib.GetMagicInfoList
GetMagicInfoList.restype = POINTER(POINTER(MagicInfo))
GetMagicInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
#DestroyMagicList = _lib.DestroyMagicList
#DestroyMagicList.restype = None
#DestroyMagicList.argtypes = []
QuantumAny = c_ulong
_BlobInfo._fields_ = [
]

# values for enumeration 'MagickThreadSupport'
MagickThreadSupport = c_int # enum
DecodeImageHandler = CFUNCTYPE(POINTER(Image), POINTER(ImageInfo), POINTER(ExceptionInfo))
EncodeImageHandler = CFUNCTYPE(MagickBooleanType, POINTER(ImageInfo), POINTER(Image))
IsImageFormatHandler = CFUNCTYPE(MagickBooleanType, POINTER(c_ubyte), size_t)
class _MagickInfo(Structure):
    pass
_MagickInfo._fields_ = [
    ('name', STRING),
    ('description', STRING),
    ('version', STRING),
    ('note', STRING),
    ('module', STRING),
    ('image_info', POINTER(ImageInfo)),
    ('decoder', POINTER(DecodeImageHandler)),
    ('encoder', POINTER(EncodeImageHandler)),
    ('magick', POINTER(IsImageFormatHandler)),
    ('client_data', c_void_p),
    ('adjoin', MagickBooleanType),
    ('raw', MagickBooleanType),
    ('endian_support', MagickBooleanType),
    ('blob_support', MagickBooleanType),
    ('seekable_stream', MagickBooleanType),
    ('thread_support', MagickStatusType),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_MagickInfo)),
    ('next', POINTER(_MagickInfo)),
    ('signature', c_ulong),
]
MagickInfo = _MagickInfo
GetMagickList = _lib.GetMagickList
GetMagickList.restype = POINTER(STRING)
GetMagickList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetImageMagick = _lib.GetImageMagick
GetImageMagick.restype = STRING
GetImageMagick.argtypes = [POINTER(c_ubyte), size_t]
GetMagickDescription = _lib.GetMagickDescription
GetMagickDescription.restype = STRING
GetMagickDescription.argtypes = [POINTER(MagickInfo)]
GetMagickAdjoin = _lib.GetMagickAdjoin
GetMagickAdjoin.restype = MagickBooleanType
GetMagickAdjoin.argtypes = [POINTER(MagickInfo)]
GetMagickBlobSupport = _lib.GetMagickBlobSupport
GetMagickBlobSupport.restype = MagickBooleanType
GetMagickBlobSupport.argtypes = [POINTER(MagickInfo)]
GetMagickEndianSupport = _lib.GetMagickEndianSupport
GetMagickEndianSupport.restype = MagickBooleanType
GetMagickEndianSupport.argtypes = [POINTER(MagickInfo)]
GetMagickSeekableStream = _lib.GetMagickSeekableStream
GetMagickSeekableStream.restype = MagickBooleanType
GetMagickSeekableStream.argtypes = [POINTER(MagickInfo)]
IsMagickInstantiated = _lib.IsMagickInstantiated
IsMagickInstantiated.restype = MagickBooleanType
IsMagickInstantiated.argtypes = []
UnregisterMagickInfo = _lib.UnregisterMagickInfo
UnregisterMagickInfo.restype = MagickBooleanType
UnregisterMagickInfo.argtypes = [STRING]
GetMagickInfo = _lib.GetMagickInfo
GetMagickInfo.restype = POINTER(MagickInfo)
GetMagickInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetMagickInfoList = _lib.GetMagickInfoList
GetMagickInfoList.restype = POINTER(POINTER(MagickInfo))
GetMagickInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
RegisterMagickInfo = _lib.RegisterMagickInfo
RegisterMagickInfo.restype = POINTER(MagickInfo)
RegisterMagickInfo.argtypes = [POINTER(MagickInfo)]
SetMagickInfo = _lib.SetMagickInfo
SetMagickInfo.restype = POINTER(MagickInfo)
SetMagickInfo.argtypes = [STRING]
GetMagickThreadSupport = _lib.GetMagickThreadSupport
GetMagickThreadSupport.restype = MagickStatusType
GetMagickThreadSupport.argtypes = [POINTER(MagickInfo)]
#DestroyMagickList = _lib.DestroyMagickList
#DestroyMagickList.restype = None
#DestroyMagickList.argtypes = []
AcquireMagickMemory = _lib.AcquireMagickMemory
AcquireMagickMemory.restype = c_void_p
AcquireMagickMemory.argtypes = [size_t]
CopyMagickMemory = _lib.CopyMagickMemory
CopyMagickMemory.restype = c_void_p
CopyMagickMemory.argtypes = [c_void_p, c_void_p, size_t]
DestroyMagickMemory = _lib.DestroyMagickMemory
DestroyMagickMemory.restype = None
DestroyMagickMemory.argtypes = []
RelinquishMagickMemory = _lib.RelinquishMagickMemory
RelinquishMagickMemory.restype = c_void_p
RelinquishMagickMemory.argtypes = [c_void_p]
ResetMagickMemory = _lib.ResetMagickMemory
ResetMagickMemory.restype = c_void_p
ResetMagickMemory.argtypes = [c_void_p, c_int, size_t]
ResizeMagickMemory = _lib.ResizeMagickMemory
ResizeMagickMemory.restype = c_void_p
ResizeMagickMemory.argtypes = [c_void_p, size_t]
class _MimeInfo(Structure):
    pass
_MimeInfo._fields_ = [
]
MimeInfo = _MimeInfo
MagickToMime = _lib.MagickToMime
MagickToMime.restype = STRING
MagickToMime.argtypes = [STRING]

# values for enumeration 'MagickModuleType'
MagickModuleType = c_int # enum
class _ModuleInfo(Structure):
    pass
__time_t = c_long
time_t = __time_t
_ModuleInfo._fields_ = [
    ('path', STRING),
    ('tag', STRING),
    ('handle', c_void_p),
    ('unregister_module', CFUNCTYPE(None)),
    ('register_module', CFUNCTYPE(c_ulong)),
    ('load_time', time_t),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_ModuleInfo)),
    ('next', POINTER(_ModuleInfo)),
    ('signature', c_ulong),
]
ModuleInfo = _ModuleInfo
ImageFilterHandler = CFUNCTYPE(c_ulong, POINTER(POINTER(Image)), c_int, POINTER(STRING), POINTER(ExceptionInfo))
GetModuleList = _lib.GetModuleList
GetModuleList.restype = POINTER(STRING)
GetModuleList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
GetModuleInfo = _lib.GetModuleInfo
GetModuleInfo.restype = POINTER(ModuleInfo)
GetModuleInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetModuleInfoList = _lib.GetModuleInfoList
GetModuleInfoList.restype = POINTER(POINTER(ModuleInfo))
GetModuleInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
ListModuleInfo = _lib.ListModuleInfo
ListModuleInfo.restype = MagickBooleanType
ListModuleInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
OpenModule = _lib.OpenModule
OpenModule.restype = MagickBooleanType
OpenModule.argtypes = [STRING, POINTER(ExceptionInfo)]
OpenModules = _lib.OpenModules
OpenModules.restype = MagickBooleanType
OpenModules.argtypes = [POINTER(ExceptionInfo)]
DestroyModuleList = _lib.DestroyModuleList
DestroyModuleList.restype = None
DestroyModuleList.argtypes = []
RegisterStaticModules = _lib.RegisterStaticModules
RegisterStaticModules.restype = None
RegisterStaticModules.argtypes = []
UnregisterStaticModules = _lib.UnregisterStaticModules
UnregisterStaticModules.restype = None
UnregisterStaticModules.argtypes = []
SetImageProgressMonitor = _lib.SetImageProgressMonitor
SetImageProgressMonitor.restype = MagickProgressMonitor
SetImageProgressMonitor.argtypes = [POINTER(Image), MagickProgressMonitor, c_void_p]
SetImageInfoProgressMonitor = _lib.SetImageInfoProgressMonitor
SetImageInfoProgressMonitor.restype = MagickProgressMonitor
SetImageInfoProgressMonitor.argtypes = [POINTER(ImageInfo), MagickProgressMonitor, c_void_p]

# values for enumeration 'MontageMode'
MontageMode = c_int # enum
class _MontageInfo(Structure):
    pass
_MontageInfo._pack_ = 4
_MontageInfo._fields_ = [
    ('geometry', STRING),
    ('tile', STRING),
    ('title', STRING),
    ('frame', STRING),
    ('texture', STRING),
    ('font', STRING),
    ('pointsize', c_double),
    ('border_width', c_ulong),
    ('shadow', MagickBooleanType),
    ('fill', PixelPacket),
    ('stroke', PixelPacket),
    ('background_color', PixelPacket),
    ('border_color', PixelPacket),
    ('matte_color', PixelPacket),
    ('gravity', GravityType),
    ('filename', c_char * 4096),
    ('debug', MagickBooleanType),
    ('signature', c_ulong),
]
MontageInfo = _MontageInfo
MontageImages = _lib.MontageImages
MontageImages.restype = POINTER(Image)
MontageImages.argtypes = [POINTER(Image), POINTER(MontageInfo), POINTER(ExceptionInfo)]
CloneMontageInfo = _lib.CloneMontageInfo
CloneMontageInfo.restype = POINTER(MontageInfo)
CloneMontageInfo.argtypes = [POINTER(ImageInfo), POINTER(MontageInfo)]
DestroyMontageInfo = _lib.DestroyMontageInfo
DestroyMontageInfo.restype = POINTER(MontageInfo)
DestroyMontageInfo.argtypes = [POINTER(MontageInfo)]
GetMontageInfo = _lib.GetMontageInfo
GetMontageInfo.restype = None
GetMontageInfo.argtypes = [POINTER(ImageInfo), POINTER(MontageInfo)]

# values for enumeration 'MagickOption'
MagickOption = c_int # enum
class _OptionInfo(Structure):
    pass
_OptionInfo._fields_ = [
    ('mnemonic', STRING),
    ('type', c_long),
]
OptionInfo = _OptionInfo
GetMagickOptions = _lib.GetMagickOptions
GetMagickOptions.restype = POINTER(STRING)
GetMagickOptions.argtypes = [MagickOption]
GetNextImageOption = _lib.GetNextImageOption
GetNextImageOption.restype = STRING
GetNextImageOption.argtypes = [POINTER(ImageInfo)]
RemoveImageOption = _lib.RemoveImageOption
RemoveImageOption.restype = STRING
RemoveImageOption.argtypes = [POINTER(ImageInfo), STRING]
GetImageOption = _lib.GetImageOption
GetImageOption.restype = STRING
GetImageOption.argtypes = [POINTER(ImageInfo), STRING]
MagickOptionToMnemonic = _lib.MagickOptionToMnemonic
MagickOptionToMnemonic.restype = STRING
MagickOptionToMnemonic.argtypes = [MagickOption, c_long]
ParseChannelOption = _lib.ParseChannelOption
ParseChannelOption.restype = c_long
ParseChannelOption.argtypes = [STRING]
ParseMagickOption = _lib.ParseMagickOption
ParseMagickOption.restype = c_long
ParseMagickOption.argtypes = [MagickOption, MagickBooleanType, STRING]
CloneImageOptions = _lib.CloneImageOptions
CloneImageOptions.restype = MagickBooleanType
CloneImageOptions.argtypes = [POINTER(ImageInfo), POINTER(ImageInfo)]
DefineImageOption = _lib.DefineImageOption
DefineImageOption.restype = MagickBooleanType
DefineImageOption.argtypes = [POINTER(ImageInfo), STRING]
DeleteImageOption = _lib.DeleteImageOption
DeleteImageOption.restype = MagickBooleanType
DeleteImageOption.argtypes = [POINTER(ImageInfo), STRING]
IsMagickOption = _lib.IsMagickOption
IsMagickOption.restype = MagickBooleanType
IsMagickOption.argtypes = [STRING]
SetImageOption = _lib.SetImageOption
SetImageOption.restype = MagickBooleanType
SetImageOption.argtypes = [POINTER(ImageInfo), STRING, STRING]
DestroyImageOptions = _lib.DestroyImageOptions
DestroyImageOptions.restype = None
DestroyImageOptions.argtypes = [POINTER(ImageInfo)]
ResetImageOptionIterator = _lib.ResetImageOptionIterator
ResetImageOptionIterator.restype = None
ResetImageOptionIterator.argtypes = [POINTER(ImageInfo)]
OilPaintImage = _lib.OilPaintImage
OilPaintImage.restype = POINTER(Image)
OilPaintImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
class _LongPixelPacket(Structure):
    pass
_LongPixelPacket._fields_ = [
    ('red', c_ulong),
    ('green', c_ulong),
    ('blue', c_ulong),
    ('opacity', c_ulong),
    ('index', c_ulong),
]
LongPixelPacket = _LongPixelPacket
ExportImagePixels = _lib.ExportImagePixels
ExportImagePixels.restype = MagickBooleanType
ExportImagePixels.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, STRING, StorageType, c_void_p, POINTER(ExceptionInfo)]
ImportImagePixels = _lib.ImportImagePixels
ImportImagePixels.restype = MagickBooleanType
ImportImagePixels.argtypes = [POINTER(Image), c_long, c_long, c_ulong, c_ulong, STRING, StorageType, c_void_p]
GetMagickPixelPacket = _lib.GetMagickPixelPacket
GetMagickPixelPacket.restype = None
GetMagickPixelPacket.argtypes = [POINTER(Image), POINTER(MagickPixelPacket)]
GetImageTotalInkDensity = _lib.GetImageTotalInkDensity
GetImageTotalInkDensity.restype = c_double
GetImageTotalInkDensity.argtypes = [POINTER(Image)]
GetNextImageProfile = _lib.GetNextImageProfile
GetNextImageProfile.restype = STRING
GetNextImageProfile.argtypes = [POINTER(Image)]
class _StringInfo(Structure):
    pass
StringInfo = _StringInfo
GetImageProfile = _lib.GetImageProfile
GetImageProfile.restype = POINTER(StringInfo)
GetImageProfile.argtypes = [POINTER(Image), STRING]
CloneImageProfiles = _lib.CloneImageProfiles
CloneImageProfiles.restype = MagickBooleanType
CloneImageProfiles.argtypes = [POINTER(Image), POINTER(Image)]
ProfileImage = _lib.ProfileImage
ProfileImage.restype = MagickBooleanType
ProfileImage.argtypes = [POINTER(Image), STRING, c_void_p, size_t, MagickBooleanType]
SetImageProfile = _lib.SetImageProfile
SetImageProfile.restype = MagickBooleanType
SetImageProfile.argtypes = [POINTER(Image), STRING, POINTER(StringInfo)]
RemoveImageProfile = _lib.RemoveImageProfile
RemoveImageProfile.restype = POINTER(StringInfo)
RemoveImageProfile.argtypes = [POINTER(Image), STRING]
DestroyImageProfiles = _lib.DestroyImageProfiles
DestroyImageProfiles.restype = None
DestroyImageProfiles.argtypes = [POINTER(Image)]
ResetImageProfileIterator = _lib.ResetImageProfileIterator
ResetImageProfileIterator.restype = None
ResetImageProfileIterator.argtypes = [POINTER(Image)]
class _QuantizeInfo(Structure):
    pass
_QuantizeInfo._fields_ = [
    ('number_colors', c_ulong),
    ('tree_depth', c_ulong),
    ('dither', MagickBooleanType),
    ('colorspace', ColorspaceType),
    ('measure_error', MagickBooleanType),
    ('signature', c_ulong),
]
QuantizeInfo = _QuantizeInfo
GetImageQuantizeError = _lib.GetImageQuantizeError
GetImageQuantizeError.restype = MagickBooleanType
GetImageQuantizeError.argtypes = [POINTER(Image)]
MapImage = _lib.MapImage
MapImage.restype = MagickBooleanType
MapImage.argtypes = [POINTER(Image), POINTER(Image), MagickBooleanType]
MapImages = _lib.MapImages
MapImages.restype = MagickBooleanType
MapImages.argtypes = [POINTER(Image), POINTER(Image), MagickBooleanType]
PosterizeImage = _lib.PosterizeImage
PosterizeImage.restype = MagickBooleanType
PosterizeImage.argtypes = [POINTER(Image), c_ulong, MagickBooleanType]
QuantizeImage = _lib.QuantizeImage
QuantizeImage.restype = MagickBooleanType
QuantizeImage.argtypes = [POINTER(QuantizeInfo), POINTER(Image)]
QuantizeImages = _lib.QuantizeImages
QuantizeImages.restype = MagickBooleanType
QuantizeImages.argtypes = [POINTER(QuantizeInfo), POINTER(Image)]
CloneQuantizeInfo = _lib.CloneQuantizeInfo
CloneQuantizeInfo.restype = POINTER(QuantizeInfo)
CloneQuantizeInfo.argtypes = [POINTER(QuantizeInfo)]
DestroyQuantizeInfo = _lib.DestroyQuantizeInfo
DestroyQuantizeInfo.restype = POINTER(QuantizeInfo)
DestroyQuantizeInfo.argtypes = [POINTER(QuantizeInfo)]
CompressImageColormap = _lib.CompressImageColormap
CompressImageColormap.restype = None
CompressImageColormap.argtypes = [POINTER(Image)]
GetQuantizeInfo = _lib.GetQuantizeInfo
GetQuantizeInfo.restype = None
GetQuantizeInfo.argtypes = [POINTER(QuantizeInfo)]

# values for enumeration 'QuantumFormatType'
QuantumFormatType = c_int # enum
class _QuantumInfo(Structure):
    pass
_QuantumInfo._pack_ = 4
_QuantumInfo._fields_ = [
    ('quantum', c_ulong),
    ('format', QuantumFormatType),
    ('minimum', c_double),
    ('maximum', c_double),
    ('scale', c_double),
    ('pad', size_t),
    ('min_is_white', MagickBooleanType),
    ('pack', MagickBooleanType),
    ('semaphore', POINTER(SemaphoreInfo)),
    ('signature', c_ulong),
]
QuantumInfo = _QuantumInfo
ExportQuantumPixels = _lib.ExportQuantumPixels
ExportQuantumPixels.restype = MagickBooleanType
ExportQuantumPixels.argtypes = [POINTER(Image), POINTER(QuantumInfo), QuantumType, POINTER(c_ubyte)]
ImportQuantumPixels = _lib.ImportQuantumPixels
ImportQuantumPixels.restype = MagickBooleanType
ImportQuantumPixels.argtypes = [POINTER(Image), POINTER(QuantumInfo), QuantumType, POINTER(c_ubyte)]
GetRandomValue = _lib.GetRandomValue
GetRandomValue.restype = c_double
GetRandomValue.argtypes = []
#DestroyRandomReservoir = _lib.DestroyRandomReservoir
#DestroyRandomReservoir.restype = None
#DestroyRandomReservoir.argtypes = []
#DistillRandomEvent = _lib.DistillRandomEvent
#DistillRandomEvent.restype = None
#DistillRandomEvent.argtypes = [POINTER(c_ubyte), size_t]
GetRandomKey = _lib.GetRandomKey
GetRandomKey.restype = None
GetRandomKey.argtypes = [POINTER(c_ubyte), size_t]
class _ResampleFilter(Structure):
    pass
_ResampleFilter._fields_ = [
]
ResampleFilter = _ResampleFilter
MagnifyImage = _lib.MagnifyImage
MagnifyImage.restype = POINTER(Image)
MagnifyImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
MinifyImage = _lib.MinifyImage
MinifyImage.restype = POINTER(Image)
MinifyImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
ResizeImage = _lib.ResizeImage
ResizeImage.restype = POINTER(Image)
ResizeImage.argtypes = [POINTER(Image), c_ulong, c_ulong, FilterTypes, c_double, POINTER(ExceptionInfo)]
SampleImage = _lib.SampleImage
SampleImage.restype = POINTER(Image)
SampleImage.argtypes = [POINTER(Image), c_ulong, c_ulong, POINTER(ExceptionInfo)]
ScaleImage = _lib.ScaleImage
ScaleImage.restype = POINTER(Image)
ScaleImage.argtypes = [POINTER(Image), c_ulong, c_ulong, POINTER(ExceptionInfo)]
ThumbnailImage = _lib.ThumbnailImage
ThumbnailImage.restype = POINTER(Image)
ThumbnailImage.argtypes = [POINTER(Image), c_ulong, c_ulong, POINTER(ExceptionInfo)]
ZoomImage = _lib.ZoomImage
ZoomImage.restype = POINTER(Image)
ZoomImage.argtypes = [POINTER(Image), c_ulong, c_ulong, POINTER(ExceptionInfo)]

# values for enumeration 'ResourceType'
ResourceType = c_int # enum
AcquireUniqueFileResource = _lib.AcquireUniqueFileResource
AcquireUniqueFileResource.restype = c_int
AcquireUniqueFileResource.argtypes = [STRING]
AcquireMagickResource = _lib.AcquireMagickResource
AcquireMagickResource.restype = MagickBooleanType
AcquireMagickResource.argtypes = [ResourceType, MagickSizeType]
RelinquishUniqueFileResource = _lib.RelinquishUniqueFileResource
RelinquishUniqueFileResource.restype = MagickBooleanType
RelinquishUniqueFileResource.argtypes = [STRING]
ListMagickResourceInfo = _lib.ListMagickResourceInfo
ListMagickResourceInfo.restype = MagickBooleanType
ListMagickResourceInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
SetMagickResourceLimit = _lib.SetMagickResourceLimit
SetMagickResourceLimit.restype = MagickBooleanType
SetMagickResourceLimit.argtypes = [ResourceType, MagickSizeType]
GetMagickResource = _lib.GetMagickResource
GetMagickResource.restype = MagickSizeType
GetMagickResource.argtypes = [ResourceType]
GetMagickResourceLimit = _lib.GetMagickResourceLimit
GetMagickResourceLimit.restype = MagickSizeType
GetMagickResourceLimit.argtypes = [ResourceType]
#AsynchronousDestroyMagickResources = _lib.AsynchronousDestroyMagickResources
#AsynchronousDestroyMagickResources.restype = None
#AsynchronousDestroyMagickResources.argtypes = []
#DestroyMagickResources = _lib.DestroyMagickResources
#DestroyMagickResources.restype = None
#DestroyMagickResources.argtypes = []
#InitializeMagickResources = _lib.InitializeMagickResources
#InitializeMagickResources.restype = None
#InitializeMagickResources.argtypes = []
RelinquishMagickResource = _lib.RelinquishMagickResource
RelinquishMagickResource.restype = None
RelinquishMagickResource.argtypes = [ResourceType, MagickSizeType]
GetImageDynamicThreshold = _lib.GetImageDynamicThreshold
GetImageDynamicThreshold.restype = MagickPixelPacket
GetImageDynamicThreshold.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
SegmentImage = _lib.SegmentImage
SegmentImage.restype = MagickBooleanType
SegmentImage.argtypes = [POINTER(Image), ColorspaceType, MagickBooleanType, c_double, c_double]
SemaphoreInfo._fields_ = [
]
LockSemaphoreInfo = _lib.LockSemaphoreInfo
LockSemaphoreInfo.restype = MagickBooleanType
LockSemaphoreInfo.argtypes = [POINTER(SemaphoreInfo)]
UnlockSemaphoreInfo = _lib.UnlockSemaphoreInfo
UnlockSemaphoreInfo.restype = MagickBooleanType
UnlockSemaphoreInfo.argtypes = [POINTER(SemaphoreInfo)]
AllocateSemaphoreInfo = _lib.AllocateSemaphoreInfo
AllocateSemaphoreInfo.restype = POINTER(SemaphoreInfo)
AllocateSemaphoreInfo.argtypes = []
DestroySemaphoreInfo = _lib.DestroySemaphoreInfo
DestroySemaphoreInfo.restype = POINTER(SemaphoreInfo)
DestroySemaphoreInfo.argtypes = [POINTER(SemaphoreInfo)]
AcquireSemaphoreInfo = _lib.AcquireSemaphoreInfo
AcquireSemaphoreInfo.restype = None
AcquireSemaphoreInfo.argtypes = [POINTER(POINTER(SemaphoreInfo))]
#DestroySemaphore = _lib.DestroySemaphore
#DestroySemaphore.restype = None
#DestroySemaphore.argtypes = []
#InitializeSemaphore = _lib.InitializeSemaphore
#InitializeSemaphore.restype = None
#InitializeSemaphore.argtypes = []
RelinquishSemaphoreInfo = _lib.RelinquishSemaphoreInfo
RelinquishSemaphoreInfo.restype = None
RelinquishSemaphoreInfo.argtypes = [POINTER(SemaphoreInfo)]
AffineTransformImage = _lib.AffineTransformImage
AffineTransformImage.restype = POINTER(Image)
AffineTransformImage.argtypes = [POINTER(Image), POINTER(AffineMatrix), POINTER(ExceptionInfo)]
RotateImage = _lib.RotateImage
RotateImage.restype = POINTER(Image)
RotateImage.argtypes = [POINTER(Image), c_double, POINTER(ExceptionInfo)]
ShearImage = _lib.ShearImage
ShearImage.restype = POINTER(Image)
ShearImage.argtypes = [POINTER(Image), c_double, c_double, POINTER(ExceptionInfo)]
class _SignatureInfo(Structure):
    pass
_SignatureInfo._fields_ = [
]
SignatureInfo = _SignatureInfo
SignatureImage = _lib.SignatureImage
SignatureImage.restype = MagickBooleanType
SignatureImage.argtypes = [POINTER(Image)]
FinalizeSignature = _lib.FinalizeSignature
FinalizeSignature.restype = None
FinalizeSignature.argtypes = [POINTER(SignatureInfo)]
UpdateSignature = _lib.UpdateSignature
UpdateSignature.restype = None
UpdateSignature.argtypes = [POINTER(SignatureInfo), POINTER(StringInfo)]
class _SplayTreeInfo(Structure):
    pass
_SplayTreeInfo._fields_ = [
]
SplayTreeInfo = _SplayTreeInfo
AddValueToSplayTree = _lib.AddValueToSplayTree
AddValueToSplayTree.restype = MagickBooleanType
AddValueToSplayTree.argtypes = [POINTER(SplayTreeInfo), c_void_p, c_void_p]
CompareSplayTreeString = _lib.CompareSplayTreeString
CompareSplayTreeString.restype = c_int
CompareSplayTreeString.argtypes = [c_void_p, c_void_p]
CompareSplayTreeStringInfo = _lib.CompareSplayTreeStringInfo
CompareSplayTreeStringInfo.restype = c_int
CompareSplayTreeStringInfo.argtypes = [c_void_p, c_void_p]
DestroySplayTree = _lib.DestroySplayTree
DestroySplayTree.restype = POINTER(SplayTreeInfo)
DestroySplayTree.argtypes = [POINTER(SplayTreeInfo)]
NewSplayTree = _lib.NewSplayTree
NewSplayTree.restype = POINTER(SplayTreeInfo)
NewSplayTree.argtypes = [CFUNCTYPE(c_int, c_void_p, c_void_p), CFUNCTYPE(c_void_p, c_void_p), CFUNCTYPE(c_void_p, c_void_p)]
GetNumberOfNodesInSplayTree = _lib.GetNumberOfNodesInSplayTree
GetNumberOfNodesInSplayTree.restype = c_ulong
GetNumberOfNodesInSplayTree.argtypes = [POINTER(SplayTreeInfo)]
GetNextKeyInSplayTree = _lib.GetNextKeyInSplayTree
GetNextKeyInSplayTree.restype = c_void_p
GetNextKeyInSplayTree.argtypes = [POINTER(SplayTreeInfo)]
GetNextValueInSplayTree = _lib.GetNextValueInSplayTree
GetNextValueInSplayTree.restype = c_void_p
GetNextValueInSplayTree.argtypes = [POINTER(SplayTreeInfo)]
GetValueFromSplayTree = _lib.GetValueFromSplayTree
GetValueFromSplayTree.restype = c_void_p
GetValueFromSplayTree.argtypes = [POINTER(SplayTreeInfo), c_void_p]
RemoveNodeByValueFromSplayTree = _lib.RemoveNodeByValueFromSplayTree
RemoveNodeByValueFromSplayTree.restype = c_void_p
RemoveNodeByValueFromSplayTree.argtypes = [POINTER(SplayTreeInfo), c_void_p]
RemoveNodeFromSplayTree = _lib.RemoveNodeFromSplayTree
RemoveNodeFromSplayTree.restype = c_void_p
RemoveNodeFromSplayTree.argtypes = [POINTER(SplayTreeInfo), c_void_p]
ResetSplayTreeIterator = _lib.ResetSplayTreeIterator
ResetSplayTreeIterator.restype = None
ResetSplayTreeIterator.argtypes = [POINTER(SplayTreeInfo)]
class _ChannelStatistics(Structure):
    pass
_ChannelStatistics._pack_ = 4
_ChannelStatistics._fields_ = [
    ('depth', c_ulong),
    ('minima', c_double),
    ('maxima', c_double),
    ('mean', c_double),
    ('standard_deviation', c_double),
]
ChannelStatistics = _ChannelStatistics
GetImageChannelStatistics = _lib.GetImageChannelStatistics
GetImageChannelStatistics.restype = POINTER(ChannelStatistics)
GetImageChannelStatistics.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
GetImageChannelExtrema = _lib.GetImageChannelExtrema
GetImageChannelExtrema.restype = MagickBooleanType
GetImageChannelExtrema.argtypes = [POINTER(Image), ChannelType, POINTER(c_ulong), POINTER(c_ulong), POINTER(ExceptionInfo)]
GetImageChannelMean = _lib.GetImageChannelMean
GetImageChannelMean.restype = MagickBooleanType
GetImageChannelMean.argtypes = [POINTER(Image), ChannelType, POINTER(c_double), POINTER(c_double), POINTER(ExceptionInfo)]
GetImageExtrema = _lib.GetImageExtrema
GetImageExtrema.restype = MagickBooleanType
GetImageExtrema.argtypes = [POINTER(Image), POINTER(c_ulong), POINTER(c_ulong), POINTER(ExceptionInfo)]
GetImageMean = _lib.GetImageMean
GetImageMean.restype = MagickBooleanType
GetImageMean.argtypes = [POINTER(Image), POINTER(c_double), POINTER(c_double), POINTER(ExceptionInfo)]
SetImageChannelDepth = _lib.SetImageChannelDepth
SetImageChannelDepth.restype = MagickBooleanType
SetImageChannelDepth.argtypes = [POINTER(Image), ChannelType, c_ulong]
SetImageDepth = _lib.SetImageDepth
SetImageDepth.restype = MagickBooleanType
SetImageDepth.argtypes = [POINTER(Image), c_ulong]
GetImageBoundingBox = _lib.GetImageBoundingBox
GetImageBoundingBox.restype = RectangleInfo
GetImageBoundingBox.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
GetImageChannelDepth = _lib.GetImageChannelDepth
GetImageChannelDepth.restype = c_ulong
GetImageChannelDepth.argtypes = [POINTER(Image), ChannelType, POINTER(ExceptionInfo)]
GetImageDepth = _lib.GetImageDepth
GetImageDepth.restype = c_ulong
GetImageDepth.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
GetImageQuantumDepth = _lib.GetImageQuantumDepth
GetImageQuantumDepth.restype = c_ulong
GetImageQuantumDepth.argtypes = [POINTER(Image), MagickBooleanType]
ReadStream = _lib.ReadStream
ReadStream.restype = POINTER(Image)
ReadStream.argtypes = [POINTER(ImageInfo), StreamHandler, POINTER(ExceptionInfo)]
WriteStream = _lib.WriteStream
WriteStream.restype = MagickBooleanType
WriteStream.argtypes = [POINTER(ImageInfo), POINTER(Image), StreamHandler]
_StringInfo._fields_ = [
    ('path', c_char * 4096),
    ('datum', POINTER(c_ubyte)),
    ('length', size_t),
    ('signature', c_ulong),
]
AcquireString = _lib.AcquireString
AcquireString.restype = STRING
AcquireString.argtypes = [STRING]
CloneString = _lib.CloneString
CloneString.restype = STRING
CloneString.argtypes = [POINTER(STRING), STRING]
ConstantString = _lib.ConstantString
ConstantString.restype = STRING
ConstantString.argtypes = [STRING]
DestroyString = _lib.DestroyString
DestroyString.restype = STRING
DestroyString.argtypes = [STRING]
DestroyStringList = _lib.DestroyStringList
DestroyStringList.restype = POINTER(STRING)
DestroyStringList.argtypes = [POINTER(STRING)]
EscapeString = _lib.EscapeString
EscapeString.restype = STRING
EscapeString.argtypes = [STRING, c_char]
FileToString = _lib.FileToString
FileToString.restype = STRING
FileToString.argtypes = [STRING, size_t, POINTER(ExceptionInfo)]
StringInfoToString = _lib.StringInfoToString
StringInfoToString.restype = STRING
StringInfoToString.argtypes = [POINTER(StringInfo)]
StringToArgv = _lib.StringToArgv
StringToArgv.restype = POINTER(STRING)
StringToArgv.argtypes = [STRING, POINTER(c_int)]
StringToList = _lib.StringToList
StringToList.restype = POINTER(STRING)
StringToList.argtypes = [STRING]
#StringToDouble = _lib.StringToDouble
#StringToDouble.restype = c_double
#StringToDouble.argtypes = [STRING, c_double]
FormatMagickString = _lib.FormatMagickString
FormatMagickString.restype = c_long
FormatMagickString.argtypes = [STRING, size_t, STRING]
FormatMagickStringList = _lib.FormatMagickStringList
FormatMagickStringList.restype = c_long
FormatMagickStringList.argtypes = [STRING, size_t, STRING, va_list]
LocaleCompare = _lib.LocaleCompare
LocaleCompare.restype = c_long
LocaleCompare.argtypes = [STRING, STRING]
LocaleNCompare = _lib.LocaleNCompare
LocaleNCompare.restype = c_long
LocaleNCompare.argtypes = [STRING, STRING, size_t]
ConcatenateString = _lib.ConcatenateString
ConcatenateString.restype = MagickBooleanType
ConcatenateString.argtypes = [POINTER(STRING), STRING]
SubstituteString = _lib.SubstituteString
SubstituteString.restype = MagickBooleanType
SubstituteString.argtypes = [POINTER(STRING), STRING, STRING]
CompareStringInfo = _lib.CompareStringInfo
CompareStringInfo.restype = c_int
CompareStringInfo.argtypes = [POINTER(StringInfo), POINTER(StringInfo)]
ConcatenateMagickString = _lib.ConcatenateMagickString
ConcatenateMagickString.restype = size_t
ConcatenateMagickString.argtypes = [STRING, STRING, size_t]
CopyMagickString = _lib.CopyMagickString
CopyMagickString.restype = size_t
CopyMagickString.argtypes = [STRING, STRING, size_t]
AcquireStringInfo = _lib.AcquireStringInfo
AcquireStringInfo.restype = POINTER(StringInfo)
AcquireStringInfo.argtypes = [size_t]
CloneStringInfo = _lib.CloneStringInfo
CloneStringInfo.restype = POINTER(StringInfo)
CloneStringInfo.argtypes = [POINTER(StringInfo)]
ConfigureFileToStringInfo = _lib.ConfigureFileToStringInfo
ConfigureFileToStringInfo.restype = POINTER(StringInfo)
ConfigureFileToStringInfo.argtypes = [STRING]
DestroyStringInfo = _lib.DestroyStringInfo
DestroyStringInfo.restype = POINTER(StringInfo)
DestroyStringInfo.argtypes = [POINTER(StringInfo)]
FileToStringInfo = _lib.FileToStringInfo
FileToStringInfo.restype = POINTER(StringInfo)
FileToStringInfo.argtypes = [STRING, size_t, POINTER(ExceptionInfo)]
SplitStringInfo = _lib.SplitStringInfo
SplitStringInfo.restype = POINTER(StringInfo)
SplitStringInfo.argtypes = [POINTER(StringInfo), size_t]
StringToStringInfo = _lib.StringToStringInfo
StringToStringInfo.restype = POINTER(StringInfo)
StringToStringInfo.argtypes = [STRING]
ConcatenateStringInfo = _lib.ConcatenateStringInfo
ConcatenateStringInfo.restype = None
ConcatenateStringInfo.argtypes = [POINTER(StringInfo), POINTER(StringInfo)]
LocaleLower = _lib.LocaleLower
LocaleLower.restype = None
LocaleLower.argtypes = [STRING]
LocaleUpper = _lib.LocaleUpper
LocaleUpper.restype = None
LocaleUpper.argtypes = [STRING]
PrintStringInfo = _lib.PrintStringInfo
PrintStringInfo.restype = None
PrintStringInfo.argtypes = [POINTER(FILE), STRING, POINTER(StringInfo)]
ResetStringInfo = _lib.ResetStringInfo
ResetStringInfo.restype = None
ResetStringInfo.argtypes = [POINTER(StringInfo)]
SetStringInfo = _lib.SetStringInfo
SetStringInfo.restype = None
SetStringInfo.argtypes = [POINTER(StringInfo), POINTER(StringInfo)]
SetStringInfoDatum = _lib.SetStringInfoDatum
SetStringInfoDatum.restype = None
SetStringInfoDatum.argtypes = [POINTER(StringInfo), POINTER(c_ubyte)]
SetStringInfoLength = _lib.SetStringInfoLength
SetStringInfoLength.restype = None
SetStringInfoLength.argtypes = [POINTER(StringInfo), size_t]
StripString = _lib.StripString
StripString.restype = None
StripString.argtypes = [STRING]
class _ThresholdMap(Structure):
    pass
_ThresholdMap._fields_ = [
]
ThresholdMap = _ThresholdMap
AdaptiveThresholdImage = _lib.AdaptiveThresholdImage
AdaptiveThresholdImage.restype = POINTER(Image)
AdaptiveThresholdImage.argtypes = [POINTER(Image), c_ulong, c_ulong, c_long, POINTER(ExceptionInfo)]
BilevelImage = _lib.BilevelImage
BilevelImage.restype = MagickBooleanType
BilevelImage.argtypes = [POINTER(Image), c_double]
BilevelImageChannel = _lib.BilevelImageChannel
BilevelImageChannel.restype = MagickBooleanType
BilevelImageChannel.argtypes = [POINTER(Image), ChannelType, c_double]
BlackThresholdImage = _lib.BlackThresholdImage
BlackThresholdImage.restype = MagickBooleanType
BlackThresholdImage.argtypes = [POINTER(Image), STRING]
OrderedDitherImage = _lib.OrderedDitherImage
OrderedDitherImage.restype = MagickBooleanType
OrderedDitherImage.argtypes = [POINTER(Image)]
RandomThresholdImage = _lib.RandomThresholdImage
RandomThresholdImage.restype = MagickBooleanType
RandomThresholdImage.argtypes = [POINTER(Image), STRING, POINTER(ExceptionInfo)]
RandomThresholdImageChannel = _lib.RandomThresholdImageChannel
RandomThresholdImageChannel.restype = MagickBooleanType
RandomThresholdImageChannel.argtypes = [POINTER(Image), ChannelType, STRING, POINTER(ExceptionInfo)]
WhiteThresholdImage = _lib.WhiteThresholdImage
WhiteThresholdImage.restype = MagickBooleanType
WhiteThresholdImage.argtypes = [POINTER(Image), STRING]
GetElapsedTime = _lib.GetElapsedTime
GetElapsedTime.restype = c_double
GetElapsedTime.argtypes = [POINTER(TimerInfo)]
GetUserTime = _lib.GetUserTime
GetUserTime.restype = c_double
GetUserTime.argtypes = [POINTER(TimerInfo)]
ContinueTimer = _lib.ContinueTimer
ContinueTimer.restype = MagickBooleanType
ContinueTimer.argtypes = [POINTER(TimerInfo)]
GetTimerInfo = _lib.GetTimerInfo
GetTimerInfo.restype = None
GetTimerInfo.argtypes = [POINTER(TimerInfo)]
ResetTimer = _lib.ResetTimer
ResetTimer.restype = None
ResetTimer.argtypes = [POINTER(TimerInfo)]
StartTimer = _lib.StartTimer
StartTimer.restype = None
StartTimer.argtypes = [POINTER(TimerInfo), MagickBooleanType]
class _TokenInfo(Structure):
    pass
_TokenInfo._fields_ = [
]
TokenInfo = _TokenInfo
Tokenizer = _lib.Tokenizer
Tokenizer.restype = c_int
Tokenizer.argtypes = [POINTER(TokenInfo), c_uint, STRING, size_t, STRING, STRING, STRING, STRING, c_char, STRING, POINTER(c_int), STRING]
GlobExpression = _lib.GlobExpression
GlobExpression.restype = MagickBooleanType
GlobExpression.argtypes = [STRING, STRING, MagickBooleanType]
IsGlob = _lib.IsGlob
IsGlob.restype = MagickBooleanType
IsGlob.argtypes = [STRING]
GetMagickToken = _lib.GetMagickToken
GetMagickToken.restype = None
GetMagickToken.argtypes = [STRING, POINTER(STRING), STRING]
ChopImage = _lib.ChopImage
ChopImage.restype = POINTER(Image)
ChopImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), POINTER(ExceptionInfo)]
ConsolidateCMYKImages = _lib.ConsolidateCMYKImages
ConsolidateCMYKImages.restype = POINTER(Image)
ConsolidateCMYKImages.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
CropImage = _lib.CropImage
CropImage.restype = POINTER(Image)
CropImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), POINTER(ExceptionInfo)]
FlipImage = _lib.FlipImage
FlipImage.restype = POINTER(Image)
FlipImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
FlopImage = _lib.FlopImage
FlopImage.restype = POINTER(Image)
FlopImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
RollImage = _lib.RollImage
RollImage.restype = POINTER(Image)
RollImage.argtypes = [POINTER(Image), c_long, c_long, POINTER(ExceptionInfo)]
ShaveImage = _lib.ShaveImage
ShaveImage.restype = POINTER(Image)
ShaveImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), POINTER(ExceptionInfo)]
SpliceImage = _lib.SpliceImage
SpliceImage.restype = POINTER(Image)
SpliceImage.argtypes = [POINTER(Image), POINTER(RectangleInfo), POINTER(ExceptionInfo)]
TrimImage = _lib.TrimImage
TrimImage.restype = POINTER(Image)
TrimImage.argtypes = [POINTER(Image), POINTER(ExceptionInfo)]
TransformImage = _lib.TransformImage
TransformImage.restype = MagickBooleanType
TransformImage.argtypes = [POINTER(POINTER(Image)), STRING, STRING]
TransformImages = _lib.TransformImages
TransformImages.restype = MagickBooleanType
TransformImages.argtypes = [POINTER(POINTER(Image)), STRING, STRING]
class _TypeInfo(Structure):
    pass
_TypeInfo._fields_ = [
    ('face', c_ulong),
    ('path', STRING),
    ('name', STRING),
    ('description', STRING),
    ('family', STRING),
    ('style', StyleType),
    ('stretch', StretchType),
    ('weight', c_ulong),
    ('encoding', STRING),
    ('foundry', STRING),
    ('format', STRING),
    ('metrics', STRING),
    ('glyphs', STRING),
    ('stealth', MagickBooleanType),
    ('previous', POINTER(_TypeInfo)),
    ('next', POINTER(_TypeInfo)),
    ('signature', c_ulong),
]
TypeInfo = _TypeInfo
GetTypeList = _lib.GetTypeList
GetTypeList.restype = POINTER(STRING)
GetTypeList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
ListTypeInfo = _lib.ListTypeInfo
ListTypeInfo.restype = MagickBooleanType
ListTypeInfo.argtypes = [POINTER(FILE), POINTER(ExceptionInfo)]
GetTypeInfo = _lib.GetTypeInfo
GetTypeInfo.restype = POINTER(TypeInfo)
GetTypeInfo.argtypes = [STRING, POINTER(ExceptionInfo)]
GetTypeInfoByFamily = _lib.GetTypeInfoByFamily
GetTypeInfoByFamily.restype = POINTER(TypeInfo)
GetTypeInfoByFamily.argtypes = [STRING, StyleType, StretchType, c_ulong, POINTER(ExceptionInfo)]
GetTypeInfoList = _lib.GetTypeInfoList
GetTypeInfoList.restype = POINTER(POINTER(TypeInfo))
GetTypeInfoList.argtypes = [STRING, POINTER(c_ulong), POINTER(ExceptionInfo)]
#DestroyTypeList = _lib.DestroyTypeList
#DestroyTypeList.restype = None
#DestroyTypeList.argtypes = []

# values for enumeration 'PathType'
PathType = c_int # enum
Base64Encode = _lib.Base64Encode
Base64Encode.restype = STRING
Base64Encode.argtypes = [POINTER(c_ubyte), size_t, POINTER(size_t)]
ListFiles = _lib.ListFiles
ListFiles.restype = POINTER(STRING)
ListFiles.argtypes = [STRING, STRING, POINTER(c_ulong)]
SystemCommand = _lib.SystemCommand
SystemCommand.restype = c_int
SystemCommand.argtypes = [MagickBooleanType, STRING]
AcquireUniqueFilename = _lib.AcquireUniqueFilename
AcquireUniqueFilename.restype = MagickBooleanType
AcquireUniqueFilename.argtypes = [STRING]
ExpandFilenames = _lib.ExpandFilenames
ExpandFilenames.restype = MagickBooleanType
ExpandFilenames.argtypes = [POINTER(c_int), POINTER(POINTER(STRING))]
GetExecutionPath = _lib.GetExecutionPath
GetExecutionPath.restype = MagickBooleanType
GetExecutionPath.argtypes = [STRING, size_t]
#IsAccessible = _lib.IsAccessible
#IsAccessible.restype = MagickBooleanType
#IsAccessible.argtypes = [STRING]
Base64Decode = _lib.Base64Decode
Base64Decode.restype = POINTER(c_ubyte)
Base64Decode.argtypes = [STRING, POINTER(size_t)]
MultilineCensus = _lib.MultilineCensus
MultilineCensus.restype = c_ulong
MultilineCensus.argtypes = [STRING]
AppendImageFormat = _lib.AppendImageFormat
AppendImageFormat.restype = None
AppendImageFormat.argtypes = [STRING, STRING]
ChopPathComponents = _lib.ChopPathComponents
ChopPathComponents.restype = None
ChopPathComponents.argtypes = [STRING, c_ulong]
ExpandFilename = _lib.ExpandFilename
ExpandFilename.restype = None
ExpandFilename.argtypes = [STRING]
GetPathComponent = _lib.GetPathComponent
GetPathComponent.restype = None
GetPathComponent.argtypes = [STRING, PathType, STRING]
GetMagickHomeURL = _lib.GetMagickHomeURL
GetMagickHomeURL.restype = STRING
GetMagickHomeURL.argtypes = []
GetMagickCopyright = _lib.GetMagickCopyright
GetMagickCopyright.restype = STRING
GetMagickCopyright.argtypes = []
GetMagickPackageName = _lib.GetMagickPackageName
GetMagickPackageName.restype = STRING
GetMagickPackageName.argtypes = []
GetMagickQuantumDepth = _lib.GetMagickQuantumDepth
GetMagickQuantumDepth.restype = STRING
GetMagickQuantumDepth.argtypes = [POINTER(c_ulong)]
GetMagickQuantumRange = _lib.GetMagickQuantumRange
GetMagickQuantumRange.restype = STRING
GetMagickQuantumRange.argtypes = [POINTER(c_ulong)]
GetMagickReleaseDate = _lib.GetMagickReleaseDate
GetMagickReleaseDate.restype = STRING
GetMagickReleaseDate.argtypes = []
GetMagickVersion = _lib.GetMagickVersion
GetMagickVersion.restype = STRING
GetMagickVersion.argtypes = [POINTER(c_ulong)]
class _XMLTreeInfo(Structure):
    pass
_XMLTreeInfo._fields_ = [
]
XMLTreeInfo = _XMLTreeInfo
class _XImportInfo(Structure):
    pass
_XImportInfo._fields_ = [
    ('frame', MagickBooleanType),
    ('borders', MagickBooleanType),
    ('screen', MagickBooleanType),
    ('descend', MagickBooleanType),
    ('silent', MagickBooleanType),
]
XImportInfo = _XImportInfo
XImportImage = _lib.XImportImage
XImportImage.restype = POINTER(Image)
XImportImage.argtypes = [POINTER(ImageInfo), POINTER(XImportInfo)]
XGetImportInfo = _lib.XGetImportInfo
XGetImportInfo.restype = None
XGetImportInfo.argtypes = [POINTER(XImportInfo)]
class _MagickWand(Structure):
    pass
_MagickWand._fields_ = [
]
MagickWand = _MagickWand
MagickGetException = _lib.MagickGetException
MagickGetException.restype = STRING
MagickGetException.argtypes = [POINTER(MagickWand), POINTER(ExceptionType)]
IsMagickWand = _lib.IsMagickWand
IsMagickWand.restype = MagickBooleanType
IsMagickWand.argtypes = [POINTER(MagickWand)]
MagickClearException = _lib.MagickClearException
MagickClearException.restype = MagickBooleanType
MagickClearException.argtypes = [POINTER(MagickWand)]
CloneMagickWand = _lib.CloneMagickWand
CloneMagickWand.restype = POINTER(MagickWand)
CloneMagickWand.argtypes = [POINTER(MagickWand)]
DestroyMagickWand = _lib.DestroyMagickWand
DestroyMagickWand.restype = POINTER(MagickWand)
DestroyMagickWand.argtypes = [POINTER(MagickWand)]
NewMagickWand = _lib.NewMagickWand
NewMagickWand.restype = POINTER(MagickWand)
NewMagickWand.argtypes = []
NewMagickWandFromImage = _lib.NewMagickWandFromImage
NewMagickWandFromImage.restype = POINTER(MagickWand)
NewMagickWandFromImage.argtypes = [POINTER(Image)]
ClearMagickWand = _lib.ClearMagickWand
ClearMagickWand.restype = None
ClearMagickWand.argtypes = [POINTER(MagickWand)]
MagickWandGenesis = _lib.MagickWandGenesis
MagickWandGenesis.restype = None
MagickWandGenesis.argtypes = []
MagickWandTerminus = _lib.MagickWandTerminus
MagickWandTerminus.restype = None
MagickWandTerminus.argtypes = []
MagickRelinquishMemory = _lib.MagickRelinquishMemory
MagickRelinquishMemory.restype = c_void_p
MagickRelinquishMemory.argtypes = [c_void_p]
MagickResetIterator = _lib.MagickResetIterator
MagickResetIterator.restype = None
MagickResetIterator.argtypes = [POINTER(MagickWand)]
MagickSetFirstIterator = _lib.MagickSetFirstIterator
MagickSetFirstIterator.restype = None
MagickSetFirstIterator.argtypes = [POINTER(MagickWand)]
MagickSetLastIterator = _lib.MagickSetLastIterator
MagickSetLastIterator.restype = None
MagickSetLastIterator.argtypes = [POINTER(MagickWand)]
AnimateImageCommand = _lib.AnimateImageCommand
AnimateImageCommand.restype = MagickBooleanType
AnimateImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
CompareImageCommand = _lib.CompareImageCommand
CompareImageCommand.restype = MagickBooleanType
CompareImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
CompositeImageCommand = _lib.CompositeImageCommand
CompositeImageCommand.restype = MagickBooleanType
CompositeImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
ConjureImageCommand = _lib.ConjureImageCommand
ConjureImageCommand.restype = MagickBooleanType
ConjureImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
ConvertImageCommand = _lib.ConvertImageCommand
ConvertImageCommand.restype = MagickBooleanType
ConvertImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
class _DrawingWand(Structure):
    pass
DrawContext = POINTER(_DrawingWand)
DrawingWand = _DrawingWand
DrawGetFillAlpha = _lib.DrawGetFillAlpha
DrawGetFillAlpha.restype = c_double
DrawGetFillAlpha.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeAlpha = _lib.DrawGetStrokeAlpha
DrawGetStrokeAlpha.restype = c_double
DrawGetStrokeAlpha.argtypes = [POINTER(DrawingWand)]
DrawPeekGraphicWand = _lib.DrawPeekGraphicWand
DrawPeekGraphicWand.restype = POINTER(DrawInfo)
DrawPeekGraphicWand.argtypes = [POINTER(DrawingWand)]
MagickDescribeImage = _lib.MagickDescribeImage
MagickDescribeImage.restype = STRING
MagickDescribeImage.argtypes = [POINTER(MagickWand)]
MagickGetImageAttribute = _lib.MagickGetImageAttribute
MagickGetImageAttribute.restype = STRING
MagickGetImageAttribute.argtypes = [POINTER(MagickWand), STRING]
class _PixelIterator(Structure):
    pass
PixelIterator = _PixelIterator
PixelIteratorGetException = _lib.PixelIteratorGetException
PixelIteratorGetException.restype = STRING
PixelIteratorGetException.argtypes = [POINTER(PixelIterator), POINTER(ExceptionType)]
MagickGetImageIndex = _lib.MagickGetImageIndex
MagickGetImageIndex.restype = c_long
MagickGetImageIndex.argtypes = [POINTER(MagickWand)]
MagickClipPathImage = _lib.MagickClipPathImage
MagickClipPathImage.restype = MagickBooleanType
MagickClipPathImage.argtypes = [POINTER(MagickWand), STRING, MagickBooleanType]
class _PixelWand(Structure):
    pass
PixelWand = _PixelWand
MagickColorFloodfillImage = _lib.MagickColorFloodfillImage
MagickColorFloodfillImage.restype = MagickBooleanType
MagickColorFloodfillImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_double, POINTER(PixelWand), c_long, c_long]
MagickGetImageChannelExtrema = _lib.MagickGetImageChannelExtrema
MagickGetImageChannelExtrema.restype = MagickBooleanType
MagickGetImageChannelExtrema.argtypes = [POINTER(MagickWand), ChannelType, POINTER(c_ulong), POINTER(c_ulong)]
MagickGetImageExtrema = _lib.MagickGetImageExtrema
MagickGetImageExtrema.restype = MagickBooleanType
MagickGetImageExtrema.argtypes = [POINTER(MagickWand), POINTER(c_ulong), POINTER(c_ulong)]
MagickMatteFloodfillImage = _lib.MagickMatteFloodfillImage
MagickMatteFloodfillImage.restype = MagickBooleanType
MagickMatteFloodfillImage.argtypes = [POINTER(MagickWand), c_double, c_double, POINTER(PixelWand), c_long, c_long]
MagickOpaqueImage = _lib.MagickOpaqueImage
MagickOpaqueImage.restype = MagickBooleanType
MagickOpaqueImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), POINTER(PixelWand), c_double]
MagickPaintOpaqueImage = _lib.MagickPaintOpaqueImage
MagickPaintOpaqueImage.restype = MagickBooleanType
MagickPaintOpaqueImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), POINTER(PixelWand), c_double]
MagickPaintTransparentImage = _lib.MagickPaintTransparentImage
MagickPaintTransparentImage.restype = MagickBooleanType
MagickPaintTransparentImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_double, c_double]
MagickSetImageAttribute = _lib.MagickSetImageAttribute
MagickSetImageAttribute.restype = MagickBooleanType
MagickSetImageAttribute.argtypes = [POINTER(MagickWand), STRING, STRING]
MagickSetImageIndex = _lib.MagickSetImageIndex
MagickSetImageIndex.restype = MagickBooleanType
MagickSetImageIndex.argtypes = [POINTER(MagickWand), c_long]
MagickSetImageOption = _lib.MagickSetImageOption
MagickSetImageOption.restype = MagickBooleanType
MagickSetImageOption.argtypes = [POINTER(MagickWand), STRING, STRING, STRING]
MagickTransparentImage = _lib.MagickTransparentImage
MagickTransparentImage.restype = MagickBooleanType
MagickTransparentImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_double, c_double]
MagickFlattenImages = _lib.MagickFlattenImages
MagickFlattenImages.restype = POINTER(MagickWand)
MagickFlattenImages.argtypes = [POINTER(MagickWand)]
MagickMosaicImages = _lib.MagickMosaicImages
MagickMosaicImages.restype = POINTER(MagickWand)
MagickMosaicImages.argtypes = [POINTER(MagickWand)]
MagickRegionOfInterestImage = _lib.MagickRegionOfInterestImage
MagickRegionOfInterestImage.restype = POINTER(MagickWand)
MagickRegionOfInterestImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickGetImageSize = _lib.MagickGetImageSize
MagickGetImageSize.restype = MagickSizeType
MagickGetImageSize.argtypes = [POINTER(MagickWand)]
PixelGetNextRow = _lib.PixelGetNextRow
PixelGetNextRow.restype = POINTER(POINTER(PixelWand))
PixelGetNextRow.argtypes = [POINTER(PixelIterator)]
MagickWriteImageBlob = _lib.MagickWriteImageBlob
MagickWriteImageBlob.restype = POINTER(c_ubyte)
MagickWriteImageBlob.argtypes = [POINTER(MagickWand), POINTER(size_t)]
MagickSetImageVirtualPixelMethod = _lib.MagickSetImageVirtualPixelMethod
MagickSetImageVirtualPixelMethod.restype = VirtualPixelMethod
MagickSetImageVirtualPixelMethod.argtypes = [POINTER(MagickWand), VirtualPixelMethod]
DrawPopGraphicContext = _lib.DrawPopGraphicContext
DrawPopGraphicContext.restype = None
DrawPopGraphicContext.argtypes = [POINTER(DrawingWand)]
DrawPushGraphicContext = _lib.DrawPushGraphicContext
DrawPushGraphicContext.restype = None
DrawPushGraphicContext.argtypes = [POINTER(DrawingWand)]
DrawSetFillAlpha = _lib.DrawSetFillAlpha
DrawSetFillAlpha.restype = None
DrawSetFillAlpha.argtypes = [POINTER(DrawingWand), c_double]
DrawSetStrokeAlpha = _lib.DrawSetStrokeAlpha
DrawSetStrokeAlpha.restype = None
DrawSetStrokeAlpha.argtypes = [POINTER(DrawingWand), c_double]
DisplayImageCommand = _lib.DisplayImageCommand
DisplayImageCommand.restype = MagickBooleanType
DisplayImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
_DrawingWand._fields_ = [
]
DrawGetTextAlignment = _lib.DrawGetTextAlignment
DrawGetTextAlignment.restype = AlignType
DrawGetTextAlignment.argtypes = [POINTER(DrawingWand)]
DrawGetClipPath = _lib.DrawGetClipPath
DrawGetClipPath.restype = STRING
DrawGetClipPath.argtypes = [POINTER(DrawingWand)]
DrawGetException = _lib.DrawGetException
DrawGetException.restype = STRING
DrawGetException.argtypes = [POINTER(DrawingWand), POINTER(ExceptionType)]
DrawGetFont = _lib.DrawGetFont
DrawGetFont.restype = STRING
DrawGetFont.argtypes = [POINTER(DrawingWand)]
DrawGetFontFamily = _lib.DrawGetFontFamily
DrawGetFontFamily.restype = STRING
DrawGetFontFamily.argtypes = [POINTER(DrawingWand)]
DrawGetTextEncoding = _lib.DrawGetTextEncoding
DrawGetTextEncoding.restype = STRING
DrawGetTextEncoding.argtypes = [POINTER(DrawingWand)]
DrawGetVectorGraphics = _lib.DrawGetVectorGraphics
DrawGetVectorGraphics.restype = STRING
DrawGetVectorGraphics.argtypes = [POINTER(DrawingWand)]
DrawGetClipUnits = _lib.DrawGetClipUnits
DrawGetClipUnits.restype = ClipPathUnits
DrawGetClipUnits.argtypes = [POINTER(DrawingWand)]
DrawGetTextDecoration = _lib.DrawGetTextDecoration
DrawGetTextDecoration.restype = DecorationType
DrawGetTextDecoration.argtypes = [POINTER(DrawingWand)]
DrawGetFillOpacity = _lib.DrawGetFillOpacity
DrawGetFillOpacity.restype = c_double
DrawGetFillOpacity.argtypes = [POINTER(DrawingWand)]
DrawGetFontSize = _lib.DrawGetFontSize
DrawGetFontSize.restype = c_double
DrawGetFontSize.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeDashArray = _lib.DrawGetStrokeDashArray
DrawGetStrokeDashArray.restype = POINTER(c_double)
DrawGetStrokeDashArray.argtypes = [POINTER(DrawingWand), POINTER(c_ulong)]
DrawGetStrokeDashOffset = _lib.DrawGetStrokeDashOffset
DrawGetStrokeDashOffset.restype = c_double
DrawGetStrokeDashOffset.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeOpacity = _lib.DrawGetStrokeOpacity
DrawGetStrokeOpacity.restype = c_double
DrawGetStrokeOpacity.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeWidth = _lib.DrawGetStrokeWidth
DrawGetStrokeWidth.restype = c_double
DrawGetStrokeWidth.argtypes = [POINTER(DrawingWand)]
PeekDrawingWand = _lib.PeekDrawingWand
PeekDrawingWand.restype = POINTER(DrawInfo)
PeekDrawingWand.argtypes = [POINTER(DrawingWand)]
CloneDrawingWand = _lib.CloneDrawingWand
CloneDrawingWand.restype = POINTER(DrawingWand)
CloneDrawingWand.argtypes = [POINTER(DrawingWand)]
DestroyDrawingWand = _lib.DestroyDrawingWand
DestroyDrawingWand.restype = POINTER(DrawingWand)
DestroyDrawingWand.argtypes = [POINTER(DrawingWand)]
DrawAllocateWand = _lib.DrawAllocateWand
DrawAllocateWand.restype = POINTER(DrawingWand)
DrawAllocateWand.argtypes = [POINTER(DrawInfo), POINTER(Image)]
NewDrawingWand = _lib.NewDrawingWand
NewDrawingWand.restype = POINTER(DrawingWand)
NewDrawingWand.argtypes = []
DrawGetClipRule = _lib.DrawGetClipRule
DrawGetClipRule.restype = FillRule
DrawGetClipRule.argtypes = [POINTER(DrawingWand)]
DrawGetFillRule = _lib.DrawGetFillRule
DrawGetFillRule.restype = FillRule
DrawGetFillRule.argtypes = [POINTER(DrawingWand)]
DrawGetGravity = _lib.DrawGetGravity
DrawGetGravity.restype = GravityType
DrawGetGravity.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeLineCap = _lib.DrawGetStrokeLineCap
DrawGetStrokeLineCap.restype = LineCap
DrawGetStrokeLineCap.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeLineJoin = _lib.DrawGetStrokeLineJoin
DrawGetStrokeLineJoin.restype = LineJoin
DrawGetStrokeLineJoin.argtypes = [POINTER(DrawingWand)]
DrawClearException = _lib.DrawClearException
DrawClearException.restype = MagickBooleanType
DrawClearException.argtypes = [POINTER(DrawingWand)]
DrawComposite = _lib.DrawComposite
DrawComposite.restype = MagickBooleanType
DrawComposite.argtypes = [POINTER(DrawingWand), CompositeOperator, c_double, c_double, c_double, c_double, POINTER(MagickWand)]
DrawGetStrokeAntialias = _lib.DrawGetStrokeAntialias
DrawGetStrokeAntialias.restype = MagickBooleanType
DrawGetStrokeAntialias.argtypes = [POINTER(DrawingWand)]
DrawGetTextAntialias = _lib.DrawGetTextAntialias
DrawGetTextAntialias.restype = MagickBooleanType
DrawGetTextAntialias.argtypes = [POINTER(DrawingWand)]
DrawPopPattern = _lib.DrawPopPattern
DrawPopPattern.restype = MagickBooleanType
DrawPopPattern.argtypes = [POINTER(DrawingWand)]
DrawPushPattern = _lib.DrawPushPattern
DrawPushPattern.restype = MagickBooleanType
DrawPushPattern.argtypes = [POINTER(DrawingWand), STRING, c_double, c_double, c_double, c_double]
DrawRender = _lib.DrawRender
DrawRender.restype = MagickBooleanType
DrawRender.argtypes = [POINTER(DrawingWand)]
DrawSetClipPath = _lib.DrawSetClipPath
DrawSetClipPath.restype = MagickBooleanType
DrawSetClipPath.argtypes = [POINTER(DrawingWand), STRING]
DrawSetFillPatternURL = _lib.DrawSetFillPatternURL
DrawSetFillPatternURL.restype = MagickBooleanType
DrawSetFillPatternURL.argtypes = [POINTER(DrawingWand), STRING]
DrawSetFont = _lib.DrawSetFont
DrawSetFont.restype = MagickBooleanType
DrawSetFont.argtypes = [POINTER(DrawingWand), STRING]
DrawSetFontFamily = _lib.DrawSetFontFamily
DrawSetFontFamily.restype = MagickBooleanType
DrawSetFontFamily.argtypes = [POINTER(DrawingWand), STRING]
DrawSetStrokeDashArray = _lib.DrawSetStrokeDashArray
DrawSetStrokeDashArray.restype = MagickBooleanType
DrawSetStrokeDashArray.argtypes = [POINTER(DrawingWand), c_ulong, POINTER(c_double)]
DrawSetStrokePatternURL = _lib.DrawSetStrokePatternURL
DrawSetStrokePatternURL.restype = MagickBooleanType
DrawSetStrokePatternURL.argtypes = [POINTER(DrawingWand), STRING]
DrawSetVectorGraphics = _lib.DrawSetVectorGraphics
DrawSetVectorGraphics.restype = MagickBooleanType
DrawSetVectorGraphics.argtypes = [POINTER(DrawingWand), STRING]
IsDrawingWand = _lib.IsDrawingWand
IsDrawingWand.restype = MagickBooleanType
IsDrawingWand.argtypes = [POINTER(DrawingWand)]
PopDrawingWand = _lib.PopDrawingWand
PopDrawingWand.restype = MagickBooleanType
PopDrawingWand.argtypes = [POINTER(DrawingWand)]
PushDrawingWand = _lib.PushDrawingWand
PushDrawingWand.restype = MagickBooleanType
PushDrawingWand.argtypes = [POINTER(DrawingWand)]
DrawGetFontStretch = _lib.DrawGetFontStretch
DrawGetFontStretch.restype = StretchType
DrawGetFontStretch.argtypes = [POINTER(DrawingWand)]
DrawGetFontStyle = _lib.DrawGetFontStyle
DrawGetFontStyle.restype = StyleType
DrawGetFontStyle.argtypes = [POINTER(DrawingWand)]
DrawGetFontWeight = _lib.DrawGetFontWeight
DrawGetFontWeight.restype = c_ulong
DrawGetFontWeight.argtypes = [POINTER(DrawingWand)]
DrawGetStrokeMiterLimit = _lib.DrawGetStrokeMiterLimit
DrawGetStrokeMiterLimit.restype = c_ulong
DrawGetStrokeMiterLimit.argtypes = [POINTER(DrawingWand)]
ClearDrawingWand = _lib.ClearDrawingWand
ClearDrawingWand.restype = None
ClearDrawingWand.argtypes = [POINTER(DrawingWand)]
DrawAffine = _lib.DrawAffine
DrawAffine.restype = None
DrawAffine.argtypes = [POINTER(DrawingWand), POINTER(AffineMatrix)]
DrawAnnotation = _lib.DrawAnnotation
DrawAnnotation.restype = None
DrawAnnotation.argtypes = [POINTER(DrawingWand), c_double, c_double, POINTER(c_ubyte)]
DrawArc = _lib.DrawArc
DrawArc.restype = None
DrawArc.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double, c_double, c_double]
DrawBezier = _lib.DrawBezier
DrawBezier.restype = None
DrawBezier.argtypes = [POINTER(DrawingWand), c_ulong, POINTER(PointInfo)]
DrawCircle = _lib.DrawCircle
DrawCircle.restype = None
DrawCircle.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawColor = _lib.DrawColor
DrawColor.restype = None
DrawColor.argtypes = [POINTER(DrawingWand), c_double, c_double, PaintMethod]
DrawComment = _lib.DrawComment
DrawComment.restype = None
DrawComment.argtypes = [POINTER(DrawingWand), STRING]
DrawEllipse = _lib.DrawEllipse
DrawEllipse.restype = None
DrawEllipse.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double, c_double, c_double]
DrawGetFillColor = _lib.DrawGetFillColor
DrawGetFillColor.restype = None
DrawGetFillColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawGetStrokeColor = _lib.DrawGetStrokeColor
DrawGetStrokeColor.restype = None
DrawGetStrokeColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawGetTextUnderColor = _lib.DrawGetTextUnderColor
DrawGetTextUnderColor.restype = None
DrawGetTextUnderColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawLine = _lib.DrawLine
DrawLine.restype = None
DrawLine.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawMatte = _lib.DrawMatte
DrawMatte.restype = None
DrawMatte.argtypes = [POINTER(DrawingWand), c_double, c_double, PaintMethod]
DrawPathClose = _lib.DrawPathClose
DrawPathClose.restype = None
DrawPathClose.argtypes = [POINTER(DrawingWand)]
DrawPathCurveToAbsolute = _lib.DrawPathCurveToAbsolute
DrawPathCurveToAbsolute.restype = None
DrawPathCurveToAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double, c_double, c_double]
DrawPathCurveToRelative = _lib.DrawPathCurveToRelative
DrawPathCurveToRelative.restype = None
DrawPathCurveToRelative.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double, c_double, c_double]
DrawPathCurveToQuadraticBezierAbsolute = _lib.DrawPathCurveToQuadraticBezierAbsolute
DrawPathCurveToQuadraticBezierAbsolute.restype = None
DrawPathCurveToQuadraticBezierAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawPathCurveToQuadraticBezierRelative = _lib.DrawPathCurveToQuadraticBezierRelative
DrawPathCurveToQuadraticBezierRelative.restype = None
DrawPathCurveToQuadraticBezierRelative.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawPathCurveToQuadraticBezierSmoothAbsolute = _lib.DrawPathCurveToQuadraticBezierSmoothAbsolute
DrawPathCurveToQuadraticBezierSmoothAbsolute.restype = None
DrawPathCurveToQuadraticBezierSmoothAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathCurveToQuadraticBezierSmoothRelative = _lib.DrawPathCurveToQuadraticBezierSmoothRelative
DrawPathCurveToQuadraticBezierSmoothRelative.restype = None
DrawPathCurveToQuadraticBezierSmoothRelative.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathCurveToSmoothAbsolute = _lib.DrawPathCurveToSmoothAbsolute
DrawPathCurveToSmoothAbsolute.restype = None
DrawPathCurveToSmoothAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawPathCurveToSmoothRelative = _lib.DrawPathCurveToSmoothRelative
DrawPathCurveToSmoothRelative.restype = None
DrawPathCurveToSmoothRelative.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawPathEllipticArcAbsolute = _lib.DrawPathEllipticArcAbsolute
DrawPathEllipticArcAbsolute.restype = None
DrawPathEllipticArcAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, MagickBooleanType, MagickBooleanType, c_double, c_double]
DrawPathEllipticArcRelative = _lib.DrawPathEllipticArcRelative
DrawPathEllipticArcRelative.restype = None
DrawPathEllipticArcRelative.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, MagickBooleanType, MagickBooleanType, c_double, c_double]
DrawPathFinish = _lib.DrawPathFinish
DrawPathFinish.restype = None
DrawPathFinish.argtypes = [POINTER(DrawingWand)]
DrawPathLineToAbsolute = _lib.DrawPathLineToAbsolute
DrawPathLineToAbsolute.restype = None
DrawPathLineToAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathLineToRelative = _lib.DrawPathLineToRelative
DrawPathLineToRelative.restype = None
DrawPathLineToRelative.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathLineToHorizontalAbsolute = _lib.DrawPathLineToHorizontalAbsolute
DrawPathLineToHorizontalAbsolute.restype = None
DrawPathLineToHorizontalAbsolute.argtypes = [POINTER(DrawingWand), c_double]
DrawPathLineToHorizontalRelative = _lib.DrawPathLineToHorizontalRelative
DrawPathLineToHorizontalRelative.restype = None
DrawPathLineToHorizontalRelative.argtypes = [POINTER(DrawingWand), c_double]
DrawPathLineToVerticalAbsolute = _lib.DrawPathLineToVerticalAbsolute
DrawPathLineToVerticalAbsolute.restype = None
DrawPathLineToVerticalAbsolute.argtypes = [POINTER(DrawingWand), c_double]
DrawPathLineToVerticalRelative = _lib.DrawPathLineToVerticalRelative
DrawPathLineToVerticalRelative.restype = None
DrawPathLineToVerticalRelative.argtypes = [POINTER(DrawingWand), c_double]
DrawPathMoveToAbsolute = _lib.DrawPathMoveToAbsolute
DrawPathMoveToAbsolute.restype = None
DrawPathMoveToAbsolute.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathMoveToRelative = _lib.DrawPathMoveToRelative
DrawPathMoveToRelative.restype = None
DrawPathMoveToRelative.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPathStart = _lib.DrawPathStart
DrawPathStart.restype = None
DrawPathStart.argtypes = [POINTER(DrawingWand)]
DrawPoint = _lib.DrawPoint
DrawPoint.restype = None
DrawPoint.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawPolygon = _lib.DrawPolygon
DrawPolygon.restype = None
DrawPolygon.argtypes = [POINTER(DrawingWand), c_ulong, POINTER(PointInfo)]
DrawPolyline = _lib.DrawPolyline
DrawPolyline.restype = None
DrawPolyline.argtypes = [POINTER(DrawingWand), c_ulong, POINTER(PointInfo)]
DrawPopClipPath = _lib.DrawPopClipPath
DrawPopClipPath.restype = None
DrawPopClipPath.argtypes = [POINTER(DrawingWand)]
DrawPopDefs = _lib.DrawPopDefs
DrawPopDefs.restype = None
DrawPopDefs.argtypes = [POINTER(DrawingWand)]
DrawPushClipPath = _lib.DrawPushClipPath
DrawPushClipPath.restype = None
DrawPushClipPath.argtypes = [POINTER(DrawingWand), STRING]
DrawPushDefs = _lib.DrawPushDefs
DrawPushDefs.restype = None
DrawPushDefs.argtypes = [POINTER(DrawingWand)]
DrawRectangle = _lib.DrawRectangle
DrawRectangle.restype = None
DrawRectangle.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double]
DrawRotate = _lib.DrawRotate
DrawRotate.restype = None
DrawRotate.argtypes = [POINTER(DrawingWand), c_double]
DrawRoundRectangle = _lib.DrawRoundRectangle
DrawRoundRectangle.restype = None
DrawRoundRectangle.argtypes = [POINTER(DrawingWand), c_double, c_double, c_double, c_double, c_double, c_double]
DrawScale = _lib.DrawScale
DrawScale.restype = None
DrawScale.argtypes = [POINTER(DrawingWand), c_double, c_double]
DrawSetClipRule = _lib.DrawSetClipRule
DrawSetClipRule.restype = None
DrawSetClipRule.argtypes = [POINTER(DrawingWand), FillRule]
DrawSetClipUnits = _lib.DrawSetClipUnits
DrawSetClipUnits.restype = None
DrawSetClipUnits.argtypes = [POINTER(DrawingWand), ClipPathUnits]
DrawSetFillColor = _lib.DrawSetFillColor
DrawSetFillColor.restype = None
DrawSetFillColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawSetFillOpacity = _lib.DrawSetFillOpacity
DrawSetFillOpacity.restype = None
DrawSetFillOpacity.argtypes = [POINTER(DrawingWand), c_double]
DrawSetFillRule = _lib.DrawSetFillRule
DrawSetFillRule.restype = None
DrawSetFillRule.argtypes = [POINTER(DrawingWand), FillRule]
DrawSetFontSize = _lib.DrawSetFontSize
DrawSetFontSize.restype = None
DrawSetFontSize.argtypes = [POINTER(DrawingWand), c_double]
DrawSetFontStretch = _lib.DrawSetFontStretch
DrawSetFontStretch.restype = None
DrawSetFontStretch.argtypes = [POINTER(DrawingWand), StretchType]
DrawSetFontStyle = _lib.DrawSetFontStyle
DrawSetFontStyle.restype = None
DrawSetFontStyle.argtypes = [POINTER(DrawingWand), StyleType]
DrawSetFontWeight = _lib.DrawSetFontWeight
DrawSetFontWeight.restype = None
DrawSetFontWeight.argtypes = [POINTER(DrawingWand), c_ulong]
DrawSetGravity = _lib.DrawSetGravity
DrawSetGravity.restype = None
DrawSetGravity.argtypes = [POINTER(DrawingWand), GravityType]
DrawSetStrokeAntialias = _lib.DrawSetStrokeAntialias
DrawSetStrokeAntialias.restype = None
DrawSetStrokeAntialias.argtypes = [POINTER(DrawingWand), MagickBooleanType]
DrawSetStrokeColor = _lib.DrawSetStrokeColor
DrawSetStrokeColor.restype = None
DrawSetStrokeColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawSetStrokeDashOffset = _lib.DrawSetStrokeDashOffset
DrawSetStrokeDashOffset.restype = None
DrawSetStrokeDashOffset.argtypes = [POINTER(DrawingWand), c_double]
DrawSetStrokeLineCap = _lib.DrawSetStrokeLineCap
DrawSetStrokeLineCap.restype = None
DrawSetStrokeLineCap.argtypes = [POINTER(DrawingWand), LineCap]
DrawSetStrokeLineJoin = _lib.DrawSetStrokeLineJoin
DrawSetStrokeLineJoin.restype = None
DrawSetStrokeLineJoin.argtypes = [POINTER(DrawingWand), LineJoin]
DrawSetStrokeMiterLimit = _lib.DrawSetStrokeMiterLimit
DrawSetStrokeMiterLimit.restype = None
DrawSetStrokeMiterLimit.argtypes = [POINTER(DrawingWand), c_ulong]
DrawSetStrokeOpacity = _lib.DrawSetStrokeOpacity
DrawSetStrokeOpacity.restype = None
DrawSetStrokeOpacity.argtypes = [POINTER(DrawingWand), c_double]
DrawSetStrokeWidth = _lib.DrawSetStrokeWidth
DrawSetStrokeWidth.restype = None
DrawSetStrokeWidth.argtypes = [POINTER(DrawingWand), c_double]
DrawSetTextAlignment = _lib.DrawSetTextAlignment
DrawSetTextAlignment.restype = None
DrawSetTextAlignment.argtypes = [POINTER(DrawingWand), AlignType]
DrawSetTextAntialias = _lib.DrawSetTextAntialias
DrawSetTextAntialias.restype = None
DrawSetTextAntialias.argtypes = [POINTER(DrawingWand), MagickBooleanType]
DrawSetTextDecoration = _lib.DrawSetTextDecoration
DrawSetTextDecoration.restype = None
DrawSetTextDecoration.argtypes = [POINTER(DrawingWand), DecorationType]
DrawSetTextEncoding = _lib.DrawSetTextEncoding
DrawSetTextEncoding.restype = None
DrawSetTextEncoding.argtypes = [POINTER(DrawingWand), STRING]
DrawSetTextUnderColor = _lib.DrawSetTextUnderColor
DrawSetTextUnderColor.restype = None
DrawSetTextUnderColor.argtypes = [POINTER(DrawingWand), POINTER(PixelWand)]
DrawSetViewbox = _lib.DrawSetViewbox
DrawSetViewbox.restype = None
DrawSetViewbox.argtypes = [POINTER(DrawingWand), c_ulong, c_ulong, c_ulong, c_ulong]
DrawSkewX = _lib.DrawSkewX
DrawSkewX.restype = None
DrawSkewX.argtypes = [POINTER(DrawingWand), c_double]
DrawSkewY = _lib.DrawSkewY
DrawSkewY.restype = None
DrawSkewY.argtypes = [POINTER(DrawingWand), c_double]
DrawTranslate = _lib.DrawTranslate
DrawTranslate.restype = None
DrawTranslate.argtypes = [POINTER(DrawingWand), c_double, c_double]
IdentifyImageCommand = _lib.IdentifyImageCommand
IdentifyImageCommand.restype = MagickBooleanType
IdentifyImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
ImportImageCommand = _lib.ImportImageCommand
ImportImageCommand.restype = MagickBooleanType
ImportImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
MagickGetImageChannelStatistics = _lib.MagickGetImageChannelStatistics
MagickGetImageChannelStatistics.restype = POINTER(ChannelStatistics)
MagickGetImageChannelStatistics.argtypes = [POINTER(MagickWand)]
MagickGetImageFilename = _lib.MagickGetImageFilename
MagickGetImageFilename.restype = STRING
MagickGetImageFilename.argtypes = [POINTER(MagickWand)]
MagickGetImageFormat = _lib.MagickGetImageFormat
MagickGetImageFormat.restype = STRING
MagickGetImageFormat.argtypes = [POINTER(MagickWand)]
MagickGetImageSignature = _lib.MagickGetImageSignature
MagickGetImageSignature.restype = STRING
MagickGetImageSignature.argtypes = [POINTER(MagickWand)]
MagickIdentifyImage = _lib.MagickIdentifyImage
MagickIdentifyImage.restype = STRING
MagickIdentifyImage.argtypes = [POINTER(MagickWand)]
MagickGetImageCompose = _lib.MagickGetImageCompose
MagickGetImageCompose.restype = CompositeOperator
MagickGetImageCompose.argtypes = [POINTER(MagickWand)]
MagickGetImageColorspace = _lib.MagickGetImageColorspace
MagickGetImageColorspace.restype = ColorspaceType
MagickGetImageColorspace.argtypes = [POINTER(MagickWand)]
MagickGetImageCompression = _lib.MagickGetImageCompression
MagickGetImageCompression.restype = CompressionType
MagickGetImageCompression.argtypes = [POINTER(MagickWand)]
MagickGetImageDispose = _lib.MagickGetImageDispose
MagickGetImageDispose.restype = DisposeType
MagickGetImageDispose.argtypes = [POINTER(MagickWand)]
MagickGetImageGamma = _lib.MagickGetImageGamma
MagickGetImageGamma.restype = c_double
MagickGetImageGamma.argtypes = [POINTER(MagickWand)]
MagickGetImageTotalInkDensity = _lib.MagickGetImageTotalInkDensity
MagickGetImageTotalInkDensity.restype = c_double
MagickGetImageTotalInkDensity.argtypes = [POINTER(MagickWand)]
GetImageFromMagickWand = _lib.GetImageFromMagickWand
GetImageFromMagickWand.restype = POINTER(Image)
GetImageFromMagickWand.argtypes = [POINTER(MagickWand)]
MagickGetImageType = _lib.MagickGetImageType
MagickGetImageType.restype = ImageType
MagickGetImageType.argtypes = [POINTER(MagickWand)]
MagickGetImageInterlaceScheme = _lib.MagickGetImageInterlaceScheme
MagickGetImageInterlaceScheme.restype = InterlaceType
MagickGetImageInterlaceScheme.argtypes = [POINTER(MagickWand)]
MagickAdaptiveThresholdImage = _lib.MagickAdaptiveThresholdImage
MagickAdaptiveThresholdImage.restype = MagickBooleanType
MagickAdaptiveThresholdImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long]
MagickAddImage = _lib.MagickAddImage
MagickAddImage.restype = MagickBooleanType
MagickAddImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand)]
MagickAddNoiseImage = _lib.MagickAddNoiseImage
MagickAddNoiseImage.restype = MagickBooleanType
MagickAddNoiseImage.argtypes = [POINTER(MagickWand), NoiseType]
MagickAffineTransformImage = _lib.MagickAffineTransformImage
MagickAffineTransformImage.restype = MagickBooleanType
MagickAffineTransformImage.argtypes = [POINTER(MagickWand), POINTER(DrawingWand)]
MagickAnnotateImage = _lib.MagickAnnotateImage
MagickAnnotateImage.restype = MagickBooleanType
MagickAnnotateImage.argtypes = [POINTER(MagickWand), POINTER(DrawingWand), c_double, c_double, c_double, STRING]
MagickAnimateImages = _lib.MagickAnimateImages
MagickAnimateImages.restype = MagickBooleanType
MagickAnimateImages.argtypes = [POINTER(MagickWand), STRING]
MagickBlackThresholdImage = _lib.MagickBlackThresholdImage
MagickBlackThresholdImage.restype = MagickBooleanType
MagickBlackThresholdImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickBlurImage = _lib.MagickBlurImage
MagickBlurImage.restype = MagickBooleanType
MagickBlurImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickBlurImageChannel = _lib.MagickBlurImageChannel
MagickBlurImageChannel.restype = MagickBooleanType
MagickBlurImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double, c_double]
MagickBorderImage = _lib.MagickBorderImage
MagickBorderImage.restype = MagickBooleanType
MagickBorderImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_ulong, c_ulong]
MagickCharcoalImage = _lib.MagickCharcoalImage
MagickCharcoalImage.restype = MagickBooleanType
MagickCharcoalImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickChopImage = _lib.MagickChopImage
MagickChopImage.restype = MagickBooleanType
MagickChopImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickClipImage = _lib.MagickClipImage
MagickClipImage.restype = MagickBooleanType
MagickClipImage.argtypes = [POINTER(MagickWand)]
MagickColorizeImage = _lib.MagickColorizeImage
MagickColorizeImage.restype = MagickBooleanType
MagickColorizeImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), POINTER(PixelWand)]
MagickCommentImage = _lib.MagickCommentImage
MagickCommentImage.restype = MagickBooleanType
MagickCommentImage.argtypes = [POINTER(MagickWand), STRING]
MagickCompositeImage = _lib.MagickCompositeImage
MagickCompositeImage.restype = MagickBooleanType
MagickCompositeImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand), CompositeOperator, c_long, c_long]
MagickConstituteImage = _lib.MagickConstituteImage
MagickConstituteImage.restype = MagickBooleanType
MagickConstituteImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, STRING, StorageType, c_void_p]
MagickContrastImage = _lib.MagickContrastImage
MagickContrastImage.restype = MagickBooleanType
MagickContrastImage.argtypes = [POINTER(MagickWand), MagickBooleanType]
MagickConvolveImage = _lib.MagickConvolveImage
MagickConvolveImage.restype = MagickBooleanType
MagickConvolveImage.argtypes = [POINTER(MagickWand), c_ulong, POINTER(c_double)]
MagickConvolveImageChannel = _lib.MagickConvolveImageChannel
MagickConvolveImageChannel.restype = MagickBooleanType
MagickConvolveImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_ulong, POINTER(c_double)]
MagickCropImage = _lib.MagickCropImage
MagickCropImage.restype = MagickBooleanType
MagickCropImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickCycleColormapImage = _lib.MagickCycleColormapImage
MagickCycleColormapImage.restype = MagickBooleanType
MagickCycleColormapImage.argtypes = [POINTER(MagickWand), c_long]
MagickDespeckleImage = _lib.MagickDespeckleImage
MagickDespeckleImage.restype = MagickBooleanType
MagickDespeckleImage.argtypes = [POINTER(MagickWand)]
MagickDisplayImage = _lib.MagickDisplayImage
MagickDisplayImage.restype = MagickBooleanType
MagickDisplayImage.argtypes = [POINTER(MagickWand), STRING]
MagickDisplayImages = _lib.MagickDisplayImages
MagickDisplayImages.restype = MagickBooleanType
MagickDisplayImages.argtypes = [POINTER(MagickWand), STRING]
MagickDrawImage = _lib.MagickDrawImage
MagickDrawImage.restype = MagickBooleanType
MagickDrawImage.argtypes = [POINTER(MagickWand), POINTER(DrawingWand)]
MagickEdgeImage = _lib.MagickEdgeImage
MagickEdgeImage.restype = MagickBooleanType
MagickEdgeImage.argtypes = [POINTER(MagickWand), c_double]
MagickEmbossImage = _lib.MagickEmbossImage
MagickEmbossImage.restype = MagickBooleanType
MagickEmbossImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickEnhanceImage = _lib.MagickEnhanceImage
MagickEnhanceImage.restype = MagickBooleanType
MagickEnhanceImage.argtypes = [POINTER(MagickWand)]
MagickEqualizeImage = _lib.MagickEqualizeImage
MagickEqualizeImage.restype = MagickBooleanType
MagickEqualizeImage.argtypes = [POINTER(MagickWand)]
MagickEvaluateImage = _lib.MagickEvaluateImage
MagickEvaluateImage.restype = MagickBooleanType
MagickEvaluateImage.argtypes = [POINTER(MagickWand), MagickEvaluateOperator, c_double]
MagickEvaluateImageChannel = _lib.MagickEvaluateImageChannel
MagickEvaluateImageChannel.restype = MagickBooleanType
MagickEvaluateImageChannel.argtypes = [POINTER(MagickWand), ChannelType, MagickEvaluateOperator, c_double]
MagickFlipImage = _lib.MagickFlipImage
MagickFlipImage.restype = MagickBooleanType
MagickFlipImage.argtypes = [POINTER(MagickWand)]
MagickFlopImage = _lib.MagickFlopImage
MagickFlopImage.restype = MagickBooleanType
MagickFlopImage.argtypes = [POINTER(MagickWand)]
MagickFrameImage = _lib.MagickFrameImage
MagickFrameImage.restype = MagickBooleanType
MagickFrameImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_ulong, c_ulong, c_long, c_long]
MagickGammaImage = _lib.MagickGammaImage
MagickGammaImage.restype = MagickBooleanType
MagickGammaImage.argtypes = [POINTER(MagickWand), c_double]
MagickGammaImageChannel = _lib.MagickGammaImageChannel
MagickGammaImageChannel.restype = MagickBooleanType
MagickGammaImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double]
MagickGaussianBlurImage = _lib.MagickGaussianBlurImage
MagickGaussianBlurImage.restype = MagickBooleanType
MagickGaussianBlurImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickGaussianBlurImageChannel = _lib.MagickGaussianBlurImageChannel
MagickGaussianBlurImageChannel.restype = MagickBooleanType
MagickGaussianBlurImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double, c_double]
MagickGetImageBackgroundColor = _lib.MagickGetImageBackgroundColor
MagickGetImageBackgroundColor.restype = MagickBooleanType
MagickGetImageBackgroundColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickGetImageBluePrimary = _lib.MagickGetImageBluePrimary
MagickGetImageBluePrimary.restype = MagickBooleanType
MagickGetImageBluePrimary.argtypes = [POINTER(MagickWand), POINTER(c_double), POINTER(c_double)]
MagickGetImageBorderColor = _lib.MagickGetImageBorderColor
MagickGetImageBorderColor.restype = MagickBooleanType
MagickGetImageBorderColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickGetImageChannelDistortion = _lib.MagickGetImageChannelDistortion
MagickGetImageChannelDistortion.restype = MagickBooleanType
MagickGetImageChannelDistortion.argtypes = [POINTER(MagickWand), POINTER(MagickWand), ChannelType, MetricType, POINTER(c_double)]
MagickGetImageDistortion = _lib.MagickGetImageDistortion
MagickGetImageDistortion.restype = MagickBooleanType
MagickGetImageDistortion.argtypes = [POINTER(MagickWand), POINTER(MagickWand), MetricType, POINTER(c_double)]
MagickGetImageChannelMean = _lib.MagickGetImageChannelMean
MagickGetImageChannelMean.restype = MagickBooleanType
MagickGetImageChannelMean.argtypes = [POINTER(MagickWand), ChannelType, POINTER(c_double), POINTER(c_double)]
MagickGetImageColormapColor = _lib.MagickGetImageColormapColor
MagickGetImageColormapColor.restype = MagickBooleanType
MagickGetImageColormapColor.argtypes = [POINTER(MagickWand), c_ulong, POINTER(PixelWand)]
MagickGetImageGreenPrimary = _lib.MagickGetImageGreenPrimary
MagickGetImageGreenPrimary.restype = MagickBooleanType
MagickGetImageGreenPrimary.argtypes = [POINTER(MagickWand), POINTER(c_double), POINTER(c_double)]
MagickGetImageMatteColor = _lib.MagickGetImageMatteColor
MagickGetImageMatteColor.restype = MagickBooleanType
MagickGetImageMatteColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickGetImagePage = _lib.MagickGetImagePage
MagickGetImagePage.restype = MagickBooleanType
MagickGetImagePage.argtypes = [POINTER(MagickWand), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_long), POINTER(c_long)]
MagickGetImagePixelColor = _lib.MagickGetImagePixelColor
MagickGetImagePixelColor.restype = MagickBooleanType
MagickGetImagePixelColor.argtypes = [POINTER(MagickWand), c_long, c_long, POINTER(PixelWand)]
MagickGetImagePixels = _lib.MagickGetImagePixels
MagickGetImagePixels.restype = MagickBooleanType
MagickGetImagePixels.argtypes = [POINTER(MagickWand), c_long, c_long, c_ulong, c_ulong, STRING, StorageType, c_void_p]
MagickGetImageRedPrimary = _lib.MagickGetImageRedPrimary
MagickGetImageRedPrimary.restype = MagickBooleanType
MagickGetImageRedPrimary.argtypes = [POINTER(MagickWand), POINTER(c_double), POINTER(c_double)]
MagickGetImageResolution = _lib.MagickGetImageResolution
MagickGetImageResolution.restype = MagickBooleanType
MagickGetImageResolution.argtypes = [POINTER(MagickWand), POINTER(c_double), POINTER(c_double)]
MagickGetImageWhitePoint = _lib.MagickGetImageWhitePoint
MagickGetImageWhitePoint.restype = MagickBooleanType
MagickGetImageWhitePoint.argtypes = [POINTER(MagickWand), POINTER(c_double), POINTER(c_double)]
MagickHasNextImage = _lib.MagickHasNextImage
MagickHasNextImage.restype = MagickBooleanType
MagickHasNextImage.argtypes = [POINTER(MagickWand)]
MagickHasPreviousImage = _lib.MagickHasPreviousImage
MagickHasPreviousImage.restype = MagickBooleanType
MagickHasPreviousImage.argtypes = [POINTER(MagickWand)]
MagickImplodeImage = _lib.MagickImplodeImage
MagickImplodeImage.restype = MagickBooleanType
MagickImplodeImage.argtypes = [POINTER(MagickWand), c_double]
MagickLabelImage = _lib.MagickLabelImage
MagickLabelImage.restype = MagickBooleanType
MagickLabelImage.argtypes = [POINTER(MagickWand), STRING]
MagickLevelImage = _lib.MagickLevelImage
MagickLevelImage.restype = MagickBooleanType
MagickLevelImage.argtypes = [POINTER(MagickWand), c_double, c_double, c_double]
MagickLevelImageChannel = _lib.MagickLevelImageChannel
MagickLevelImageChannel.restype = MagickBooleanType
MagickLevelImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double, c_double, c_double]
MagickMagnifyImage = _lib.MagickMagnifyImage
MagickMagnifyImage.restype = MagickBooleanType
MagickMagnifyImage.argtypes = [POINTER(MagickWand)]
MagickMapImage = _lib.MagickMapImage
MagickMapImage.restype = MagickBooleanType
MagickMapImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand), MagickBooleanType]
MagickMedianFilterImage = _lib.MagickMedianFilterImage
MagickMedianFilterImage.restype = MagickBooleanType
MagickMedianFilterImage.argtypes = [POINTER(MagickWand), c_double]
MagickMinifyImage = _lib.MagickMinifyImage
MagickMinifyImage.restype = MagickBooleanType
MagickMinifyImage.argtypes = [POINTER(MagickWand)]
MagickModulateImage = _lib.MagickModulateImage
MagickModulateImage.restype = MagickBooleanType
MagickModulateImage.argtypes = [POINTER(MagickWand), c_double, c_double, c_double]
MagickMotionBlurImage = _lib.MagickMotionBlurImage
MagickMotionBlurImage.restype = MagickBooleanType
MagickMotionBlurImage.argtypes = [POINTER(MagickWand), c_double, c_double, c_double]
MagickNegateImage = _lib.MagickNegateImage
MagickNegateImage.restype = MagickBooleanType
MagickNegateImage.argtypes = [POINTER(MagickWand), MagickBooleanType]
MagickNegateImageChannel = _lib.MagickNegateImageChannel
MagickNegateImageChannel.restype = MagickBooleanType
MagickNegateImageChannel.argtypes = [POINTER(MagickWand), ChannelType, MagickBooleanType]
MagickNewImage = _lib.MagickNewImage
MagickNewImage.restype = MagickBooleanType
MagickNewImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, POINTER(PixelWand)]
MagickNextImage = _lib.MagickNextImage
MagickNextImage.restype = MagickBooleanType
MagickNextImage.argtypes = [POINTER(MagickWand)]
MagickNormalizeImage = _lib.MagickNormalizeImage
MagickNormalizeImage.restype = MagickBooleanType
MagickNormalizeImage.argtypes = [POINTER(MagickWand)]
MagickOilPaintImage = _lib.MagickOilPaintImage
MagickOilPaintImage.restype = MagickBooleanType
MagickOilPaintImage.argtypes = [POINTER(MagickWand), c_double]
MagickPingImage = _lib.MagickPingImage
MagickPingImage.restype = MagickBooleanType
MagickPingImage.argtypes = [POINTER(MagickWand), STRING]
MagickPosterizeImage = _lib.MagickPosterizeImage
MagickPosterizeImage.restype = MagickBooleanType
MagickPosterizeImage.argtypes = [POINTER(MagickWand), c_ulong, MagickBooleanType]
MagickPreviousImage = _lib.MagickPreviousImage
MagickPreviousImage.restype = MagickBooleanType
MagickPreviousImage.argtypes = [POINTER(MagickWand)]
MagickQuantizeImage = _lib.MagickQuantizeImage
MagickQuantizeImage.restype = MagickBooleanType
MagickQuantizeImage.argtypes = [POINTER(MagickWand), c_ulong, ColorspaceType, c_ulong, MagickBooleanType, MagickBooleanType]
MagickQuantizeImages = _lib.MagickQuantizeImages
MagickQuantizeImages.restype = MagickBooleanType
MagickQuantizeImages.argtypes = [POINTER(MagickWand), c_ulong, ColorspaceType, c_ulong, MagickBooleanType, MagickBooleanType]
MagickRadialBlurImage = _lib.MagickRadialBlurImage
MagickRadialBlurImage.restype = MagickBooleanType
MagickRadialBlurImage.argtypes = [POINTER(MagickWand), c_double]
MagickRadialBlurImageChannel = _lib.MagickRadialBlurImageChannel
MagickRadialBlurImageChannel.restype = MagickBooleanType
MagickRadialBlurImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double]
MagickRaiseImage = _lib.MagickRaiseImage
MagickRaiseImage.restype = MagickBooleanType
MagickRaiseImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long, MagickBooleanType]
MagickReadImage = _lib.MagickReadImage
MagickReadImage.restype = MagickBooleanType
MagickReadImage.argtypes = [POINTER(MagickWand), STRING]
MagickReadImageBlob = _lib.MagickReadImageBlob
MagickReadImageBlob.restype = MagickBooleanType
MagickReadImageBlob.argtypes = [POINTER(MagickWand), c_void_p, size_t]
MagickReadImageFile = _lib.MagickReadImageFile
MagickReadImageFile.restype = MagickBooleanType
MagickReadImageFile.argtypes = [POINTER(MagickWand), POINTER(FILE)]
MagickReduceNoiseImage = _lib.MagickReduceNoiseImage
MagickReduceNoiseImage.restype = MagickBooleanType
MagickReduceNoiseImage.argtypes = [POINTER(MagickWand), c_double]
MagickRemoveImage = _lib.MagickRemoveImage
MagickRemoveImage.restype = MagickBooleanType
MagickRemoveImage.argtypes = [POINTER(MagickWand)]
MagickResampleImage = _lib.MagickResampleImage
MagickResampleImage.restype = MagickBooleanType
MagickResampleImage.argtypes = [POINTER(MagickWand), c_double, c_double, FilterTypes, c_double]
MagickResizeImage = _lib.MagickResizeImage
MagickResizeImage.restype = MagickBooleanType
MagickResizeImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, FilterTypes, c_double]
MagickRollImage = _lib.MagickRollImage
MagickRollImage.restype = MagickBooleanType
MagickRollImage.argtypes = [POINTER(MagickWand), c_long, c_long]
MagickRotateImage = _lib.MagickRotateImage
MagickRotateImage.restype = MagickBooleanType
MagickRotateImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_double]
MagickSampleImage = _lib.MagickSampleImage
MagickSampleImage.restype = MagickBooleanType
MagickSampleImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickScaleImage = _lib.MagickScaleImage
MagickScaleImage.restype = MagickBooleanType
MagickScaleImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickSeparateImageChannel = _lib.MagickSeparateImageChannel
MagickSeparateImageChannel.restype = MagickBooleanType
MagickSeparateImageChannel.argtypes = [POINTER(MagickWand), ChannelType]
MagickSepiaToneImage = _lib.MagickSepiaToneImage
MagickSepiaToneImage.restype = MagickBooleanType
MagickSepiaToneImage.argtypes = [POINTER(MagickWand), c_double]
MagickSetImage = _lib.MagickSetImage
MagickSetImage.restype = MagickBooleanType
MagickSetImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand)]
MagickSetImageBackgroundColor = _lib.MagickSetImageBackgroundColor
MagickSetImageBackgroundColor.restype = MagickBooleanType
MagickSetImageBackgroundColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickSetImageBias = _lib.MagickSetImageBias
MagickSetImageBias.restype = MagickBooleanType
MagickSetImageBias.argtypes = [POINTER(MagickWand), c_double]
MagickSetImageBluePrimary = _lib.MagickSetImageBluePrimary
MagickSetImageBluePrimary.restype = MagickBooleanType
MagickSetImageBluePrimary.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSetImageBorderColor = _lib.MagickSetImageBorderColor
MagickSetImageBorderColor.restype = MagickBooleanType
MagickSetImageBorderColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickSetImageChannelDepth = _lib.MagickSetImageChannelDepth
MagickSetImageChannelDepth.restype = MagickBooleanType
MagickSetImageChannelDepth.argtypes = [POINTER(MagickWand), ChannelType, c_ulong]
MagickSetImageColormapColor = _lib.MagickSetImageColormapColor
MagickSetImageColormapColor.restype = MagickBooleanType
MagickSetImageColormapColor.argtypes = [POINTER(MagickWand), c_ulong, POINTER(PixelWand)]
MagickSetImageCompose = _lib.MagickSetImageCompose
MagickSetImageCompose.restype = MagickBooleanType
MagickSetImageCompose.argtypes = [POINTER(MagickWand), CompositeOperator]
MagickSetImageCompression = _lib.MagickSetImageCompression
MagickSetImageCompression.restype = MagickBooleanType
MagickSetImageCompression.argtypes = [POINTER(MagickWand), CompressionType]
MagickSetImageDelay = _lib.MagickSetImageDelay
MagickSetImageDelay.restype = MagickBooleanType
MagickSetImageDelay.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetImageDepth = _lib.MagickSetImageDepth
MagickSetImageDepth.restype = MagickBooleanType
MagickSetImageDepth.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetImageDispose = _lib.MagickSetImageDispose
MagickSetImageDispose.restype = MagickBooleanType
MagickSetImageDispose.argtypes = [POINTER(MagickWand), DisposeType]
MagickSetImageColorspace = _lib.MagickSetImageColorspace
MagickSetImageColorspace.restype = MagickBooleanType
MagickSetImageColorspace.argtypes = [POINTER(MagickWand), ColorspaceType]
MagickSetImageCompressionQuality = _lib.MagickSetImageCompressionQuality
MagickSetImageCompressionQuality.restype = MagickBooleanType
MagickSetImageCompressionQuality.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetImageGreenPrimary = _lib.MagickSetImageGreenPrimary
MagickSetImageGreenPrimary.restype = MagickBooleanType
MagickSetImageGreenPrimary.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSetImageGamma = _lib.MagickSetImageGamma
MagickSetImageGamma.restype = MagickBooleanType
MagickSetImageGamma.argtypes = [POINTER(MagickWand), c_double]
MagickSetImageExtent = _lib.MagickSetImageExtent
MagickSetImageExtent.restype = MagickBooleanType
MagickSetImageExtent.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickSetImageFilename = _lib.MagickSetImageFilename
MagickSetImageFilename.restype = MagickBooleanType
MagickSetImageFilename.argtypes = [POINTER(MagickWand), STRING]
MagickSetImageFormat = _lib.MagickSetImageFormat
MagickSetImageFormat.restype = MagickBooleanType
MagickSetImageFormat.argtypes = [POINTER(MagickWand), STRING]
MagickSetImageInterlaceScheme = _lib.MagickSetImageInterlaceScheme
MagickSetImageInterlaceScheme.restype = MagickBooleanType
MagickSetImageInterlaceScheme.argtypes = [POINTER(MagickWand), InterlaceType]
MagickSetImageIterations = _lib.MagickSetImageIterations
MagickSetImageIterations.restype = MagickBooleanType
MagickSetImageIterations.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetImageMatteColor = _lib.MagickSetImageMatteColor
MagickSetImageMatteColor.restype = MagickBooleanType
MagickSetImageMatteColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickSetImagePage = _lib.MagickSetImagePage
MagickSetImagePage.restype = MagickBooleanType
MagickSetImagePage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickSetImagePixels = _lib.MagickSetImagePixels
MagickSetImagePixels.restype = MagickBooleanType
MagickSetImagePixels.argtypes = [POINTER(MagickWand), c_long, c_long, c_ulong, c_ulong, STRING, StorageType, c_void_p]
MagickSetImageRedPrimary = _lib.MagickSetImageRedPrimary
MagickSetImageRedPrimary.restype = MagickBooleanType
MagickSetImageRedPrimary.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSetImageRenderingIntent = _lib.MagickSetImageRenderingIntent
MagickSetImageRenderingIntent.restype = MagickBooleanType
MagickSetImageRenderingIntent.argtypes = [POINTER(MagickWand), RenderingIntent]
MagickSetImageResolution = _lib.MagickSetImageResolution
MagickSetImageResolution.restype = MagickBooleanType
MagickSetImageResolution.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSetImageScene = _lib.MagickSetImageScene
MagickSetImageScene.restype = MagickBooleanType
MagickSetImageScene.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetImageTicksPerSecond = _lib.MagickSetImageTicksPerSecond
MagickSetImageTicksPerSecond.restype = MagickBooleanType
MagickSetImageTicksPerSecond.argtypes = [POINTER(MagickWand), c_long]
MagickSetImageType = _lib.MagickSetImageType
MagickSetImageType.restype = MagickBooleanType
MagickSetImageType.argtypes = [POINTER(MagickWand), ImageType]
MagickSetImageUnits = _lib.MagickSetImageUnits
MagickSetImageUnits.restype = MagickBooleanType
MagickSetImageUnits.argtypes = [POINTER(MagickWand), ResolutionType]
MagickSetImageWhitePoint = _lib.MagickSetImageWhitePoint
MagickSetImageWhitePoint.restype = MagickBooleanType
MagickSetImageWhitePoint.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickShadowImage = _lib.MagickShadowImage
MagickShadowImage.restype = MagickBooleanType
MagickShadowImage.argtypes = [POINTER(MagickWand), c_double, c_double, c_long, c_long]
MagickSharpenImage = _lib.MagickSharpenImage
MagickSharpenImage.restype = MagickBooleanType
MagickSharpenImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSharpenImageChannel = _lib.MagickSharpenImageChannel
MagickSharpenImageChannel.restype = MagickBooleanType
MagickSharpenImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double, c_double]
MagickShaveImage = _lib.MagickShaveImage
MagickShaveImage.restype = MagickBooleanType
MagickShaveImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickShearImage = _lib.MagickShearImage
MagickShearImage.restype = MagickBooleanType
MagickShearImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), c_double, c_double]
MagickSigmoidalContrastImage = _lib.MagickSigmoidalContrastImage
MagickSigmoidalContrastImage.restype = MagickBooleanType
MagickSigmoidalContrastImage.argtypes = [POINTER(MagickWand), MagickBooleanType, c_double, c_double]
MagickSigmoidalContrastImageChannel = _lib.MagickSigmoidalContrastImageChannel
MagickSigmoidalContrastImageChannel.restype = MagickBooleanType
MagickSigmoidalContrastImageChannel.argtypes = [POINTER(MagickWand), ChannelType, MagickBooleanType, c_double, c_double]
MagickSolarizeImage = _lib.MagickSolarizeImage
MagickSolarizeImage.restype = MagickBooleanType
MagickSolarizeImage.argtypes = [POINTER(MagickWand), c_double]
MagickSpliceImage = _lib.MagickSpliceImage
MagickSpliceImage.restype = MagickBooleanType
MagickSpliceImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickSpreadImage = _lib.MagickSpreadImage
MagickSpreadImage.restype = MagickBooleanType
MagickSpreadImage.argtypes = [POINTER(MagickWand), c_double]
MagickStripImage = _lib.MagickStripImage
MagickStripImage.restype = MagickBooleanType
MagickStripImage.argtypes = [POINTER(MagickWand)]
MagickSwirlImage = _lib.MagickSwirlImage
MagickSwirlImage.restype = MagickBooleanType
MagickSwirlImage.argtypes = [POINTER(MagickWand), c_double]
MagickTintImage = _lib.MagickTintImage
MagickTintImage.restype = MagickBooleanType
MagickTintImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand), POINTER(PixelWand)]
MagickThresholdImage = _lib.MagickThresholdImage
MagickThresholdImage.restype = MagickBooleanType
MagickThresholdImage.argtypes = [POINTER(MagickWand), c_double]
MagickThresholdImageChannel = _lib.MagickThresholdImageChannel
MagickThresholdImageChannel.restype = MagickBooleanType
MagickThresholdImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double]
MagickThumbnailImage = _lib.MagickThumbnailImage
MagickThumbnailImage.restype = MagickBooleanType
MagickThumbnailImage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickTrimImage = _lib.MagickTrimImage
MagickTrimImage.restype = MagickBooleanType
MagickTrimImage.argtypes = [POINTER(MagickWand), c_double]
MagickUnsharpMaskImage = _lib.MagickUnsharpMaskImage
MagickUnsharpMaskImage.restype = MagickBooleanType
MagickUnsharpMaskImage.argtypes = [POINTER(MagickWand), c_double, c_double, c_double, c_double]
MagickUnsharpMaskImageChannel = _lib.MagickUnsharpMaskImageChannel
MagickUnsharpMaskImageChannel.restype = MagickBooleanType
MagickUnsharpMaskImageChannel.argtypes = [POINTER(MagickWand), ChannelType, c_double, c_double, c_double, c_double]
MagickWaveImage = _lib.MagickWaveImage
MagickWaveImage.restype = MagickBooleanType
MagickWaveImage.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickWhiteThresholdImage = _lib.MagickWhiteThresholdImage
MagickWhiteThresholdImage.restype = MagickBooleanType
MagickWhiteThresholdImage.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickWriteImage = _lib.MagickWriteImage
MagickWriteImage.restype = MagickBooleanType
MagickWriteImage.argtypes = [POINTER(MagickWand), STRING]
MagickWriteImageFile = _lib.MagickWriteImageFile
MagickWriteImageFile.restype = MagickBooleanType
MagickWriteImageFile.argtypes = [POINTER(MagickWand), POINTER(FILE)]
MagickWriteImages = _lib.MagickWriteImages
MagickWriteImages.restype = MagickBooleanType
MagickWriteImages.argtypes = [POINTER(MagickWand), STRING, MagickBooleanType]
MagickWriteImagesFile = _lib.MagickWriteImagesFile
MagickWriteImagesFile.restype = MagickBooleanType
MagickWriteImagesFile.argtypes = [POINTER(MagickWand), POINTER(FILE)]
MagickSetImageProgressMonitor = _lib.MagickSetImageProgressMonitor
MagickSetImageProgressMonitor.restype = MagickProgressMonitor
MagickSetImageProgressMonitor.argtypes = [POINTER(MagickWand), MagickProgressMonitor, c_void_p]
MagickAppendImages = _lib.MagickAppendImages
MagickAppendImages.restype = POINTER(MagickWand)
MagickAppendImages.argtypes = [POINTER(MagickWand), MagickBooleanType]
MagickAverageImages = _lib.MagickAverageImages
MagickAverageImages.restype = POINTER(MagickWand)
MagickAverageImages.argtypes = [POINTER(MagickWand)]
MagickCoalesceImages = _lib.MagickCoalesceImages
MagickCoalesceImages.restype = POINTER(MagickWand)
MagickCoalesceImages.argtypes = [POINTER(MagickWand)]
MagickCombineImages = _lib.MagickCombineImages
MagickCombineImages.restype = POINTER(MagickWand)
MagickCombineImages.argtypes = [POINTER(MagickWand), ChannelType]
MagickCompareImageChannels = _lib.MagickCompareImageChannels
MagickCompareImageChannels.restype = POINTER(MagickWand)
MagickCompareImageChannels.argtypes = [POINTER(MagickWand), POINTER(MagickWand), ChannelType, MetricType, POINTER(c_double)]
MagickCompareImages = _lib.MagickCompareImages
MagickCompareImages.restype = POINTER(MagickWand)
MagickCompareImages.argtypes = [POINTER(MagickWand), POINTER(MagickWand), MetricType, POINTER(c_double)]
MagickDeconstructImages = _lib.MagickDeconstructImages
MagickDeconstructImages.restype = POINTER(MagickWand)
MagickDeconstructImages.argtypes = [POINTER(MagickWand)]
MagickFxImage = _lib.MagickFxImage
MagickFxImage.restype = POINTER(MagickWand)
MagickFxImage.argtypes = [POINTER(MagickWand), STRING]
MagickFxImageChannel = _lib.MagickFxImageChannel
MagickFxImageChannel.restype = POINTER(MagickWand)
MagickFxImageChannel.argtypes = [POINTER(MagickWand), ChannelType, STRING]
MagickGetImage = _lib.MagickGetImage
MagickGetImage.restype = POINTER(MagickWand)
MagickGetImage.argtypes = [POINTER(MagickWand)]
MagickGetImageRegion = _lib.MagickGetImageRegion
MagickGetImageRegion.restype = POINTER(MagickWand)
MagickGetImageRegion.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickMorphImages = _lib.MagickMorphImages
MagickMorphImages.restype = POINTER(MagickWand)
MagickMorphImages.argtypes = [POINTER(MagickWand), c_ulong]
MagickMontageImage = _lib.MagickMontageImage
MagickMontageImage.restype = POINTER(MagickWand)
MagickMontageImage.argtypes = [POINTER(MagickWand), POINTER(DrawingWand), STRING, STRING, MontageMode, STRING]
MagickPreviewImages = _lib.MagickPreviewImages
MagickPreviewImages.restype = POINTER(MagickWand)
MagickPreviewImages.argtypes = [POINTER(MagickWand), PreviewType]
MagickSteganoImage = _lib.MagickSteganoImage
MagickSteganoImage.restype = POINTER(MagickWand)
MagickSteganoImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand), c_long]
MagickStereoImage = _lib.MagickStereoImage
MagickStereoImage.restype = POINTER(MagickWand)
MagickStereoImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand)]
MagickTextureImage = _lib.MagickTextureImage
MagickTextureImage.restype = POINTER(MagickWand)
MagickTextureImage.argtypes = [POINTER(MagickWand), POINTER(MagickWand)]
MagickTransformImage = _lib.MagickTransformImage
MagickTransformImage.restype = POINTER(MagickWand)
MagickTransformImage.argtypes = [POINTER(MagickWand), STRING, STRING]
MagickGetImageHistogram = _lib.MagickGetImageHistogram
MagickGetImageHistogram.restype = POINTER(POINTER(PixelWand))
MagickGetImageHistogram.argtypes = [POINTER(MagickWand), POINTER(c_ulong)]
MagickGetImageRenderingIntent = _lib.MagickGetImageRenderingIntent
MagickGetImageRenderingIntent.restype = RenderingIntent
MagickGetImageRenderingIntent.argtypes = [POINTER(MagickWand)]
MagickGetImageUnits = _lib.MagickGetImageUnits
MagickGetImageUnits.restype = ResolutionType
MagickGetImageUnits.argtypes = [POINTER(MagickWand)]
MagickGetImageBlob = _lib.MagickGetImageBlob
MagickGetImageBlob.restype = POINTER(c_ubyte)
MagickGetImageBlob.argtypes = [POINTER(MagickWand), POINTER(size_t)]
MagickGetImagesBlob = _lib.MagickGetImagesBlob
MagickGetImagesBlob.restype = POINTER(c_ubyte)
MagickGetImagesBlob.argtypes = [POINTER(MagickWand), POINTER(size_t)]
MagickGetImageColors = _lib.MagickGetImageColors
MagickGetImageColors.restype = c_ulong
MagickGetImageColors.argtypes = [POINTER(MagickWand)]
MagickGetImageCompressionQuality = _lib.MagickGetImageCompressionQuality
MagickGetImageCompressionQuality.restype = c_ulong
MagickGetImageCompressionQuality.argtypes = [POINTER(MagickWand)]
MagickGetImageDelay = _lib.MagickGetImageDelay
MagickGetImageDelay.restype = c_ulong
MagickGetImageDelay.argtypes = [POINTER(MagickWand)]
MagickGetImageChannelDepth = _lib.MagickGetImageChannelDepth
MagickGetImageChannelDepth.restype = c_ulong
MagickGetImageChannelDepth.argtypes = [POINTER(MagickWand), ChannelType]
MagickGetImageDepth = _lib.MagickGetImageDepth
MagickGetImageDepth.restype = c_ulong
MagickGetImageDepth.argtypes = [POINTER(MagickWand)]
MagickGetImageHeight = _lib.MagickGetImageHeight
MagickGetImageHeight.restype = c_ulong
MagickGetImageHeight.argtypes = [POINTER(MagickWand)]
MagickGetImageIterations = _lib.MagickGetImageIterations
MagickGetImageIterations.restype = c_ulong
MagickGetImageIterations.argtypes = [POINTER(MagickWand)]
MagickGetImageScene = _lib.MagickGetImageScene
MagickGetImageScene.restype = c_ulong
MagickGetImageScene.argtypes = [POINTER(MagickWand)]
MagickGetImageTicksPerSecond = _lib.MagickGetImageTicksPerSecond
MagickGetImageTicksPerSecond.restype = c_ulong
MagickGetImageTicksPerSecond.argtypes = [POINTER(MagickWand)]
MagickGetImageWidth = _lib.MagickGetImageWidth
MagickGetImageWidth.restype = c_ulong
MagickGetImageWidth.argtypes = [POINTER(MagickWand)]
MagickGetNumberImages = _lib.MagickGetNumberImages
MagickGetNumberImages.restype = c_ulong
MagickGetNumberImages.argtypes = [POINTER(MagickWand)]
MagickGetImageVirtualPixelMethod = _lib.MagickGetImageVirtualPixelMethod
MagickGetImageVirtualPixelMethod.restype = VirtualPixelMethod
MagickGetImageVirtualPixelMethod.argtypes = [POINTER(MagickWand)]
MagickGetFilename = _lib.MagickGetFilename
MagickGetFilename.restype = STRING
MagickGetFilename.argtypes = [POINTER(MagickWand)]
MagickGetFormat = _lib.MagickGetFormat
MagickGetFormat.restype = STRING
MagickGetFormat.argtypes = [POINTER(MagickWand)]
MagickGetHomeURL = _lib.MagickGetHomeURL
MagickGetHomeURL.restype = STRING
MagickGetHomeURL.argtypes = []
MagickGetOption = _lib.MagickGetOption
MagickGetOption.restype = STRING
MagickGetOption.argtypes = [POINTER(MagickWand), STRING]
MagickQueryConfigureOption = _lib.MagickQueryConfigureOption
MagickQueryConfigureOption.restype = STRING
MagickQueryConfigureOption.argtypes = [STRING]
MagickQueryConfigureOptions = _lib.MagickQueryConfigureOptions
MagickQueryConfigureOptions.restype = POINTER(STRING)
MagickQueryConfigureOptions.argtypes = [STRING, POINTER(c_ulong)]
MagickQueryFonts = _lib.MagickQueryFonts
MagickQueryFonts.restype = POINTER(STRING)
MagickQueryFonts.argtypes = [STRING, POINTER(c_ulong)]
MagickQueryFormats = _lib.MagickQueryFormats
MagickQueryFormats.restype = POINTER(STRING)
MagickQueryFormats.argtypes = [STRING, POINTER(c_ulong)]
MagickGetCompression = _lib.MagickGetCompression
MagickGetCompression.restype = CompressionType
MagickGetCompression.argtypes = [POINTER(MagickWand)]
MagickGetCopyright = _lib.MagickGetCopyright
MagickGetCopyright.restype = STRING
MagickGetCopyright.argtypes = []
MagickGetPackageName = _lib.MagickGetPackageName
MagickGetPackageName.restype = STRING
MagickGetPackageName.argtypes = []
MagickGetQuantumDepth = _lib.MagickGetQuantumDepth
MagickGetQuantumDepth.restype = STRING
MagickGetQuantumDepth.argtypes = [POINTER(c_ulong)]
MagickGetQuantumRange = _lib.MagickGetQuantumRange
MagickGetQuantumRange.restype = STRING
MagickGetQuantumRange.argtypes = [POINTER(c_ulong)]
MagickGetReleaseDate = _lib.MagickGetReleaseDate
MagickGetReleaseDate.restype = STRING
MagickGetReleaseDate.argtypes = []
MagickGetVersion = _lib.MagickGetVersion
MagickGetVersion.restype = STRING
MagickGetVersion.argtypes = [POINTER(c_ulong)]
MagickGetSamplingFactors = _lib.MagickGetSamplingFactors
MagickGetSamplingFactors.restype = POINTER(c_double)
MagickGetSamplingFactors.argtypes = [POINTER(MagickWand), POINTER(c_ulong)]
MagickQueryFontMetrics = _lib.MagickQueryFontMetrics
MagickQueryFontMetrics.restype = POINTER(c_double)
MagickQueryFontMetrics.argtypes = [POINTER(MagickWand), POINTER(DrawingWand), STRING]
MagickQueryMultilineFontMetrics = _lib.MagickQueryMultilineFontMetrics
MagickQueryMultilineFontMetrics.restype = POINTER(c_double)
MagickQueryMultilineFontMetrics.argtypes = [POINTER(MagickWand), POINTER(DrawingWand), STRING]
MagickGetInterlaceScheme = _lib.MagickGetInterlaceScheme
MagickGetInterlaceScheme.restype = InterlaceType
MagickGetInterlaceScheme.argtypes = [POINTER(MagickWand)]
MagickGetPage = _lib.MagickGetPage
MagickGetPage.restype = MagickBooleanType
MagickGetPage.argtypes = [POINTER(MagickWand), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_long), POINTER(c_long)]
MagickGetSize = _lib.MagickGetSize
MagickGetSize.restype = MagickBooleanType
MagickGetSize.argtypes = [POINTER(MagickWand), POINTER(c_ulong), POINTER(c_ulong)]
MagickProfileImage = _lib.MagickProfileImage
MagickProfileImage.restype = MagickBooleanType
MagickProfileImage.argtypes = [POINTER(MagickWand), STRING, c_void_p, size_t]
MagickSetBackgroundColor = _lib.MagickSetBackgroundColor
MagickSetBackgroundColor.restype = MagickBooleanType
MagickSetBackgroundColor.argtypes = [POINTER(MagickWand), POINTER(PixelWand)]
MagickSetCompression = _lib.MagickSetCompression
MagickSetCompression.restype = MagickBooleanType
MagickSetCompression.argtypes = [POINTER(MagickWand), CompressionType]
MagickSetCompressionQuality = _lib.MagickSetCompressionQuality
MagickSetCompressionQuality.restype = MagickBooleanType
MagickSetCompressionQuality.argtypes = [POINTER(MagickWand), c_ulong]
MagickSetFilename = _lib.MagickSetFilename
MagickSetFilename.restype = MagickBooleanType
MagickSetFilename.argtypes = [POINTER(MagickWand), STRING]
MagickSetFormat = _lib.MagickSetFormat
MagickSetFormat.restype = MagickBooleanType
MagickSetFormat.argtypes = [POINTER(MagickWand), STRING]
MagickSetImageProfile = _lib.MagickSetImageProfile
MagickSetImageProfile.restype = MagickBooleanType
MagickSetImageProfile.argtypes = [POINTER(MagickWand), STRING, c_void_p, size_t]
MagickSetImageAlphaChannel = _lib.MagickSetImageAlphaChannel
MagickSetImageAlphaChannel.restype = MagickBooleanType
MagickSetImageAlphaChannel.argtypes = [POINTER(MagickWand), MagickBooleanType]
MagickSetInterlaceScheme = _lib.MagickSetInterlaceScheme
MagickSetInterlaceScheme.restype = MagickBooleanType
MagickSetInterlaceScheme.argtypes = [POINTER(MagickWand), InterlaceType]
MagickSetOption = _lib.MagickSetOption
MagickSetOption.restype = MagickBooleanType
MagickSetOption.argtypes = [POINTER(MagickWand), STRING, STRING]
MagickSetPage = _lib.MagickSetPage
MagickSetPage.restype = MagickBooleanType
MagickSetPage.argtypes = [POINTER(MagickWand), c_ulong, c_ulong, c_long, c_long]
MagickSetPassphrase = _lib.MagickSetPassphrase
MagickSetPassphrase.restype = MagickBooleanType
MagickSetPassphrase.argtypes = [POINTER(MagickWand), STRING]
MagickSetResolution = _lib.MagickSetResolution
MagickSetResolution.restype = MagickBooleanType
MagickSetResolution.argtypes = [POINTER(MagickWand), c_double, c_double]
MagickSetResourceLimit = _lib.MagickSetResourceLimit
MagickSetResourceLimit.restype = MagickBooleanType
MagickSetResourceLimit.argtypes = [ResourceType, MagickSizeType]
MagickSetSamplingFactors = _lib.MagickSetSamplingFactors
MagickSetSamplingFactors.restype = MagickBooleanType
MagickSetSamplingFactors.argtypes = [POINTER(MagickWand), c_ulong, POINTER(c_double)]
MagickSetSize = _lib.MagickSetSize
MagickSetSize.restype = MagickBooleanType
MagickSetSize.argtypes = [POINTER(MagickWand), c_ulong, c_ulong]
MagickSetType = _lib.MagickSetType
MagickSetType.restype = MagickBooleanType
MagickSetType.argtypes = [POINTER(MagickWand), ImageType]
MagickSetProgressMonitor = _lib.MagickSetProgressMonitor
MagickSetProgressMonitor.restype = MagickProgressMonitor
MagickSetProgressMonitor.argtypes = [POINTER(MagickWand), MagickProgressMonitor, c_void_p]
MagickGetImageProfile = _lib.MagickGetImageProfile
MagickGetImageProfile.restype = POINTER(c_ubyte)
MagickGetImageProfile.argtypes = [POINTER(MagickWand), STRING, POINTER(size_t)]
MagickRemoveImageProfile = _lib.MagickRemoveImageProfile
MagickRemoveImageProfile.restype = POINTER(c_ubyte)
MagickRemoveImageProfile.argtypes = [POINTER(MagickWand), STRING, POINTER(size_t)]
MagickGetCompressionQuality = _lib.MagickGetCompressionQuality
MagickGetCompressionQuality.restype = c_ulong
MagickGetCompressionQuality.argtypes = [POINTER(MagickWand)]
MagickGetResource = _lib.MagickGetResource
MagickGetResource.restype = c_ulong
MagickGetResource.argtypes = [ResourceType]
MagickGetResourceLimit = _lib.MagickGetResourceLimit
MagickGetResourceLimit.restype = c_ulong
MagickGetResourceLimit.argtypes = [ResourceType]
MogrifyImage = _lib.MogrifyImage
MogrifyImage.restype = MagickBooleanType
MogrifyImage.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(POINTER(Image)), POINTER(ExceptionInfo)]
MogrifyImageCommand = _lib.MogrifyImageCommand
MogrifyImageCommand.restype = MagickBooleanType
MogrifyImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
MogrifyImageInfo = _lib.MogrifyImageInfo
MogrifyImageInfo.restype = MagickBooleanType
MogrifyImageInfo.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(ExceptionInfo)]
MogrifyImageList = _lib.MogrifyImageList
MogrifyImageList.restype = MagickBooleanType
MogrifyImageList.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(POINTER(Image)), POINTER(ExceptionInfo)]
MogrifyImages = _lib.MogrifyImages
MogrifyImages.restype = MagickBooleanType
MogrifyImages.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(POINTER(Image)), POINTER(ExceptionInfo)]
MontageImageCommand = _lib.MontageImageCommand
MontageImageCommand.restype = MagickBooleanType
MontageImageCommand.argtypes = [POINTER(ImageInfo), c_int, POINTER(STRING), POINTER(STRING), POINTER(ExceptionInfo)]
_PixelIterator._fields_ = [
]
PixelGetIteratorException = _lib.PixelGetIteratorException
PixelGetIteratorException.restype = STRING
PixelGetIteratorException.argtypes = [POINTER(PixelIterator), POINTER(ExceptionType)]
IsPixelIterator = _lib.IsPixelIterator
IsPixelIterator.restype = MagickBooleanType
IsPixelIterator.argtypes = [POINTER(PixelIterator)]
PixelClearIteratorException = _lib.PixelClearIteratorException
PixelClearIteratorException.restype = MagickBooleanType
PixelClearIteratorException.argtypes = [POINTER(PixelIterator)]
PixelSetIteratorRow = _lib.PixelSetIteratorRow
PixelSetIteratorRow.restype = MagickBooleanType
PixelSetIteratorRow.argtypes = [POINTER(PixelIterator), c_long]
PixelSyncIterator = _lib.PixelSyncIterator
PixelSyncIterator.restype = MagickBooleanType
PixelSyncIterator.argtypes = [POINTER(PixelIterator)]
DestroyPixelIterator = _lib.DestroyPixelIterator
DestroyPixelIterator.restype = POINTER(PixelIterator)
DestroyPixelIterator.argtypes = [POINTER(PixelIterator)]
NewPixelIterator = _lib.NewPixelIterator
NewPixelIterator.restype = POINTER(PixelIterator)
NewPixelIterator.argtypes = [POINTER(MagickWand)]
NewPixelRegionIterator = _lib.NewPixelRegionIterator
NewPixelRegionIterator.restype = POINTER(PixelIterator)
NewPixelRegionIterator.argtypes = [POINTER(MagickWand), c_long, c_long, c_ulong, c_ulong]
PixelGetNextIteratorRow = _lib.PixelGetNextIteratorRow
PixelGetNextIteratorRow.restype = POINTER(POINTER(PixelWand))
PixelGetNextIteratorRow.argtypes = [POINTER(PixelIterator), POINTER(c_ulong)]
PixelGetPreviousIteratorRow = _lib.PixelGetPreviousIteratorRow
PixelGetPreviousIteratorRow.restype = POINTER(POINTER(PixelWand))
PixelGetPreviousIteratorRow.argtypes = [POINTER(PixelIterator), POINTER(c_ulong)]
ClearPixelIterator = _lib.ClearPixelIterator
ClearPixelIterator.restype = None
ClearPixelIterator.argtypes = [POINTER(PixelIterator)]
PixelResetIterator = _lib.PixelResetIterator
PixelResetIterator.restype = None
PixelResetIterator.argtypes = [POINTER(PixelIterator)]
PixelSetFirstIteratorRow = _lib.PixelSetFirstIteratorRow
PixelSetFirstIteratorRow.restype = None
PixelSetFirstIteratorRow.argtypes = [POINTER(PixelIterator)]
PixelSetLastIteratorRow = _lib.PixelSetLastIteratorRow
PixelSetLastIteratorRow.restype = None
PixelSetLastIteratorRow.argtypes = [POINTER(PixelIterator)]
_PixelWand._fields_ = [
]
PixelGetColorAsString = _lib.PixelGetColorAsString
PixelGetColorAsString.restype = STRING
PixelGetColorAsString.argtypes = [POINTER(PixelWand)]
PixelGetException = _lib.PixelGetException
PixelGetException.restype = STRING
PixelGetException.argtypes = [POINTER(PixelWand), POINTER(ExceptionType)]
PixelGetAlpha = _lib.PixelGetAlpha
PixelGetAlpha.restype = c_double
PixelGetAlpha.argtypes = [POINTER(PixelWand)]
PixelGetBlack = _lib.PixelGetBlack
PixelGetBlack.restype = c_double
PixelGetBlack.argtypes = [POINTER(PixelWand)]
PixelGetBlue = _lib.PixelGetBlue
PixelGetBlue.restype = c_double
PixelGetBlue.argtypes = [POINTER(PixelWand)]
PixelGetCyan = _lib.PixelGetCyan
PixelGetCyan.restype = c_double
PixelGetCyan.argtypes = [POINTER(PixelWand)]
PixelGetGreen = _lib.PixelGetGreen
PixelGetGreen.restype = c_double
PixelGetGreen.argtypes = [POINTER(PixelWand)]
PixelGetMagenta = _lib.PixelGetMagenta
PixelGetMagenta.restype = c_double
PixelGetMagenta.argtypes = [POINTER(PixelWand)]
PixelGetOpacity = _lib.PixelGetOpacity
PixelGetOpacity.restype = c_double
PixelGetOpacity.argtypes = [POINTER(PixelWand)]
PixelGetRed = _lib.PixelGetRed
PixelGetRed.restype = c_double
PixelGetRed.argtypes = [POINTER(PixelWand)]
PixelGetYellow = _lib.PixelGetYellow
PixelGetYellow.restype = c_double
PixelGetYellow.argtypes = [POINTER(PixelWand)]
PixelGetIndex = _lib.PixelGetIndex
PixelGetIndex.restype = IndexPacket
PixelGetIndex.argtypes = [POINTER(PixelWand)]
IsPixelWand = _lib.IsPixelWand
IsPixelWand.restype = MagickBooleanType
IsPixelWand.argtypes = [POINTER(PixelWand)]
IsPixelWandSimilar = _lib.IsPixelWandSimilar
IsPixelWandSimilar.restype = MagickBooleanType
IsPixelWandSimilar.argtypes = [POINTER(PixelWand), POINTER(PixelWand), c_double]
PixelClearException = _lib.PixelClearException
PixelClearException.restype = MagickBooleanType
PixelClearException.argtypes = [POINTER(PixelWand)]
PixelSetColor = _lib.PixelSetColor
PixelSetColor.restype = MagickBooleanType
PixelSetColor.argtypes = [POINTER(PixelWand), STRING]
DestroyPixelWand = _lib.DestroyPixelWand
DestroyPixelWand.restype = POINTER(PixelWand)
DestroyPixelWand.argtypes = [POINTER(PixelWand)]
DestroyPixelWands = _lib.DestroyPixelWands
DestroyPixelWands.restype = POINTER(POINTER(PixelWand))
DestroyPixelWands.argtypes = [POINTER(POINTER(PixelWand)), c_ulong]
NewPixelWand = _lib.NewPixelWand
NewPixelWand.restype = POINTER(PixelWand)
NewPixelWand.argtypes = []
NewPixelWands = _lib.NewPixelWands
NewPixelWands.restype = POINTER(POINTER(PixelWand))
NewPixelWands.argtypes = [c_ulong]
PixelGetAlphaQuantum = _lib.PixelGetAlphaQuantum
PixelGetAlphaQuantum.restype = Quantum
PixelGetAlphaQuantum.argtypes = [POINTER(PixelWand)]
PixelGetBlackQuantum = _lib.PixelGetBlackQuantum
PixelGetBlackQuantum.restype = Quantum
PixelGetBlackQuantum.argtypes = [POINTER(PixelWand)]
PixelGetBlueQuantum = _lib.PixelGetBlueQuantum
PixelGetBlueQuantum.restype = Quantum
PixelGetBlueQuantum.argtypes = [POINTER(PixelWand)]
PixelGetCyanQuantum = _lib.PixelGetCyanQuantum
PixelGetCyanQuantum.restype = Quantum
PixelGetCyanQuantum.argtypes = [POINTER(PixelWand)]
PixelGetGreenQuantum = _lib.PixelGetGreenQuantum
PixelGetGreenQuantum.restype = Quantum
PixelGetGreenQuantum.argtypes = [POINTER(PixelWand)]
PixelGetMagentaQuantum = _lib.PixelGetMagentaQuantum
PixelGetMagentaQuantum.restype = Quantum
PixelGetMagentaQuantum.argtypes = [POINTER(PixelWand)]
PixelGetOpacityQuantum = _lib.PixelGetOpacityQuantum
PixelGetOpacityQuantum.restype = Quantum
PixelGetOpacityQuantum.argtypes = [POINTER(PixelWand)]
PixelGetRedQuantum = _lib.PixelGetRedQuantum
PixelGetRedQuantum.restype = Quantum
PixelGetRedQuantum.argtypes = [POINTER(PixelWand)]
PixelGetYellowQuantum = _lib.PixelGetYellowQuantum
PixelGetYellowQuantum.restype = Quantum
PixelGetYellowQuantum.argtypes = [POINTER(PixelWand)]
PixelGetColorCount = _lib.PixelGetColorCount
PixelGetColorCount.restype = c_ulong
PixelGetColorCount.argtypes = [POINTER(PixelWand)]
ClearPixelWand = _lib.ClearPixelWand
ClearPixelWand.restype = None
ClearPixelWand.argtypes = [POINTER(PixelWand)]
PixelGetMagickColor = _lib.PixelGetMagickColor
PixelGetMagickColor.restype = None
PixelGetMagickColor.argtypes = [POINTER(PixelWand), POINTER(MagickPixelPacket)]
PixelGetQuantumColor = _lib.PixelGetQuantumColor
PixelGetQuantumColor.restype = None
PixelGetQuantumColor.argtypes = [POINTER(PixelWand), POINTER(PixelPacket)]
PixelSetAlpha = _lib.PixelSetAlpha
PixelSetAlpha.restype = None
PixelSetAlpha.argtypes = [POINTER(PixelWand), c_double]
PixelSetAlphaQuantum = _lib.PixelSetAlphaQuantum
PixelSetAlphaQuantum.restype = None
PixelSetAlphaQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetBlack = _lib.PixelSetBlack
PixelSetBlack.restype = None
PixelSetBlack.argtypes = [POINTER(PixelWand), c_double]
PixelSetBlackQuantum = _lib.PixelSetBlackQuantum
PixelSetBlackQuantum.restype = None
PixelSetBlackQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetBlue = _lib.PixelSetBlue
PixelSetBlue.restype = None
PixelSetBlue.argtypes = [POINTER(PixelWand), c_double]
PixelSetBlueQuantum = _lib.PixelSetBlueQuantum
PixelSetBlueQuantum.restype = None
PixelSetBlueQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetColorCount = _lib.PixelSetColorCount
PixelSetColorCount.restype = None
PixelSetColorCount.argtypes = [POINTER(PixelWand), c_ulong]
PixelSetCyan = _lib.PixelSetCyan
PixelSetCyan.restype = None
PixelSetCyan.argtypes = [POINTER(PixelWand), c_double]
PixelSetCyanQuantum = _lib.PixelSetCyanQuantum
PixelSetCyanQuantum.restype = None
PixelSetCyanQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetGreen = _lib.PixelSetGreen
PixelSetGreen.restype = None
PixelSetGreen.argtypes = [POINTER(PixelWand), c_double]
PixelSetGreenQuantum = _lib.PixelSetGreenQuantum
PixelSetGreenQuantum.restype = None
PixelSetGreenQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetIndex = _lib.PixelSetIndex
PixelSetIndex.restype = None
PixelSetIndex.argtypes = [POINTER(PixelWand), IndexPacket]
PixelSetMagenta = _lib.PixelSetMagenta
PixelSetMagenta.restype = None
PixelSetMagenta.argtypes = [POINTER(PixelWand), c_double]
PixelSetMagentaQuantum = _lib.PixelSetMagentaQuantum
PixelSetMagentaQuantum.restype = None
PixelSetMagentaQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetOpacity = _lib.PixelSetOpacity
PixelSetOpacity.restype = None
PixelSetOpacity.argtypes = [POINTER(PixelWand), c_double]
PixelSetOpacityQuantum = _lib.PixelSetOpacityQuantum
PixelSetOpacityQuantum.restype = None
PixelSetOpacityQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetQuantumColor = _lib.PixelSetQuantumColor
PixelSetQuantumColor.restype = None
PixelSetQuantumColor.argtypes = [POINTER(PixelWand), POINTER(PixelPacket)]
PixelSetRed = _lib.PixelSetRed
PixelSetRed.restype = None
PixelSetRed.argtypes = [POINTER(PixelWand), c_double]
PixelSetRedQuantum = _lib.PixelSetRedQuantum
PixelSetRedQuantum.restype = None
PixelSetRedQuantum.argtypes = [POINTER(PixelWand), Quantum]
PixelSetYellow = _lib.PixelSetYellow
PixelSetYellow.restype = None
PixelSetYellow.argtypes = [POINTER(PixelWand), c_double]
PixelSetYellowQuantum = _lib.PixelSetYellowQuantum
PixelSetYellowQuantum.restype = None
PixelSetYellowQuantum.argtypes = [POINTER(PixelWand), Quantum]
