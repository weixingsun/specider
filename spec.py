import os,glob,requests,pandas,bs4,datetime

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


def merge_csv(flist,name):
    sublist = [elem for elem in flist if elem.startswith(name)]
    all = pandas.concat([pandas.read_csv(f) for f in sublist])  #.dropna()
    all.to_csv(name+".csv", index=False)


def merge_csv_all():
    flist = os.listdir(os.getcwd())
    merge_csv(flist,"CINT2017_rate")
    merge_csv(flist,"CFP2017_rate")
    merge_csv(flist,"CINT2017_speed")
    merge_csv(flist,"CFP2017_speed")


def delete_csv(pattern):
    for f in glob.glob("*"+pattern+"*.csv"):
        os.remove(f)


####################################################
delete_csv("")
y = datetime.datetime.now().year
q = get_quarter(datetime.datetime.now())
before(y,q)
#download(2017,4)
download(y,q)
quarter(y,q)
merge_csv_all()
delete_csv("res")