#!/usr/bin/python3.10


################################################################################
#                                                                              #
#                                                                              #
#                   GNU AFFERO GENERAL PUBLIC LICENSE                          #
#                       Version 3, 19 November 2007                            #
#                                                                              #
#    This programms aims at runing anti-virus analysis.                        #
#    Copyright (C) 2022 Gavroche, Roxane                                       #
#                                                                              #
#    This program is free software: you can redistribute it and/or modify      #
#    it under the terms of the GNU Affero General Public License as published  #
#    by the Free Software Foundation, either version 3 of the License, or      #
#    (at your option) any later version.                                       #
#                                                                              #
#     This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU Affero General Public License for more details.                       #
#                                                                              #
#    You should have received a copy of the GNU Affero General Public License  #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.    #
#                                                                              #
#                                                                              #
################################################################################


import argparse
import json
import os

from pyfiglet import figlet_format as pff

from libs import defender, kaspersky, clamav
from datetime import datetime
from Asterix_libs import hash
from Asterix_libs.prints import *


################################################################################


def tests():

    warning('Software test started on [' + str(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")) + ']')

    # Test examples :
    f_path = "D:\\Pentest\\holo.rar"
    try:
        success('Hash : ' + hash.sha('Inputs/test.jpg'))
    except:
        fail('Hash failed.')
    defender.analyze(f_path)
    kaspersky.analyze(f_path)
    clamav.analyze(f_path)

    warning('Software test ended on [' + str(datetime.now().strftime("%d/%m/%Y-%H:%M:%S")) + ']')


################################################################################


def analyze(path, d, k, c):

    if not os.path.isfile(path): fail('Path is not a file path'); exit()

    info(f'Analysing {path}')

    try:
        # Run analysis
        analysis = []

        if d: analysis.append(defender.analyze(path))
        if k: analysis.append(kaspersky.analyze(path))
        if c: analysis.append(clamav.analyze(path))
    except:
        fail('Analysis failed')
        return False, False

    state = analysis.count(False)

    if state == 0 and None not in analysis :
        success('Done. No was threat detected.')
        stat = 0

    elif None in analysis:
        fail('Analysis process did not perform as expected')
        print(analysis)
        stat = 1

    elif state > 0:
        warning(f'Done. File was flaged as malicious by {state}/{len(analysis)} AV Solution vendors')
        stat = 2

    return stat, analysis


################################################################################


if __name__ == '__main__':

    # Argument parser creation
    parser = argparse.ArgumentParser(description='PYthon Wrapper for Anti-Virus Analysis. Copyright (C) 2022 Gavroche, Roxane.')

    parser.add_argument('--test', help="Run software test", action="store_true")
    parser.add_argument('-f', metavar='file', type=str, help="Target file path")
    parser.add_argument('-b', help="Disable banner", action="store_true")
    parser.add_argument('-a', help="Full AV selection", action="store_true", default=False)
    parser.add_argument('-d', help="Defender AV Analysis", action='store_const', const=True, default=False)
    parser.add_argument('-k', help="Kaspersky AV Analysis", action='store_const', const=True, default=False)
    parser.add_argument('-c', help="ClamAV AV Analysis", action='store_const', const=True, default=False)

    parser.add_argument('-r', help="Source file removal flag", action="store_true")

    args=parser.parse_args()

    if args.b is not True: print(pff("PyWAVA"))

    if args.test: tests(); exit()

    d = args.d
    k = args.k
    c = args.c

    if  args.a: d, k, c = True, True, True

    if not d | k | c: fail('No AV solution was selected.'); exit()

    # Retrieve file path and type
    f_path = args.f

    if f_path is None: fail('No file path specified'); exit()

    stat, analysis = analyze(f_path, d, k, c)

    res = []
    for i in range(3):
        if i < len(analysis):
            res.append(analysis[i])
        else:
            res.append(None)

    try:

        # Save operation results
        with open("scan_results.json", "r+") as results:

            # Read existing results
            f_data = json.load(results)

            # Create JSON dump individual results
            ind_result = {
                "Date": datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
                "PATH": f_path,
                "FILESTat": stat,
                "DEFENDER": res[0],
                "KASPERSKY": res[1],
                "CLAMAV": res[2],
                "HASH": hash.sha(f_path),
            }

            # Append individual data
            f_data["ind_results"].append(ind_result)

            results.seek(0)

            js = json.dumps(f_data, indent=4)

            # Write to result file
            results.write(js)

    except:
        fail("Failed to write scan results. The file will be considered as not sanitized.")

    try:
        # Remove source file if required
        if args.r : os.remove(f_path)
    except:
        fail('Failed to remove source file. This is not fatal.')
