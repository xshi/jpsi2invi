#!/usr/bin/env python
"""
Event Selection
"""

__author__ = "R. Kiuchi <kiuchi@ihep.ac.cn>"
__copyright__ = "Copyright (c) Ryuta Kiuchi"
__created__ = "[2016-12-28 Wed 11:00]" 

 
import sys
import os
import math 
import ROOT 
from progressbar import Bar, Percentage, ProgressBar
from time import time 
from tools import duration, check_outfile_path
from array import array

#TEST=True 
TEST=False

# Global constants 
JPSI_MASS = 3.096916; 

#NonPiPiJpsi=True
NonPiPiJpsi=False

PID_PSIP=100443
PID_PION_PLUS=211
PID_PION_MINUS=-211
PID_JPSI=443

# Global histograms

h_evtflw = ROOT.TH1F('hevtflw', 'eventflow', 10, 0, 10) 
h_evtflw.GetXaxis().SetBinLabel(1, 'raw')
h_evtflw.GetXaxis().SetBinLabel(2, 'N_{#gamma}=0')
h_evtflw.GetXaxis().SetBinLabel(3, '|cos#theta|<0.8')
h_evtflw.GetXaxis().SetBinLabel(4, '|p|<0.45') 
h_evtflw.GetXaxis().SetBinLabel(5, 'PID') 
h_evtflw.GetXaxis().SetBinLabel(6, 'cos#theta_{#pi^{+}#pi^{-}}<0.95') 
h_evtflw.GetXaxis().SetBinLabel(7, 'cos#theta_{#pi#pi sys}<0.9') 
h_evtflw.GetXaxis().SetBinLabel(8, '3<M_{#pi#pi}^{rec}<3.2') 

h_mrecpipi = ROOT.TH1D('h_mrecpipi', 'mrecpipi', 100, 3.03, 3.17)
h_mrecpipi_fit = ROOT.TH1D('h_mrecpipi_fit', 'mrecpipi_fit', 1400, 3.03, 3.17)
#h_mrecpipi_fit = ROOT.TH1D('h_mrecpipi_fit', 'mrecpipi_fit', 1400, 3.02, 3.18)
#h_mrecpipi_fit = ROOT.TH1D('h_mrecpipi_fit', 'mrecpipi_fit', 1400, 3.04, 3.16)
h_mrecpipi_narrow = ROOT.TH1D('h_mrecpipi_narrow', 'mrecpipi_narrow', 100, 3.03, 3.17)
h_mpipi = ROOT.TH1D('h_mpipi', 'mpipi', 100, 0.2, 0.7) 
h_pip_p = ROOT.TH1D('h_pip_p', 'pip_p', 100, 0.0, 0.5) 
h_pim_p = ROOT.TH1D('h_pim_p', 'pim_p', 100, 0.0, 0.5) 
h_pip_costhe = ROOT.TH1D('h_pip_costhe', 'pip_costhe', 100, -1.0, 1.0)
h_pim_costhe = ROOT.TH1D('h_pim_costhe', 'pim_costhe', 100, -1.0, 1.0)
h_cospipi = ROOT.TH1D('h_cospipi', 'cospipi', 200, -1.0, 1.0)
h_cos2pisys = ROOT.TH1D('h_cos2pisys', 'cos2pisys', 100, -1.0, 1.0)
h_ncharged = ROOT.TH1D('h_ncharged', 'ncharged', 100, 0, 20)

vtx_mrecpipi = ROOT.vector('double')()


# ROOT.gROOT.ProcessLine(
# "struct MyTreeStruct{\
#    Double_t vtx_mrecpipi;\
# };"	);

