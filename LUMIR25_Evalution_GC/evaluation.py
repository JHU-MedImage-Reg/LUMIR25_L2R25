"""
Evaluation Script for the L2R Challenge.
For details, please visit: https://github.com/MDL-UzL/L2R/
"""


import os
import json, glob
import argparse
import nibabel as nib
from utils import *
from surface_distance import *
from collections import OrderedDict
import digital_diffeomorphism as dd

def evaluate_L2R(INPUT_PATH, GT_PATH, OUTPUT_PATH, JSON_PATH, verbose=False):
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    name = data['name']
    expected_shape = np.array(data['expected_shape'])
    evaluation_methods_metrics = [tmp['metric']
                                  for tmp in data['evaluation_methods']]
    if 'masked_evaluation' in data:
        use_mask = data['masked_evaluation']
    else:
        use_mask = False
    eval_pairs = data['eval_pairs']
    len_eval_pairs = len(eval_pairs)
    # Check if files are available beforehand
    for idx, pair in enumerate(eval_pairs):
        # allow short displacement file names when 
        # a) same modalities
        # b) modality is the same or modality is 0 and 1
        fix_subject, fix_modality = pair['fixed'][-16:-12], pair['fixed'][-11:-7]
        mov_subject, mov_modality = pair['moving'][-16:-12], pair['moving'][-11:-7]
        ##allow for npz files

        disp_lazy_name = f"disp_{fix_subject}_{mov_subject}"
        disp_full_name = f"disp_{fix_subject}_{fix_modality}_{mov_subject}_{mov_modality}"
        if (fix_modality == mov_modality or (fix_modality == '0000' and mov_modality == '0001')):
            if os.path.isfile(os.path.join(INPUT_PATH, disp_lazy_name+'.nii.gz')):
                continue
        elif os.path.isfile(os.path.join(INPUT_PATH, disp_full_name+'.nii.gz')):
            continue
        raise_missing_file_error(disp_lazy_name+'.nii.gz')

    if verbose:
        print(
            f"Evaluate {len_eval_pairs} cases for: {[tmp['name'] for tmp in data['evaluation_methods']]}")
    if use_mask and verbose:
        print("Will use masks for evaluation.")
    cases_results = {}
    for idx, pair in enumerate(eval_pairs):
        case_results = {}
        fix_subject, fix_modality = pair['fixed'][-16:-12], pair['fixed'][-11:-7]
        mov_subject, mov_modality = pair['moving'][-16:-12], pair['moving'][-11:-7]

        fix_label_path = os.path.join(
            GT_PATH, pair['fixed'].replace('images', 'labels'))
        mov_label_path = os.path.join(
            GT_PATH, pair['moving'].replace('images', 'labels'))
        # with nii.gz

        # allow short displacement file names when 
        # a) same modalities
        # b) modality is the same or modality is 0 and 1

        disp_lazy_name = f"disp_{fix_subject}_{mov_subject}"
        disp_full_name = f"disp_{fix_subject}_{fix_modality}_{mov_subject}_{mov_modality}"

        corrfield_kpts_condition = (fix_modality == mov_modality or (fix_modality == '0000' and mov_modality == '0001'))

        if corrfield_kpts_condition:
            for file in [disp_lazy_name+'.nii.gz',]:
                if os.path.isfile(os.path.join(INPUT_PATH, file)):
                    disp_field = load_disp(os.path.join(INPUT_PATH, file))
                    break
        else:
            for file in [disp_full_name+'.nii.gz',]:
                if os.path.isfile(os.path.join(INPUT_PATH, file)):
                    disp_field = load_disp(os.path.join(INPUT_PATH, file))
                    break
                
        
        if disp_field.shape[0] == 3:
            disp_field = disp_field.transpose(1, 2, 3, 0)
        shape = np.array(disp_field.shape)
        if not np.all(shape == expected_shape):
            raise_shape_error(f'{fix_subject}_{fix_modality}-->{mov_subject}_{mov_modality}', shape, expected_shape) ##error here

        # load neccessary files
        if any([True for eval_ in ['tre'] if eval_ in evaluation_methods_metrics]):
            spacing_fix = nib.load(os.path.join(
                GT_PATH, pair['fixed'])).header.get_zooms()[:3]
            spacing_mov = nib.load(os.path.join(
                GT_PATH, pair['moving'])).header.get_zooms()[:3]

        if any([True for eval_ in ['dice', 'hd95'] if eval_ in evaluation_methods_metrics]):
            fixed_seg = nib.load(fix_label_path).get_fdata()
            moving_seg = nib.load(mov_label_path).get_fdata()
            D, H, W = fixed_seg.shape
            identity = np.meshgrid(np.arange(D), np.arange(
                H), np.arange(W), indexing='ij')
            warped_seg = map_coordinates(
                moving_seg, identity + disp_field.transpose(3, 0, 1, 2), order=0)

        if use_mask:
            mask_path = os.path.join(
                GT_PATH, pair['fixed'].replace('images', 'masks'))
            if os.path.exists(mask_path):
                mask = nib.load(mask_path).get_fdata()
                mask_ready = True
            else:
                print(
                    f'Tried to use mask but did not find {mask_path}. Will evaluate without mask.')
                mask_ready = False

        # iterate over designated evaluation metrics
        for _eval in data['evaluation_methods']:
            _name = _eval['name']
            # mean is one value, detailed is list
            # SDlogJ
            if 'sdlogj' == _eval['metric']:
                jac_det = (jacobian_determinant(disp_field[np.newaxis, :, :, :, :].transpose(
                    (0, 4, 1, 2, 3))) + 3).clip(0.000000001, 1000000000)
                log_jac_det = np.log(jac_det)
                if use_mask and mask_ready:
                    single_value = np.ma.MaskedArray(
                        log_jac_det, 1-mask[2:-2, 2:-2, 2:-2]).std()
                else:
                    single_value = log_jac_det.std()
                num_foldings = (jac_det <= 0).astype(float).sum()

                case_results[_name] = {
                    'mean': single_value, 'detailed': single_value}
                case_results['num_foldings'] = {
                    'mean': num_foldings, 'detailed': num_foldings}
            
            if 'ndv' == _eval['metric']:
                
                mask = nib.load(os.path.join(GT_PATH, pair['fixed'])).get_fdata()[1:-1, 1:-1, 1:-1]
                mask = mask > 0
                if disp_field.shape[0] != 3:
                    disp_field_ = disp_field.transpose(3, 0, 1, 2)
                else:
                    disp_field_ = np.copy(disp_field)
                trans_ = disp_field_ + dd.get_identity_grid(disp_field_)
                jac_dets = dd.calc_jac_dets(trans_)
                non_diff_voxels, non_diff_tetrahedra, non_diff_volume, non_diff_volume_map = dd.calc_measurements(jac_dets, mask)
                total_voxels = np.sum(mask)
                jac_det_vol = non_diff_volume / total_voxels * 100

                case_results[_name] = {
                    'mean': jac_det_vol, 'detailed': jac_det_vol}

            # DSC
            if 'dice' == _eval['metric']:
                labels = _eval['labels']
                mean, detailed = compute_dice(
                    fixed_seg, moving_seg, warped_seg, labels)
                case_results[_name] = {'mean': mean, 'detailed': detailed}
                print('case dice {:.4f}'.format(mean))
            # HD95
            if 'hd95' == _eval['metric']:
                labels = _eval['labels']
                mean, detailed = compute_hd95(
                    fixed_seg, moving_seg, warped_seg, labels)
                case_results[_name] = {'mean': mean, 'detailed': detailed}

            # TRE
            if 'tre' == _eval['metric']:
                destination = _eval['dest']
                ## corrfield correspondences are calculated for corresponding images
                ## therefore, if modalities are different, the keypoint paths have to be changed
                ## if same modalities : keypointsTr / keypointsTs
                ## if different modalities: keypoints01Tr / keypoints02Tr 

                if destination == 'keypoints' and not (fix_modality == mov_modality or (fix_modality == '0000' and mov_modality == '0001')):
                    modality_suffix = sorted([int(fix_modality), int(mov_modality)])
                    modality_suffix = str(modality_suffix[0]) + str(modality_suffix[1])
                    lms_fix_path = os.path.join(GT_PATH, pair['fixed'].replace(
                    'images', destination+modality_suffix))
                    lms_mov_path = os.path.join(GT_PATH, pair['moving'].replace(
                    'images', destination+modality_suffix))
                else:
                    lms_fix_path = os.path.join(GT_PATH, pair['fixed'].replace(
                        'images', destination))
                    lms_mov_path = os.path.join(GT_PATH, pair['moving'].replace(
                        'images', destination))
                    
                fix_lms = nib.load(lms_fix_path).get_fdata()
                mov_lms = nib.load(lms_mov_path).get_fdata()
                D, H, W = fix_lms.shape
                identity = np.meshgrid(np.arange(D), np.arange(H), np.arange(W), indexing='ij')
                warped_mov_lms = map_coordinates(mov_lms, identity + disp_field.transpose(3, 0, 1, 2), order=0)
                tre = calc_TRE(warped_mov_lms, fix_lms)
                print(('landmark error (vox): after {}'.format(tre)))
                mean = tre.mean()
                detailed = tre.tolist()
                case_results[_name] = {'mean': mean, 'detailed': detailed}

        cases_results[f'{fix_subject}_{fix_modality}<--{mov_subject}_{mov_modality}'] = case_results
        if verbose:
            print(
                f"case_results [{idx}] [{fix_subject}_{fix_modality}<--{mov_subject}_{mov_modality}']:")
            for k, v in case_results.items():
                print(f"\t{k: <{20}}: {v['mean']:.5f}")
    return cases_results, name

