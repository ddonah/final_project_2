import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_name_data(stte):
    r1 = requests.get('https://www.ssa.gov/OACT/babynames/state/index.html')
    soup = BeautifulSoup(r1.content)
    yrs = [x['value'] for x in soup.find('select', {'name': 'year'}).find_all('option')]
    name_list = []
    for yr in yrs:
        selection = {
            'state': stte,
            'year': yr
        }
        r2 = requests.post('https://www.ssa.gov/cgi-bin/namesbystate.cgi', data=selection)
        df = pd.read_html(r2.text)[1].iloc[4:,:].reset_index()
        f_name_df = df.iloc[:, 4:6]
        f_name_df.columns = ['name', yr]
        f_name_df['gender'] = 'female'
        m_name_df = df.iloc[:, 2:4]
        m_name_df.columns = ['name', yr]
        m_name_df['gender'] = 'male'
        name_df = pd.concat([f_name_df, m_name_df], ignore_index=True)
        name_list.append(name_df)
    final_name_df = name_list[0][['name', 'gender', '2022']]
    for el in name_list[1:]:
        final_name_df = final_name_df.merge(el, on=['name', 'gender'], how='outer')
    df['total'] = df.loc[:, '2022':'1960'].apply(pd.to_numeric).sum(axis=1, skipna=True)
    return final_name_df

    
    






def main():
    pass

if __name__ == '__main__':
    main()