def usage():
    sys.stdout.write('''
NAME
    sel_events_inclusive.py 

SYNOPSIS

    ./sel_events_inclusive.py infile outfile 

AUTHOR 
    R. Kiuchi <kiuchi@ihep.ac.cn>"

DATE
    December 2016 
\n''')

    
def main():

    if TEST:
        sys.stdout.write('Run in TEST mode! \n')
    
    args = sys.argv[1:]
    if len(args) < 2:
        return usage()
    
    infile = args[0]
    outfile = args[1]
    print "outfile : ",outfile
    check_outfile_path(outfile)

    fin = ROOT.TFile(infile)
    t = fin.Get('tree')
    entries = t.GetEntriesFast()

    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=entries).start()
    time_start = time()

    fout = ROOT.TFile(outfile, "RECREATE")
    t_out = ROOT.TTree('signal', 'signal')
    # mystruct = ROOT.MyTreeStruct()
    t_out.Branch('vtx_mrecpipi', vtx_mrecpipi)

    n_run = array('i',[0])
    n_event = array('i',[0])
    n_indexmc = array('i',[0])
    t_out.Branch('run', n_run, 'run/I')
    t_out.Branch('event', n_event, 'event/I')
    t_out.Branch('indexmc', n_indexmc, 'indexmc/I')
    n_pdgid = array('i',100*[-99])
    n_motheridx = array('i',100*[-99])
    t_out.Branch('pdgid', n_pdgid, 'pdgid[100]/I')
    t_out.Branch('motheridx', n_motheridx, 'motheridx[100]/I')
 
#    fout = ROOT.TFile(outfile, "RECREATE")
#    t_out = ROOT.TTree('signal', 'signal')
#    mystruct = ROOT.MyTreeStruct()
# #    mystruct2 = ROOT.MyTreeStruct2()
#    t_out.Branch('vtx_mrecpipi', mystruct, 'vtx_mrecpipi/D')

#    t_out.Branch('indexmc', mystruct2, 'indexmc/D')
#    t_out.Branch('pdgid', mystruct, 'm_pdgid[100]/I')
#    t_out.Branch('trkidx', mystruct, 'm_trkidx[100]/I')
#    t_out.Branch('motherpid', mystruct, 'm_motherpid[100]/I')
#    t_out.Branch('motheridx', mystruct, 'm_motheridx[100]/I')

    for jentry in xrange(entries):
        pbar.update(jentry+1)
        # get the next tree in the chain and verify
        ientry = t.LoadTree(jentry)
        if ientry < 0:
            break
        # copy next entry into memory and verify

        if TEST and ientry > 10000:
            break
        
        nb = t.GetEntry(jentry)
        if nb<=0:
            continue

        #print type(vtx_mrecpipi)
        #print dir(ROOT.vector.__doc__)

        # if NonPiPiJpsi:                            # Non-PiPiJpsi
        #     if not ( check_pipiJpsi(t) ):
        #         fill_histograms_all_combination(t)
        # else:                                      # Normal 
        #     fill_histograms_all_combination(t)
 
    if (t.run<0):
        
        n_run[0] = t.run
        n_event[0] = t.event
        n_indexmc[0] = t.indexmc
        for ii in range(t.indexmc):
            n_pdgid[ii] = t.m_pdgid[ii]
            n_motheridx[ii] = t.m_motheridx[ii]

        # t_out.Fill()
        # vtx_cospipi.clear()

    fill_histograms_all_combination(t)    

    t_out.Fill()
    t_out.Write()
    write_histograms() 
    fout.Close()
    pbar.finish()
    
    dur = duration(time()-time_start)
    sys.stdout.write(' \nDone in %s. \n' % dur) 


def check_pipiJpsi(t):

    pion_plus_flag =0
    pion_minus_flag = 0
    jpsi_flag = 0
    for i in range(100):
        mother_pid = t.m_motherpid[i]
        pid        = t.m_pdgid[i]

        if( mother_pid==PID_PSIP and pid==PID_PION_PLUS ):  
            pion_plus_flag = 1
        if( mother_pid==PID_PSIP and pid==PID_PION_MINUS ):
            pion_minus_flag = 1
        if( mother_pid==PID_PSIP and pid==PID_JPSI ):
            jpsi_flag = 1

    flag = pion_plus_flag * pion_minus_flag * jpsi_flag
    
    return flag


