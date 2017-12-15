import os,glob,requests,pandas,bs4,datetime,numpy

def ascii_chars(string):
    return ''.join(char for char in string if ord(char) < 128)

def write_csv(fname, mode, rows):
    with open(fname, mode) as f:
        for row in rows:
            for td in row:
                f.write(td + ',')
            if row:
                f.write('\n')

def table2list(table):
    rows = []
    txt_link = ""
    for row in table.tbody.find_all('tr'):
        values0 = [val.text for val in row.find_all('td')]
        if len(values0) > 0:
            values = []
            ass = row.find_all('a')
            txt_link = ass[2]['href']
            download_txt(txt_link)
            for v in values0:
                pv = ascii_chars(v.splitlines()[0])
                #pv.replace('&nbsp;','')
                #pv.replace('Not Run','-1')
                values.append('"' + pv + '"')
            values.append('"' + txt_link + '"')
            rows.append(values)
    return rows


def replace_list_item(items,if_value,value):
    return [value if if_value==x else x for x in items]

def find_headers(div):
    head = div.find("thead")
    if head == None:
        return None
    headers = [header.text for header in head.find_all('th')]
    headers.remove("Processor")
    headers.remove("Results")
    if any("Energy" in s for s in headers):
        headers.remove("Energy")
        headers[-2] = headers[-2] + "Energy"
        headers[-1] = headers[-1] + "Energy"
    headers = replace_list_item(headers,"Test Sponsor","Company")
    headers = replace_list_item(headers,"System Name","System")
    headers = replace_list_item(headers,"Threads/Core","ThreadsPerCore")
    headers = replace_list_item(headers, "Cores/Chip", "CoresPerChip")
    headers.append("txt")
    return headers

def get_section(soup, tname, fname):
    dname=tname+'div'
    content = soup.find(id=dname)
    headers = find_headers(content)
    if headers == None:
        return
    csv_fname = tname +'_'+ fname + '.csv'
    write_csv(csv_fname, 'w', [headers])
    write_csv(csv_fname, 'a', table2list(content))

def read_cfg(k):
    with open("map.txt", "r") as fi:
        for ln in fi:
            if ln.startswith(k):
                return ln.replace(k,'').strip()

def benchmark(bmk):
    fname = bmk+'.html'
    if os.path.exists(fname):
        soup = bs4.BeautifulSoup(open(fname), "lxml")
        get_section(soup, read_cfg(bmk), bmk)

def delete_csv(pattern):
    for f in glob.glob("*"+pattern+"*.csv"):
        os.remove(f)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def download_txt(fname):
    bmk=find_between( fname, "/", "-2" )
    dir0 = 'txt/'+bmk
    f = dir0 +'/'+fname
    if not os.path.exists(f):
        print('downloading '+fname)
        dir1 = dir0 + '/' +fname.split('/')[0]
        os.makedirs(dir0, exist_ok=True)
        os.makedirs(dir1, exist_ok=True)
        url = 'http://spec.org/'+bmk+'/results/'+fname
        f = open(f, 'wb')
        f.write(requests.get(url).content)
        f.close()

def run_cpu2017():
    benchmark('cint2017')
    benchmark('cfp2017')
    benchmark('rint2017')
    benchmark('rfp2017')

def run_cpu2006():
    # benchmark('cint2006')
    # benchmark('cfp2006')
    benchmark('rint2006')
    #benchmark('rfp2006')
####################################################
#delete_csv("")
run_cpu2006()