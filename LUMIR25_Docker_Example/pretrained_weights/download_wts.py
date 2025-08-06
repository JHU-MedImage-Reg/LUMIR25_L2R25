import os, gdown

pretrained_wts_multi = 'VFA_LUMIR25.pth'
pretrained_wts_mono = 'VFA_LUMIR24.pth'

if not os.path.isfile(pretrained_dir+pretrained_wts_multi):
    # download VFA24 model
    file_id = '17XEfRYJbnrtCVhaBCOvQVOLkWhix9PAK'
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, pretrained_wts_multi, quiet=False)

if not os.path.isfile(pretrained_dir+pretrained_wts_mono):
    # download VFA25 model
    file_id = '1cDY3isltI-uSCiivgP2zcx_5LeR8vIJ6'
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, pretrained_wts_mono, quiet=False)