def fill_histograms_all_combination(t):
    
    nentry = t.npipi
    nsurvived = 0
    for loop in range(nentry):
        cut_ngam = 1
        
        cut_pip_costhe = (abs(math.cos(t.trkp_theta[loop])) < 0.8)
        cut_pim_costhe = (abs(math.cos(t.trkm_theta[loop])) < 0.8)
        cut_pip_p = (abs(t.trkp_p[loop]) < 0.45)
        cut_pim_p = (abs(t.trkm_p[loop]) < 0.45)
        cut_cospipi =  (t.vtx_cospipi[loop] < 0.95)
        cut_cos2pisys = (abs(t.vtx_cos2pisys[loop]) < 0.9)
        cut_pi_PID = (t.pip_prob_pip[loop] > t.pip_prob_kp[loop] and t.pip_prob_pip[loop] > 0.001 and
                      t.pim_prob_pim[loop] > t.pim_prob_km[loop] and t.pim_prob_pim[loop] > 0.001)
        cut_mjpsi_win = (t.vtx_mrecpipi[loop] > 3.0 and t.vtx_mrecpipi[loop] < 3.2)
        cut_mjpsi_sig = (abs(t.vtx_mrecpipi[loop] - JPSI_MASS)<0.015)

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe and cut_pip_p and cut_pim_p and
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_win):            
            h_mrecpipi.Fill(t.vtx_mrecpipi[loop])
            h_mrecpipi_fit.Fill(t.vtx_mrecpipi[loop])
            h_ncharged.Fill(t.ncharged)
            # for mrec in t.vtx_mrecpipi:
            #     print mrec
            vtx_mrecpipi.push_back(t.vtx_mrecpipi.at(loop))
            # t_out.Fill()


            # print vtx_mrecpipi.size()
            if (nsurvived==0 and (3.03 < t.vtx_mrecpipi[loop] and t.vtx_mrecpipi[loop] < 3.17)): 
                nsurvived = 1
                h_mrecpipi_narrow.Fill(t.vtx_mrecpipi[loop])

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe and cut_pip_p and cut_pim_p and
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_mpipi.Fill(t.vtx_mpipi[loop])

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe                and cut_pim_p and
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_pip_p.Fill(t.pip_p[loop])

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe and cut_pip_p                and 
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_pim_p.Fill(t.pim_p[loop])
                    
        if (cut_ngam                                        and cut_pip_p and cut_pim_p and
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_pip_costhe.Fill(math.cos(t.pip_theta[loop]))
                        
        if (cut_ngam                                        and cut_pip_p and cut_pim_p and
            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_pim_costhe.Fill(math.cos(t.pim_theta[loop]))

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe and cut_pip_p and cut_pim_p and
            cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
            h_cospipi.Fill(t.vtx_cospipi[loop])

        if (cut_ngam and cut_pip_costhe and cut_pim_costhe and cut_pip_p and cut_pim_p and
            cut_cospipi                   and cut_pi_PID and cut_mjpsi_sig):
            h_cos2pisys.Fill(t.vtx_cos2pisys[loop])

#        if (             cut_pip_costhe and cut_pim_costhe and cut_pip_p and cut_pim_p and
#            cut_cospipi and cut_cos2pisys and cut_pi_PID and cut_mjpsi_sig):
#            h_ngam.Fill(t.ngam)


        # t_out.Fill()
        # vtx_cospipi.clear()
        
    
def write_histograms():
    # t_out.Write()
    h_evtflw.Write()
    h_mrecpipi.Write()
    h_mrecpipi_fit.Write()
    h_mrecpipi_narrow.Write()
    h_mpipi.Write()
    h_pip_p.Write()
    h_pim_p.Write()
    h_pip_costhe.Write()
    h_pim_costhe.Write()
    h_cospipi.Write()
    h_cos2pisys.Write()
    h_ncharged.Write()

    
def select_jpsi_to_invisible(t):
    h_evtflw.Fill(0) 

    if not (t.ngam == 0):
        return False
    h_evtflw.Fill(1) 
    
    if not ( abs(math.cos(t.trkp_theta)) < 0.8 and abs(math.cos(t.trkm_theta)) < 0.8):
        return False
    h_evtflw.Fill(2) 

    if not (abs(t.trkp_p) < 0.45 and abs(t.trkm_p) < 0.45):
        return False 
    h_evtflw.Fill(3) 

    if not (t.prob_pip > t.prob_kp and t.prob_pip > 0.001 and
            t.prob_pim > t.prob_km and t.prob_pim > 0.001):
        return False
    h_evtflw.Fill(4)

    if not (t.vtx_cospipi < 0.95):
        return False
    h_evtflw.Fill(5)

    if not (t.vtx_cos2pisys < 0.9):
        return False
    h_evtflw.Fill(6)

    if not (t.vtx_mrecpipi > 3.0 and t.vtx_mrecpipi < 3.2):
        return False
    h_evtflw.Fill(7)
    
    return True
    
    
if __name__ == '__main__':
    main()
