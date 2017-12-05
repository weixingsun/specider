import os,glob,requests,pandas,bs4,datetime,querycsv_redux,numpy

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
  for row in table.tbody.find_all('tr'):
    values0 = [val.text for val in row.find_all('td')]
    values = []
    for v in values0:
      pv = ascii_chars(v.splitlines()[0])
      values.append('"' + pv + '"')
    rows.append(values)
  return rows


def download(y, q):
  url = 'http://spec.org/cpu2017/results/res'+str(y)+'q' + str(q)
  name = url.split('/')[-1]
  f = open(name+'.html', 'wb')
  f.write(requests.get(url).content)
  f.close()


def replace_list_item(items,if_value,value):
    return [value if if_value==x else x for x in items]

def find_headers(div):
  head = div.find("thead")
  if head == None:
      return None
  headers = [header.text for header in head.find_all('th')]
  headers.remove("Processor")
  headers.remove("Results")
  headers.remove("Energy")
  headers[-2] = headers[-2] + "Energy"
  headers[-1] = headers[-1] + "Energy"
  headers = replace_list_item(headers,"Test Sponsor","Company")
  headers = replace_list_item(headers,"System Name","System")
  headers = replace_list_item(headers,"Threads/Core","ThreadsPerCore")
  return headers


def get_quarter(date):
  return int((date.month - 1) / 3 + 1)


def get_section(soup, tname, fname):
  dname=tname+'div'
  intrate = soup.find(id=dname)
  headers = find_headers(intrate)
  if headers == None:
      return
  csv_fname = tname +'_'+ fname + '.csv'
  write_csv(csv_fname, 'w', [headers])
  write_csv(csv_fname, 'a', table2list(intrate))


def quarter(y,q):
  name='res'+str(y)+'q'+str(q)
  soup = bs4.BeautifulSoup(open(name+'.html'), "lxml")
  get_section(soup, "CINT2017_rate", name)
  get_section(soup, "CFP2017_rate", name)
  get_section(soup, "CINT2017_speed", name)
  get_section(soup, "CFP2017_speed", name)


def before(y,q):
    for yq in ['2017q2', '2017q3', '2017q4', '2018q1', '2018q2', '2018q3']:
        if yq == str(y) + 'q' + str(q):
            return
        else:
            y1 = yq.split('q')[0]
            q1 = yq.split('q')[1]
            quarter(y1, q1)
            print(yq)

def find_cpu_name(list):
    for item in list:
        if item.strip().startswith("Intel") or item.strip().startswith("AMD"):
            return item


def get_simple_name(CPU_NAME):
    names = str(CPU_NAME).split(',')
    if len(names) == 1:
        return names[0]
    else:
        return find_cpu_name(names)

def merge_csv(flist,name):
    sublist = [elem for elem in flist if elem.startswith(name)]
    all = pandas.concat([pandas.read_csv(f) for f in sublist])  #.dropna()
    all = all.iloc[:, :-1]
    all["CPU"] = all['System'].str.extract(r"\((.*?)\)", expand=False)
    #all["SCPU"] = all["CPU"].str.extract(r"(?:Intel|AMD|UltraSPARC).*$", expand=False)
    all["SCPU"] = all["CPU"].str.extract("([Intel|AMD|UltraSPARC].*?)$", expand=False)
    all["CPU0"] = all["SCPU"].str.split(',').str[0]
    all.to_csv(name+".csv", index=False)
    f = {'Base': ['max'], 'Peak': ['max']}
    group1 = all.groupby(['Company','EnabledChips', 'CPU0']).agg(f)
    group1.to_csv(name+"_group.csv")

def merge_csv_all():
    flist = os.listdir(os.getcwd())
    merge_csv(flist,"CINT2017_rate")
    merge_csv(flist,"CFP2017_rate")
    merge_csv(flist,"CINT2017_speed")
    merge_csv(flist,"CFP2017_speed")


def delete_csv(pattern):
    for f in glob.glob("*"+pattern+"*.csv"):
        os.remove(f)

def add_cpu(values):
    CPU="None"
    if len(values) > 1:
        sys=values[1]
        CPU=sys[sys.find("(")+1:sys.find(")")]
    values.append(CPU)
####################################################
delete_csv("")
y = datetime.datetime.now().year
q = get_quarter(datetime.datetime.now())
before(y,q)
#download(2017,4)
#download(y,q)
quarter(y,q)
merge_csv_all()
delete_csv("res")

#df2.groupby('Company','CPU').transform('max')