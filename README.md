# gmx_mmpbsa_py
A Python script employs the MMPBSA (Molecular Mechanics Poisson-Boltzmann Surface Area) method to integrate GROMACS 
and APBS software, facilitating the calculation of binding free energy between proteins and small molecules.

## Introduction
This script is designed for individuals who have completed molecular dynamics simulations and need to calculate the 
binding free energy between proteins and small molecules. 

Building on the foundational shell script, [gmx_mmpbsa.bsh](https://github.com/Jerkwin/gmxtools/blob/master/gmx_mmpbsa/gmx_mmpbsa.bsh), 
originally developed by [Jicun Li](https://github.com/Jerkwin)
for calculating the binding free energy between proteins and small molecules, we have enhanced it with further analyses 
and illustrative graphics.

**Further analyses and illustrative graphics:**
1. Calculate the total binding free energy (ΔGbinding) between the protein and the small molecules. 
Calculate the van der Waals energy (ΔGvdw), electrostatic energy (ΔGele), polar-solvation energy (ΔGpolar), 
nonpolar solvation energy (ΔGnonpolar) and entropy change (-TΔS) between the protein and the small molecules. 
Present these energy values in a visual histogram.
2. Assess the energy contribution of each amino acid within the protein towards the binding free energy. 
Highlight the top 15 amino acids, ranked in descending order based on their contribution magnitude. 
Display the energy contributions of the top 15 amino acids using a descriptive pie chart.
3. Show the calculation formula of binding free energy. 
According to the relationship between the binding free energy and the dissociation constant (ln Kd =ΔG/RT), 
the corresponding dissociation constant was converted, and the affinity between proteins and small molecules was further analyzed. 



We provide a protocol for users to follow up. The example analysis results are stored in the 
`gmx_mmpbsa_py/example` folder.

## Installation
The instructions below are for the installation of the required software. 
**It should be noticed that there should be no space in the path of APBS and GROMACS.**
### APBS
The recommended version for APBS is 3.0.0, 
please download the software with [link](https://github.com/Electrostatics/apbs/releases/tag/v3.0.0).
### GROMACS
Please refer to the [link](https://manual.gromacs.org/documentation/current/index.html) for GROMACS installation.
### Python3
Please install Python3 with the [link](https://www.python.org/downloads/).
Version 3.6 or higher is preferred.
### Git for Windows
For the windows' users, a Linux/Unix-like environment is required. Please install Git for Windows with the 
[link](https://git-scm.com/downloads). Other bash environment is also valid.


## Protocol

### 1. Clone and deploy the repository
Open git bash in target directory, clone the repository to local.
```bash
# clone the repository to local
git clone https://github.com/JasonJiangs/gmx_mmpbsa_py.git
cd gmx_mmpbsa_py
# install requirements
pip install -r requirements.txt  # or pip3 install -r requirements.txt
```
### 2. Put your files in the data folder
Put three files in the created `gmx_mmpbsa_py/data` folder:
1. Trajectory file (.xtc)
2. Tpr file (.tpr)
3. Index file (.ndx)

### 3. Deploy the parameter.yaml file
The parameter.yaml file is used for setting the very basic parameters for the script.
Here is an example of the parameter.yaml file:
```yaml
trj: md_0_1_noPBC.xtc  # trajectory file
tpr: md_0_1.tpr  # tpr file
ndx: index.ndx  # index file

pro: Protein  # index group name of protein
lig: UNK  # index group name of ligand
com: Protein_UNK

# For Windows' users, USE "/", NOT "\"
apbs: 'I:/Xiao_Lab/APBS/APBS-3.0.0/bin/apbs'  
gmx: 'I:/Xiao_Lab/gmx2018.8/bin/gmx'
```
Change the `gmx_mmpbsa_py/parameter.yaml` file according to your needs. Be aware that this
is the minimal requirement for the script to execute. For more parameter adjustment, please refer to the
`gmx_mmpbsa/gmx_mmpbsa.bsh` for more details, you can adjust it there and execute the script as well.

### 4. Execute the script
Open git bash in the `gmx_mmpbsa_py` folder and execute the script with the command below:
```bash
python main.py # or python3 main.py
```

### 5. Analyze the results
The original shell script output will be stored in the `gmx_mmpbsa_py/results/execution` folder.
The analytical results are stored in the `gmx_mmpbsa_py/results/analysis` folder.

The organized analytical results are briefly introduced:
1. Calculation of the binding free energy between the ligand small molecule and the protein
2. MM/PBSA binding free energy calculation results (Figure 1)
3. The 15 amino acids that contribute the most to binding free energy in the protein (Figure 2)

## Reference



## Cite Us
If you find the script is useful for your work and used for your publication(s).
It will be appreciated if you cite our paper:


As well as the original shell script by Jicun Li: [10.5281/zenodo.6408973](https://zenodo.org/record/6408973)
