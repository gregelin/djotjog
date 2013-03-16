"""
Benford's law in Python.
"""
import re

def heuristic_to_html(string = None, description = None, ip = None):
    """ like 'heuristic' function but returns HTML page instead of just the sparkline part """
    if string != None:
        if type(string) not in (str,unicode):
            try:
                string = str(string)
            except:
                return []
        import word_methods as wm
        data = wm.latin1_to_ascii(string)
        if len(data) < 50: # too short!
            return []
    else:
        return []

    import logging
    LOG_FILENAME = 'error.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(str(data)[:100])
    
    results = benford(data) #returns a dictionary
    if results.get('benford') == []:
        return "<HTML><body>Error: No numbers detected, go back and try again.</body></html>"
    score = percent_estimated(data)
    bias = percent_keypad_bias(data)
    dates = percent_date_like(data)
    logging.debug(str(dates))
    repeats = percent_repeated_numbers(data) # a dictionary of data
    #print bias,"% of numbers have keypad-biased patterns."
    #print score,"% of numbers could be estimates or rounded off."
    import json    
    results['estimated']=score
    results['keypad bias']=bias
    results['dates']=dates
    results.update(repeats) #adds 'repeated twice', 'repeated 5x', 'uniques', 'top five'--list of (X,freqs) tuples            
    sparkline = [x['actual'] for x in results.get('benford')]
    spark_ref = [x['ideal'] for x in results.get('benford')]    
    logging.debug( str(sparkline+[0]+spark_ref) )
    
    if len(sparkline) > 0 and len(spark_ref) > 0:
        try:
            deviation = round( sum( [abs(sparkline[i]-spark_ref[i]) for i in range(len(sparkline))] ) ,2)
        except:
            deviation = "Unknown"
            logging.exception( '' )
    results['deviation']=deviation
        
    #SAVE copy in MySQL
    if 'benford' in results:
        try:
            msg = save_to_mysql(results, data, description, ip)
            logging.debug( str(msg) )
        except:
            logging.exception( 'mysql FAIL ' )
    
    #HTML part
    html = ("""
    <html>
    <head>
    <title>Djotjog heuristic financial auditing</title>
      <style type="text/css">
        @import url("http://djotjog.com/default.css");
        .chart div {
           font: 14px sans-serif;
           background-color: red;
           text-align: right;
           padding: 5px;
           margin: 2px;
           color: white;
         }


      </style>      
    <script type="text/javascript" src="/jquery-1.8.0.min.js"></script>
    <script type="text/javascript" src="/jquery.sparkline.min.js"></script>
    </head>
    <body>
    <div class="container">    
    <h2>Compare your uploaded data (left) against an ideal distribution (right) </h2>

    <p>
    Any data that involves counting real objects will tend toward the pattern on the right.
    If your data (left) looks random, or flat, then this data does not contain realistic accounting
    records.
    <br>
    <div class="box" >
        <span STYLE="font-size: x-large;" class="benford">Calculating...</span>
        <br><SPAN STYLE="font-size: x-large;"> 1....2....3....4....5....6....7....8....9.......(Benford leading digit test)</span>
    </div>
    <br><h2> Summary</h2>
    <br><SPAN STYLE="font-size: large;">
    Total numbers found in your document: 
    """+str(results.get('total numbers') or '0')+"""</span>
    <br><SPAN STYLE="font-size: large;">
    Total deviation from the ideal first digit distribution: 
    """+str(results.get('deviation') or "No data")+"""</span><SPAN STYLE="font-size: x-small;"> (ZERO is ideal. More than 20% is suspicious, if your document has at least 500 numbers.)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent estimated numbers: 
    """+str(results.get('estimated') or "No data")+"""% </span><SPAN STYLE="font-size: x-small;"> (% of numbers could be estimates or rounded off.)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent keypad-biased numbers: 
    """+str(results.get('keypad bias') or "No data")+"""% </span><SPAN STYLE="font-size: x-small;"> (i.e. 2-5-8-0 are arranged vertical on phones and keypads and get overused when fraudsters get lazy. </span>
    <br><SPAN STYLE="font-size: large;">
    Percent duplicate numbers:
    """+str(results.get('repeated twice') or "0")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Percent numbers repeated 5 or more times:
    """+str(results.get('repeated 5x') or "0")+"""% </span><SPAN STYLE="font-size: x-small;">(really lazy fraudsters just cut-n-paste data)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent unique numbers:
    """+str(results.get('uniques') or "No data")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Percent of numbers that look like dates:
    """+str(results.get('dates') or "No data")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Top five numbers (and # of times each appears):<br>
    """+str(results.get('top five') or "No data")[1:-1]+""" </span><SPAN STYLE="font-size: x-small;"> (if large, obscure numbers appear frequently, this is a sign of fraud!)</span>
    </p>
    <script type="text/javascript"> 
    function sparks_benford(){
            $(".benford").sparkline("""+str(sparkline+[0]+spark_ref)+"""
            , {type:'bar', colorMap:{
                ':1':'Pink',
                '0':'White',
                '1:':'LightSteelBlue'
                },
                 height: 150,
                 barWidth: 55,
                 barSpacing: 1
                 });	
                }

    $(window).bind("load", function() {
        sparks_benford();
        console.log("""+str(sparkline+[0]+spark_ref)+""");
        console.log("""+str(results)+""");
    });
    
    /* used to auto-select the text so it can be deleted when you paste in the textarea*/
    window.onload = function(){
      var text_input = document.getElementById ('textarea_1_1');
      text_input.focus ();
      text_input.select ();
    }
    </script>


    <!-- need to use jquery to POST all data directly to cherrypy and avoid the max-size problem -->
    <div class="box-white" size="0.8em">
        <form id="pasted" action="/cp2/benford/" method="post">     
         <textarea id="textarea_1_1" name="textarea_1_1" rows="10" cols="120" autofocus>Paste another spreadsheet!
    </textarea>         
        <br>		    
        <input id="submit" type="submit" name="submit" value="Check Again" />
        Describe your data:        
        <input type="text" name="description" id="description" size="50">
        </form>
        <br>
        Submitting a description will refine this fraud-detection algorithm by benchmarking
        your document against a group of similar documents; the more keywords you include,
        the more-precise the comparison.
    </div>
        <div class="box-blue">
            <SPAN STYLE="font-size:small;"> [For developers] API instructions:
            <br><br>
            You can [POST] your data as a string to http://djotjog.com/cp2/benford_json/
            and the result will be a json format that looks like this:
            <br>
            <br>
            """+str(results)+"""
            <br>
            </span>
        </div>
    <br></span><SPAN STYLE="font-size: x-large;">
    Enjoy! -- the djotjog team.
    </div>
        
    </body>     
    """)
    return html
   


def benford_json(string = None, description = None, ip = None):
    """ API VERSION: JSON only heuristic function """
    if string != None:
        if type(string) not in (str,unicode):
            try:
                string = str(string)
            except:
                return []
        import word_methods as wm
        data = wm.latin1_to_ascii(string)
        if len(data) < 10: # too short!
            return []
    else:
        return []

    import logging
    LOG_FILENAME = 'error.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(str(data)[:100])
    
    results = benford(data) #returns a dictionary
    if type(results) == None:
        results = {}
        return []
    score = percent_estimated(data)
    bias = percent_keypad_bias(data)
    dates = percent_date_like(data)
    repeats = percent_repeated_numbers(data) # a dictionary of data
    #print bias,"% of numbers have keypad-biased patterns."
    #print score,"% of numbers could be estimates or rounded off."
    import json    
    results['estimated']=score
    results['keypad bias']=bias
    results['dates']=dates    
    results.update(repeats) #adds 'repeated twice', 'repeated 5x', 'uniques', 'top five'--list of (X,freqs) tuples            
    sparkline = [x['actual'] for x in results.get('benford')]
    spark_ref = [x['ideal'] for x in results.get('benford')]    
    logging.debug( str(sparkline+[0]+spark_ref) )
    if len(sparkline) > 0 and len(spark_ref) > 0:
        try:
            deviation = sum( [abs(sparkline[i]-spark_ref[i]) for i in range(len(sparkline))] )
        except:
            deviation = "Unknown"
    results['deviation']=deviation
    return results


def heuristic_sparkline(string):
    results = benford(data) #returns a dictionary
    if type(results) == None:
        return []
    sparkline = [x['actual'] for x in results.get('benford')]
    spark_ref = [x['ideal'] for x in results.get('benford')]
    return sparkline+[0]+spark_ref


def benford(iterable):
    """Plot leading digit distribution in a string iterable. """
    import logging
    LOG_FILENAME = 'error.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

    # generate the ideal values (zero cannot be leading)
    from math import log10
    ideal = [log10(1 + 1.00 / d) for d in [1,2,3,4,5,6,7,8,9]] 

    # 'digits' pulls out the numbers from a string; groupby gets you a freq-histogram
    from itertools import groupby
    if type(iterable) in (str,unicode):
        first_digits = list(digits(str(iterable))) #sucks all numbers out of string
        #print "found string"
        logging.debug( str(len(first_digits))+" first digits found" )
    elif type(iterable) in (list,tuple):
        logging.debug( "not a string, trying list..." )
        first_digits = []
        for x in iterable:
            more_digits = list(digits(x))
            first_digits.extend(more_digits)
    else:
        logging.debug( "invalid data type: "+str(type(iterable)) )
        return {}

    data = [] #list of dicts test data
    II = sorted(first_digits) #reqd for groupby
    for i,(k,g) in enumerate(groupby(II)):
        G = len(list(g)) #generator kills it
        data.append({'digit':k,
                     'freq':G,
                     'actual':round(100.0*G/float(len(II)),3),
                     'ideal':round(100.0*ideal[i],3)})
        logging.debug( str(k)+' : '+str(G)+' T: '+str(G/float(len(II)))+' B: '+str(ideal[i]) )
    results = {'benford':data, 'total numbers':len(II)}
    return results

def digits(iterable):
    """Yield leading digits of number-like strings in an iterable.
    ## {{{ http://code.activestate.com/recipes/577431/ (r1)
    BASIC NUMBER MATCH
    re.compile(r'\d+(\.\d+)?([eE]\d+)?')

    ADVANCED NUMBER MATCH FROM http://stackoverflow.com/questions/5917082/regular-expression-to-match-numbers-with-or-without-commas-and-decimals-in-text
    re.compile(r'[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0')
    
    [1-9](?:\d{0,2}) #A sequence of 1-3 numerals not starting with 0
    (?:,\d{3})*      #Any number of three-digit groups, each preceded by a comma
    (?:\.\d*[1-9])?  #Optionally, a decimal point followed by any number of digits not ending in 0
    |                #OR...
    0?\.\d*[1-9]     #Only the decimal portion, optionally preceded by a 0
    |                #OR...
    0                #Zero.


    re.compile(r'^[+-]?[0-9]{1,3}'
    '(?:'
        '(?:\,[0-9]{3})*'
        '(?:.[0-9]{2})?'
    '|'
        '(?:\.[0-9]{3})*'
        '(?:\,[0-9]{2})?'
    '|'
        '[0-9]*'
        '(?:[\.\,][0-9]{2})?'
    ')$')
        
    """
    #numexp = re.compile(r'[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0')
    numexp = re.compile(r'\d[\d,]*[\.]*[\d{2}]*')
    leading = set("123456789")

    for item in iterable:
        for match in numexp.finditer(str(item)): #returns a list of groups = all numbers found
            for digit in match.group(0):
                if digit in leading:
                    yield int(digit)
                    break

def csv_to_string(filepath):
    import csv
    f = open(filepath,'rb')
    fc = csv.reader(f)
    data = [x for x in fc]
    return ' '.join([' '.join([y for y in x]) for x in data])

def percent_estimated(string):
    """ given a string, pull out all the numbers and look at ends of large 4+ digit numbers
    for 0, 00, 500, 50, 000, etc and calculate fraction that fit this pattern. """
    est = {'0':5,'5':2,
           '00':10,'50':9,
           '000':50,'500':50,
           '0000':100,'5000':80} #likiness that numbers are estimates
    estimated = 0
    numbers = get_numbers(string) #list of cleaned numbers, with decimals, but commas stripped
    for N in numbers: #list of all numbers as strings
        if N[-1] in est:
            estimated += est.get(N[-1],0)
        elif N[-2:] in est:
            estimated += est.get(N[-2:],0)
        elif N[-3:] in est:
            estimated += est.get(N[-3:],0)
        elif N[-4:] in est:
            estimated += est.get(N[-4:],0)
        else:
            estimated += 1 # okay characters
    return round(100*(estimated/(100.00* len(numbers))),2) #100* denominator - assume okay chars = 100
        
def percent_keypad_bias(string):
    """ given a string, pull out all the numbers and look at patterns within numbers
    for (111, 123, 258, 147, 369, 159, 357, 456, 789, 987, 654, 321) etc and calculate fraction that fit this pattern. """
    patterns = ('111','222','333','444','555','666','777','888','999',
                '123','321','231','213',
                '258','852', '582','825',
                '147','741','471','714',
                '369','963','693','396',
                '159','951','915','591',
                '357','753','537','735',
                '456','789','987','654')
    estimated = 0
    numbers = get_numbers(string, decimals=False) #list cleaned numbers, commas/decimals stripped
    for N in numbers: #list of all numbers as strings
        for code in patterns:
            if code in N: #string within string yields True
                estimated += 1
    # returns the ~ percent of numbers that contain suspicious patterns
    return round(100*(estimated/float(len(numbers))),2)
       
def percent_repeated_numbers(string):
    """ given a string, pull out list of numbers, loop through set of unique numbers,
    count repeats,
    RETURN
    % repeated twice,
    % repeated more than 5 times,
    count of set uniques,
    top five numbers that appear.
    uses itertools.Counter """
    numbers = get_numbers(string) #list of cleaned numbers, with decimals, but commas stripped
    from collections import Counter
    N = Counter(numbers) #instant freq_dict
    if len(N) > 0:
        uniques = len(N)
        repeat2 = len([k for k,v in N.iteritems() if v >= 2])
        repeat5 = len([k for k,v in N.iteritems() if v >= 5])
        top5 = N.most_common(5)
        repeated = {'repeated twice': round(100*repeat2/float(len(numbers)),2),
                    'repeated 5x': round(100*repeat5/float(len(numbers)),2),
                    'uniques':round(100*uniques/float(len(numbers)),2),
                    'top five':top5, # list of tuples
                    }
    else:
        repeated = {}
    return repeated

def percent_date_like(string):
    """ returns percent of numbers that resemble years 19xx and 20xx """
    numbers = get_numbers(string) #list of cleaned numbers, with decimals, but commas stripped
    years = 0
    for N in numbers:
        if len(N) == 4: #years are 4 digits long
            if re.match('19',N) or re.match('20',N): #starts with 19xx, 20xx
                years += 1
    return round(100*(years/float(len(numbers))),2)

def get_numbers(string, decimals = True):
    """ returns a list of numbers from a string. Can detect numbers with commas and decimals,
    but automatically removes the commas, and leaves decimals in final list """
    #allnum = re.compile(r'(\d+)') # whole numbers, but misses numbers with commas, decimals -- don't use!
    # n = re.compile(r'(\d[\d,]*)(\.\d{2})?') #too strict -- need to recombine two parts of number
    numexp = re.compile(r'\d[\d,]*[\.]*[\d{2}]*') #WORKS - test?! 
    #numexp = re.compile(r'[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0') #pulls out numbers
    numbers = numexp.findall(str(string))
    #strip out non-digit numbers
    numbers = [x.replace(',','') for x in numbers] #leave decimals
    if decimals == True:
        return numbers
    try:
        numbers = [str(int(float(x))) for x in numbers] #strip sub-zero parts
    except:
        import logging
        LOG_FILENAME = 'error.log'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)        
        logging.exception( 'percent estimated cannot int() the numbers' )
    # future option for rounded numbers = [str(int(round(float(x),0))) for x in numbers]
    return numbers


def get_line_items(string):
    """ uses a reference dictionary based on 400 XLS and PDF GG DD documents
    to estimate
        percent overlap with legitimate financials
            --- sum(union)/terms_in_doc (%)
            --- if all of test_doc terms are found in ref_dict, then 100% overlap.
        percent of common line items in legit financials that are present in document
            --- compare all words/phrases with score 0.50 or higher
            --- score is added for each matching term (weighted by VAL)
            --- best score is the sum of all terms > 0.85 == 61.5 best score (quotient)
        total budget (number after the word 'total' and largest number found)
    """
    import re
    from collections import Counter
    import cPickle
    import word_methods as wm

    approved_dd = open('approved_dd.pickle','rb')
    D = cPickle.load(approved_dd)
    D = {k:round(v/400.0,2) for k,v in D.items()} # 1.00 appears once per documents.
    REF = set({k:v for k,v in D.items() if v > 0.1}) # set of typical line items
    # extracting words from string into a set
    wordlist = string.split() # on whitespace
    wordlist = [x.lower() for x in wordlist] #make lowercase first
    bigram_list = [wordlist[i]+' '+wordlist[i+1] for i,x in enumerate(wordlist[:-1]) if re.match(r'^[a-zA-Z]+$',wordlist[i]) and re.match(r'^[a-zA-Z]+$',wordlist[i+1])]
    freq_dict = Counter(wordlist+bigram_list)
    freq_dict = {k:v for k,v in freq_dict.items() if k.lower() not in wm.stop_words()}
    freq_dict = {k:v for k,v in freq_dict.items() if re.match(r'^[a-zA-Z ]+$',k)} #also allows spaces
    TEST = set(freq_dict)    
    percent_overlap = round(100* len(TEST & REF)/float(len(TEST)),1)
    weighted_items = round(100* sum([D[d] for d in D if D[d] > 0.3 and d in TEST])/sum([D[d] for d in D if D[d] > 0.85]),1)
    return percent_overlap, weighted_items
 

    


def save_to_mysql(r, data, description,ip):
    """ puts the meta data into a mysql table for later analysis:
    id | date_time | IP | description | string_data | estimated | keypad_bias |
    repeat2 | repeat5 | uniques | top5 | 1s | 2s |3s ... 9s | (20 fields to fill)
    BENFORD is a required key in (r) the result dict.
    """
    #add 'total numbers', 'deviation'
    #skip id auto-increment column
    import database as db
    import MySQLdb
    descr = str(MySQLdb.escape_string(description))
    escdata = str(MySQLdb.escape_string(data))
    if r.get('top five') != None:
        escfive = str(MySQLdb.escape_string(str(r.get('top five'))[1:-1]))
    else:
        escfive = ''
    if len(escdata) < 100:
        return "MYSQL SKIPPED because data was too short"
    query = ("""INSERT INTO audit_meta
    (create_date, ip, data, description, total_numbers, deviation, estimated, keypad_bias, repeat2, repeat5,
    uniques, top5, 1s, 2s, 3s, 4s, 5s, 6s, 7s, 8s, 9s)
    VALUES
    (now(),
    '"""+str(ip)+"""',
    '"""+str(escdata)+"""',
    '"""+str(descr or 'NULL')+"""',
    '"""+str(r.get('total numbers') or 0)+"""',
    '"""+str(r.get('deviation') or 0)+"""',
    '"""+str(r.get('estimated') or 0)+"""',
    '"""+str(r.get('keypad bias') or 0)+"""',
    '"""+str(r.get('repeated twice') or 0)+"""',
    '"""+str(r.get('repeated 5x') or 0)+"""',
    '"""+str(r.get('uniques') or 0)+"""',
    '"""+str(escfive)+"""',
    '"""+str(r['benford'][0]['actual'])+"""',
    '"""+str(r['benford'][1]['actual'])+"""',
    '"""+str(r['benford'][2]['actual'])+"""',
    '"""+str(r['benford'][3]['actual'])+"""',
    '"""+str(r['benford'][4]['actual'])+"""',
    '"""+str(r['benford'][5]['actual'])+"""',
    '"""+str(r['benford'][6]['actual'])+"""',
    '"""+str(r['benford'][7]['actual'])+"""',
    '"""+str(r['benford'][8]['actual'])+"""'
    ); """)
    try:
        msg = db.mysql(query)    
    except:
        msg = "FAILED - likely incomplete data in results dictionary."
        import logging
        LOG_FILENAME = 'error.log'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
        logging.debug(str(query))
        logging.debug(str(msg))
    return msg



def heuristic_to_words_html(string = None, description = None, ip = None):
    """ like 'heuristic' function but returns HTML page instead of just the sparkline part """
    if string != None:
        if type(string) not in (str,unicode):
            try:
                string = str(string)
            except:
                return []
        import word_methods as wm
        data = wm.latin1_to_ascii(string)
        if len(data) < 50: # too short!
            return []
    else:
        return []

    import logging
    LOG_FILENAME = 'error.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(str(data)[:100])
    
    results = benford(data) #returns a dictionary
    if results.get('benford') == []:
        return "<HTML><body>Error: No numbers detected, go back and try again.</body></html>"
    score = percent_estimated(data)
    bias = percent_keypad_bias(data)
    dates = percent_date_like(data)
    logging.debug(str(dates))
    repeats = percent_repeated_numbers(data) # a dictionary of data
    #print bias,"% of numbers have keypad-biased patterns."
    #print score,"% of numbers could be estimates or rounded off."
    import json    
    results['estimated']=score
    results['keypad bias']=bias
    results['dates']=dates
    results.update(repeats) #adds 'repeated twice', 'repeated 5x', 'uniques', 'top five'--list of (X,freqs) tuples            
    sparkline = [x['actual'] for x in results.get('benford')]
    spark_ref = [x['ideal'] for x in results.get('benford')]    
    logging.debug( str(sparkline+[0]+spark_ref) )
    
    if len(sparkline) > 0 and len(spark_ref) > 0:
        try:
            deviation = round( sum( [abs(sparkline[i]-spark_ref[i]) for i in range(len(sparkline))] ) ,2)
        except:
            deviation = "Unknown"
            logging.exception( '' )
    results['deviation']=deviation

    try:
        overlap, best_items = get_line_items(string)
        #print "% X in Y:       ",overlap,"percent of your budget's line items also found in legitimate docs."
        #print "% common Y in X:",best_items,"percent of common budget line items are also found in your document."
    except:
        overlap = 'Unknown'
        best_items = 'Unknown'
        
    #SAVE copy in MySQL
    if 'benford' in results:
        try:
            msg = save_to_mysql(results, data, description, ip)
            logging.debug( str(msg) )
        except:
            logging.exception( 'mysql FAIL ' )
    
    #HTML part
    html = ("""
    <html>
    <head>
    <title>Djotjog heuristic financial auditing</title>
      <style type="text/css">
        @import url("http://djotjog.com/default.css");
        .chart div {
           font: 14px sans-serif;
           background-color: red;
           text-align: right;
           padding: 5px;
           margin: 2px;
           color: white;
         }


      </style>      
    <script type="text/javascript" src="/jquery-1.8.0.min.js"></script>
    <script type="text/javascript" src="/jquery.sparkline.min.js"></script>
    </head>
    <body>
    <div class="container">    
    <h2>Compare your uploaded data (left) against an ideal distribution (right) </h2>

    <p>
    Any data that involves counting real objects will tend toward the pattern on the right.
    If your data (left) looks random, or flat, then this data does not contain realistic accounting
    records.
    <br>
    <div class="box" >
        <span STYLE="font-size: x-large;" class="benford">Calculating...</span>
        <br><SPAN STYLE="font-size: x-large;"> 1....2....3....4....5....6....7....8....9.......(Benford leading digit test)</span>
    </div>
    <br><h2> Summary</h2>
    <br><SPAN STYLE="font-size: large;">
    Total numbers found in your document: 
    """+str(results.get('total numbers') or '0')+"""</span>
    <br><SPAN STYLE="font-size: large;">
    Total deviation from the ideal first digit distribution: 
    """+str(results.get('deviation') or "No data")+"""</span><SPAN STYLE="font-size: x-small;"> (ZERO is ideal. More than 20% is suspicious, if your document has at least 500 numbers.)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent estimated numbers: 
    """+str(results.get('estimated') or "No data")+"""% </span><SPAN STYLE="font-size: x-small;"> (% of numbers could be estimates or rounded off.)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent keypad-biased numbers: 
    """+str(results.get('keypad bias') or "No data")+"""% </span><SPAN STYLE="font-size: x-small;"> (i.e. 2-5-8-0 are arranged vertical on phones and keypads and get overused when fraudsters get lazy. </span>
    <br><SPAN STYLE="font-size: large;">
    Percent duplicate numbers:
    """+str(results.get('repeated twice') or "0")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Percent numbers repeated 5 or more times:
    """+str(results.get('repeated 5x') or "0")+"""% </span><SPAN STYLE="font-size: x-small;">(really lazy fraudsters just cut-n-paste data)</span>
    <br><SPAN STYLE="font-size: large;">
    Percent unique numbers:
    """+str(results.get('uniques') or "No data")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Percent of numbers that look like dates:
    """+str(results.get('dates') or "No data")+"""% </span>
    <br><SPAN STYLE="font-size: large;">
    Top five numbers (and # of times each appears):<br>
    """+str(results.get('top five') or "No data")[1:-1]+""" </span><SPAN STYLE="font-size: x-small;"> (if large, obscure numbers appear frequently, this is a sign of fraud!)</span>

    <br><SPAN STYLE="font-size: large;">
    """+str(overlap)+"""% of your budget's line items also found in legitimate docs.
    """+str(best_items)+"""% of common budget line items are also found in your document.
    </span>
    
    </p>
    <script type="text/javascript"> 
    function sparks_benford(){
            $(".benford").sparkline("""+str(sparkline+[0]+spark_ref)+"""
            , {type:'bar', colorMap:{
                ':1':'Pink',
                '0':'White',
                '1:':'LightSteelBlue'
                },
                 height: 150,
                 barWidth: 55,
                 barSpacing: 1
                 });	
                }

    $(window).bind("load", function() {
        sparks_benford();
        console.log("""+str(sparkline+[0]+spark_ref)+""");
        console.log("""+str(results)+""");
    });
    
    /* used to auto-select the text so it can be deleted when you paste in the textarea*/
    window.onload = function(){
      var text_input = document.getElementById ('textarea_1_1');
      text_input.focus ();
      text_input.select ();
    }
    </script>


    <!-- need to use jquery to POST all data directly to cherrypy and avoid the max-size problem -->
    <div class="box-white" size="0.8em">
        <form id="pasted" action="/cp2/benford/" method="post">     
         <textarea id="textarea_1_1" name="textarea_1_1" rows="10" cols="120" autofocus>Paste another spreadsheet!
    </textarea>         
        <br>		    
        <input id="submit" type="submit" name="submit" value="Check Again" />
        Describe your data:        
        <input type="text" name="description" id="description" size="50">
        </form>
        <br>
        Submitting a description will refine this fraud-detection algorithm by benchmarking
        your document against a group of similar documents; the more keywords you include,
        the more-precise the comparison.
    </div>
        <div class="box-blue">
            <SPAN STYLE="font-size:small;"> [For developers] API instructions:
            <br><br>
            You can [POST] your data as a string to http://djotjog.com/cp2/benford_json/
            and the result will be a json format that looks like this:
            <br>
            <br>
            """+str(results)+"""
            <br>
            </span>
        </div>
    <br></span><SPAN STYLE="font-size: x-large;">
    Enjoy! -- the djotjog team.
    </div>
        
    </body>     
    """)
    return html
   



if __name__ == "__main__":
    data = csv_to_string('C:\Users\Marc\Documents\\2012 Phase 3 Rockefeller Community Feedback Sessions\\testreport.csv')
    results = heuristic_to_words_html(data)

    print results
