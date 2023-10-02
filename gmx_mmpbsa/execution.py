import yaml
import subprocess
import os
import re
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(style="white", context="talk")
import pandas as pd


class GMX_MMPBSA:
    def __init__(self, config_file='./parameter.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        # input files
        self.trj = self.config['trj']
        self.tpr = self.config['tpr']
        self.ndx = self.config['ndx']

        # settings
        self.pro = self.config['pro']
        self.lig = self.config['lig']
        self.com = self.config['com']

        # software path
        self.gmx = self.config['gmx']
        self.apbs = self.config['apbs']

        # create ./results
        self.results_path = './results'
        if not os.path.exists(self.results_path):
            os.mkdir(self.results_path)

        # analysis output path
        self.analysis_path = './results/analysis'
        if not os.path.exists(self.analysis_path):
            os.mkdir(self.analysis_path)

        # execution output path
        self.execution_path = './results/execution'
        if not os.path.exists(self.execution_path):
            os.mkdir(self.execution_path)

        # clear previous results
        self.file_list = [self.config['trj'], self.config['tpr'], self.config['ndx']]
        self._clear_temp_files_in_dir('./results/execution', self.file_list)
        # copy data files
        self._copy_files('./data', './results/execution')
        # copy gmx_mmpbsa.bsh to './results/execution'
        shutil.copy('./gmx_mmpbsa/gmx_mmpbsa.bsh', './results/execution/gmx_mmpbsa.bsh')

    def execute(self):
        """
        Deploys the execution of gmx_mmpbsa.bsh
        """
        self._run_gmx_mmpbsa()
        self._clear_temp_files_in_dir('./results/execution', self.file_list)

    def _clear_temp_files_in_dir(self, dir_path, file_list):
        for file in file_list:
            file_path = os.path.join(dir_path, file)
            if os.path.exists(file_path):
                os.remove(file_path)

    def _copy_files(self, src_dir, dst_dir):
        for file in os.listdir(src_dir):
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dst_dir, file)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_file)

    def _run_gmx_mmpbsa(self):
        # construct command
        command = [
            'sh',
            './results/execution/gmx_mmpbsa.bsh',
            '--trj', self.trj.strip('\''),
            '--tpr', self.tpr.strip('\''),
            '--ndx', self.ndx.strip('\''),
            '--pro', self.pro.strip('\''),
            '--lig', self.lig.strip('\''),
            '--com', self.com.strip('\''),
            '--apbs', self.apbs,
            '--gmx', self.gmx,
            '--workdir', './results/execution'
        ]

        # execute command
        try:
            subprocess.run(command, check=True, shell=True)
            print('Command executed successfully...')
        except subprocess.CalledProcessError as e:
            self._clear_temp_files_in_dir('./results/execution', self.file_list)
            print(f"Command failed with error: {e}")

    def analyze(self):
        file_mmpbsa = self.execution_path + '/_pid~MMPBSA.dat'
        file_res_mmpbsa = self.execution_path + '/_pid~res_MMPBSA.dat'

        if not os.path.exists(file_mmpbsa):
            print(f'No file named {file_mmpbsa} found.')
            return
        if not os.path.exists(file_res_mmpbsa):
            print(f'No file named {file_res_mmpbsa} found.')
            return

        line_list = []
        with open('./results/execution/_pid~MMPBSA.dat', 'r') as f:
            for line in f:
                line_list.append(line)

        dH_line = None
        TdS_line = None
        Ki_line = None
        for line in line_list:
            if 'dH=' in line:
                dH_line = self._parse_string2float(line)
            elif 'TdS=' in line:
                TdS_line = self._parse_string2float(line)
            elif 'Ki=' in line:
                Ki_line = self._parse_string2float_s(line)
            else:
                pass

        dH_dict = {'Binding (with DH)': dH_line[1],
                   'VDW': dH_line[-1],
                   'COU (with DH)': dH_line[-2],
                   'PB': dH_line[4],
                   'SA': dH_line[5],
                   }
        TdS_dict = {'Binding (with DH)': TdS_line[1]}
        Ki_dict = {'uM': Ki_line[1], 'nM': Ki_line[3]}

        value_list = [dH_dict["VDW"], dH_dict["COU (with DH)"], dH_dict["PB"], dH_dict["SA"],
                      TdS_dict["Binding (with DH)"], dH_dict["Binding (with DH)"]]
        name_list = ['ΔG vdw', 'ΔG ele', 'ΔG polar', 'ΔG nonpolar', '-TΔS', 'ΔG binding']
        df = pd.DataFrame({'Energy Items': name_list, 'Energy kcal/mol': value_list})
        sns.barplot(x='Energy Items', y='Energy kcal/mol', data=df)
        # show value of each bar
        for x, y in enumerate(value_list):
            plt.text(x, y, '%s' % round(y, 3), ha='center', va='bottom')
        plt.xticks(rotation=45)
        plt.tight_layout()
        # set figure size
        fig = plt.gcf()
        fig.set_size_inches(8, 10)
        # small font size
        plt.rcParams.update({'font.size': 5})
        # add line at y=0
        plt.axhline(y=0, color='black', linestyle='-', linewidth=3)
        # title and move up the title
        plt.title('MM/PBSA binding free energy calculation results', y=1.05)
        # crop the figure and save
        plt.savefig('results/analysis/fig1.png', dpi=100, bbox_inches='tight'
                    , pad_inches=0.1, transparent=False)
        plt.close()

        line_list = []
        with open('results/execution/_pid~res_MMPBSA.dat', 'r') as f:
            for line in f:
                line_list.append(line)

        for line in line_list:
            if 'mean' in line:
                mean_list = self._parse_string2float(line)[2:]
            elif 'Frame' in line:
                frame_list = self._parse_frame(line)[2:]
            else:
                pass

        # get the value in mean list where index is odd, and match with the frame list
        mean_list_odd = []
        frmae_list_odd = []
        for i in range(len(frame_list)):
            mean_list_odd.append(mean_list[i * 2 + 1])
            frmae_list_odd.append(frame_list[i])

        # sort the mean list and get the first 15 smallest values, match with the frame list
        first_15 = sorted(mean_list_odd)[0:15]
        first_15_index = []
        for i in first_15:
            first_15_index.append(mean_list_odd.index(i))
        first_15_frame = []
        for i in first_15_index:
            first_15_frame.append(frmae_list_odd[i])

        value_list = first_15
        name_list = first_15_frame

        # crop name
        for i in range(len(name_list)):
            name_list[i] = name_list[i][2:].strip('(with DH)')

        df = pd.DataFrame({'Residue': name_list, 'Energy kcal/mol': value_list})

        # small font size
        plt.rcParams.update({'font.size': 15})
        sns.barplot(x='Residue', y='Energy kcal/mol', data=df)
        # show value of each bar
        for x, y in enumerate(value_list):
            plt.text(x, y, '%s' % round(y, 3), ha='center', va='bottom')
        plt.xticks(rotation=45)
        # plt.tight_layout()
        # set figure size
        fig = plt.gcf()
        fig.set_size_inches(16, 8)
        # set title
        plt.title('The 15 amino acids that contribute the most to binding free energy in the protein', y=1.0)
        # save
        plt.savefig('results/analysis/fig2.png', dpi=80, bbox_inches='tight'
                    , pad_inches=0.1, transparent=False)
        plt.close()

        # create a output.md file
        with open('results/analysis/output_test.md', 'w') as f:
            f.write(f'=== Calculate the binding free energy between the ligand small molecule and the protein ===  \n')
            f.write(f'Δ*G*<sub>binding</sub>  \n')
            f.write(f'= Δ*H* - *T*Δ*S*  \n')
            f.write(
                f'= Δ*G*<sub>vdw</sub> + Δ*G*<sub>ele</sub> + Δ*G*<sub>polar</sub> + Δ*G*<sub>nonpolar</sub> + (-*T*Δ*S*)  \n')
            f.write(
                f'= ({dH_dict["VDW"]}) + ({dH_dict["COU (with DH)"]}) + ({dH_dict["PB"]}) + ({dH_dict["SA"]}) + ({TdS_dict["Binding (with DH)"]})  \n')
            f.write(
                f'= {round(dH_dict["VDW"] + dH_dict["COU (with DH)"] + dH_dict["PB"] + dH_dict["SA"] + TdS_dict["Binding (with DH)"], 3)} kJ/mol  \n')
            f.write(f'  \n')
            f.write(f'=== Convert to **kcal/mol** ===  \n')
            f.write(f'Δ*G*<sub>binding</sub>  \n')
            f.write(f'= Δ*H* - *T*Δ*S*  \n')
            f.write(
                f'= Δ*G*<sub>vdw</sub> + Δ*G*<sub>ele</sub> + Δ*G*<sub>polar</sub> + Δ*G*<sub>nonpolar</sub> + (-*T*Δ*S*)  \n')
            f.write(
                f'= ({round(dH_dict["VDW"] / 4.184, 3)}) + ({round(dH_dict["COU (with DH)"] / 4.184, 3)}) + ({round(dH_dict["PB"] / 4.184, 3)}) + ({round(dH_dict["SA"] / 4.184, 3)}) + ({round(TdS_dict["Binding (with DH)"] / 4.184, 3)})  \n')
            f.write(
                f'= {round((dH_dict["VDW"] + dH_dict["COU (with DH)"] + dH_dict["PB"] + dH_dict["SA"] + TdS_dict["Binding (with DH)"]) / 4.184, 3)} kcal/mol  \n')
            f.write(f'  \n')
            f.write(f'  \n')
            f.write(
                f'=== The dissociation constant is derived from the relationship between the binding free energy and the dissociation constant ===  \n')
            f.write(f'ln(*K<sub>d</sub>*)  \n')
            f.write(f'= Δ*G* &divide; *RT*  \n')
            f.write(f'= {Ki_dict["nM"]} nM  \n')
            f.write(f'  \n')
            f.write(f'  \n')
            f.write(f'=== Interpretation ===  \n')
            f.write(f'Δ*G*<sub>vdw</sub>: Van der Waals interaction energy  \n')
            f.write(f'Δ*G*<sub>ele</sub>: Electrostatic interaction energy  \n')
            f.write(f'Δ*G*<sub>polar</sub>: Polar solvation energy  \n')
            f.write(f'Δ*G*<sub>nonpolar</sub>: Nonpolar solvation energy  \n')
            f.write(f'Δ*H*: Enthalpy change  \n')
            f.write(f'-*T*Δ*S*: Entropy change  \n')
            f.write(f'*ΔG*<sub>binding</sub>: Binding free energy  \n')
            f.write(f'*K<sub>d</sub>*: Dissociation constant  \n')
            f.write(f'  \n')
            f.write(f'  \n')
            f.write(f'=== Figure 1 ===  \n')
            f.write(f'![fig1](fig1.png)  \n')
            f.write(f'  \n')
            f.write(f'=== Figure 2  ===  \n')
            f.write(f'![fig2](fig2.png)  \n')
            f.write(f'  \n')
        f.close()

    def _parse_string2float(self, s):
        numbers = re.findall(r'-?\d+\.\d+', s)
        float_numbers = [float(num) for num in numbers]
        return float_numbers

    def _parse_string2float_s(self, s):
        pattern = r"(-?\d+\.\d+E[-+]?\d+)"
        float_numbers = re.findall(pattern, s)
        return float_numbers

    def _parse_frame(self, s):
        return re.split(r'\s\s+', s)