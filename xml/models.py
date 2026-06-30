# AUTO-GENERATED - DO NOT EDIT
# Regenerate by running: python main.py

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DwgExportSummary:
    object_class: str = "DwgExportSummary"
    exptxtnb: Optional[str] = None
    instobjnb: Optional[str] = None
    joincolnb: Optional[str] = None
    joinnb: Optional[str] = None
    keycolnb: Optional[str] = None
    keynb: Optional[str] = None
    linkdiagnb: Optional[str] = None
    morigtxtnb: Optional[str] = None
    mtxtnb: Optional[str] = None
    odiversion: Optional[str] = None
    origtxtnb: Optional[str] = None
    originrepositoryid: Optional[str] = None
    otherobjectsnb: Optional[str] = None
    planagentnb: Optional[str] = None
    repositoryversion: Optional[str] = None
    scentxtnb: Optional[str] = None
    stepnb: Optional[str] = None
    txtnb: Optional[str] = None
    ueorignb: Optional[str] = None
    ueusednb: Optional[str] = None
    varplanagentnb: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DwgExportSummary"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpDeploySpec:
    object_class: str = "SnpDeploySpec"
    businessname: Optional[str] = None
    cleanuponerror: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    globalid: Optional[str] = None
    ideployspec: Optional[str] = None
    imapref: Optional[str] = None
    iownermapping: Optional[str] = None
    isconcurrent: Optional[str] = None
    isfrozen: Optional[str] = None
    logstagelocname: Optional[str] = None
    name: Optional[str] = None
    syncreqd: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpDeploySpec"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpExecUnit:
    object_class: str = "SnpExecUnit"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    gentype: Optional[str] = None
    globalid: Optional[str] = None
    ieukmref: Optional[str] = None
    iexecunit: Optional[str] = None
    iexecunitgrp: Optional[str] = None
    ilschemaref: Optional[str] = None
    iownerds: Optional[str] = None
    iparexecunit: Optional[str] = None
    istap: Optional[str] = None
    lschemaname: Optional[str] = None
    multicongentype: Optional[str] = None
    name: Optional[str] = None
    optclassname: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpExecUnit"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpExecUnitGrp:
    object_class: str = "SnpExecUnitGrp"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    globalid: Optional[str] = None
    iexecunitgrp: Optional[str] = None
    iownerds: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpExecUnitGrp"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpFKXRef:
    object_class: str = "SnpFKXRef"
    refkey: Optional[str] = None
    refobjfqname: Optional[str] = None
    refobjfqnamelengths: Optional[str] = None
    refobjfqtype: Optional[str] = None
    refobjglobalid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpFKXRef"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapAttr:
    object_class: str = "SnpMapAttr"
    alias: Optional[str] = None
    attrpos: Optional[str] = None
    attrtype: Optional[str] = None
    businessname: Optional[str] = None
    datatypename: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    extdtqualname: Optional[str] = None
    firstdate: Optional[str] = None
    firstuser: Optional[str] = None
    globalid: Optional[str] = None
    grpfunc: Optional[str] = None
    idatamapref: Optional[str] = None
    imapattr: Optional[str] = None
    imapref: Optional[str] = None
    iownermapcp: Optional[str] = None
    iparmapattr: Optional[str] = None
    indchange: Optional[str] = None
    intdtqualname: Optional[str] = None
    intversion: Optional[str] = None
    isderivedname: Optional[str] = None
    isrequired: Optional[str] = None
    lastdate: Optional[str] = None
    lastuser: Optional[str] = None
    length: Optional[str] = None
    name: Optional[str] = None
    prec: Optional[str] = None
    propvalues: Optional[str] = None
    scale: Optional[str] = None
    sortpos: Optional[str] = None
    sourcedt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapAttr"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapComp:
    object_class: str = "SnpMapComp"
    alias: Optional[str] = None
    businessname: Optional[str] = None
    comptypeversion: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    globalid: Optional[str] = None
    imapcomp: Optional[str] = None
    imapcomptype: Optional[str] = None
    imapref: Optional[str] = None
    iownermapcomp: Optional[str] = None
    iownermapping: Optional[str] = None
    itechno: Optional[str] = None
    iscardinal: Optional[str] = None
    isderivedname: Optional[str] = None
    ishidden: Optional[str] = None
    name: Optional[str] = None
    propvalues: Optional[str] = None
    sortpos: Optional[str] = None
    typename: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapComp"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapConn:
    object_class: str = "SnpMapConn"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    globalid: Optional[str] = None
    iendmapcp: Optional[str] = None
    imapconn: Optional[str] = None
    iownermapping: Optional[str] = None
    istartmapcp: Optional[str] = None
    ishidden: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapConn"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapCp:
    object_class: str = "SnpMapCp"
    businessname: Optional[str] = None
    cardinality: Optional[str] = None
    compsubtype: Optional[str] = None
    cporder: Optional[str] = None
    cppos: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    direction: Optional[str] = None
    globalid: Optional[str] = None
    imapcp: Optional[str] = None
    imapcprole: Optional[str] = None
    imapref: Optional[str] = None
    iownermapcomp: Optional[str] = None
    iparmapcp: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapCp"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapExpr:
    object_class: str = "SnpMapExpr"
    execonhint: Optional[str] = None
    firstdate: Optional[str] = None
    firstuser: Optional[str] = None
    globalid: Optional[str] = None
    hasunparsedident: Optional[str] = None
    idistechref: Optional[str] = None
    iexonlsref: Optional[str] = None
    imapcp: Optional[str] = None
    imapexpr: Optional[str] = None
    iownermapattr: Optional[str] = None
    iownermapprop: Optional[str] = None
    indchange: Optional[str] = None
    intversion: Optional[str] = None
    isactive: Optional[str] = None
    isparsed: Optional[str] = None
    lastdate: Optional[str] = None
    lastuser: Optional[str] = None
    parsedtext: Optional[str] = None
    parsedtxt: Optional[str] = None
    propvalues: Optional[str] = None
    text: Optional[str] = None
    texthash: Optional[str] = None
    textonly: Optional[str] = None
    txt: Optional[str] = None
    validationcode: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapExpr"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapExprRef:
    object_class: str = "SnpMapExprRef"
    globalid: Optional[str] = None
    imapexprref: Optional[str] = None
    iownermapexpr: Optional[str] = None
    irefmapattr: Optional[str] = None
    irefmapcomp: Optional[str] = None
    irefmapref: Optional[str] = None
    iscopingmapcp: Optional[str] = None
    isvalid: Optional[str] = None
    refkey: Optional[str] = None
    reftext: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapExprRef"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapProp:
    object_class: str = "SnpMapProp"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    dispnamekey: Optional[str] = None
    globalid: Optional[str] = None
    ideployspec: Optional[str] = None
    iexecunit: Optional[str] = None
    imapattr: Optional[str] = None
    imapcomp: Optional[str] = None
    imapcp: Optional[str] = None
    imapprop: Optional[str] = None
    imappropparent: Optional[str] = None
    imapping: Optional[str] = None
    iownermapping: Optional[str] = None
    iphynode: Optional[str] = None
    ipropdef: Optional[str] = None
    ipropxrefvalue: Optional[str] = None
    ishidden: Optional[str] = None
    name: Optional[str] = None
    propdefguid: Optional[str] = None
    propdefqualifiedname: Optional[str] = None
    proporder: Optional[str] = None
    proptype: Optional[str] = None
    propvalue: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapProp"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapRef:
    object_class: str = "SnpMapRef"
    adapterintftype: Optional[str] = None
    adaptername: Optional[str] = None
    businessname: Optional[str] = None
    description: Optional[str] = None
    fcoguid: Optional[str] = None
    fcoqualifiedname: Optional[str] = None
    fcoqualifiedname2: Optional[str] = None
    fcoqualifiedname3: Optional[str] = None
    firstdate: Optional[str] = None
    firstuser: Optional[str] = None
    globalid: Optional[str] = None
    ifcoid: Optional[str] = None
    imapref: Optional[str] = None
    iownermapping: Optional[str] = None
    irefid: Optional[str] = None
    iscid: Optional[str] = None
    indchange: Optional[str] = None
    intversion: Optional[str] = None
    lastdate: Optional[str] = None
    lastuser: Optional[str] = None
    name: Optional[str] = None
    qualifiedname: Optional[str] = None
    qualifiedname2: Optional[str] = None
    qualifiedname3: Optional[str] = None
    refcount: Optional[str] = None
    refguid: Optional[str] = None
    scguid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapRef"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpMapping:
    object_class: str = "SnpMapping"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    extversion: Optional[str] = None
    firstdate: Optional[str] = None
    firstuser: Optional[str] = None
    globalid: Optional[str] = None
    icontextmapref: Optional[str] = None
    ifolder: Optional[str] = None
    imapping: Optional[str] = None
    iproject: Optional[str] = None
    iscbasemapping: Optional[str] = None
    iscmapping: Optional[str] = None
    iscorigmapping: Optional[str] = None
    indchange: Optional[str] = None
    intversion: Optional[str] = None
    isreusable: Optional[str] = None
    lastdate: Optional[str] = None
    lastuser: Optional[str] = None
    metadataversion: Optional[str] = None
    name: Optional[str] = None
    propvalues: Optional[str] = None
    scorigmappingtag: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpMapping"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpPhyExpr:
    object_class: str = "SnpPhyExpr"
    globalid: Optional[str] = None
    hintsyncstate: Optional[str] = None
    ifromphynode: Optional[str] = None
    imapexpr: Optional[str] = None
    iownerphynode: Optional[str] = None
    iphyexpr: Optional[str] = None
    irmexprref: Optional[str] = None
    itophynode: Optional[str] = None
    pushedbyhint: Optional[str] = None
    refexprqualname: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpPhyExpr"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })



@dataclass
class SnpPhyNode:
    object_class: str = "SnpPhyNode"
    businessname: Optional[str] = None
    descript: Optional[str] = None
    description: Optional[str] = None
    globalid: Optional[str] = None
    hintsyncstate: Optional[str] = None
    icheckkm: Optional[str] = None
    iexecunit: Optional[str] = None
    imapcomp: Optional[str] = None
    imapcp: Optional[str] = None
    imapref: Optional[str] = None
    imaprefcp: Optional[str] = None
    iownerds: Optional[str] = None
    iparphynode: Optional[str] = None
    iphynode: Optional[str] = None
    irefphynode: Optional[str] = None
    isrccompkm: Optional[str] = None
    itgtcompkm: Optional[str] = None
    indfixedbyhint: Optional[str] = None
    indfixedbytechno: Optional[str] = None
    isfixedeu: Optional[str] = None
    name: Optional[str] = None
    nodetype: Optional[str] = None
    refcompname: Optional[str] = None
    refcpname: Optional[str] = None
    refdsinputcp: Optional[str] = None
    stagetablename: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SnpPhyNode"
        return cls(**{
            k: v for k, v in data.items() if k in {f.name for f in fields(cls)}
        })


