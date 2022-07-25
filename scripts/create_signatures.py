from types import SimpleNamespace

import matplotlib.pyplot as plt
import pandas as pd

from data_loader.data_loader import DataLoader
from preparator.preparator import Preparator
from utils.plot_utils import display_images
from utils.utils import get_logger, load_data, save_data

logger = get_logger(name="create_signatures")

def parse_data(images, parsed_data_out, cfg):
    # create emply simple namespace from columns of parsed_data_out
    parsed_data = SimpleNamespace(**dict.fromkeys(parsed_data_out.columns))
    path_deliminator = cfg.preparator.labels_path_deliminator
    labels_deliminator = cfg.preparator.labels_deliminator

    for image in images:
        signature_mean = image.mean(axis=(0,1))
        indices, labels = image.filename.split(path_deliminator)[0:2]
        indices = indices.split(labels_deliminator)
        labels = labels.split(labels_deliminator)

        parsed_data.signature = signature_mean
        parsed_data.labels = labels
        parsed_data.filename = image.filename
        parsed_data.camera_name = image.camera_name

        parsed_data.image_idx = indices[0]
        parsed_data.object_idx = indices[1]

        # if slicing performed there are three indices, else two
        if len(indices) == 3:
            parsed_data.slice_idx = indices[2]

		# append paresed data to parsed_data_out
        parsed_data_out = pd.concat([parsed_data_out, pd.DataFrame.from_records([parsed_data.__dict__])])
    return parsed_data_out.reset_index(drop=True)

def parse_labels(row, ref_panel):
    object_idx = int(row.object_idx)
    if ref_panel:
        if object_idx == 0:
            return "panel"
        else:
            return row.labels[object_idx - 1]
    else:
        return row.labels[object_idx]

def main(cfg):
    data_loader = DataLoader(cfg)
    data_loader.change_dir("converted_images").load_images()

    parsed_data_out = pd.DataFrame(columns = ["image_idx", "object_idx", "slice_idx",
                                                 "labels", "signature", "filename", "camera_name"])

    images_cam1 = data_loader.images.cam1
    parsed_data_out = parse_data(images_cam1, parsed_data_out, cfg)

    if cfg.camera2 is not None:
        images_cam2 = data_loader.images.cam2
        parsed_data_out = parse_data(images_cam2, parsed_data_out, cfg)

	# check if first object represents reference panel
    ref_panel = True if cfg.preparator.reflectance_panel else False
    match_indices = cfg.preparator.match_labels_to_indices

	# if parsed labels will be matched to object_indices
    if match_indices:
        parsed_data_out["label"] = parsed_data_out.apply(lambda row: parse_labels(row, ref_panel), axis=1)

    # save parsed data
    save_data(cfg, data=parsed_data_out,
              data_file_name=f"files/data", saver="df_csv")

    data = load_data(cfg, data_file_name=f"files/data", loader="df_csv")
    pass

