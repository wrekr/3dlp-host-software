# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _freesteelpy

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


class FileLocation(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, FileLocation, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, FileLocation, name)
    def __repr__(self):
        return "<C FileLocation instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FileLocation, 'this', _freesteelpy.new_FileLocation(*args))
        _swig_setattr(self, FileLocation, 'thisown', 1)
    def isValid(*args, **kwargs): return _freesteelpy.FileLocation_isValid(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FileLocation):
        try:
            if self.thisown: destroy(self)
        except: pass

class FileLocationPtr(FileLocation):
    def __init__(self, this):
        _swig_setattr(self, FileLocation, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FileLocation, 'thisown', 0)
        _swig_setattr(self, FileLocation,self.__class__,FileLocation)
_freesteelpy.FileLocation_swigregister(FileLocationPtr)

class DynamicObject(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, DynamicObject, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, DynamicObject, name)
    def __repr__(self):
        return "<C DynamicObject instance at %s>" % (self.this,)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, DynamicObject, 'this', _freesteelpy.new_DynamicObject(*args, **kwargs))
        _swig_setattr(self, DynamicObject, 'thisown', 1)
    def getFileLocation(*args, **kwargs): return _freesteelpy.DynamicObject_getFileLocation(*args, **kwargs)
    def setFileLocation(*args, **kwargs): return _freesteelpy.DynamicObject_setFileLocation(*args, **kwargs)
    def getObjectId(*args, **kwargs): return _freesteelpy.DynamicObject_getObjectId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_DynamicObject):
        try:
            if self.thisown: destroy(self)
        except: pass

class DynamicObjectPtr(DynamicObject):
    def __init__(self, this):
        _swig_setattr(self, DynamicObject, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, DynamicObject, 'thisown', 0)
        _swig_setattr(self, DynamicObject,self.__class__,DynamicObject)
_freesteelpy.DynamicObject_swigregister(DynamicObjectPtr)

class FsSurfInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurfInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurfInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsSurf)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsSurfInstanceCounter, 'this', _freesteelpy.new_FsSurfInstanceCounter(*args))
        _swig_setattr(self, FsSurfInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsSurfInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurfInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsSurfInstanceCounterPtr(FsSurfInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsSurfInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurfInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsSurfInstanceCounter,self.__class__,FsSurfInstanceCounter)
_freesteelpy.FsSurfInstanceCounter_swigregister(FsSurfInstanceCounterPtr)

class FsFibreInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsFibreInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsFibreInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsFibre)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsFibreInstanceCounter, 'this', _freesteelpy.new_FsFibreInstanceCounter(*args))
        _swig_setattr(self, FsFibreInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsFibreInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsFibreInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsFibreInstanceCounterPtr(FsFibreInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsFibreInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsFibreInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsFibreInstanceCounter,self.__class__,FsFibreInstanceCounter)
_freesteelpy.FsFibreInstanceCounter_swigregister(FsFibreInstanceCounterPtr)

class FsSurfaceHitRegistryInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurfaceHitRegistryInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsSurfaceHitRegistry)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter, 'this', _freesteelpy.new_FsSurfaceHitRegistryInstanceCounter(*args))
        _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsSurfaceHitRegistryInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurfaceHitRegistryInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsSurfaceHitRegistryInstanceCounterPtr(FsSurfaceHitRegistryInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsSurfaceHitRegistryInstanceCounter,self.__class__,FsSurfaceHitRegistryInstanceCounter)
_freesteelpy.FsSurfaceHitRegistryInstanceCounter_swigregister(FsSurfaceHitRegistryInstanceCounterPtr)

class FsSurfaceHitRegInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurfaceHitRegInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurfaceHitRegInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsSurfaceHitReg)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsSurfaceHitRegInstanceCounter, 'this', _freesteelpy.new_FsSurfaceHitRegInstanceCounter(*args))
        _swig_setattr(self, FsSurfaceHitRegInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsSurfaceHitRegInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurfaceHitRegInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsSurfaceHitRegInstanceCounterPtr(FsSurfaceHitRegInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsSurfaceHitRegInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurfaceHitRegInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsSurfaceHitRegInstanceCounter,self.__class__,FsSurfaceHitRegInstanceCounter)
_freesteelpy.FsSurfaceHitRegInstanceCounter_swigregister(FsSurfaceHitRegInstanceCounterPtr)

class FsWeaveInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsWeaveInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsWeaveInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsWeave)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsWeaveInstanceCounter, 'this', _freesteelpy.new_FsWeaveInstanceCounter(*args))
        _swig_setattr(self, FsWeaveInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsWeaveInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsWeaveInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsWeaveInstanceCounterPtr(FsWeaveInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsWeaveInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsWeaveInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsWeaveInstanceCounter,self.__class__,FsWeaveInstanceCounter)
_freesteelpy.FsWeaveInstanceCounter_swigregister(FsWeaveInstanceCounterPtr)

class FsBoundariesInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsBoundariesInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsBoundariesInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsBoundaries)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsBoundariesInstanceCounter, 'this', _freesteelpy.new_FsBoundariesInstanceCounter(*args))
        _swig_setattr(self, FsBoundariesInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsBoundariesInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsBoundariesInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsBoundariesInstanceCounterPtr(FsBoundariesInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsBoundariesInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsBoundariesInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsBoundariesInstanceCounter,self.__class__,FsBoundariesInstanceCounter)
_freesteelpy.FsBoundariesInstanceCounter_swigregister(FsBoundariesInstanceCounterPtr)

class FsBoxedPathInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsBoxedPathInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsBoxedPathInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsBoxedPath)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsBoxedPathInstanceCounter, 'this', _freesteelpy.new_FsBoxedPathInstanceCounter(*args))
        _swig_setattr(self, FsBoxedPathInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsBoxedPathInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsBoxedPathInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsBoxedPathInstanceCounterPtr(FsBoxedPathInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsBoxedPathInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsBoxedPathInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsBoxedPathInstanceCounter,self.__class__,FsBoxedPathInstanceCounter)
_freesteelpy.FsBoxedPathInstanceCounter_swigregister(FsBoxedPathInstanceCounterPtr)

class FsHorizontalInflexionAvoidanceInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsHorizontalInflexionAvoidance)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, 'this', _freesteelpy.new_FsHorizontalInflexionAvoidanceInstanceCounter(*args))
        _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsHorizontalInflexionAvoidanceInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsHorizontalInflexionAvoidanceInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsHorizontalInflexionAvoidanceInstanceCounterPtr(FsHorizontalInflexionAvoidanceInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsHorizontalInflexionAvoidanceInstanceCounter,self.__class__,FsHorizontalInflexionAvoidanceInstanceCounter)
_freesteelpy.FsHorizontalInflexionAvoidanceInstanceCounter_swigregister(FsHorizontalInflexionAvoidanceInstanceCounterPtr)

class FsHorizontalToolSurfaceInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsHorizontalToolSurfaceInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsHorizontalToolSurface)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter, 'this', _freesteelpy.new_FsHorizontalToolSurfaceInstanceCounter(*args))
        _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurfaceInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsHorizontalToolSurfaceInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsHorizontalToolSurfaceInstanceCounterPtr(FsHorizontalToolSurfaceInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsHorizontalToolSurfaceInstanceCounter,self.__class__,FsHorizontalToolSurfaceInstanceCounter)
_freesteelpy.FsHorizontalToolSurfaceInstanceCounter_swigregister(FsHorizontalToolSurfaceInstanceCounterPtr)

class FsImplicitAreaInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsImplicitAreaInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsImplicitAreaInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsImplicitArea)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsImplicitAreaInstanceCounter, 'this', _freesteelpy.new_FsImplicitAreaInstanceCounter(*args))
        _swig_setattr(self, FsImplicitAreaInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsImplicitAreaInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsImplicitAreaInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsImplicitAreaInstanceCounterPtr(FsImplicitAreaInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsImplicitAreaInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsImplicitAreaInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsImplicitAreaInstanceCounter,self.__class__,FsImplicitAreaInstanceCounter)
_freesteelpy.FsImplicitAreaInstanceCounter_swigregister(FsImplicitAreaInstanceCounterPtr)

class FsPath2XInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsPath2XInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsPath2XInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsPath2X)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsPath2XInstanceCounter, 'this', _freesteelpy.new_FsPath2XInstanceCounter(*args))
        _swig_setattr(self, FsPath2XInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsPath2XInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsPath2XInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsPath2XInstanceCounterPtr(FsPath2XInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsPath2XInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsPath2XInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsPath2XInstanceCounter,self.__class__,FsPath2XInstanceCounter)
_freesteelpy.FsPath2XInstanceCounter_swigregister(FsPath2XInstanceCounterPtr)

class ThinnerInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, ThinnerInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, ThinnerInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(Thinner)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, ThinnerInstanceCounter, 'this', _freesteelpy.new_ThinnerInstanceCounter(*args))
        _swig_setattr(self, ThinnerInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.ThinnerInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_ThinnerInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class ThinnerInstanceCounterPtr(ThinnerInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, ThinnerInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, ThinnerInstanceCounter, 'thisown', 0)
        _swig_setattr(self, ThinnerInstanceCounter,self.__class__,ThinnerInstanceCounter)
_freesteelpy.ThinnerInstanceCounter_swigregister(ThinnerInstanceCounterPtr)

class FsFreeFibreInstanceCounter(DynamicObject):
    __swig_setmethods__ = {}
    for _s in [DynamicObject]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsFreeFibreInstanceCounter, name, value)
    __swig_getmethods__ = {}
    for _s in [DynamicObject]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsFreeFibreInstanceCounter, name)
    def __repr__(self):
        return "<C InstanceCounter<(FsFreeFibre)> instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FsFreeFibreInstanceCounter, 'this', _freesteelpy.new_FsFreeFibreInstanceCounter(*args))
        _swig_setattr(self, FsFreeFibreInstanceCounter, 'thisown', 1)
    def getInstanceId(*args, **kwargs): return _freesteelpy.FsFreeFibreInstanceCounter_getInstanceId(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsFreeFibreInstanceCounter):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsFreeFibreInstanceCounterPtr(FsFreeFibreInstanceCounter):
    def __init__(self, this):
        _swig_setattr(self, FsFreeFibreInstanceCounter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsFreeFibreInstanceCounter, 'thisown', 0)
        _swig_setattr(self, FsFreeFibreInstanceCounter,self.__class__,FsFreeFibreInstanceCounter)
_freesteelpy.FsFreeFibreInstanceCounter_swigregister(FsFreeFibreInstanceCounterPtr)

class FsKernel(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsKernel, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, FsKernel, name)
    def __repr__(self):
        return "<C FsKernel instance at %s>" % (self.this,)
    __swig_getmethods__["IsDebugging"] = lambda x: _freesteelpy.FsKernel_IsDebugging
    if _newclass:IsDebugging = staticmethod(_freesteelpy.FsKernel_IsDebugging)
    __swig_getmethods__["SetDebugging"] = lambda x: _freesteelpy.FsKernel_SetDebugging
    if _newclass:SetDebugging = staticmethod(_freesteelpy.FsKernel_SetDebugging)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, FsKernel, 'this', _freesteelpy.new_FsKernel(*args, **kwargs))
        _swig_setattr(self, FsKernel, 'thisown', 1)
    def __del__(self, destroy=_freesteelpy.delete_FsKernel):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsKernelPtr(FsKernel):
    def __init__(self, this):
        _swig_setattr(self, FsKernel, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsKernel, 'thisown', 0)
        _swig_setattr(self, FsKernel,self.__class__,FsKernel)
_freesteelpy.FsKernel_swigregister(FsKernelPtr)

FsKernel_IsDebugging = _freesteelpy.FsKernel_IsDebugging

FsKernel_SetDebugging = _freesteelpy.FsKernel_SetDebugging

class ProgressListener(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ProgressListener, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ProgressListener, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C ProgressListener instance at %s>" % (self.this,)
    def onProgress(*args, **kwargs): return _freesteelpy.ProgressListener_onProgress(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_ProgressListener):
        try:
            if self.thisown: destroy(self)
        except: pass

class ProgressListenerPtr(ProgressListener):
    def __init__(self, this):
        _swig_setattr(self, ProgressListener, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, ProgressListener, 'thisown', 0)
        _swig_setattr(self, ProgressListener,self.__class__,ProgressListener)
_freesteelpy.ProgressListener_swigregister(ProgressListenerPtr)

class MappedProgressListener(ProgressListener):
    __swig_setmethods__ = {}
    for _s in [ProgressListener]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, MappedProgressListener, name, value)
    __swig_getmethods__ = {}
    for _s in [ProgressListener]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, MappedProgressListener, name)
    def __repr__(self):
        return "<C MappedProgressListener instance at %s>" % (self.this,)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, MappedProgressListener, 'this', _freesteelpy.new_MappedProgressListener(*args, **kwargs))
        _swig_setattr(self, MappedProgressListener, 'thisown', 1)
    def onProgress(*args, **kwargs): return _freesteelpy.MappedProgressListener_onProgress(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_MappedProgressListener):
        try:
            if self.thisown: destroy(self)
        except: pass

class MappedProgressListenerPtr(MappedProgressListener):
    def __init__(self, this):
        _swig_setattr(self, MappedProgressListener, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, MappedProgressListener, 'thisown', 0)
        _swig_setattr(self, MappedProgressListener,self.__class__,MappedProgressListener)
_freesteelpy.MappedProgressListener_swigregister(MappedProgressListenerPtr)

class ContactConditionContext(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ContactConditionContext, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ContactConditionContext, name)
    def __repr__(self):
        return "<C ContactConditionContext instance at %s>" % (self.this,)
    __swig_setmethods__["tipPoint"] = _freesteelpy.ContactConditionContext_tipPoint_set
    __swig_getmethods__["tipPoint"] = _freesteelpy.ContactConditionContext_tipPoint_get
    if _newclass:tipPoint = property(_freesteelpy.ContactConditionContext_tipPoint_get, _freesteelpy.ContactConditionContext_tipPoint_set)
    __swig_setmethods__["normal"] = _freesteelpy.ContactConditionContext_normal_set
    __swig_getmethods__["normal"] = _freesteelpy.ContactConditionContext_normal_get
    if _newclass:normal = property(_freesteelpy.ContactConditionContext_normal_get, _freesteelpy.ContactConditionContext_normal_set)
    __swig_setmethods__["contactPoint"] = _freesteelpy.ContactConditionContext_contactPoint_set
    __swig_getmethods__["contactPoint"] = _freesteelpy.ContactConditionContext_contactPoint_get
    if _newclass:contactPoint = property(_freesteelpy.ContactConditionContext_contactPoint_get, _freesteelpy.ContactConditionContext_contactPoint_set)
    __swig_setmethods__["contact"] = _freesteelpy.ContactConditionContext_contact_set
    __swig_getmethods__["contact"] = _freesteelpy.ContactConditionContext_contact_get
    if _newclass:contact = property(_freesteelpy.ContactConditionContext_contact_get, _freesteelpy.ContactConditionContext_contact_set)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, ContactConditionContext, 'this', _freesteelpy.new_ContactConditionContext(*args, **kwargs))
        _swig_setattr(self, ContactConditionContext, 'thisown', 1)
    def __del__(self, destroy=_freesteelpy.delete_ContactConditionContext):
        try:
            if self.thisown: destroy(self)
        except: pass

class ContactConditionContextPtr(ContactConditionContext):
    def __init__(self, this):
        _swig_setattr(self, ContactConditionContext, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, ContactConditionContext, 'thisown', 0)
        _swig_setattr(self, ContactConditionContext,self.__class__,ContactConditionContext)
_freesteelpy.ContactConditionContext_swigregister(ContactConditionContextPtr)

