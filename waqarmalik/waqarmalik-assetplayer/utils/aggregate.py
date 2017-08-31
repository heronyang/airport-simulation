#!/opt/local/bin/python
import os
import sys
import fnmatch


def aggregate(out_dir, pattern, output_file):
    """Aggregate *.out files matching given pattern into one output file
    :param out_dir: directory with the *.out files
    :param pattern: pattern of file to be found
    :param output_file: name of file with all other files aggregated (absolute path required).

    The program is used to aggregate all multiple simulation outputs (files generate dby analyze.py) and aggregate them
    into one mega output file. Extensive analysis is then carried out on this file, and comparative study can be done.
    """
    out_files = fnmatch.filter(os.listdir(out_dir), pattern)
    if len(out_files) == 0:
        raise ValueError('No {} files found in {}'.format(pattern, out_dir))
    with open(output_file, 'w') as out:
        header = False
        for file in out_files:
            print('Processing {}'.format(file))
            with open(os.path.join(out_dir, file), 'r') as fin:
                line = fin.readline()
                if not header:
                    out.write(line)
                    header = True
                for line in fin:
                    out.write(line)


def main():
    """Usage: ./aggregate.py --pattern=<regex_out> --out=<out_file>

    pattern: (required) pattern to be matched in relative folder (e.g. ../data_track/H1*.out)
    out: name of file where output will be aggregated
    """
    out_dir = None
    pattern = None
    out_file = 'wam.out'

    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'pattern':
            out_dir = os.path.dirname(os.path.realpath(param[1]))
            pattern = os.path.basename(param[1])
        elif param[0].lower() == 'out':
            out_file = param[1]
        elif param[0].lower() == 'help':
            print(main.__doc__)
            sys.exit(1)
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            sys.exit(1)

    if not pattern:
        print(main.__doc__)
        sys.exit(1)

    if not os.path.isdir(out_dir):
        raise ValueError('{} is not a directory'.format(sys.argv[1]))

    aggregate(out_dir, pattern, out_file)


if __name__ == '__main__':
    main()
