import os
import glob
import pandas as pd
from pytrends.request import TrendReq
from time import sleep

# find workaround for rate limit

# separate function to confirm if topic available for query and extract code

# compatibility for mac & windows


STATES =    ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 
            'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 
            'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 
            'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR',
            'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 
            'WI', 'WY']


def makeName(keyword):
    words = keyword.split(' ')
    name = ''
    for word in words:
        name = name + word

    return name


def makeDirs(dir_path, name):
    state_list = STATES

    try: os.mkdir(dir_path + '/' + name)  
    except: pass

    try: os.mkdir(dir_path + '/' + name + '/Keyword')  
    except: pass
        
    try: os.mkdir(dir_path + '/' + name + '/Keyword' + '/State')  
    except: state_list = findLastState(dir_path, name)

    try: os.mkdir(dir_path + '/' + name + '/Keyword' + '/DMA')  
    except: pass

    return state_list


def findLastState(dir_path, name):
    files = os.listdir(dir_path + '/' + name + '/Keyword/State')
    files.sort()

    last_idx = STATES.index(files[-1].split(".")[0])
    last_states = STATES[last_idx:]
    print(last_states)

    return last_states


def makeDate(date):
    times = date.split('/')
    new_date = times[2] + '-' + times[0] + '-' + times[1]

    return new_date
    

def get_input_date(when):
    date = input("Please enter {w} date in MM/DD/YYYY format: ".format(w = when))
    print("{w} date is: ".format(w = when.capitalize()), date)
    confirm = input("Press y to confirm, any other key to go back: ")
    while confirm != "y":
        date = input("Please re-enter {w} date in MM/DD/YYYY format: ".format(w = when))
        confirm = input("Press y to confirm, any other key to go back: ")
    print("\n")
    format_date = makeDate(date.strip())

    return format_date


def topic_or_keyword():
    t_or_k = input("Search by topic (enter t) or by keyword (enter k)? ")
    while t_or_k != "t" or t_or_k != "k":
        print("Error: input was not t for topic or k for keyword")
        t_or_k = input("Search by topic (enter t) or by keyword (enter k)? ")
    print("\n")

    return t_or_k


def get_keyword_input():
    keyword = input("Please enter search query: ")
    print("Query is: ", keyword)
    confirm = input("Press y to confirm, any other key to go back: ")
    while confirm != "y":
        keyword = input("Please re-enter search query: ")
        confirm = input("Press y to confirm, any other key to go back: ")
    print("\n")
    name = makeName(keyword)

    return keyword, name


def get_all_inputs():
    print("This is the Google Trend Scraper! :)")
    print("I take your query, find the data, and store the csv neatly for you. \n")

    print("I need to know the date range - start to end - to set for the search.")
    start_date = get_input_date("start")
    end_date = get_input_date("end")
    timeframe = str(start_date + " " + end_date)

    print("\nNow I need to know what to search for.")
    keyword, name = get_keyword_input()

    return timeframe, keyword, name


def makeGoogleReq(keyword, loc, tf):
    pytrend = TrendReq(retries=5, backoff_factor=0.5)

    if loc == 'PR' or loc == 'US': 
        pytrend.build_payload(kw_list=[keyword], geo=loc, timeframe=tf)
    else:
        pytrend.build_payload(kw_list=[keyword], geo='US-'+loc, timeframe=tf)
    
    return pytrend


def dfCleaner(df, loc, metro):
    try: df.pop('isPartial')
    except: pass

    isData = True
    log = ''

    if len(df.columns) == 0:
        print("     Can't get data for " + loc)
        isData = False
        log = loc
   
    else:
        print("     Found data for " + loc)
        
        if metro != -1:
            df["State"] = metro[-2:]
            df["DMA"] = metro[:-2]
            df["Full"] = metro
        else:
            df["State"] = loc
    
    return df, isData, log


def saveCSV(df, dir_path, name, loc, isState):
    if isState:
        if len(df.columns) != 0: 
            df.to_csv(os.path.join(dir_path + '/' + name + '/Keyword/State/', "{key}.csv".format(key=loc)))
    else:
        if len(df.columns) != 0: 
            df.to_csv(os.path.join(dir_path + '/' + name + '/Keyword/DMA/', "{key}.csv".format(key=loc)))

    return


def makeMetrolist(df):
    metros = df.loc[:,'geoCode']
    
    names = []
    for idx in df.index:
        names.append(idx)
    
    metrolist = []
    for m in range(len(metros)-1):
        metrolist.append([names[m], metros[m]])

    return metrolist


def getMetros(keyword, loc, tf):   
    pytrend = makeGoogleReq(keyword, loc, tf)

    df = pytrend.interest_by_region("DMA", inc_geo_code=True)

    metrolist = makeMetrolist(df)

    return metrolist


def get_suggestions(keyword, tf):
    pytrend = makeGoogleReq(keyword, 'US', tf)
    suggestions = pytrend.suggestions(keyword)
    print(suggestions)

    return suggestions


def suggestions(keyword, tf):
    suggests = get_suggestions(keyword, tf)

    if suggests[0]['title'].lower() == keyword:
        return suggests[0]['mid']
    
    return -1


def stateReq(keyword, loc, tf, dir_path, name):
    print("\nLooking at ", loc)
    pytrend = makeGoogleReq(keyword, loc, tf)

    df = pytrend.interest_over_time()

    df_clean, isData, log = dfCleaner(df, loc, -1)

    saveCSV(df_clean, dir_path, name, loc, True)

    if isData: return log
    else: return


def DMAReq(keyword, state, m, tf, dir_path, name):
    loc = state + '-' + m[1]
    print("Trying ", loc)
    pytrend = makeGoogleReq(keyword, loc, tf)

    df = pytrend.interest_over_time()

    df_clean, isData, log = dfCleaner(df, loc, m[0])

    saveCSV(df_clean, dir_path, name, m[0], False)

    if isData: return log
    else: return


def saveLog(logfile, dir_path, name):
    with open(dir_path + '/' + name + '/Keyword/output.txt', "w") as f:
        for line in logfile:
            if line != None:
                f.write(line + '\n')
    
    return

def megaCSV(path):
    all_csvs = glob.glob(os.path.join(path, '*.csv'))
    mega = pd.concat(map(pd.read_csv, all_csvs), ignore_index=True)
    mega.to_csv(os.path.join(path, "mega.csv"))

    return 


def done(dir_path, name):
    print("Done!")
    print("All data saved to: ", dir_path, "/", name)
    sleep(5)
    
    return

