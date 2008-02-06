MAIN_DIR = 'D:/work/uhbd_salts/D20'
PH_TO_PLOT = [4,7,10]

"""Accessory program to plot results of UHBD calculations using rpy interface
to R."""

__author__ = "Michael J. Harms"
__date__ = "February 22, 2006"
__version__ = "0.2"

import os
import RTools
from sys import exit

class titration:
    """A class that stores pH, Z, dGion, dGelec, and ionic strength of a
    hybrid.out file."""
    
    def __init__(self,ionic_strength):
        self.pH = []
        self.Z = []
    
        self.dGion = []
        self.dGelec = []
        self.ionic_strength = ionic_strength

def plot_pH(all_titrations,ionic_strengths,output_dir,title):
    """Plots variation of Z, dGelec, and dGion as a function of pH for a set of
    hybrid.out (generated in UHBD) calculations."""
    
    # set up data series to be plotted as a function of pH
    Z = []
    dGion = []
    dGelec = []
    for indiv_titration in all_titrations:
        Z.append([indiv_titration.pH,indiv_titration.Z])
        dGion.append([indiv_titration.pH,indiv_titration.dGion])
        dGelec.append([indiv_titration.pH,indiv_titration.dGelec])
    
    # Plot series as a function of pH
    RTools.plotSeries(output_dir+os.sep+title+'_Z_pH.png',Z,ionic_strengths,
                      title+': Charge versus pH','pH','charge',[],[],True,True,800,800)
    """
    RTools.plotSeries(output_dir+os.sep+title+'_dGion_pH.png',dGion,ionic_strengths,
                      title+': dG ion versus pH','pH','dG ion (kcal/mol)',[],[],True,True,800,800)
    RTools.plotSeries(output_dir+os.sep+title+'_dGelec_pH.png',dGelec,ionic_strengths,
                      title+': dG elec versus pH','pH','dG elec (kcal/mol)',[],[],True,True,800,800)
    """

    RTools.plotSeries(output_dir+os.sep+title+'_dGion_pH.png',dGion,ionic_strengths,
                      title+': dG ion versus pH','pH','dG ion (kcal/mol)',[0,16],[-10,100],True,True,800,800)
    RTools.plotSeries(output_dir+os.sep+title+'_dGelec_pH.png',dGelec,ionic_strengths,
                      title+': dG elec versus pH','pH','dG elec (kcal/mol)',[0,16],[-10,100],True,True,800,800)

    
def plot_IS(all_titrations,ionic_strengths,pH_to_plot,output_dir,title):
    """Plots variation of Z, dGelec, and dGion as a function of ionic strength
    for a set of pH values (in pH_to_plot)."""
    
    # Set up data to be plotted as a function of ionic strength
    IS_values = [float(x) for x in ionic_strengths]
    Z_IS = [[IS_values,[]] for x in range(len(pH_to_plot))]
    dGion_IS = [[IS_values,[]] for x in range(len(pH_to_plot))]
    dGelec_IS = [[IS_values,[]] for x in range(len(pH_to_plot))]
    
    # This essentially performs a matrix transposition: each series is now an
    # ionic strength titration at a different pH.  
    for indiv_titration in all_titrations:
        pH_index = 0
        for index, pH in enumerate(indiv_titration.pH):
            if (pH in pH_to_plot) == True:
                Z_IS[pH_index][1].append(indiv_titration.Z[index])
                dGion_IS[pH_index][1].append(indiv_titration.dGion[index])
                dGelec_IS[pH_index][1].append(indiv_titration.dGelec[index])
                pH_index += 1

    # Plot series as a function of ionic strength
    RTools.plotSeries(output_dir+os.sep+title+'_Z_IS.png',Z_IS,pH_to_plot,
                      title+': Charge versus ionic strength',
                      'Ionic strength (M)','charge',[],[],True,True,800,800)
    """
    RTools.plotSeries(output_dir+os.sep+title+'_dGion_IS.png',dGion_IS,pH_to_plot,
                      title+': dG ion versus ionic strength',
                      'Ionic strength (M)','dG ion (kcal/mol)',[],[],True,True,800,800)
    RTools.plotSeries(output_dir+os.sep+title+'_dGelec_IS.png',dGelec_IS,pH_to_plot,
                      title+': dG elec versus ionic strength',
                      'Ionic strength (M)','dG elec (kcal/mol)',[],[],True,True,800,800)
    """
    RTools.plotSeries(output_dir+os.sep+title+'_dGion_IS.png',dGion_IS,pH_to_plot,
                      title+': dG ion versus ionic strength',
                      'Ionic strength (M)','dG ion (kcal/mol)',[0,1],[-10,50],True,True,800,800)
    RTools.plotSeries(output_dir+os.sep+title+'_dGelec_IS.png',dGelec_IS,pH_to_plot,
                      title+': dG elec versus ionic strength',
                      'Ionic strength (M)','dG elec (kcal/mol)',[0,1],[-10,50],True,True,800,800)


    
    # Dump to file
    g = open(output_dir + os.sep + title + "IStitr.dat","w")
    for i in range(len(dGion_IS[0][0])):
        g.write("%-10i%10.4F" % (i,dGion_IS[0][0][i]))
        for series in dGion_IS:
            g.write("%10.4F" % series[1][i])
        g.write("\n")
    g.close()
            

