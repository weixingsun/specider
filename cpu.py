import os,glob,requests,bs4,csv

def ascii_chars(string):
  return ''.join(char for char in string if ord(char) < 128)

def write_csv(fname, mode, row):
    with open(fname, mode) as f:
        for td in row:
            f.write(td + ',')
        if row:
            f.write('\n')

def get_cpu_spec(name):
    fname=name.replace(' ','+')
    soup = bs4.BeautifulSoup(open('cpu/'+fname + '.html', encoding="utf-8"), "lxml")
    ul_node = soup.find_all("ul", {"class": "list-status"})
    head=[name]
    values = []
    spans = ul_node[0].find_all("span", {"class": "value"})
    for v in spans:
        pv = ascii_chars(v.text)
        if pv.endswith('GHz'):
            values.append('"' + pv.rsplit(' ', 1)[0] + '"')
        else:
            values.append('"' + pv + '"')

    return head+values[-3:]

####################################################

def download(fname):
    print('downloading '+fname)
    url = 'https://ark.intel.com/search?q='+fname
    f = open('cpu/'+fname+'.html', 'wb')
    f.write(requests.get(url).content)
    f.close()

def delete_files(pattern,type):
    for f in glob.glob("*"+pattern+"*."+type):
        os.remove(f)

def html2csv(name):
    fname=name.replace(' ','+')
    if not os.path.isfile('cpu/'+fname+'.html'):
        download(fname)
    headers = ["name","max_f","base_f","cache"]
    if not os.path.isfile('all.csv'):
        write_csv('all.csv', 'w', headers)
    row = get_cpu_spec(name)
    write_csv('all.csv','a',row)
    #delete_files(fname,'html')

def csv2list(fname):
    with open(fname, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader, None)
        return list(reader)

def loop_csv():
    list = csv2list('cpu/cpus.csv')
    for row in list:
        html2csv(row[0])

loop_csv()
