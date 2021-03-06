# bokeh is imported and unused as a quick way to check for directory bokeh/bokeh/static/js
# which is required for many (but not all) examples to run properly.
import bokeh
import glob
import os
from six.moves import input
import sys
import time


# TODO: --no-log option
#       --test-all option (run through tests on every file in a given directory, rather than a small subset)
#           - This is currently the default behavior
#       --clean option (remove .html files created by running examples)

directories = {
    'file'    : 'plotting/file',
    'notebook': 'plotting/notebook',
    'server'  : 'plotting/server',
    'ggplot'  : 'ggplot',
    'glyphs'  : 'glyphs',
    'mpl'     : 'mpl',
    'pandas'  : 'pandas',
    'seaborn' : 'seaborn'
}


def tester(TestingGround, HomeDir):
    """
    Collect and run all .py or .ipynb files in an examples directory, ignoring __init__.py
    User input is collected to determine a properly or improperly displayed page

    """

    os.chdir(TestingGround)

    TestFiles = [
        fileName for fileName in os.listdir('.')
        if fileName.endswith(('.py', '.ipynb')) and fileName != '__init__.py'
    ]

    Log = []

    for fileName in TestFiles:
        try:
            print("\nOpening %s\n" % fileName)
            runner(fileName)

            TestStatus = input("Did the plot(s) in %s display correctly? (y/n) " % fileName)
            while not TestStatus.startswith(('y', 'n')):
                print()
                TestStatus = input("Unexpected answer. Please type y or n. ")
            if TestStatus.startswith('n'):
                ErrorReport = input("Please describe the problem: ")
                Log.append("\n\n%s: \n %s" % (fileName, ErrorReport))
        except KeyboardInterrupt:
            break

    cleaner()
    os.chdir(HomeDir)

    if Log:
        logger(Log)


def runner(someFile):
    """Determines how to open a file depending
    on whether it is a .py or a .ipynb file
    """

    if someFile.endswith('.py'):
        command = "python"
    elif someFile.endswith('.ipynb'):
        command = "ipython notebook"

    os.system("%s %s" % (command, someFile))


def cleaner():
    """
    Remove all .html files created by running each of these python files.
    """

    dustbin = glob.glob('*.html')
    for dust in dustbin:
        os.remove(dust)


def logger(ErrorArray):
    """
    Log errors by appending to a log.txt file.
    """

    with open(logfile, 'a') as f:
        print()
        print("\nWriting error log to %s" % logfile)
        f.write("%s\n" % base_dir)
        for error in ErrorArray:
            f.write("%s\n" % error)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in directories:
        target = sys.argv[1]

        if sys.argv[1] == 'server':
            print("Server examples require bokeh-server to run. Make sure you've typed 'bokeh-server' in another terminal tab.")
            time.sleep(5)

        logfile = "%sExamplesTestlog.txt" % target
        if os.path.exists(logfile):
            os.remove(logfile)

        base_dir = os.getcwd()
        test_dir = os.path.join(base_dir, directories[target])
        tester(test_dir, base_dir)
    else:
        # # This is kept necessarily explicit so that you don't
        # accidentally provide a directory that has .html files
        # you don't want to have deleted.
        print("Please choose an examples directory to test in ('python interactiveTester.py <plotting/file>")
        sys.exit(1)
