'''
A translation function for Spartanburg county shp roads data. 


The following fields are used:    

Field           Used For            Reason
LANECOUNT       lanes
FULLNAME        name                If STNAME + TYPE + PREDIR do not work
PREDIR          Road direction prefix
TYPE            Road type (street, ave, etc)
STNAME          Base road name
STATEHWYCL      highway=*           Type of the road



Internal mappings:
OWNER=Provincial    <==> ROADTYPE=Highway Ramp|Ministry of Transportation
OWNER=Regional       ==> ROADTYPE=Major Road Network

OSM Mappings
Source value                            OSM value                           Shortcomings
ROADTYPE=Arterial                       highway=secondary           
ROADTYPE=Collector                      highway=tertiary            
ROADTYPE=Local                          highway=residential                 May need to be changed to highway=unclassified for some roads
ROADTYPE=Lane                           highway=service                     Source data does not indicate if service=alley
ROADTYPE=Gravel                         highway=residential surface=gravel
ROADTYPE=Ministry of Transportation     highway=primary|motorway            Huristics used to differentiate between highways. Double-check these
ROADTYPE=Major Road Network             highway=secondary                   Does not identify Highway 1A as primary
ROADTYPE=Highway Ramp                   highway=motorway_link
'''

import re

def translateName(rawname,warn):
    '''
    A general purpose name expander.
    '''
    suffixlookup = {
    'Aly':'Alley',
    'Ave':'Avenue',
    'Br':'Branch',
    'Blf':'Bluff',
    'Rd':'Road',
    'Hts':'Heights',
    'St':'Street',
    'Pl':'Place',
    'Hl':'Hill',
    'Holw':'Hollow',
    'Pk':'Park',
    'Cres':'Crescent',
    'Blvd':'Boulevard',
    'Dr':'Drive',
    'Dwns':'Downs',
    'Ext':'Extension',
    'Pkwy':'Parkway',
    'Lndg':'Landing',
    'Xing':'Crossing',
    'Lane':'Lane',
    'Cv':'Cove',
    'Crt':'Court',
    'Trl':'Trail',
    'Tr':'Trail',
    'Ter':'Terrace',
    'Trc':'Trace',
    'Trce':'Trace',
    'Vly':'Valley',
    'Xovr':'Crossover',
    'Gr':'Grove',
    'Grv':'Grove',
    'Ln':'Lane',
    'Lk':'Lake',
    'Cl':'Close',
    'Cv':'Cove',
    'Cir':'Circle',
    'Ct':'Court',
    'Est':'Estate',
    'Rdg':'Ridge',
    'Plz':'Plaza',
    'Pne':'Pine',
    'Pte':'Pointe',
    'Pnes':'Pines',
    'Pt':'Point',
    'Ctr':'Center',
    'Rwy':'Railway',
    'Div':'Diversion',
    'Mnr':'Manor',
    'Hwy':'Highway',
    'Hwy':'Highway',
    'Conn': 'Connector',
    'Chase': 'Chase',
    'View': 'View',
    'Cliff': 'Cliff',
    'Walk': 'Walk',
    'Gate': 'Gate',
    'Grove': 'Grove',
    'Path': 'Path',
    'Trail': 'Trail',
    'Place': 'Place',
    'Real': 'Realignment',
    'Pass': 'Pass',
    'Row': 'Row',
    'Way': 'Way',
    'Farm': 'Farm',
    'Run': 'Run',
    'Drive': 'Drive',
    'Loop': 'Loop',
    'Line': 'Line',
    'E':'East',
    'S':'South',
    'N':'North',
    'W':'West'}
	
    newName = ''
    for partName in rawname.split():
        trns = suffixlookup.get(partName,partName)
        if (trns == partName):
            if partName not in suffixlookup:
                if warn:
                    print ('Unknown suffix translation - ', partName)
        newName = newName + ' ' + trns

    return newName.strip()