def plotSalts(input_dir):
    """Plots UHBD results within a single directory.  Directory must contain
    uhbd_calcs directory, which in turn contains a set of directories organized
    by ionic strength."""
    
    root_dir = MAIN_DIR + os.sep + input_dir + os.sep + "uhbd_calcs"
    
    # Create list of directories containing hybrid files
    directories = os.listdir(root_dir)
    #directories = [dir for dir in directories if dir[-4] != '.']
    ionic_strengths_dict = {}
    for dir in directories:
        ionic_strengths_dict.update([(.001*float(dir),dir)])
    ionic_strengths = ionic_strengths_dict.keys()
    ionic_strengths.sort() 
    directories = [ionic_strengths_dict[x] for x in ionic_strengths]
    
    
    # Create global variable to hold all titration data (as instances of titration
    # class)
    global all_titrations
    all_titrations = []
    
    for index, dir in enumerate(directories):
        
        # Read individual hybrid file
        f = open(root_dir + os.sep + dir + os.sep + "hybrid.out",'r')
        hybrid = f.readlines()
        f.close()
        
        # initialize instance of titration class to store titration data
        all_titrations.append(titration(ionic_strengths[index]))
        
        # Remove all data except titration data from hybrid
        titr_end = hybrid.index("atom  type  resid  Group  pk(model)  pK(app)  DpK(app)  z  Gself  Gborn  Gback\n")
        titr_hybrid = hybrid[2:titr_end-1]
    
        # Extract pH, Z, dGion, and dGelec data from hybrid and place in all_titrations
        for line in titr_hybrid:
            column = line.split()
            all_titrations[index].pH.append(float(column[0]))
            all_titrations[index].Z.append(float(column[1]))
            all_titrations[index].dGion.append(float(column[3]))
            all_titrations[index].dGelec.append(float(column[4]))
    
    # Plot data as a function of pH and ionic strength
#    plot_pH(all_titrations,ionic_strengths,MAIN_DIR + os.sep + input_dir,input_dir)
#    plot_IS(all_titrations,ionic_strengths,PH_TO_PLOT,MAIN_DIR + os.sep + input_dir,input_dir)

    plot_pH(all_titrations,ionic_strengths,MAIN_DIR,input_dir)
    plot_IS(all_titrations,ionic_strengths,PH_TO_PLOT,MAIN_DIR,input_dir)


#*****************************************************************************#
#                               MAIN CODE                                     #
#*****************************************************************************#

main_dir_list = os.listdir(MAIN_DIR)
main_dir_list = [dir for dir in main_dir_list if dir[-4] != '.']
for dir in main_dir_list:
    print dir
    plotSalts(dir)

print 'Complete'
