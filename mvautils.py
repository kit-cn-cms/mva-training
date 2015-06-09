import ROOT
from array import array

def getOptionAndValueFromString(optionassignment):
    optionassignment=optionassignment.strip()
    option_value=optionassignment.split('=')
    option=''
    value=''
    if len(option_value)==2:
        option=option_value[0]
        value=option_value[1]
    elif len(option_value)==1:
        if option_value[0][0]=='!':
            option=option_value[0][1:]
            value='!'
        else:
            option=option_value[0]
    option=option.strip()
    value=value.strip()
    return option,value


def getStringFromOptionAndValue(option,value):
    if value=='':
        return option
    elif value=='!':
        return '!'+option
    else:
        return option+'='+value
    
def replaceOption(newoption_assignment,oldoptions):
    newoption,newvalue=getOptionAndValueFromString(newoption_assignment)
    oldlistofoptions=oldoptions.split(':')
    newlistofoptions=[]
    found=False
    for o in oldlistofoptions:
        o=o.strip()
        if len(o)==0:
            continue
        oldoption,oldvalue=getOptionAndValueFromString(o)
        if oldoption==newoption:
            newlistofoptions.append(getStringFromOptionAndValue(newoption,newvalue))
            found=True
        else :
            newlistofoptions.append(getStringFromOptionAndValue(oldoption,oldvalue))
    if not found:
        newlistofoptions.append(newoption_assignment)
    newoptions=":".join(newlistofoptions)
    return newoptions

def replaceOptions(newoption_assignments,oldoptions):
    listofnewoptions=newoption_assignments.split(':')
    for o in listofnewoptions:
        o=o.strip()
        if(len(o)>0):
            oldoptions=replaceOption(o,oldoptions)
    return oldoptions

def getValueOf(option,optionstring):
    spl=optionstring.split(':')
    for o in spl:
        o=o.strip()
        opt,val=getOptionAndValueFromString(o)
        if opt==option:
            return val
    return None

def split_evenodd(path,pathOdd,pathEven):
    oldfile = ROOT.TFile( path )
    oldtree = oldfile.Get( "MVATree" )
    nentries =oldtree.GetEntries()
   
    file1 = ROOT.TFile(pathOdd ,"recreate" )
    tree1 = oldtree.CloneTree(0)

    file2 = ROOT.TFile(pathEven ,"recreate" )
    tree2 = oldtree.CloneTree(0)

    odd=array('i',[0])
    oldtree.SetBranchAddress( "Evt_Odd", odd )
   
    print "splitting even odd "+path+" into "+pathOdd+" and "+pathEven
    for i in range(nentries):
        if i>0 and i%100000==0:
            print "at entry "+str(i)
        oldtree.GetEntry( i )
        if odd[0]==1 :
            tree1.Fill()
        if odd[0]==0 :
            tree2.Fill()

    tree1.AutoSave()
    tree2.AutoSave()
    file1.Close()
    file2.Close()
    oldfile.Close()


def split_jtcategories(path):
    oldfile = ROOT.TFile( path )
    oldtree = oldfile.Get( "MVATree" )
    nentries =oldtree.GetEntries()
   
    file64 = ROOT.TFile(path.replace('.root','6j4t.root') ,"recreate" )
    tree64 = oldtree.CloneTree(0)
    file63 = ROOT.TFile(path.replace('.root','6j3t.root') ,"recreate" )
    tree63 = oldtree.CloneTree(0)
    file62 = ROOT.TFile(path.replace('.root','6j2t.root') ,"recreate" )
    tree62 = oldtree.CloneTree(0)
    file54 = ROOT.TFile(path.replace('.root','5j4t.root') ,"recreate" )
    tree54 = oldtree.CloneTree(0)
    file53 = ROOT.TFile(path.replace('.root','5j3t.root') ,"recreate" )
    tree53 = oldtree.CloneTree(0)
    file44 = ROOT.TFile(path.replace('.root','4j4t.root') ,"recreate" )
    tree44 = oldtree.CloneTree(0)
    file43 = ROOT.TFile(path.replace('.root','4j3t.root') ,"recreate" )
    tree43 = oldtree.CloneTree(0)

    njets=array('i',[0])
    oldtree.SetBranchAddress( "N_Jets", njets )

    ntags=array('i',[0])
    oldtree.SetBranchAddress( "N_BTagsM", ntags )
   
    for i in range(nentries):
        
        oldtree.GetEntry( i )
        if njets[0]==4 and ntags[0]==3 :
            tree43.Fill()
        elif njets[0]==4 and ntags[0]>=4 :
            tree44.Fill()
        elif njets[0]==5 and ntags[0]==3 :
            tree53.Fill()
        elif njets[0]==5 and ntags[0]>=4 :
            tree54.Fill()
        elif njets[0]>=6 and ntags[0]==2 :
            tree62.Fill()
        elif njets[0]>=6 and ntags[0]==3 :
            tree63.Fill()
        elif njets[0]>=6 and ntags[0]>=4 :
            tree64.Fill()

    tree64.AutoSave()
    tree63.AutoSave()
    tree62.AutoSave()
    tree54.AutoSave()
    tree53.AutoSave()
    tree44.AutoSave()
    tree43.AutoSave()

    file64.Close()
    file63.Close()
    file62.Close()
    file54.Close()
    file53.Close()
    file44.Close()
    file43.Close()

