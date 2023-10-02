from gmx_mmpbsa.execution import GMX_MMPBSA
import os

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gmx_mmpbsa = GMX_MMPBSA()
    gmx_mmpbsa.execute()
    print('Done with GMX_MMPBSA and starting to analyze the results...')
    gmx_mmpbsa.analyze()
    print('Done with the analysis of the results.')
