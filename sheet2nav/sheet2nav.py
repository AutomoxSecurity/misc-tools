import argparse
import json
import pandas as pd
from lib2to3.pytree import convert
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth', type=str,
                        help='Provide a path to JSON file containing Google API auth', required=True)
    parser.add_argument('-s', '--sheet', type=str,
                        help='Provide the name of the Sheet', required=True)
    parser.add_argument('-os', '--platform', type=str,
                        help='Provide the OS platform as a list', nargs='+', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='Provide an output path for Navigator JSON', default="navigator.json")

    return parser


def build_navigator(args):
    navigator = {
        "name": args.sheet,
        "versions": {
            "attack": "11",
            "navigator": "4.6.1",
            "layer": "4.3"
        },
        "domain": "enterprise-attack",
        "description": "",
        "filters": {
            "platforms": args.platform
        },
        "sorting": 0,
        "layout": {
            "layout": "side",
            "aggregateFunction": "average",
            "showID": False,
            "showName": True,
            "showAggregateScores": False,
            "countUnscored": False
        },
        "hideDisabled": False,
        "techniques": [],

        "gradient": {
            "colors": [
                "#ff6666ff",
                "#ffe766ff",
                "#8ec843ff"
            ],
            "minValue": 0,
            "maxValue": 100
        },
        "legendItems": [],
        "metadata": [],
        "links": [],
        "showTacticRowBackground": False,
        "tacticRowBackground": "#dddddd",
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False
    }
    return navigator


def convert_technique(technique):
    technique_stage = {}
    if technique.get('STID'):
        technique_stage['subtechniqueID'] = technique.get('STID')
    if technique.get('TID'):
        technique_stage['techniqueID'] = technique.get('TID')

    technique_stage['enabled'] = True
    technique_stage['comment'] = technique.get('Notes')
    technique_stage['showSubtechniques'] = False

    return technique_stage


def consolidate_techniques(orig_technique, techniques):
    for technique in techniques:
        if orig_technique['techniqueID'] == technique['techniqueID'] and orig_technique['comment'] != technique['comment']:
            orig_technique['comment'] += "\n\n{}".format(technique['comment'])

    return orig_technique


def main():
    parser = get_parser()
    args = parser.parse_args()

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        args.auth, scope)
    client = gspread.authorize(creds)
    sheet = client.open(args.sheet)
    sheet_instance = sheet.get_worksheet(0)
    all_techniques_from_gsheet = sheet_instance.get_all_records()
    all_techniques = []

    for technique in all_techniques_from_gsheet:
        converted_technique = convert_technique(technique)
        all_techniques.append(converted_technique)

    df = pd.DataFrame(all_techniques)
    df['TIDs'] = df.groupby('techniqueID')['techniqueID'].transform('count')
    df['STIDs'] = df.groupby('subtechniqueID')[
        'subtechniqueID'].transform('count')
    all_techniques = json.loads(df.to_json(orient='records'))

    color_choice = {
        1: "#e6c8ff",
        2: "#bc99d9",
        3: "#926db5",
        4: "#6a4391",
        5: "#41196f"
    }

    for index, value in enumerate(all_techniques):
        tid_count = all_techniques[index]['TIDs']
        stid_count = all_techniques[index]['STIDs']
        if tid_count >= 5:
            color = color_choice[5]
        else:
            color = color_choice[tid_count]

        all_techniques[index]['color'] = color

    stid_techniques = []
    for technique in all_techniques:
        if technique.get('subtechniqueID'):
            stid_technique = technique.copy()
            stid_count = stid_technique['STIDs']
            stid_technique['techniqueID'] = technique['subtechniqueID']
            if stid_count >= 5:
                color = color_choice[5]
            else:
                color = color_choice[stid_count]
            stid_technique['color'] = color
            stid_techniques.append(stid_technique)
    for stid in stid_techniques:
        all_techniques.append(stid)

    completed_techniques = []
    consolidated_techniques = []
    for technique in all_techniques:
        if technique['techniqueID'] not in completed_techniques:
            consolidated_techniques.append(
                consolidate_techniques(technique, all_techniques))
        completed_techniques.append(technique['techniqueID'])

    navigator_meta = build_navigator(args)
    navigator_meta['techniques'] = consolidated_techniques

    with open(args.output, 'w') as outfile:
        json.dump(navigator_meta, outfile)

    print("[!] Navigate to https://mitre-attack.github.io/attack-navigator and import this file: {}".format(args.output))


if __name__ == '__main__':
    main()