def to_json(cases_results1, cases_results2, cases_results3, cases_results4, OUTPUT_PATH, name):
    
    # aggregate all cases
    cases_results = {**cases_results1, **cases_results2, **cases_results3, **cases_results4}
    aggregated_results = {}
    metrics = []
    for item in list(cases_results.values()):
        metric = item.keys()
        metrics += list(metric)
    metrics = sorted(list(set(metrics)))
    for metric in metrics:
        # calculate mean of all cases
        all_means_metric = []
        for k in cases_results.keys():
            try:
                val = cases_results[k][metric]['mean']
            except Exception:
                continue
            all_means_metric.append(val)
        all_means_metric = np.array(all_means_metric)
        if metric == 'TRE_lm':
            robustness = np.quantile(all_means_metric, .7)
        else:
            robustness = np.quantile(all_means_metric, .3)
        aggregated_results[metric] = {'mean': all_means_metric.mean(),
                                      'std': all_means_metric.std(),
                                      '30': robustness}
    
    metric = 'DSC'
    # aggregate all In-Domain cases    
    cases_ID_results = {**cases_results2,}
    all_ID_metric = []
    for k in cases_ID_results.keys():
        try:
            val = cases_ID_results[k][metric]['mean']
        except Exception:
            continue
        all_ID_metric.append(val)
    all_ID_metric = np.array(all_ID_metric)
    aggregated_results['ID_dice'] = {'mean': all_ID_metric.mean(),
                                    'std': all_ID_metric.std(),
                                    '30': np.quantile(all_ID_metric, .3)}
    
    # aggregate all Out-Of-Domain cases
    cases_OOD_results = {**cases_results3,}
    all_OOD_metric = []
    for k in cases_OOD_results.keys():
        try:
            val = cases_OOD_results[k][metric]['mean']
        except Exception:
            continue
        all_OOD_metric.append(val)
    all_OOD_metric = np.array(all_OOD_metric)
    aggregated_results['OOD_dice'] = {'mean': all_OOD_metric.mean(),
                                    'std': all_OOD_metric.std(),
                                    '30': np.quantile(all_OOD_metric, .3)}
    
    # aggregate all Multi-Modal cases
    cases_MM_results = {**cases_results4,}
    all_MM_metric = []
    for k in cases_MM_results.keys():
        try:
            val = cases_MM_results[k][metric]['mean']
        except Exception:
            continue
        all_MM_metric.append(val)
    all_MM_metric = np.array(all_MM_metric)
    aggregated_results['MM_dice'] = {'mean': all_MM_metric.mean(),
                                    'std': all_MM_metric.std(),
                                    '30': np.quantile(all_MM_metric, .3)}
        

    with open(os.path.join(OUTPUT_PATH), 'w', encoding='utf-8') as f:
        json.dump(OrderedDict({'name': name,
                   'aggregates': aggregated_results,
                   'cases': cases_results,
                   'eval_version': '3.0'}), f, indent=4, allow_nan=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='L2R Evaluation script\n'
                                     'Docker PATHS:\n'
                                     'DEFAULT_INPUT_PATH = Path("/input/")\n'
                                     'DEFAULT_GROUND_TRUTH_PATH = Path("/opt/evaluation/ground-truth/")\n'
                                     'DEFAULT_EVALUATION_OUTPUT_FILE_PATH = Path("/output/metrics.json")')
    parser.add_argument("-i", "--input", dest="input_path",
                        help="path to deformation_field", default="test")
    parser.add_argument("-d", "--data", dest="gt_path",
                        help="path to data", default="ground-truth")
    parser.add_argument("-o", "--output", dest="output_path",
                        help="path to write results(e.g. 'results/metrics.json')", default="metrics.json")
    parser.add_argument("-l1", "--landmark_config", dest="landmark_config",
                        help="path to the first config json-File (e.g. 'evaluation_config.json')", default='ground-truth/evaluation_config.json')
    parser.add_argument("-s1", "--seg_config1", dest="segmentation_config_1",
                        help="path to the second config json-File (e.g. 'evaluation_config.json')", default='ground-truth/evaluation_config.json')
    parser.add_argument("-s2", "--seg_config2", dest="segmentation_config_2",
                        help="path to the second config json-File (e.g. 'evaluation_config.json')", default='ground-truth/evaluation_config.json')
    parser.add_argument("-s3", "--seg_config3", dest="segmentation_config_3",
                        help="path to the second config json-File (e.g. 'evaluation_config.json')", default='ground-truth/evaluation_config.json')
    parser.add_argument("-v", "--verbose", dest="verbose",
                        action='store_true', default=False)
    args = parser.parse_args()
    # In-Domain Landmark evaluation
    cases_results1, name = evaluate_L2R(args.input_path, args.gt_path, args.output_path,
                 args.landmark_config, args.verbose)
    # In-Domain Segmentation evaluation
    cases_results2, name = evaluate_L2R(args.input_path, args.gt_path, args.output_path,
                 args.segmentation_config_1, args.verbose)
    # Out-Of-Domain Segmentation evaluation
    cases_results3, name = evaluate_L2R(args.input_path, args.gt_path, args.output_path,
                 args.segmentation_config_2, args.verbose)
    # Multi-Modal Segmentation evaluation
    cases_results4, name = evaluate_L2R(args.input_path, args.gt_path, args.output_path,
                 args.segmentation_config_3, args.verbose)
    to_json(cases_results1, cases_results2, cases_results3, cases_results4, args.output_path, name)
