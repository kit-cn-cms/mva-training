from trainer import Trainer
import sys
sys.path.insert(0, '../pyroot-plotscripts')
from plotutils import *
from mvautils import *


variables=["BDTOhio_v2_input_avg_dr_tagged_jets",
           "BDTOhio_v2_input_avg_btag_disc_btags",
           "BDTOhio_v2_input_h2",
           "BDTOhio_v2_input_h3",
           "BDTOhio_v2_input_second_highest_btag",
           "BDTOhio_v2_input_third_highest_btag",
           "BDTOhio_v2_input_fourth_highest_btag",
           "BDTOhio_v2_input_maxeta_jet_jet",
           "BDTOhio_v2_input_maxeta_jet_tag",
           "BDTOhio_v2_input_maxeta_tag_tag",
           "BDTOhio_v2_input_pt_all_jets_over_E_all_jets",
           "BDTOhio_v2_input_tagged_dijet_mass_closest_to_125",
           "BDTOhio_v2_input_dEta_fn"
]

addtional_variables=["BDTOhio_v2_input_h0",
                     "BDTOhio_v2_input_h1"]

#samples have a name, a color, a path, and a selection (not implemented yet for training)
#only the path is really relevant atm
cat='6j4t'
signal_test=Sample('t#bar{t}H test',ROOT.kBlue,'/nfs/dust/cms/user/hmildner/mva-training/trees/tthbb_fast_'+cat+'_even.root','') 
signal_train=Sample('t#bar{t}H training',ROOT.kGreen,'/nfs/dust/cms/user/hmildner/mva-training/trees/tthbb_fast_'+cat+'_odd.root','')
background_test=Sample('t#bar{t} test',ROOT.kRed+1,'/nfs/dust/cms/user/hmildner/mva-training/trees/ttbar_'+cat+'_even.root','')
background_train=Sample('t#bar{t} training',ROOT.kRed-1,'/nfs/dust/cms/user/hmildner/mva-training/trees/ttbar_'+cat+'_odd.root','')
trainer=Trainer(variables,addtional_variables)

trainer.addSamples(signal_train,background_train,signal_test,background_test) #add the sample defined above
trainer.setTreeName('MVATree') # name of tree in files
trainer.setReasonableDefaults() # set some configurations to reasonable values
trainer.setEqualNumEvents(True) # reweight events so that integral in training and testsample is the same
trainer.useTransformations(False) # faster this way
trainer.setVerbose(False) # no output during BDT training and testing
trainer.setWeightExpression('(Weight>0)-(Weight<0)') #ignore CSV weights etc, only pm 1 # Weight should correspond to the weightexpression in your tree
trainer.setSelection('N_Jets>=6&&N_BTagsM>=4') # selection for category (not necessary if trees are split)
trainer.removeWorstUntil(10) # removes worst variable until only 10 are left 
trainer.optimizeOption('NTrees') # optimizies the number of trees by trying more and less trees # you need to reoptimize ntrees depending on the variables and on other parameters
trainer.addBestUntil(12) # add best variables until 12 are used
trainer.optimizeOption('NTrees')
trainer.removeWorstUntil(10)
trainer.optimizeOption('NTrees')
trainer.removeWorstUntil(8)
trainer.optimizeOption('NTrees')
print "these are found to be the 8 best variables and best bdt and factory options"
print trainer.best_variables
print trainer.bdtoptions
print trainer.factoryoptions
