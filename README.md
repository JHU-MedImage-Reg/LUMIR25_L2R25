# Large Scale Unsupervised Brain MRI Image Registration 2025 (LUMIR25)
[![Static Badge](https://img.shields.io/badge/MICCAI-SIG_BIR-%2337677e?style=flat&labelColor=%23ececec&link=https%3A%2F%2Fmiccai.org%2Findex.php%2Fspecial-interest-groups%2Fbir%2F)](https://miccai.org/index.php/special-interest-groups/bir/) ![Static Badge](https://img.shields.io/badge/MICCAI-Learn2Reg-%23214f5f?labelColor=%23ececec&link=https%3A%2F%2Flearn2reg.grand-challenge.org%2F) <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>

This official repository houses baseline methods, training scripts, and pretrained models for the LUMIR challenge at Learn2Reg 2025.\
The challenge is dedicated to ***unsupervised*** brain MRI image registration and offers a comprehensive dataset of over 5000 preprocessed T1-weighted 3D brain MRI images, available for training, testing, and validation purposes.

Please visit [***learn2reg.grand-challenge.org***](https://learn2reg.grand-challenge.org/learn2reg-2025/) for more information.

$${\color{red}New!}$$ - 06/01/2025 - Check out our preprint summarizing LUMIR 2024 -> [![arXiv](https://img.shields.io/badge/arXiv-2505.24160-b31b1b.svg)](https://arxiv.org/abs/2505.24160)\
$${\color{red}New!}$$ - 05/06/2025 - Launching the LUMIR challenge at Learn2Reg 2025!

## LUMIR25 Detailed Rankings
![Detailed_rankings](https://github.com/user-attachments/assets/3ddafd8e-6f54-474d-bd77-0e73125dbd00)


## Dataset: 
- ***Download Training Dataset:*** Access the training dataset via Google Drive ([~51GB](https://drive.google.com/uc?export=download&id=1c9OWODseHA-2cLCkcRKKu_NxouhKOUyY)).
- ***Download Validation Dataset:*** Access the validation dataset via Google Drive ([~430MB](https://drive.google.com/uc?export=download&id=1Zsgt03tvOe9SGMo85d1fM_wZpRkSDLVv)).
    - To support participants, we also provide ***coarse anatomical label maps (10 classes)*** for the validation datasets, enabling participants to perform quick self-validation prior to leaderboard submission. However, evaluations on the leaderboard as well as the test phase will be conducted on ***much finer anatomical structures (over 100 classes)***. Access the simplified label maps via Google Drive ([~14MB](https://drive.google.com/uc?export=download&id=1c1gY-2c43uiEt599yha5FszdfZLcUZxa)).
- ***Preprocessing:*** The OpenBHB dataset underwent initial preprocessing by its creators, which included skull stripping and affine registration. For comprehensive details, refer to the [OpenBHB GitHub](https://baobablab.github.io/bhb/dataset) page and their [article](https://www.sciencedirect.com/science/article/pii/S1053811922007522). Subsequently, we performed N4 bias correction with ITK and intensity normalization using a [pre-existing tool](https://github.com/jcreinhold/intensity-normalization).
- ***Annotation:*** We conducted segmentation of the anatomical structures using automated software. To enhance the dataset for evaluation purposes, an experienced radiologist and neurologist contributed manual landmark annotations to a subset of the images.
- ***Image size:*** The dimensions of each image are `160 x 224 x 192`.
- ***Normalization:*** Intensity values for each image volume have been normalized to fall within the range `[0,255]`.
- ***Dataset structure:***
    ```bash
    LUMIR/imagesTr/------
            LUMIRMRI_0000_0000.nii.gz   <--- a single brain T1 MR image
            LUMIRMRI_0001_0000.nii.gz
            LUMIRMRI_0002_0000.nii.gz
            .......
    LUMIR/imagesVal/------
            LUMIRMRI_3454_0000.nii.gz
            LUMIRMRI_3455_0000.nii.gz
    ```
- ***Dataset json file:*** [LUMIR25_dataset.json](https://drive.google.com/uc?export=download&id=164Flc1C6oufONGimvpKlrNtq5t3obXEo)

## Baseline methods:
***Learning-based models:***
TBA

***Learning-based foundation models:***
- SynthMorph ([Official website](https://martinos.org/malte/synthmorph/) | [Scripts](https://github.com/JHU-MedImage-Reg/LUMIR_L2R/tree/main/SynthMorph))
- ConvexAdam ([Official website](https://github.com/multimodallearning/convexAdam) | [Scripts](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/tree/main/Baseline_Methods/ConvexAdam))
- SynthSR + VFA ([SynthSR official website](https://github.com/BBillot/SynthSR) | [VFA official website](https://github.com/yihao6/vfa/) | [Scripts](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/tree/main/Baseline_Methods/VFA))

***Optimization-based methods:***
- SyN (ATNs) TBA
- deedsBCV TBA

## Evaluation metrics:
1. TRE ([Code](https://github.com/JHU-MedImage-Reg/LUMIR_L2R/blob/2e98e0f936d2806ba2e40cbbd78a36219e4f9610/L2R_LUMIR_Eval/evaluation.py#L169-L197))
2. Dice ([Code](https://github.com/JHU-MedImage-Reg/LUMIR_L2R/blob/2e98e0f936d2806ba2e40cbbd78a36219e4f9610/L2R_LUMIR_Eval/evaluation.py#L155-L159))
3. HD95 ([Code](https://github.com/JHU-MedImage-Reg/LUMIR_L2R/blob/2e98e0f936d2806ba2e40cbbd78a36219e4f9610/L2R_LUMIR_Eval/evaluation.py#L162-L166))
4. **Non-diffeomorphic volumes (NDV)** ([Code](https://github.com/JHU-MedImage-Reg/LUMIR_L2R/blob/c19670ba91f1cffb33bdfff040daa42bfbf72058/L2R_LUMIR_Eval/evaluation.py#L139-L154)) *See this [article](https://link.springer.com/article/10.1007/s11263-024-02047-1) published in IJCV, and its associated [GitHub papge](https://github.com/yihao6/digital_diffeomorphism)* 

## Validation Submission guidelines:
We expect to provide displacement fields for all registrations in the file naming format should be `disp_PatID1_PatID2`, where `PatID1` and `PatID2` represent the subject IDs for the fixed and moving images, respectively. The evaluation process requires the files to be organized in the following structure:
```bash
folder.zip
└── folder
    ├── disp_3455_3454.nii.gz
    ├── disp_3456_3455.nii.gz
    ├── disp_3457_3456.nii.gz
    ├── disp_3458_3457.nii.gz
    ├── ...
    └── ...
```
Submissions must be uploaded as zip file containing displacement fields (displacements only) for all validation pairs for all tasks (even when only participating in a subset of the tasks, in that case submit deformation fields of zeroes for all remaining tasks). You can find the validation pairs for in the LUMIR_dataset.json. The convention used for displacement fields depends on scipy's `map_coordinates()` function, expecting displacement fields in the format `[X, Y, Z,[x, y, z]]` or `[[x, y, z],X, Y, Z]`, where `X, Y, Z` and `x, y, z` represent voxel displacements and image dimensions, respectively. The evaluation script expects `.nii.gz` files using full-precision format and having shapes `160x224x196x3`. Further information can be found here.

Note for PyTorch users: When using PyTorch as deep learning framework you are most likely to transform your images with the `grid_sample()` routine. Please be aware that this function uses a different convention than ours, expecting displacement fields in the format `[X, Y, Z,[x, y, z]]` and normalized coordinates between -1 and 1. Prior to your submission you should therefore convert your displacement fields to match our convention.

## Citations for dataset usage:
    @article{chen2025beyond,
    title={Beyond the LUMIR challenge: The pathway to foundational registration models},
    author={Chen, Junyu and Wei, Shuwen and Honkamaa, Joel and Marttinen, Pekka and Zhang, Hang and Liu, Min and Zhou, Yichao and Tan, Zuopeng and Wang, Zhuoyuan and Wang, Yi and others},
    journal={arXiv preprint arXiv:2505.24160},
    year={2025}
    }
    
    @article{dufumier2022openbhb,
    title={Openbhb: a large-scale multi-site brain mri data-set for age prediction and debiasing},
    author={Dufumier, Benoit and Grigis, Antoine and Victor, Julie and Ambroise, Corentin and Frouin, Vincent and Duchesnay, Edouard},
    journal={NeuroImage},
    volume={263},
    pages={119637},
    year={2022},
    publisher={Elsevier}
    }

    @article{taha2023magnetic,
    title={Magnetic resonance imaging datasets with anatomical fiducials for quality control and registration},
    author={Taha, Alaa and Gilmore, Greydon and Abbass, Mohamad and Kai, Jason and Kuehn, Tristan and Demarco, John and Gupta, Geetika and Zajner, Chris and Cao, Daniel and Chevalier, Ryan and others},
    journal={Scientific Data},
    volume={10},
    number={1},
    pages={449},
    year={2023},
    publisher={Nature Publishing Group UK London}
    }
    
    @article{marcus2007open,
    title={Open Access Series of Imaging Studies (OASIS): cross-sectional MRI data in young, middle aged, nondemented, and demented older adults},
    author={Marcus, Daniel S and Wang, Tracy H and Parker, Jamie and Csernansky, John G and Morris, John C and Buckner, Randy L},
    journal={Journal of cognitive neuroscience},
    volume={19},
    number={9},
    pages={1498--1507},
    year={2007},
    publisher={MIT Press One Rogers Street, Cambridge, MA 02142-1209, USA journals-info~…}
    }

If you have used **Non-diffeomorphic volumes** in the evaluation of the deformation regularity, please cite the following:

    @article{liu2024finite,
      title={On finite difference jacobian computation in deformable image registration},
      author={Liu, Yihao and Chen, Junyu and Wei, Shuwen and Carass, Aaron and Prince, Jerry},
      journal={International Journal of Computer Vision},
      pages={1--11},
      year={2024},
      publisher={Springer}
    }

