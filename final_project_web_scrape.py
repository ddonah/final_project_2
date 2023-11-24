
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_name_data(stte, yr):
    r1 = requests.get()
    selection = {
        'state': stte,
        'year': yr
    }
    r = requests.post('https://www.ssa.gov/cgi-bin/namesbystate.cgi', data=selection)
    df = pd.read_html(r.text)[1].iloc[4:,:].reset_index()
    f_name_df = df.iloc[:, 4:6]
    m_name_df = df.iloc[:, 2:4]
    return f_name_df, m_name_df

    
    






def main():
    pass

if __name__ == '__main__':
    main()
