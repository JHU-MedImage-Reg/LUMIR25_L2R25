'''
SynthMorph for LUMIR at Learn2Reg 2025
Author: Junyu Chen
        Johns Hopkins University
        jchen245@jhmi.edu
Date: 05/06/2025
'''
import os, random, glob, sys, json
import numpy as np
from torch.utils.data import DataLoader
import torch
import torch.nn.functional as F
import nibabel as nib
from torch.utils.data import Dataset

class L2RLUMIRJSONDataset(Dataset):
    def __init__(self, base_dir, json_path, stage='train'):
        with open(json_path) as f:
            d = json.load(f)
        if stage.lower()=='train':
            self.imgs = d['training']
        elif stage.lower()=='validation':
            self.imgs = d['validation']
        else:
            raise 'Not implemented!'
        self.base_dir = base_dir
        self.stage = stage

    def __getitem__(self, index):
        if self.stage == 'train':
            mov_dict = self.imgs[index]
            fix_dicts = self.imgs.copy()
            fix_dicts.remove(mov_dict)
            random.shuffle(fix_dicts)
            fix_dict = fix_dicts[0]
            x = nib.load(self.base_dir+mov_dict['image'])
            y = nib.load(self.base_dir+fix_dict['image'])

        else:
            img_dict = self.imgs[index]
            mov_path = img_dict['moving']
            fix_path = img_dict['fixed']
            x = nib.load(self.base_dir + mov_path)
            y = nib.load(self.base_dir + fix_path)
        x = x.get_fdata() / 255.
        y = y.get_fdata() / 255.
        x, y = x[None, ...], y[None, ...]
        x = np.ascontiguousarray(x)  # [channels,Height,Width,Depth]
        y = np.ascontiguousarray(y)
        x, y = torch.from_numpy(x), torch.from_numpy(y)
        return x.float(), y.float()

    def __len__(self):
        return len(self.imgs)

def nib_load(file_name):
    if not os.path.exists(file_name):
        return np.array([1])

    proxy = nib.load(file_name)
    data = proxy.get_fdata()
    proxy.uncache()
    return data

def csv_writter(line, name):
    with open(name+'.csv', 'a') as file:
        file.write(line)
        file.write('\n')

def save_nii(img, file_name, pix_dim=[1., 1., 1.]):
    x_nib = nib.Nifti1Image(img, np.eye(4))
    x_nib.header.get_xyzt_units()
    x_nib.header['pixdim'][1:4] = pix_dim
    x_nib.to_filename('{}.nii.gz'.format(file_name))

def main():
    val_dir = '/scratch/jchen/DATA/LUMIR/LUMIR25/'
    if not os.path.exists('/scratch/jchen/python_projects/LUMIR_output/LUMIR25_SynthMorph_ValPhase/'):
        os.makedirs('/scratch/jchen/python_projects/LUMIR_output/LUMIR25_SynthMorph_ValPhase/')

    val_set = L2RLUMIRJSONDataset(base_dir=val_dir, json_path='/scratch/jchen/DATA/LUMIR/LUMIR25/LUMIR25_dataset.json',
                                           stage='validation')
    val_loader = DataLoader(val_set, batch_size=1, shuffle=False, num_workers=4, pin_memory=True, drop_last=True)
    val_files = val_set.imgs

    '''
    Validation
    '''
    with torch.no_grad():
        for i, data in enumerate(val_loader):
            mv_id = val_files[i]['moving'].split('_')[-2]
            fx_id = val_files[i]['fixed'].split('_')[-2]
            x_image = data[0]
            y_image = data[1]
            x = x_image.squeeze(0).squeeze(0).detach().cpu().numpy()
            y = y_image.squeeze(0).squeeze(0).detach().cpu().numpy()
            print('start registration: {}'.format(i))
            x_nib = nib.Nifti1Image(x, np.eye(4))
            x_nib.header.get_xyzt_units()
            x_nib.header['pixdim'][1:4] = [1., 1., 1.]
            x_nib.to_filename('x.nii.gz')

            y_nib = nib.Nifti1Image(y, np.eye(4))
            y_nib.header.get_xyzt_units()
            y_nib.header['pixdim'][1:4] = [1., 1., 1.]
            y_nib.to_filename('y.nii.gz')

            
            #print(def_.shape)
            os.system('/scratch/jchen/python_projects/synthmorph/synthmorph -m deform -t def.nii.gz x.nii.gz y.nii.gz')
            flow = nib_load('def.nii.gz')
            
            save_nii(flow, '/scratch/jchen/python_projects/LUMIR_output/LUMIR25_SynthMorph_ValPhase/' + 'disp_{}_{}'.format(fx_id, mv_id))
            print('disp_{}_{}.nii.gz saved to {}'.format(fx_id, mv_id, '/scratch/jchen/python_projects/LUMIR_output/LUMIR25_SynthMorph_ValPhase/'))


def seedBasic(seed=2021):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)

def seedTorch(seed=2021):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

if __name__ == '__main__':
    '''
    GPU configuration
    '''
    DEFAULT_RANDOM_SEED = 12
    seedBasic(DEFAULT_RANDOM_SEED)
    seedTorch(DEFAULT_RANDOM_SEED)
    main()