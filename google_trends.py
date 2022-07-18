import os
import sys
import utils

def main():
    dir_path = os.path.dirname(sys.executable)

    timeframe, keyword, name = utils.get_all_inputs()

    states = utils.makeDirs(dir_path, name)
    
    logfile = []

    for state in states:

        log = utils.stateReq(keyword, state, timeframe, dir_path, name)
        logfile.append(log)

        if state != 'PR':
            metros = utils.getMetros(keyword, state, timeframe)

            for m in metros:
                log = utils.DMAReq(keyword, state, m, timeframe, dir_path, name) 
                logfile.append(log)
        
    utils.saveLog(logfile, dir_path, name)

    utils.done(dir_path, name)


# ask to search by topic or keyword

if __name__ == "__main__":
    main()
