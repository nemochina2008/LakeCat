# -*- coding: utf-8 -*-
"""
Created on Fri May 06 10:30:14 2016

this is a sandbox script to work out details for findisolatedLakes.py

@author: Rdebbout
"""
import os
import sys
import pandas as pd
import geopandas as gpd
sys.path.append('D:/Projects/LakeCat')
from LakeCat_functions import NHD_Dict, NHDTblMerge
NHD_dir = 'D:/NHDPlusV21'                    
inputs = NHD_Dict(NHD_dir)  # dictionaries to iterate thru NHD folder structure
rasterUnits = NHD_Dict(NHD_dir, unit='RPU')
outdir = 'D:/Projects/LakeCat/sinkTest'
if not os.path.exists(outdir):
    os.mkdir(outdir)
boundShp = gpd.read_file(
            "%s/NHDPlusGlobalData/BoundaryUnit.shp" % NHD_dir).drop(
            ['AreaSqKM','DrainageID','Shape_Area',
            'Shape_Leng','UnitName'], axis=1)
vpus = boundShp.query("UnitType == 'VPU'")
count = 0
for zone in inputs:  # .keys()[14:]
    print zone
    hr = inputs[zone]
    pre = "%s/NHDPlus%s/NHDPlus%s" % (NHD_dir, hr, zone)
    vpu = vpus.query("UnitID == '%s'" % zone)
    wbs, cat, allTbls, Xs = NHDTblMerge(pre, vpu)                     
    onNetDF = pd.DataFrame(columns=('catCOMID','CatAreaSqKm', 'wbCOMID'))
    catCon = {}
    for name, group in allTbls.groupby('COMID_wb'):
        if not pd.isnull(group.FEATUREID).any():
            base = group.ix[group.HYDROSEQ.idxmin()]
            onNetDF = onNetDF.append(pd.Series([int(base.COMID_cat),  #there is a chance here that some zones don't cap. all letters!
                                                int(base.COMID_wb),
                                                base.AREASQKM_cat],
                                                index=['catCOMID',
                                                'wbCOMID',
                                                'CatAreaSqKm']),
                                         ignore_index=True)
    print 'OnNet: %s' % str(len(onNetDF))
    count += len(onNetDF)
    onNetDF.to_csv("%s/join_%s.csv" % (outdir, zone), index=False)
print 'Total OnNet lakes: %s' % str(count)