# import os, time, re, sys
from datetime import datetime, timezone
# from dateutil import tz
import argparse
#from pathlib import Path
import re
import json



from diff import Myers


def find_diff(str_a,str_b):
    diff_total = Myers.diff(str_a, str_b,{'compare':'array','ignorecase':True})
    # diff_records = Myers.to_records(diff_total,str_a,str_b)
    # diff_records_serializable = [ '{record}'.format(record=record) for record in diff_records ]
    # return diff_records_serializable
    # return [ {'lhs':{**record['lhs'],'get_part':None},'rhs':{**record['rhs'],'get_part':None}} for record in diff_total ]
    return diff_total



if __name__ == '__main__':
    time_start = datetime.now()
    parser = argparse.ArgumentParser(
        description="Test Diff"
    )
    # parser.add_argument(
    #     '-1',
    #     '--str_a',
    #     help='String A',
    #     required=True
    # )
    # parser.add_argument(
    #     '-2',
    #     '--str_b',
    #     help='String B',
    #     required=True
    # )
    # args = parser.parse_args()
    # str_a = None
    # if args.str_a:
    #     str_a = args.str_a
    # str_b = None
    # if args.str_b:
    #     str_b = args.str_b
    str_a = '-aaha xxy 1'
    str_b = '-aanv1 12'


    print('Diff script started at {dt}'.format(dt=time_start))

    output = find_diff(str_a,str_b)
    output = json.dumps(output,indent=2)
    report_file_name = 'test.json'
    print("Writing results...\n")
    with open(report_file_name,'w') as output_file:
        output_file.write(output)

    time_finish = datetime.now()
    print('Diff script finished at {dt} (elapsed {duration})'.format(dt=time_finish,duration=time_finish-time_start))
