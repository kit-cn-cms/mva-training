

import ROOT
import math
import sys
import os
import datetime
from array import array
from subprocess import call
sys.path.insert(0, '../pyroot-plotscripts')
from plotutils import *
from mvautils import *

class Trainer:
    def __init__(self, variables, variables_to_try=[], verbose=False):
        self.best_variables=variables
        self.variables_to_try=variables_to_try
        self.verbose=verbose

        self.ntrainings=0
        self.verbose=verbose
        self.stopwatch=ROOT.TStopwatch()
        self.weightfile='weights/weights.xml'
        weightpath='/'.join((self.weightfile.split('/'))[:-1])
        if not os.path.exists( weightpath ):
            os.makedirs(weightpath)
        self.rootfile='outfile/autotrain.root'
        outfilepath='/'.join((self.rootfile.split('/'))[:-1])
        if not os.path.exists( outfilepath ):
            os.makedirs(outfilepath)

        self.treename='MVATree'
        self.weightexpression='1'
        self.equalnumevents=True
        self.selection=''
        self.factoryoptions="!V:Silent:!Color:DrawProgressBar:AnalysisType=Classification:Transformations=I;D;P;G,D"
        self.bdtoptions= "!H:!V:NTrees=1000:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2:NegWeightTreatment=IgnoreNegWeightsInTraining"     
        self.setVerbose(verbose)

    def setVerbose(self,v=True):
        self.verbose=v
        if self.verbose:
            self.setFactoryOption('!Silent')
        else:
            self.setFactoryOption('Silent')
           
    def addSamples(self, signal_train,background_train,signal_test,background_test):
        self.signal_train=signal_train
        self.signal_test=signal_test
        self.background_train=background_train
        self.background_test=background_test
        
    def setSelection(self, selection):
        self.selection=selection

    def setFactoryOption(self, option):
        self.factoryoptions=replaceOption(option,self.factoryoptions)

    def setBDTOption(self, option):
        self.bdtoptions=replaceOption(option,self.bdtoptions)

    def setEqualNumEvents(self, b=True):
        self.equalnumevents=b

    def setWeightExpression(self, exp):
        self.weightexpression=exp

    def setTreeName(self, treename):
        self.treename=treename

    def setReasonableDefaults(self):
        self.setBDTOption('MaxDepth=2')
        self.setBDTOption('nCuts=50')
        self.setBDTOption('Shrinkage=0.05')
        self.setBDTOption('NTrees=150')
        self.setBDTOption('NegWeightTreatment=IgnoreNegWeightsInTraining')
        self.equalnumevents=True

    def useTransformations(self, b=True):
        # transformation make the training slower
        if b:
            self.setFactoryOption('Transformations=I;D;P;G,D')
        else:
            self.setFactoryOption('Transformations=I')

    def showGui(self):
        ROOT.gROOT.SetMacroPath( "./tmvascripts" )
        ROOT.gROOT.Macro       ( "./TMVAlogon.C" )    
        ROOT.gROOT.LoadMacro   ( "./TMVAGui.C" )


    # trains a without changing the defaults of the trainer
    def trainBDT(self,variables_=[],bdtoptions_="",factoryoptions_=""):
        if not hasattr(self, 'signal_train') or not hasattr(self, 'signal_test') or not hasattr(self, 'background_train')  or not hasattr(self, 'background_test'):
            print 'set training and test samples first'
            return
        fout = ROOT.TFile(self.rootfile,"RECREATE")
        # use given options and trainer defaults if an options is not specified
        newbdtoptions=replaceOptions(bdtoptions_,self.bdtoptions)
        newfactoryoptions=replaceOptions(factoryoptions_,self.factoryoptions)
        factory = ROOT.TMVA.Factory("TMVAClassification",fout,newfactoryoptions)
        # add variables
        variables=variables_
        if len(variables)==0:
            variables = self.best_variables
        for var in variables:
            factory.AddVariable(var)
        # add signal and background trees
        inputS = ROOT.TFile( self.signal_train.path )
        inputB = ROOT.TFile( self.background_train.path )          
        treeS     = inputS.Get(self.treename)
        treeB = inputB.Get(self.treename)

        inputS_test = ROOT.TFile( self.signal_test.path )
        inputB_test = ROOT.TFile( self.background_test.path )          
        treeS_test     = inputS_test.Get(self.treename)
        treeB_test = inputB_test.Get(self.treename)

        # use equal weights for signal and bkg
        signalWeight     = 1.
        backgroundWeight = 1.
        factory.AddSignalTree    ( treeS, signalWeight,ROOT.TMVA.Types.kTraining )
        factory.AddBackgroundTree( treeB, backgroundWeight,ROOT.TMVA.Types.kTraining)
        factory.AddSignalTree    ( treeS_test, signalWeight,ROOT.TMVA.Types.kTesting )
        factory.AddBackgroundTree( treeB_test, backgroundWeight,ROOT.TMVA.Types.kTesting)
        factory.SetWeightExpression(self.weightexpression)
        # make cuts
        mycuts = ROOT.TCut(self.selection)
        mycutb = ROOT.TCut(self.selection)
        # train and test all methods
        normmode="NormMode=NumEvents:"
        if self.equalnumevents:
            normmode="NormMode=EqualNumEvents:"
        factory.PrepareTrainingAndTestTree( mycuts, mycutb,
                                            "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:!V:"+normmode )
        #norm modes: NumEvents, EqualNumEvents
        factory.BookMethod( ROOT.TMVA.Types.kBDT, "BDTG",newbdtoptions )
        factory.TrainAllMethods()
        factory.TestAllMethods()
        factory.EvaluateAllMethods()
        fout.Close()
        weightfile=self.weightfile
        dt=datetime.datetime.now().strftime("%Y_%m%d_%H%M%S")
        weightfile=weightfile.replace('.xml','_'+dt+'.xml')
        call(['cp','weights/TMVAClassification_BDTG.weights.xml',weightfile])
        movedfile=self.rootfile
        movedfile=movedfile.replace('.root','_'+dt+'.root')
        call(['cp',self.rootfile,movedfile])

    def evaluateLastTraining(self):
        f = ROOT.TFile(self.rootfile)
    
        histoS = f.FindObjectAny('MVA_BDTG_S')
        histoB = f.FindObjectAny('MVA_BDTG_B')
        histoTrainS = f.FindObjectAny('MVA_BDTG_Train_S')
        histoTrainB = f.FindObjectAny('MVA_BDTG_Train_B')
        histo_rejBvsS = f.FindObjectAny('MVA_BDTG_rejBvsS')
        histo_effBvsS = f.FindObjectAny('MVA_BDTG_effBvsS')
        histo_effS = f.FindObjectAny('MVA_BDTG_effS')
        histo_effB = f.FindObjectAny('MVA_BDTG_effB')
        histo_trainingRejBvsS = f.FindObjectAny('MVA_BDTG_trainingRejBvsS')    

        rocintegral=histo_rejBvsS.Integral()/histo_rejBvsS.GetNbinsX()
        rocintegral_training=histo_trainingRejBvsS.Integral()/histo_trainingRejBvsS.GetNbinsX()
        bkgRej50=histo_rejBvsS.GetBinContent(histo_rejBvsS.FindBin(0.5))
        bkgRej50_training=histo_trainingRejBvsS.GetBinContent(histo_trainingRejBvsS.FindBin(0.5))
        ksS=histoTrainS.KolmogorovTest(histoS)
        ksB=histoTrainB.KolmogorovTest(histoB)
        return rocintegral
    
    def drawBDT(self):
        f = ROOT.TFile(self.rootfile)

        histoS = f.FindObjectAny('MVA_BDTG_S')
        histoB = f.FindObjectAny('MVA_BDTG_B')
        histoTrainS = f.FindObjectAny('MVA_BDTG_Train_S')
        histoTrainB = f.FindObjectAny('MVA_BDTG_Train_B')
        
        histoS.SetLineColor(self.signal_test.color)
        histoS.Draw('histo')
        histoB.SetLineColor(self.background_test.color)
        histoB.Draw('samehisto')
        histoTrainS.SetLineColor(self.signal_train.color)
        histoTrainS.Draw('same')
        histoTrainB.SetLineColor(self.background_train.color)
        histoTrainB.Draw('same')

    def removeWorstUntil(self,length):
        if(len(self.best_variables)<=length):
            return 
        else:
            print "####### findig variable to remove, nvars is "+str(len(self.best_variables))+", removing until nvars is "+str(length)+"."
            bestscore=-1.
            bestvars=[]
            worstvar=""
            for i in range(len(self.best_variables)):
                # sublist excluding variables i
                sublist=self.best_variables[:i]+self.best_variables[i+1:]
                self.trainBDT(sublist)
                score=self.evaluateLastTraining()
                if score>bestscore:
                    bestscore=score
                    bestvars=sublist
                    worstvar=self.best_variables[i]
            print "####### removing ",
            print worstvar
            self.variables_to_try.append(worstvar)
            self.best_variables=bestvars
            self.removeWorstUntil(length)

    def addBestUntil(self,length):
        if(len(self.best_variables)>=length):
            return
        elif len(self.variables_to_try)==0:
            return        
        else:
            print "####### findig variable to add, nvars is "+str(len(self.best_variables))+", adding until nvars is "+str(length)+"."
            bestscore=-1.
            bestvar=""
            for var in self.variables_to_try:
                newlist=self.best_variables+[var]
                self.trainBDT(newlist)
                score=self.evaluateLastTraining()
                if score>bestscore:
                    bestscore=score
                    bestvar=var
            print "####### adding ",
            print bestvar
            self.variables_to_try.remove(bestvar)
            self.best_variables=self.best_variables+[bestvar]
            self.addBestUntil(length)
        

    def optimizeOption(self,option,factorlist=[0.3,0.5,0.7,1.,1.5,2.,3.]):
        currentvalue=float(getValueOf(option,self.bdtoptions))
        print "####### optimizing "+option+", starting value",currentvalue
        valuelist=[x * currentvalue for x in factorlist] 
        print "####### trying values ",
        print valuelist
        best=valuelist[0]
        bestscore=-1
        for n in valuelist:
            theoption=option+'='+str(n)
            print 'training BDT with',theoption
            self.trainBDT([],theoption)
            score=self.evaluateLastTraining()
            print 'score:',score
            if score>bestscore:
                bestscore=score
                best=n
        print "####### optiminal value is ",
        print best
        self.setBDTOption(option+'='+str(best))
        if best==valuelist[-1] and len(valuelist)>2:
            print "####### optiminal value is highest value, optimizing again"
            highfactorlist=[f for f in factorlist if f > factorlist[-2]/factorlist[-1]]
            self.optimizeOption(option,highfactorlist)
        if best==valuelist[0]and len(valuelist)>2:
            print "####### optiminal value is lowest value, optimizing again"
            lowfactorlist=[f for f in factorlist if f < factorlist[1]/factorlist[0]]            
            self.optimizeOption(option,lowfactorlist)
