import omegaconf

from utils.utils import dict_zip, equalize_dict_len, get_logger

logger = get_logger(name="checkers")


def check_value_type(dict_types, dict_values, config_name):
    for key, val_types, val in dict_zip(dict_types, dict_values):
        if isinstance(val_types, str):
            val_types = [val_types]
        flag = 0
        for val_type in val_types:
            if val_type == 'list':
                val_type = 'omegaconf.listconfig.ListConfig'
            elif val_type == 'dict':
                val_type = 'omegaconf.dictconfig.DictConfig'
            if type(val) is eval(val_type) or (val is None and val_type == "None"):
                flag += 1
        if flag == 0:
            msg = f"{key} is not of type <{val_types}> in {config_name}.yaml"
            logger.error(msg)
            raise ValueError(msg)

def check_against_base(dict_types, dict_values, config_name):
    if dict_values is None:
        return
    dict_types, dict_values = equalize_dict_len(dict_types, dict_values)
    check_value_type(dict_types, dict_values, config_name)

def check_visualiser(config):
    temp_cfg = {"images_indices": config.images_indices, "objects_indices": config.objects_indices,
                "slices_indices": config.slices_indices, "labels_names": config.labels_names}
    options = ["__include_all__", "__include_only__", "__exclude_only__"]
    for key, val in temp_cfg.items():
        if val[0] not in options:
            msg = f"{key}:{val} not supported. Available options in visualiser.yaml: {options}"
            logger.error(msg)
            raise ValueError(msg)


def check_config(config):
    if "camera2" not in config:
        config.camera2 = None
    check_against_base(config.base.camera, config.camera1, "camera1")
    check_against_base(config.base.camera, config.camera2, "camera2")
    check_against_base(config.base.data_loader, config.data_loader, "data_loader")
    check_against_base(config.base.preparator, config.preparator, "preparator")
    check_against_base(config.base.segmentator, config.segmentator, "segmentator")
    check_against_base(config.base.selector, config.selector, "selector")
    check_against_base(config.base.visualiser, config.visualiser, "visualiser")

    check_visualiser(config.visualiser)

    return config