class ContactConditionFilter(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ContactConditionFilter, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ContactConditionFilter, name)
    def __repr__(self):
        return "<C ContactConditionFilter instance at %s>" % (self.this,)
    __swig_getmethods__["getInclude"] = lambda x: _freesteelpy.ContactConditionFilter_getInclude
    if _newclass:getInclude = staticmethod(_freesteelpy.ContactConditionFilter_getInclude)
    __swig_getmethods__["getExclude"] = lambda x: _freesteelpy.ContactConditionFilter_getExclude
    if _newclass:getExclude = staticmethod(_freesteelpy.ContactConditionFilter_getExclude)
    def filter(*args): return _freesteelpy.ContactConditionFilter_filter(*args)
    def lowerAtWall(*args, **kwargs): return _freesteelpy.ContactConditionFilter_lowerAtWall(*args, **kwargs)
    def liftAtWall(*args, **kwargs): return _freesteelpy.ContactConditionFilter_liftAtWall(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, ContactConditionFilter, 'this', _freesteelpy.new_ContactConditionFilter(*args, **kwargs))
        _swig_setattr(self, ContactConditionFilter, 'thisown', 1)
    def __del__(self, destroy=_freesteelpy.delete_ContactConditionFilter):
        try:
            if self.thisown: destroy(self)
        except: pass

class ContactConditionFilterPtr(ContactConditionFilter):
    def __init__(self, this):
        _swig_setattr(self, ContactConditionFilter, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, ContactConditionFilter, 'thisown', 0)
        _swig_setattr(self, ContactConditionFilter,self.__class__,ContactConditionFilter)
_freesteelpy.ContactConditionFilter_swigregister(ContactConditionFilterPtr)

ContactConditionFilter_getInclude = _freesteelpy.ContactConditionFilter_getInclude

ContactConditionFilter_getExclude = _freesteelpy.ContactConditionFilter_getExclude