# Only apply translation to first and last word
def translateFullName(rawname):
    newName = ''
    nameParts = rawname.split()
    for idx, partName in enumerate(nameParts):
        if idx == 0:
            partName = translatePrefix(partName)
        elif idx == (len(nameParts)-1):
            partName = translateName(partName,True)
        newName = newName + ' ' + partName

    return newName.strip()


def translatePrefix(rawname):
    '''
    Directional name expander.
    '''
    prefixLookup = {
        'O':'Old',
        'N':'New',
        'NW':'NorthWest',
        'NE':'NorthEast',
        'SE':'SouthEast',
        'SW':'SouthWest',
        'E':'East',
        'S':'South',
        'N':'North',
        'W':'West'}

    newName = ''
    for partName in rawname.split():
        newName = newName + ' ' + prefixLookup.get(partName,partName)

    return newName.strip()


# Convert from 22Nd to 22nd
def CorrectNumberedCapitalization(rawname):
    newName = ''
    for partName in rawname.split():
        word = partName
        if (word[0].isdigit()):
            word = word.lower()
        newName = newName + ' ' + word

    return newName.strip()

#see if type was apecified in both base STNAME and on type
#For example Oak Street Street
def CheckDoubleType(rawName):
    newName = rawName
    nameParts = rawName.split()
    numberOfParts = len(nameParts)
    if numberOfParts >= 3:
        testSuffix = translateName(nameParts[numberOfParts-2],False)
        lastWord = nameParts[numberOfParts-1]
        if (lastWord == testSuffix):
            del nameParts[-1]  # remove last element
            nameParts[numberOfParts-2] = testSuffix # replace last word with expanded word
            newName = ' '.join(nameParts)

    return newName.strip()


    
def filterTags(attrs):
    if not attrs:
        return
    tags = {}
    
    roadName =''
        
    if 'PREDIR' in attrs:
        translated = translatePrefix(attrs['PREDIR'])
        roadName = roadName + translated
        #if translated != '(Lane)' and translated != '(Ramp)':
        #    tags['name'] = translated

    if 'STNAME' in attrs:
        roadName = roadName + ' ' + attrs['STNAME'].title().strip()

    if 'TYPE' in attrs:
        translated = translateName(attrs['TYPE'].title(),True)
        roadName = roadName + ' ' + translated

    roadName = roadName.strip()
    if roadName=='':
        # couldn't build road name from parts, try full name
        if 'FULLNAME' in attrs:
            roadName = translateFullName(attrs['FULLNAME'].title())

    roadName = roadName.strip();
    roadName = CorrectNumberedCapitalization(roadName)
    roadName = re.sub("\s\s+", " ", roadName)  # Remove multiple spaces
    roadName = CheckDoubleType(roadName)
    if roadName != '':
        tags['name'] = roadName
        
        
    if 'LANECOUNT' in attrs:
        lanes  = attrs['LANECOUNT'].strip()
        if lanes != "0":
            tags['lanes'] = lanes
        
    if 'STATEHWYCL' in attrs:
        hwy = attrs['STATEHWYCL'].strip()
        if hwy == 'INT':
            tags['highway'] = 'motorway'
        elif hwy == 'MAJA':
            tags['highway'] = 'primary'
        elif hwy == 'MINA':
            tags['highway'] = 'secondary'
        elif hwy == 'COLL':
            tags['highway'] = 'tertiary'
        elif hwy == 'Local':
            tags['highway'] = 'residential'
        elif hwy == 'Lane':
            tags['highway'] = 'service'
        elif hwy == 'Gravel':
            tags['highway'] = 'residential'
            tags['surface'] = 'gravel'
        elif hwy == 'Highway Ramp':
            tags['highway'] = 'motorway_link'
        else:
            if hwy != '':
                print ('Unknown highway type:  ', hwy)
            tags['highway'] = 'residential'
    else:
        tags['highway'] = 'residential'
            

    return tags