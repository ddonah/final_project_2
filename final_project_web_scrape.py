import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch  

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

def figure_1(df):
    names_2022 = list(df.sort_values('2022', ascending = False).iloc[0:5, :].name.values)
    values_2022 = list(df.sort_values('2022', ascending = False).iloc[0:5, :]['2022'].values)
    year_2022 = [2022]*5
    names_1960 = list(df.sort_values('1960', ascending = False).iloc[0:5, :].name.values)
    values_1960 = list(df.sort_values('1960', ascending = False).iloc[0:5, :]['1960'].values)
    year_1960 = [1960]*5
    all_names = names_2022 + names_1960
    all_values = values_2022 + values_1960
    all_years = year_2022 + year_1960
    n_df = pd.DataFrame(data={
        'name': all_names,
        'count' : all_values,
        'year' : all_years
    })
    plt.bar(x = n_df[n_df.year == 2022].name.values, height = n_df[n_df.year == 2022].population.values, color = 'darkblue')
    plt.bar(x = n_df[n_df.year == 1960].name.values, height = n_df[n_df.year == 1960].population.values, color = 'orange')
    plt.xticks(rotation=45, ha='right')
    legend_info = [Patch(color='orange', label='1960'), 
                Patch(color='darkblue', label='2022')]
    plt.legend(handles=legend_info)
    plt.ylabel('Number of babies', fontsize = 16.0)
    plt.title('Number of children named the top 5 most \npopular names in 1960 & 2022', fontsize = 18.0)
    return None

    
    






def main():
    pass

if __name__ == '__main__':
    main()