class FsSurf(FsSurfInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsSurfInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurf, name, value)
    __swig_getmethods__ = {}
    for _s in [FsSurfInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurf, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsSurf instance at %s>" % (self.this,)
    __swig_setmethods__["bOrientTrianglesByZ"] = _freesteelpy.FsSurf_bOrientTrianglesByZ_set
    __swig_getmethods__["bOrientTrianglesByZ"] = _freesteelpy.FsSurf_bOrientTrianglesByZ_get
    if _newclass:bOrientTrianglesByZ = property(_freesteelpy.FsSurf_bOrientTrianglesByZ_get, _freesteelpy.FsSurf_bOrientTrianglesByZ_set)
    def SetMaximumMemoryUsage(*args, **kwargs): return _freesteelpy.FsSurf_SetMaximumMemoryUsage(*args, **kwargs)
    def PushTriangle(*args, **kwargs): return _freesteelpy.FsSurf_PushTriangle(*args, **kwargs)
    def PushIsolatedEdge(*args, **kwargs): return _freesteelpy.FsSurf_PushIsolatedEdge(*args, **kwargs)
    def PushIsolatedPoint(*args, **kwargs): return _freesteelpy.FsSurf_PushIsolatedPoint(*args, **kwargs)
    def Build(*args, **kwargs): return _freesteelpy.FsSurf_Build(*args, **kwargs)
    def ReleaseBoxing(*args, **kwargs): return _freesteelpy.FsSurf_ReleaseBoxing(*args, **kwargs)
    def IsBoxed(*args, **kwargs): return _freesteelpy.FsSurf_IsBoxed(*args, **kwargs)
    def GetNTriangles(*args, **kwargs): return _freesteelpy.FsSurf_GetNTriangles(*args, **kwargs)
    def GetNEdges(*args, **kwargs): return _freesteelpy.FsSurf_GetNEdges(*args, **kwargs)
    def GetNFreeEdges(*args, **kwargs): return _freesteelpy.FsSurf_GetNFreeEdges(*args, **kwargs)
    def GetNPoints(*args, **kwargs): return _freesteelpy.FsSurf_GetNPoints(*args, **kwargs)
    def GetXlo(*args, **kwargs): return _freesteelpy.FsSurf_GetXlo(*args, **kwargs)
    def GetXhi(*args, **kwargs): return _freesteelpy.FsSurf_GetXhi(*args, **kwargs)
    def GetYlo(*args, **kwargs): return _freesteelpy.FsSurf_GetYlo(*args, **kwargs)
    def GetYhi(*args, **kwargs): return _freesteelpy.FsSurf_GetYhi(*args, **kwargs)
    def GetZlo(*args, **kwargs): return _freesteelpy.FsSurf_GetZlo(*args, **kwargs)
    def GetZhi(*args, **kwargs): return _freesteelpy.FsSurf_GetZhi(*args, **kwargs)
    def GetMemorySize(*args, **kwargs): return _freesteelpy.FsSurf_GetMemorySize(*args, **kwargs)
    def GetCapacity(*args, **kwargs): return _freesteelpy.FsSurf_GetCapacity(*args, **kwargs)
    def BestAvoidInflexion(*args, **kwargs): return _freesteelpy.FsSurf_BestAvoidInflexion(*args, **kwargs)
    def FigureFlatTriangles(*args, **kwargs): return _freesteelpy.FsSurf_FigureFlatTriangles(*args, **kwargs)
    def AddFlatPlaceZ(*args, **kwargs): return _freesteelpy.FsSurf_AddFlatPlaceZ(*args, **kwargs)
    def GetFlatPlaceZ(*args, **kwargs): return _freesteelpy.FsSurf_GetFlatPlaceZ(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurf):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsSurf_New
    if _newclass:New = staticmethod(_freesteelpy.FsSurf_New)

class FsSurfPtr(FsSurf):
    def __init__(self, this):
        _swig_setattr(self, FsSurf, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurf, 'thisown', 0)
        _swig_setattr(self, FsSurf,self.__class__,FsSurf)
_freesteelpy.FsSurf_swigregister(FsSurfPtr)

FsSurf_New = _freesteelpy.FsSurf_New

class FsFibre(FsFibreInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsFibreInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsFibre, name, value)
    __swig_getmethods__ = {}
    for _s in [FsFibreInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsFibre, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsFibre instance at %s>" % (self.this,)
    def __del__(self, destroy=_freesteelpy.delete_FsFibre):
        try:
            if self.thisown: destroy(self)
        except: pass
    def SetFPath(*args, **kwargs): return _freesteelpy.FsFibre_SetFPath(*args, **kwargs)
    def SetShapeSurfZdisp(*args, **kwargs): return _freesteelpy.FsFibre_SetShapeSurfZdisp(*args, **kwargs)
    def SetShapeFiveAxTraj(*args, **kwargs): return _freesteelpy.FsFibre_SetShapeFiveAxTraj(*args, **kwargs)
    def IsTrimmed(*args, **kwargs): return _freesteelpy.FsFibre_IsTrimmed(*args, **kwargs)
    def GetNBoundaries(*args, **kwargs): return _freesteelpy.FsFibre_GetNBoundaries(*args, **kwargs)
    def GetBoundary(*args, **kwargs): return _freesteelpy.FsFibre_GetBoundary(*args, **kwargs)
    def GetFBoundaryI(*args, **kwargs): return _freesteelpy.FsFibre_GetFBoundaryI(*args, **kwargs)
    def GetFBoundaryC(*args, **kwargs): return _freesteelpy.FsFibre_GetFBoundaryC(*args, **kwargs)
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsFibre_New
    if _newclass:New = staticmethod(_freesteelpy.FsFibre_New)

class FsFibrePtr(FsFibre):
    def __init__(self, this):
        _swig_setattr(self, FsFibre, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsFibre, 'thisown', 0)
        _swig_setattr(self, FsFibre,self.__class__,FsFibre)
_freesteelpy.FsFibre_swigregister(FsFibrePtr)

FsFibre_New = _freesteelpy.FsFibre_New

class FsSurfaceHitRegistry(FsSurfaceHitRegistryInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsSurfaceHitRegistryInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurfaceHitRegistry, name, value)
    __swig_getmethods__ = {}
    for _s in [FsSurfaceHitRegistryInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurfaceHitRegistry, name)
    def __repr__(self):
        return "<C FsSurfaceHitRegistry instance at %s>" % (self.this,)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, FsSurfaceHitRegistry, 'this', _freesteelpy.new_FsSurfaceHitRegistry(*args, **kwargs))
        _swig_setattr(self, FsSurfaceHitRegistry, 'thisown', 1)
    def GetSurfaceHitRegistryImpl(*args, **kwargs): return _freesteelpy.FsSurfaceHitRegistry_GetSurfaceHitRegistryImpl(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurfaceHitRegistry):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsSurfaceHitRegistryPtr(FsSurfaceHitRegistry):
    def __init__(self, this):
        _swig_setattr(self, FsSurfaceHitRegistry, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurfaceHitRegistry, 'thisown', 0)
        _swig_setattr(self, FsSurfaceHitRegistry,self.__class__,FsSurfaceHitRegistry)
_freesteelpy.FsSurfaceHitRegistry_swigregister(FsSurfaceHitRegistryPtr)


GetSurfaceHitRegistryImpl = _freesteelpy.GetSurfaceHitRegistryImpl
class FsSurfaceHitReg(FsSurfaceHitRegInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsSurfaceHitRegInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsSurfaceHitReg, name, value)
    __swig_getmethods__ = {}
    for _s in [FsSurfaceHitRegInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsSurfaceHitReg, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsSurfaceHitReg instance at %s>" % (self.this,)
    def AddSurf(*args, **kwargs): return _freesteelpy.FsSurfaceHitReg_AddSurf(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsSurfaceHitReg):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsSurfaceHitReg_New
    if _newclass:New = staticmethod(_freesteelpy.FsSurfaceHitReg_New)

class FsSurfaceHitRegPtr(FsSurfaceHitReg):
    def __init__(self, this):
        _swig_setattr(self, FsSurfaceHitReg, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsSurfaceHitReg, 'thisown', 0)
        _swig_setattr(self, FsSurfaceHitReg,self.__class__,FsSurfaceHitReg)
_freesteelpy.FsSurfaceHitReg_swigregister(FsSurfaceHitRegPtr)

FsSurfaceHitReg_New = _freesteelpy.FsSurfaceHitReg_New


DClosestApproach = _freesteelpy.DClosestApproach
class FsWeave(FsWeaveInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsWeaveInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsWeave, name, value)
    __swig_getmethods__ = {}
    for _s in [FsWeaveInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsWeave, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsWeave instance at %s>" % (self.this,)
    def GetMemorySize(*args, **kwargs): return _freesteelpy.FsWeave_GetMemorySize(*args, **kwargs)
    def GetCapacity(*args, **kwargs): return _freesteelpy.FsWeave_GetCapacity(*args, **kwargs)
    def SetWeaveDrawMode(*args, **kwargs): return _freesteelpy.FsWeave_SetWeaveDrawMode(*args, **kwargs)
    def SetShape(*args, **kwargs): return _freesteelpy.FsWeave_SetShape(*args, **kwargs)
    def StructureContours(*args, **kwargs): return _freesteelpy.FsWeave_StructureContours(*args, **kwargs)
    def IsStructured(*args, **kwargs): return _freesteelpy.FsWeave_IsStructured(*args, **kwargs)
    def FindContourFragments(*args, **kwargs): return _freesteelpy.FsWeave_FindContourFragments(*args, **kwargs)
    def GetNFibres(*args, **kwargs): return _freesteelpy.FsWeave_GetNFibres(*args, **kwargs)
    def GetNBoundaries(*args, **kwargs): return _freesteelpy.FsWeave_GetNBoundaries(*args, **kwargs)
    def GetBoundary(*args, **kwargs): return _freesteelpy.FsWeave_GetBoundary(*args, **kwargs)
    def GetDist(*args, **kwargs): return _freesteelpy.FsWeave_GetDist(*args, **kwargs)
    def GetNContours(*args, **kwargs): return _freesteelpy.FsWeave_GetNContours(*args, **kwargs)
    def GetZlo(*args, **kwargs): return _freesteelpy.FsWeave_GetZlo(*args, **kwargs)
    def GetZhi(*args, **kwargs): return _freesteelpy.FsWeave_GetZhi(*args, **kwargs)
    def IsCavity(*args, **kwargs): return _freesteelpy.FsWeave_IsCavity(*args, **kwargs)
    def Is2PointContour(*args, **kwargs): return _freesteelpy.FsWeave_Is2PointContour(*args, **kwargs)
    def GetContourOutside(*args, **kwargs): return _freesteelpy.FsWeave_GetContourOutside(*args, **kwargs)
    def GetContourScallopOutForced(*args, **kwargs): return _freesteelpy.FsWeave_GetContourScallopOutForced(*args, **kwargs)
    def GetContourArea(*args, **kwargs): return _freesteelpy.FsWeave_GetContourArea(*args, **kwargs)
    def GetContourDiameter(*args, **kwargs): return _freesteelpy.FsWeave_GetContourDiameter(*args, **kwargs)
    def GetMaxDistanceToContour(*args, **kwargs): return _freesteelpy.FsWeave_GetMaxDistanceToContour(*args, **kwargs)
    def MeasureMaxDistanceBetween(*args, **kwargs): return _freesteelpy.FsWeave_MeasureMaxDistanceBetween(*args, **kwargs)
    def GetMaxRad(*args, **kwargs): return _freesteelpy.FsWeave_GetMaxRad(*args, **kwargs)
    def GetClosestPocket(*args, **kwargs): return _freesteelpy.FsWeave_GetClosestPocket(*args, **kwargs)
    def CreatePocketOpening(*args, **kwargs): return _freesteelpy.FsWeave_CreatePocketOpening(*args, **kwargs)
    def GetContactHistogramPeak(*args, **kwargs): return _freesteelpy.FsWeave_GetContactHistogramPeak(*args, **kwargs)
    def Clear(*args, **kwargs): return _freesteelpy.FsWeave_Clear(*args, **kwargs)
    def Compact(*args, **kwargs): return _freesteelpy.FsWeave_Compact(*args, **kwargs)
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsWeave_New
    if _newclass:New = staticmethod(_freesteelpy.FsWeave_New)
    def __del__(self, destroy=_freesteelpy.delete_FsWeave):
        try:
            if self.thisown: destroy(self)
        except: pass
    def IsExteriorFull(*args, **kwargs): return _freesteelpy.FsWeave_IsExteriorFull(*args, **kwargs)
    def DCheckWeaveZ(*args, **kwargs): return _freesteelpy.FsWeave_DCheckWeaveZ(*args, **kwargs)
    def DGet(*args, **kwargs): return _freesteelpy.FsWeave_DGet(*args, **kwargs)

class FsWeavePtr(FsWeave):
    def __init__(self, this):
        _swig_setattr(self, FsWeave, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsWeave, 'thisown', 0)
        _swig_setattr(self, FsWeave,self.__class__,FsWeave)
_freesteelpy.FsWeave_swigregister(FsWeavePtr)

FsWeave_New = _freesteelpy.FsWeave_New


DWeavePocketInside = _freesteelpy.DWeavePocketInside
class FsBoundaries(FsBoundariesInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsBoundariesInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsBoundaries, name, value)
    __swig_getmethods__ = {}
    for _s in [FsBoundariesInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsBoundaries, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsBoundaries instance at %s>" % (self.this,)
    def AddBoundary(*args, **kwargs): return _freesteelpy.FsBoundaries_AddBoundary(*args, **kwargs)
    def Build(*args, **kwargs): return _freesteelpy.FsBoundaries_Build(*args, **kwargs)
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsBoundaries_New
    if _newclass:New = staticmethod(_freesteelpy.FsBoundaries_New)
    def __del__(self, destroy=_freesteelpy.delete_FsBoundaries):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsBoundariesPtr(FsBoundaries):
    def __init__(self, this):
        _swig_setattr(self, FsBoundaries, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsBoundaries, 'thisown', 0)
        _swig_setattr(self, FsBoundaries,self.__class__,FsBoundaries)
_freesteelpy.FsBoundaries_swigregister(FsBoundariesPtr)

FsBoundaries_New = _freesteelpy.FsBoundaries_New

class FsBoxedPath(FsBoxedPathInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsBoxedPathInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsBoxedPath, name, value)
    __swig_getmethods__ = {}
    for _s in [FsBoxedPathInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsBoxedPath, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsBoxedPath instance at %s>" % (self.this,)
    def AddPathToBoxedPath(*args, **kwargs): return _freesteelpy.FsBoxedPath_AddPathToBoxedPath(*args, **kwargs)
    def SetOffsetRadius(*args, **kwargs): return _freesteelpy.FsBoxedPath_SetOffsetRadius(*args, **kwargs)
    def BuildBoxedPath(*args, **kwargs): return _freesteelpy.FsBoxedPath_BuildBoxedPath(*args, **kwargs)
    def AddPathChainToBoxedPath(*args, **kwargs): return _freesteelpy.FsBoxedPath_AddPathChainToBoxedPath(*args, **kwargs)
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsBoxedPath_New
    if _newclass:New = staticmethod(_freesteelpy.FsBoxedPath_New)
    def __del__(self, destroy=_freesteelpy.delete_FsBoxedPath):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsBoxedPathPtr(FsBoxedPath):
    def __init__(self, this):
        _swig_setattr(self, FsBoxedPath, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsBoxedPath, 'thisown', 0)
        _swig_setattr(self, FsBoxedPath,self.__class__,FsBoxedPath)
_freesteelpy.FsBoxedPath_swigregister(FsBoxedPathPtr)

FsBoxedPath_New = _freesteelpy.FsBoxedPath_New

class FsRibbon(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsRibbon, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, FsRibbon, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsRibbon instance at %s>" % (self.this,)
    def SetRibbonShape(*args, **kwargs): return _freesteelpy.FsRibbon_SetRibbonShape(*args, **kwargs)
    def GetRibbonArea(*args, **kwargs): return _freesteelpy.FsRibbon_GetRibbonArea(*args, **kwargs)
    def PushIntoSurface(*args, **kwargs): return _freesteelpy.FsRibbon_PushIntoSurface(*args, **kwargs)
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsRibbon_New
    if _newclass:New = staticmethod(_freesteelpy.FsRibbon_New)
    def __del__(self, destroy=_freesteelpy.delete_FsRibbon):
        try:
            if self.thisown: destroy(self)
        except: pass

class FsRibbonPtr(FsRibbon):
    def __init__(self, this):
        _swig_setattr(self, FsRibbon, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsRibbon, 'thisown', 0)
        _swig_setattr(self, FsRibbon,self.__class__,FsRibbon)
_freesteelpy.FsRibbon_swigregister(FsRibbonPtr)

FsRibbon_New = _freesteelpy.FsRibbon_New

class FsHorizontalInflexionAvoidance(FsHorizontalInflexionAvoidanceInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsHorizontalInflexionAvoidanceInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsHorizontalInflexionAvoidance, name, value)
    __swig_getmethods__ = {}
    for _s in [FsHorizontalInflexionAvoidanceInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsHorizontalInflexionAvoidance, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsHorizontalInflexionAvoidance instance at %s>" % (self.this,)
    def AddSurf(*args, **kwargs): return _freesteelpy.FsHorizontalInflexionAvoidance_AddSurf(*args, **kwargs)
    def AddZoffset(*args, **kwargs): return _freesteelpy.FsHorizontalInflexionAvoidance_AddZoffset(*args, **kwargs)
    def BestAvoidInflexion(*args, **kwargs): return _freesteelpy.FsHorizontalInflexionAvoidance_BestAvoidInflexion(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsHorizontalInflexionAvoidance):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsHorizontalInflexionAvoidance_New
    if _newclass:New = staticmethod(_freesteelpy.FsHorizontalInflexionAvoidance_New)

class FsHorizontalInflexionAvoidancePtr(FsHorizontalInflexionAvoidance):
    def __init__(self, this):
        _swig_setattr(self, FsHorizontalInflexionAvoidance, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsHorizontalInflexionAvoidance, 'thisown', 0)
        _swig_setattr(self, FsHorizontalInflexionAvoidance,self.__class__,FsHorizontalInflexionAvoidance)
_freesteelpy.FsHorizontalInflexionAvoidance_swigregister(FsHorizontalInflexionAvoidancePtr)

FsHorizontalInflexionAvoidance_New = _freesteelpy.FsHorizontalInflexionAvoidance_New

class FsHorizontalToolSurface(FsHorizontalToolSurfaceInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsHorizontalToolSurfaceInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsHorizontalToolSurface, name, value)
    __swig_getmethods__ = {}
    for _s in [FsHorizontalToolSurfaceInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsHorizontalToolSurface, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsHorizontalToolSurface instance at %s>" % (self.this,)
    def AddSurf(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_AddSurf(*args, **kwargs)
    def AddTipShape(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_AddTipShape(*args, **kwargs)
    def AddCone(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_AddCone(*args, **kwargs)
    def AddCylinder(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_AddCylinder(*args, **kwargs)
    def AddZFrustrum(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_AddZFrustrum(*args, **kwargs)
    def SetIntersectionCondition(*args, **kwargs): return _freesteelpy.FsHorizontalToolSurface_SetIntersectionCondition(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsHorizontalToolSurface):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsHorizontalToolSurface_New
    if _newclass:New = staticmethod(_freesteelpy.FsHorizontalToolSurface_New)

class FsHorizontalToolSurfacePtr(FsHorizontalToolSurface):
    def __init__(self, this):
        _swig_setattr(self, FsHorizontalToolSurface, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsHorizontalToolSurface, 'thisown', 0)
        _swig_setattr(self, FsHorizontalToolSurface,self.__class__,FsHorizontalToolSurface)
_freesteelpy.FsHorizontalToolSurface_swigregister(FsHorizontalToolSurfacePtr)

FsHorizontalToolSurface_New = _freesteelpy.FsHorizontalToolSurface_New

class FsImplicitArea(FsImplicitAreaInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsImplicitAreaInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsImplicitArea, name, value)
    __swig_getmethods__ = {}
    for _s in [FsImplicitAreaInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsImplicitArea, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsImplicitArea instance at %s>" % (self.this,)
    def AddHorizToolSurf(*args, **kwargs): return _freesteelpy.FsImplicitArea_AddHorizToolSurf(*args, **kwargs)
    def AddUpperWeaveForSpeed(*args, **kwargs): return _freesteelpy.FsImplicitArea_AddUpperWeaveForSpeed(*args, **kwargs)
    def AddWeaveForOffset2D(*args, **kwargs): return _freesteelpy.FsImplicitArea_AddWeaveForOffset2D(*args, **kwargs)
    def DCheckInflexionDistance(*args, **kwargs): return _freesteelpy.FsImplicitArea_DCheckInflexionDistance(*args, **kwargs)
    def SetMachiningBoundaries(*args, **kwargs): return _freesteelpy.FsImplicitArea_SetMachiningBoundaries(*args, **kwargs)
    def SwapInMachiningBoundary(*args, **kwargs): return _freesteelpy.FsImplicitArea_SwapInMachiningBoundary(*args, **kwargs)
    def SetContourConditions(*args, **kwargs): return _freesteelpy.FsImplicitArea_SetContourConditions(*args, **kwargs)
    def AddToolpath(*args, **kwargs): return _freesteelpy.FsImplicitArea_AddToolpath(*args, **kwargs)
    def HasContactConditionFilters(*args, **kwargs): return _freesteelpy.FsImplicitArea_HasContactConditionFilters(*args, **kwargs)
    def AddContactConditionFilter(*args, **kwargs): return _freesteelpy.FsImplicitArea_AddContactConditionFilter(*args, **kwargs)
    def SetZHigh(*args, **kwargs): return _freesteelpy.FsImplicitArea_SetZHigh(*args, **kwargs)
    def GenWeaveZProfile(*args, **kwargs): return _freesteelpy.FsImplicitArea_GenWeaveZProfile(*args, **kwargs)
    def GenFibreF(*args, **kwargs): return _freesteelpy.FsImplicitArea_GenFibreF(*args, **kwargs)
    def GetPropGenweaveDone(*args, **kwargs): return _freesteelpy.FsImplicitArea_GetPropGenweaveDone(*args, **kwargs)
    def GetProgress(*args, **kwargs): return _freesteelpy.FsImplicitArea_GetProgress(*args, **kwargs)
    def MakeToTerminate(*args, **kwargs): return _freesteelpy.FsImplicitArea_MakeToTerminate(*args, **kwargs)
    def GenRibbonBite(*args, **kwargs): return _freesteelpy.FsImplicitArea_GenRibbonBite(*args, **kwargs)
    def ReleaseWorkspaces(*args, **kwargs): return _freesteelpy.FsImplicitArea_ReleaseWorkspaces(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsImplicitArea):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsImplicitArea_New
    if _newclass:New = staticmethod(_freesteelpy.FsImplicitArea_New)

class FsImplicitAreaPtr(FsImplicitArea):
    def __init__(self, this):
        _swig_setattr(self, FsImplicitArea, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsImplicitArea, 'thisown', 0)
        _swig_setattr(self, FsImplicitArea,self.__class__,FsImplicitArea)
_freesteelpy.FsImplicitArea_swigregister(FsImplicitAreaPtr)

FsImplicitArea_New = _freesteelpy.FsImplicitArea_New

class FsPath2X(FsPath2XInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsPath2XInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsPath2X, name, value)
    __swig_getmethods__ = {}
    for _s in [FsPath2XInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsPath2X, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsPath2X instance at %s>" % (self.this,)
    RADIUS_COMPENSATION_CENTER = _freesteelpy.FsPath2X_RADIUS_COMPENSATION_CENTER
    RADIUS_COMPENSATION_LEFT = _freesteelpy.FsPath2X_RADIUS_COMPENSATION_LEFT
    RADIUS_COMPENSATION_RIGHT = _freesteelpy.FsPath2X_RADIUS_COMPENSATION_RIGHT
    __swig_setmethods__["z"] = _freesteelpy.FsPath2X_z_set
    __swig_getmethods__["z"] = _freesteelpy.FsPath2X_z_get
    if _newclass:z = property(_freesteelpy.FsPath2X_z_get, _freesteelpy.FsPath2X_z_set)
    __swig_setmethods__["movement_type"] = _freesteelpy.FsPath2X_movement_type_set
    __swig_getmethods__["movement_type"] = _freesteelpy.FsPath2X_movement_type_get
    if _newclass:movement_type = property(_freesteelpy.FsPath2X_movement_type_get, _freesteelpy.FsPath2X_movement_type_set)
    __swig_setmethods__["bthinned"] = _freesteelpy.FsPath2X_bthinned_set
    __swig_getmethods__["bthinned"] = _freesteelpy.FsPath2X_bthinned_get
    if _newclass:bthinned = property(_freesteelpy.FsPath2X_bthinned_get, _freesteelpy.FsPath2X_bthinned_set)
    def GetMemorySize(*args, **kwargs): return _freesteelpy.FsPath2X_GetMemorySize(*args, **kwargs)
    def GetCapacity(*args, **kwargs): return _freesteelpy.FsPath2X_GetCapacity(*args, **kwargs)
    def Compact(*args, **kwargs): return _freesteelpy.FsPath2X_Compact(*args, **kwargs)
    def GetNMiddleStartFrees(*args, **kwargs): return _freesteelpy.FsPath2X_GetNMiddleStartFrees(*args, **kwargs)
    def GetMiddleStartFreeNumber(*args, **kwargs): return _freesteelpy.FsPath2X_GetMiddleStartFreeNumber(*args, **kwargs)
    def SetPrevCutPath(*args, **kwargs): return _freesteelpy.FsPath2X_SetPrevCutPath(*args, **kwargs)
    def SetPrevLinkPath(*args, **kwargs): return _freesteelpy.FsPath2X_SetPrevLinkPath(*args, **kwargs)
    def GetPrevCutPath(*args, **kwargs): return _freesteelpy.FsPath2X_GetPrevCutPath(*args, **kwargs)
    def GetPrevLinkPath(*args, **kwargs): return _freesteelpy.FsPath2X_GetPrevLinkPath(*args, **kwargs)
    def Is3D(*args, **kwargs): return _freesteelpy.FsPath2X_Is3D(*args, **kwargs)
    def Is5D(*args, **kwargs): return _freesteelpy.FsPath2X_Is5D(*args, **kwargs)
    def IsFullLoop(*args, **kwargs): return _freesteelpy.FsPath2X_IsFullLoop(*args, **kwargs)
    def IsClosed(*args, **kwargs): return _freesteelpy.FsPath2X_IsClosed(*args, **kwargs)
    def GetStartEndDistance2(*args, **kwargs): return _freesteelpy.FsPath2X_GetStartEndDistance2(*args, **kwargs)
    def DumpInfo(*args, **kwargs): return _freesteelpy.FsPath2X_DumpInfo(*args, **kwargs)
    def Close(*args, **kwargs): return _freesteelpy.FsPath2X_Close(*args, **kwargs)
    def Start(*args): return _freesteelpy.FsPath2X_Start(*args)
    def AddLine(*args): return _freesteelpy.FsPath2X_AddLine(*args)
    def AddArcNoSplit(*args, **kwargs): return _freesteelpy.FsPath2X_AddArcNoSplit(*args, **kwargs)
    def AddArc(*args, **kwargs): return _freesteelpy.FsPath2X_AddArc(*args, **kwargs)
    def AddArcCorrectCentre(*args, **kwargs): return _freesteelpy.FsPath2X_AddArcCorrectCentre(*args, **kwargs)
    def AddVerticalArc(*args, **kwargs): return _freesteelpy.FsPath2X_AddVerticalArc(*args, **kwargs)
    def AddHelix(*args, **kwargs): return _freesteelpy.FsPath2X_AddHelix(*args, **kwargs)
    def AddHelixNoSplit(*args, **kwargs): return _freesteelpy.FsPath2X_AddHelixNoSplit(*args, **kwargs)
    def Compress(*args, **kwargs): return _freesteelpy.FsPath2X_Compress(*args, **kwargs)
    def Clear(*args, **kwargs): return _freesteelpy.FsPath2X_Clear(*args, **kwargs)
    def Reserve(*args, **kwargs): return _freesteelpy.FsPath2X_Reserve(*args, **kwargs)
    def IsEmpty(*args, **kwargs): return _freesteelpy.FsPath2X_IsEmpty(*args, **kwargs)
    def GetNpts(*args, **kwargs): return _freesteelpy.FsPath2X_GetNpts(*args, **kwargs)
    def GetX(*args, **kwargs): return _freesteelpy.FsPath2X_GetX(*args, **kwargs)
    def GetY(*args, **kwargs): return _freesteelpy.FsPath2X_GetY(*args, **kwargs)
    def GetZ(*args): return _freesteelpy.FsPath2X_GetZ(*args)
    def GetP2(*args, **kwargs): return _freesteelpy.FsPath2X_GetP2(*args, **kwargs)
    def GetP(*args, **kwargs): return _freesteelpy.FsPath2X_GetP(*args, **kwargs)
    def GetTangentX(*args, **kwargs): return _freesteelpy.FsPath2X_GetTangentX(*args, **kwargs)
    def GetTangentY(*args, **kwargs): return _freesteelpy.FsPath2X_GetTangentY(*args, **kwargs)
    def GetToolAxis(*args, **kwargs): return _freesteelpy.FsPath2X_GetToolAxis(*args, **kwargs)
    def GetD(*args, **kwargs): return _freesteelpy.FsPath2X_GetD(*args, **kwargs)
    def ConvertTo2D(*args, **kwargs): return _freesteelpy.FsPath2X_ConvertTo2D(*args, **kwargs)
    def ConvertTo3D(*args, **kwargs): return _freesteelpy.FsPath2X_ConvertTo3D(*args, **kwargs)
    def IsArc(*args, **kwargs): return _freesteelpy.FsPath2X_IsArc(*args, **kwargs)
    def IsHArc(*args, **kwargs): return _freesteelpy.FsPath2X_IsHArc(*args, **kwargs)
    def IsVArc(*args, **kwargs): return _freesteelpy.FsPath2X_IsVArc(*args, **kwargs)
    def GetXC(*args, **kwargs): return _freesteelpy.FsPath2X_GetXC(*args, **kwargs)
    def GetYC(*args, **kwargs): return _freesteelpy.FsPath2X_GetYC(*args, **kwargs)
    def GetZC(*args, **kwargs): return _freesteelpy.FsPath2X_GetZC(*args, **kwargs)
    def IsClock(*args, **kwargs): return _freesteelpy.FsPath2X_IsClock(*args, **kwargs)
    def IsAbove(*args, **kwargs): return _freesteelpy.FsPath2X_IsAbove(*args, **kwargs)
    def GetC(*args, **kwargs): return _freesteelpy.FsPath2X_GetC(*args, **kwargs)
    def GetC2(*args, **kwargs): return _freesteelpy.FsPath2X_GetC2(*args, **kwargs)
    def GetN(*args, **kwargs): return _freesteelpy.FsPath2X_GetN(*args, **kwargs)
    def GetEntityType(*args, **kwargs): return _freesteelpy.FsPath2X_GetEntityType(*args, **kwargs)
    def GetClosestNode(*args, **kwargs): return _freesteelpy.FsPath2X_GetClosestNode(*args, **kwargs)
    def GetXlo(*args, **kwargs): return _freesteelpy.FsPath2X_GetXlo(*args, **kwargs)
    def GetXhi(*args, **kwargs): return _freesteelpy.FsPath2X_GetXhi(*args, **kwargs)
    def GetYlo(*args, **kwargs): return _freesteelpy.FsPath2X_GetYlo(*args, **kwargs)
    def GetYhi(*args, **kwargs): return _freesteelpy.FsPath2X_GetYhi(*args, **kwargs)
    def GetZlo(*args, **kwargs): return _freesteelpy.FsPath2X_GetZlo(*args, **kwargs)
    def GetZhi(*args, **kwargs): return _freesteelpy.FsPath2X_GetZhi(*args, **kwargs)
    def IsContourFollowing(*args, **kwargs): return _freesteelpy.FsPath2X_IsContourFollowing(*args, **kwargs)
    def HasEngageData(*args, **kwargs): return _freesteelpy.FsPath2X_HasEngageData(*args, **kwargs)
    def GetCutEngage(*args, **kwargs): return _freesteelpy.FsPath2X_GetCutEngage(*args, **kwargs)
    def GetMaxCutEngageToClear(*args, **kwargs): return _freesteelpy.FsPath2X_GetMaxCutEngageToClear(*args, **kwargs)
    def DoesEngageNoncuttingShaft(*args, **kwargs): return _freesteelpy.FsPath2X_DoesEngageNoncuttingShaft(*args, **kwargs)
    def IsOnContour(*args, **kwargs): return _freesteelpy.FsPath2X_IsOnContour(*args, **kwargs)
    def IsClockwise(*args, **kwargs): return _freesteelpy.FsPath2X_IsClockwise(*args, **kwargs)
    def GetContourNumber(*args, **kwargs): return _freesteelpy.FsPath2X_GetContourNumber(*args, **kwargs)
    __swig_getmethods__["EqualOnContour"] = lambda x: _freesteelpy.FsPath2X_EqualOnContour
    if _newclass:EqualOnContour = staticmethod(_freesteelpy.FsPath2X_EqualOnContour)
    __swig_getmethods__["BetweenOnContourTailOpen"] = lambda x: _freesteelpy.FsPath2X_BetweenOnContourTailOpen
    if _newclass:BetweenOnContourTailOpen = staticmethod(_freesteelpy.FsPath2X_BetweenOnContourTailOpen)
    def HeadEqualsTail(*args, **kwargs): return _freesteelpy.FsPath2X_HeadEqualsTail(*args, **kwargs)
    __swig_getmethods__["ContourLength"] = lambda x: _freesteelpy.FsPath2X_ContourLength
    if _newclass:ContourLength = staticmethod(_freesteelpy.FsPath2X_ContourLength)
    def ClearCutWeaveConditions(*args, **kwargs): return _freesteelpy.FsPath2X_ClearCutWeaveConditions(*args, **kwargs)
    def SetCumuleng(*args, **kwargs): return _freesteelpy.FsPath2X_SetCumuleng(*args, **kwargs)
    def GetCumuleng(*args, **kwargs): return _freesteelpy.FsPath2X_GetCumuleng(*args, **kwargs)
    def GetMLeng(*args, **kwargs): return _freesteelpy.FsPath2X_GetMLeng(*args, **kwargs)
    def SetRadiusCompensation(*args, **kwargs): return _freesteelpy.FsPath2X_SetRadiusCompensation(*args, **kwargs)
    def GetRadiusCompensation(*args, **kwargs): return _freesteelpy.FsPath2X_GetRadiusCompensation(*args, **kwargs)
    def SetMaxCutEngage(*args, **kwargs): return _freesteelpy.FsPath2X_SetMaxCutEngage(*args, **kwargs)
    def IsMachined(*args, **kwargs): return _freesteelpy.FsPath2X_IsMachined(*args, **kwargs)
    def SetMachined(*args, **kwargs): return _freesteelpy.FsPath2X_SetMachined(*args, **kwargs)
    def IsThinned(*args, **kwargs): return _freesteelpy.FsPath2X_IsThinned(*args, **kwargs)
    def SetThinned(*args, **kwargs): return _freesteelpy.FsPath2X_SetThinned(*args, **kwargs)
    def GetMovement(*args, **kwargs): return _freesteelpy.FsPath2X_GetMovement(*args, **kwargs)
    def SetMovement(*args, **kwargs): return _freesteelpy.FsPath2X_SetMovement(*args, **kwargs)
    def GetGenerator(*args, **kwargs): return _freesteelpy.FsPath2X_GetGenerator(*args, **kwargs)
    def SetGenerator(*args, **kwargs): return _freesteelpy.FsPath2X_SetGenerator(*args, **kwargs)
    FLAG_CONTOUR_FILTERED = _freesteelpy.FsPath2X_FLAG_CONTOUR_FILTERED
    FLAG_CONTOUR_NOT_FILTERED = _freesteelpy.FsPath2X_FLAG_CONTOUR_NOT_FILTERED
    FLAG_CONTOUR_MACHINING_BOUNDARY = _freesteelpy.FsPath2X_FLAG_CONTOUR_MACHINING_BOUNDARY
    FLAG_CONTOUR_NO_MACHINING_BOUNDARY = _freesteelpy.FsPath2X_FLAG_CONTOUR_NO_MACHINING_BOUNDARY
    def RecordContour(*args, **kwargs): return _freesteelpy.FsPath2X_RecordContour(*args, **kwargs)
    def RecordContourFragments(*args, **kwargs): return _freesteelpy.FsPath2X_RecordContourFragments(*args, **kwargs)
    def RecordInnerPoints(*args, **kwargs): return _freesteelpy.FsPath2X_RecordInnerPoints(*args, **kwargs)
    def RecordSection(*args, **kwargs): return _freesteelpy.FsPath2X_RecordSection(*args, **kwargs)
    def RecordClosestOnPocketBounds(*args, **kwargs): return _freesteelpy.FsPath2X_RecordClosestOnPocketBounds(*args, **kwargs)
    def GetArea(*args, **kwargs): return _freesteelpy.FsPath2X_GetArea(*args, **kwargs)
    def IsPolygon(*args, **kwargs): return _freesteelpy.FsPath2X_IsPolygon(*args, **kwargs)
    def Thin(*args, **kwargs): return _freesteelpy.FsPath2X_Thin(*args, **kwargs)
    def Reverse(*args, **kwargs): return _freesteelpy.FsPath2X_Reverse(*args, **kwargs)
    def CopyPath(*args, **kwargs): return _freesteelpy.FsPath2X_CopyPath(*args, **kwargs)
    def CopyPathSection(*args, **kwargs): return _freesteelpy.FsPath2X_CopyPathSection(*args, **kwargs)
    def CopyMetaState(*args, **kwargs): return _freesteelpy.FsPath2X_CopyMetaState(*args, **kwargs)
    def GenTrackPthItersOnFree(*args, **kwargs): return _freesteelpy.FsPath2X_GenTrackPthItersOnFree(*args, **kwargs)
    def GenTrackPthIters(*args, **kwargs): return _freesteelpy.FsPath2X_GenTrackPthIters(*args, **kwargs)
    def GetNTrimmedPaths(*args, **kwargs): return _freesteelpy.FsPath2X_GetNTrimmedPaths(*args, **kwargs)
    def RecordTrimmedPath(*args, **kwargs): return _freesteelpy.FsPath2X_RecordTrimmedPath(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_FsPath2X):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsPath2X_New
    if _newclass:New = staticmethod(_freesteelpy.FsPath2X_New)
    __swig_getmethods__["CreateSame"] = lambda x: _freesteelpy.FsPath2X_CreateSame
    if _newclass:CreateSame = staticmethod(_freesteelpy.FsPath2X_CreateSame)

class FsPath2XPtr(FsPath2X):
    def __init__(self, this):
        _swig_setattr(self, FsPath2X, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsPath2X, 'thisown', 0)
        _swig_setattr(self, FsPath2X,self.__class__,FsPath2X)
_freesteelpy.FsPath2X_swigregister(FsPath2XPtr)

FsPath2X_EqualOnContour = _freesteelpy.FsPath2X_EqualOnContour

FsPath2X_BetweenOnContourTailOpen = _freesteelpy.FsPath2X_BetweenOnContourTailOpen

FsPath2X_ContourLength = _freesteelpy.FsPath2X_ContourLength

FsPath2X_New = _freesteelpy.FsPath2X_New

FsPath2X_CreateSame = _freesteelpy.FsPath2X_CreateSame

class Thinner(ThinnerInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [ThinnerInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, Thinner, name, value)
    __swig_getmethods__ = {}
    for _s in [ThinnerInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, Thinner, name)
    def __repr__(self):
        return "<C Thinner instance at %s>" % (self.this,)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, Thinner, 'this', _freesteelpy.new_Thinner(*args, **kwargs))
        _swig_setattr(self, Thinner, 'thisown', 1)
    def __del__(self, destroy=_freesteelpy.delete_Thinner):
        try:
            if self.thisown: destroy(self)
        except: pass
    def Thin(*args, **kwargs): return _freesteelpy.Thinner_Thin(*args, **kwargs)
    def AddPath(*args, **kwargs): return _freesteelpy.Thinner_AddPath(*args, **kwargs)
    def IsEmpty(*args, **kwargs): return _freesteelpy.Thinner_IsEmpty(*args, **kwargs)
    def End(*args, **kwargs): return _freesteelpy.Thinner_End(*args, **kwargs)

class ThinnerPtr(Thinner):
    def __init__(self, this):
        _swig_setattr(self, Thinner, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, Thinner, 'thisown', 0)
        _swig_setattr(self, Thinner,self.__class__,Thinner)
_freesteelpy.Thinner_swigregister(ThinnerPtr)

class BumpySurfTransform(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, BumpySurfTransform, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, BumpySurfTransform, name)
    def __repr__(self):
        return "<C BumpySurfTransform instance at %s>" % (self.this,)
    def AddPockms(*args, **kwargs): return _freesteelpy.BumpySurfTransform_AddPockms(*args, **kwargs)
    def PushTriangle(*args, **kwargs): return _freesteelpy.BumpySurfTransform_PushTriangle(*args, **kwargs)
    def GetTriangCoord(*args, **kwargs): return _freesteelpy.BumpySurfTransform_GetTriangCoord(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        _swig_setattr(self, BumpySurfTransform, 'this', _freesteelpy.new_BumpySurfTransform(*args, **kwargs))
        _swig_setattr(self, BumpySurfTransform, 'thisown', 1)
    def __del__(self, destroy=_freesteelpy.delete_BumpySurfTransform):
        try:
            if self.thisown: destroy(self)
        except: pass

class BumpySurfTransformPtr(BumpySurfTransform):
    def __init__(self, this):
        _swig_setattr(self, BumpySurfTransform, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, BumpySurfTransform, 'thisown', 0)
        _swig_setattr(self, BumpySurfTransform,self.__class__,BumpySurfTransform)
_freesteelpy.BumpySurfTransform_swigregister(BumpySurfTransformPtr)

class FsFreeFibre(FsFreeFibreInstanceCounter):
    __swig_setmethods__ = {}
    for _s in [FsFreeFibreInstanceCounter]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FsFreeFibre, name, value)
    __swig_getmethods__ = {}
    for _s in [FsFreeFibreInstanceCounter]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FsFreeFibre, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<C FsFreeFibre instance at %s>" % (self.this,)
    def __del__(self, destroy=_freesteelpy.delete_FsFreeFibre):
        try:
            if self.thisown: destroy(self)
        except: pass
    __swig_getmethods__["New"] = lambda x: _freesteelpy.FsFreeFibre_New
    if _newclass:New = staticmethod(_freesteelpy.FsFreeFibre_New)
    def AddSurf(*args, **kwargs): return _freesteelpy.FsFreeFibre_AddSurf(*args, **kwargs)
    def AddPockSphere(*args, **kwargs): return _freesteelpy.FsFreeFibre_AddPockSphere(*args, **kwargs)
    def GetNBoundaries(*args, **kwargs): return _freesteelpy.FsFreeFibre_GetNBoundaries(*args, **kwargs)
    def GetBoundary(*args, **kwargs): return _freesteelpy.FsFreeFibre_GetBoundary(*args, **kwargs)
    def PointInsideSurface(*args, **kwargs): return _freesteelpy.FsFreeFibre_PointInsideSurface(*args, **kwargs)
    def WFibreCutNew(*args, **kwargs): return _freesteelpy.FsFreeFibre_WFibreCutNew(*args, **kwargs)
    def WFibreCutNewV(*args, **kwargs): return _freesteelpy.FsFreeFibre_WFibreCutNewV(*args, **kwargs)
    def WFibreCutZ(*args, **kwargs): return _freesteelpy.FsFreeFibre_WFibreCutZ(*args, **kwargs)
    def CutPattern(*args, **kwargs): return _freesteelpy.FsFreeFibre_CutPattern(*args, **kwargs)
    def GetPi(*args, **kwargs): return _freesteelpy.FsFreeFibre_GetPi(*args, **kwargs)
    def GetOi(*args, **kwargs): return _freesteelpy.FsFreeFibre_GetOi(*args, **kwargs)

class FsFreeFibrePtr(FsFreeFibre):
    def __init__(self, this):
        _swig_setattr(self, FsFreeFibre, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FsFreeFibre, 'thisown', 0)
        _swig_setattr(self, FsFreeFibre,self.__class__,FsFreeFibre)
_freesteelpy.FsFreeFibre_swigregister(FsFreeFibrePtr)

FsFreeFibre_New = _freesteelpy.FsFreeFibre_New

class WeaveBisectorGenerator(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, WeaveBisectorGenerator, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, WeaveBisectorGenerator, name)
    def __repr__(self):
        return "<C WeaveBisectorGenerator instance at %s>" % (self.this,)
    def __init__(self, *args):
        _swig_setattr(self, WeaveBisectorGenerator, 'this', _freesteelpy.new_WeaveBisectorGenerator(*args))
        _swig_setattr(self, WeaveBisectorGenerator, 'thisown', 1)
    def generateBisectors(*args, **kwargs): return _freesteelpy.WeaveBisectorGenerator_generateBisectors(*args, **kwargs)
    def popPath(*args, **kwargs): return _freesteelpy.WeaveBisectorGenerator_popPath(*args, **kwargs)
    def __del__(self, destroy=_freesteelpy.delete_WeaveBisectorGenerator):
        try:
            if self.thisown: destroy(self)
        except: pass

class WeaveBisectorGeneratorPtr(WeaveBisectorGenerator):
    def __init__(self, this):
        _swig_setattr(self, WeaveBisectorGenerator, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, WeaveBisectorGenerator, 'thisown', 0)
        _swig_setattr(self, WeaveBisectorGenerator,self.__class__,WeaveBisectorGenerator)
_freesteelpy.WeaveBisectorGenerator_swigregister(WeaveBisectorGeneratorPtr)


