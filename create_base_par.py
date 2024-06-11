#! /usr/bin/env python3

import argparse
import json
import re

regex_expr: str = r"g_nl_trig_map\[([0-9]+)\]\[([0-9]+)\]\[([0-9]+)\] = ([0-9]+);$"


def get_bar_id(plane_num: int, bar_num: int):
    return plane_num * 50 + bar_num + 1


def to_object(line: str):
    res = re.search(regex_expr, line)
    if res is not None:
        bar_id: int = get_bar_id(int(res.group(1)), int(res.group(3)))
        trig_id: int = int(res.group(4)) + 1
        return {"barID": bar_id, "side": int(res.group(2)), "trigID": trig_id}
    return None


def construct_json_object(obj, objs):
    bar_id = obj["barID"]
    trig_id_0 = obj["trigID"]
    other = next(x for x in objs if x is not None and x["barID"] == bar_id and x["side"] == 1)
    trig_id_1 = other["trigID"]
    return {"barID": bar_id, "trigID_left": trig_id_0, "trigID_right": trig_id_1}


def to_json_object(objs):
    return [construct_json_object(obj, objs) for obj in objs if obj is not None and obj["side"] == 0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="trigMapID json converter",
        description="Convert trigMapID from hh file to json file",
        epilog="If any issue occurs, please report it to the R3BRoot github webpage.",
    )
    parser.add_argument(
        "-i",
        "--input-file",
        required=False,
        help="specify the full path of input trig .hh file",
    )
    parser.add_argument(
        "--expIDs",
        required=True,
        help="specify the experimental IDs (semicolon separated)",
    )
    parser.add_argument(
        "--np",
        required=True,
        help="specify the number of planes",
    )
    parser.add_argument(
        "--offspill-tpat",
        required=True,
        help="specify neuland offspill tpat position",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        help="specify the full path of output json file",
    )
    args = parser.parse_args()

    input_filename: str = args.input_file
    output_fileanme: str = args.output_file
    exp_ids: str = args.expIDs
    offspill_pos: int = int(args.offspill_tpat)
    num_of_plane: int = int(args.np)

    mapping_objs = {}
    json_obj = {}
    if input_filename != None:
        with open(input_filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
            objects = [to_object(x) for x in lines]
            mapping_objs = to_json_object(objects)
        mapping_objs.sort(key=lambda x: x["barID"])
    else:
        print("input trig file is empty. No trig info is generated!");

    json_obj = {
        "expIDs": exp_ids,
        "detector": "neuland",
        "num_of_planes": num_of_plane,
        "offspill": offspill_pos,
        "trig_mapping": mapping_objs,
    }
    with open(output_fileanme, "w", encoding="utf-8") as file:
        json.dump(json_obj, fp=file, indent=2)
