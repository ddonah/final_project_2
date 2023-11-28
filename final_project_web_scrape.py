import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import PyPDF2
from io import BytesIO
import statsmodels.api as sm

def get_name_data(stte):
    r1 = requests.get('https://www.ssa.gov/OACT/babynames/state/index.html')
    soup = BeautifulSoup(r1.content, features='lxml')
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
    final_name_df.loc[:, '2022':'1960'] = final_name_df.loc[:, '2022':'1960'].apply(pd.to_numeric)
    final_name_df['total'] = final_name_df.loc[:, '2022':'1960'].apply(pd.to_numeric).sum(axis=1, skipna=True)
    final_name_df = final_name_df.sort_values('total', ascending=False)
    return final_name_df

def make_births_sr():
    pdf_r = requests.get('https://pub.azdhs.gov/health-stats/report/ahs/ahs2020/pdf/8a1.pdf')
    pdf_file = PyPDF2.PdfFileReader(BytesIO(pdf_r.content))
    text = pdf_file.getPage(0).extractText()
    text = text.split('\n')[1:39]
    year = []
    births = []
    for el in text:
        if len(el.split()) < 2:
            year.append(int(el[0:4]))
            births.append(float(el[4:10].replace(',', '')))
        elif len(el.split()) == 2:
            year.append(int(el.split()[0][0:4]))
            year.append(int(el.split()[1][0:4]))
            births.append(float(el.split()[0][4:10].replace(',', '')))
            births.append(float(el.split()[1][4:10].replace(',', '')))
        else:
            year.append(int(el.split()[0]))
            births.append(float(el.split()[1].replace(',', '')))
    seventies_sr = pd.Series(births, index = year)
    #I realized the site I was getting the info from also had posted excel files of their data
    #but I had already made the earlier series so I wanted to use it.
    tens_df = pd.read_excel('https://pub.azdhs.gov/health-stats/report/ahs/ahs2020/excel/t5b3.xlsx', header=3)
    tens_sr = tens_df.loc[0, 2010:2020]
    total_sr = pd.concat([seventies_sr, tens_sr])
    return total_sr

def get_ols(df, ydat):
    x = df.index.values
    a = sm.add_constant(x)
    mdl = sm.OLS(df[ydat].values, a)
    line = mdl.fit()
    result = [line.params[1], line.params[0], line.rsquared]
    y = result[0] * x + result[1]
    return y, x, result


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
        'population' : all_values,
        'year' : all_years
    }).sort_values('population')
    plt.bar(x = n_df[n_df.year == 2022].name.values, height = n_df[n_df.year == 2022].population.values, color = 'darkblue')
    plt.bar(x = n_df[n_df.year == 1960].name.values, height = n_df[n_df.year == 1960].population.values, color = 'orange')
    plt.xticks(rotation=45, ha='right')
    legend_info = [Patch(color='orange', label='1960'), 
                Patch(color='darkblue', label='2022')]
    plt.legend(handles=legend_info)
    plt.ylabel('Number of births', fontsize = 16.0)
    plt.xlabel('Newborn\'s Name', fontsize = 14.0)
    plt.title('Number of children named the top 5 most \npopular names in 1960 & 2022', fontsize = 18.0)
    fig = plt.gcf()
    fig.set_size_inches(9, 7.5)
    return None

def figure_2(df):
    births_sr = make_births_sr()
    names_sr = df.loc[:, '2020':'1970'].sum()[::-1] 
    full_df = pd.DataFrame(index=list(range(1970,2021)))
    full_df['ssa'] = names_sr.values
    full_df['births'] = births_sr.values
    full_df = full_df.drop(2006)
    plt.scatter(full_df.index, full_df.ssa, color = 'darkblue')
    plt.scatter(full_df.index, full_df.births, color = 'orange')
    ssa_line_x, ssa_line_y, ssa_line_params = get_ols(full_df, 'ssa')
    plt.plot(ssa_line_y, ssa_line_x, color = 'darkblue')
    births_line_x, births_line_y, births_line_params = get_ols(full_df, 'births')
    plt.plot(births_line_y, births_line_x, color = 'orange')
    legend_info = [Patch(color='darkorange', label='total births'), 
                Patch(color='darkblue', label='births with top \n100 names')]
    plt.legend(handles=legend_info)
    plt.title('Population Trends of Top 100 Most Popular\n Names in Arizona Over Time', fontsize=18.0)
    plt.yticks(rotation=25, ha='right')
    plt.ylabel('Number of births', fontsize = 14.0)
    fig = plt.gcf()
    fig.set_size_inches(8, 4.78)

def figure_3(df):
    n_df = df.loc[:,'gender':'1960'].groupby('gender').agg(['sum'])
    n_df.columns =  list(range(2022, 1959, -1))
    n_df.index.name = None
    n_dft = n_df.T[::-1]
    n_dft['percent_change_female'] = n_dft.female.pct_change() * 100
    n_dft['percent_change_male'] = n_dft.male.pct_change() * 100
    n_dft.loc[1960, 'percent_change_female'] = 0
    n_dft.loc[1960, 'percent_change_male'] = 0
    plt.axhline(y=0, color='grey', linestyle='--')
    plt.axhline(y=20, color='lightgrey', linestyle='--')
    plt.axhline(y=-20, color='lightgrey', linestyle='--')
    plt.plot(n_dft.index, n_dft.percent_change_female, color = 'darkblue')
    plt.plot(n_dft.index, n_dft.percent_change_male, color = 'darkorange')
    plt.title('Percent change in popularity of male \nand female names', fontsize = 18.0)
    plt.ylabel('Percent change', fontsize = 14.0)
    legend_info = [Patch(color='darkblue', label='female names'), 
                Patch(color='darkorange', label='male names')]
    plt.legend(handles=legend_info)

def figure_4(df):
    n_df = df.T
    n_df.columns = n_df.iloc[0]
    n_df = n_df.drop(['gender', 'total', 'name'], axis=0)[::-1]
    n_df = n_df[['Michael', 'Jennifer']]
    n_df['Michael_cot'] = n_df.Michael.pct_change() * 100
    n_df['Jennifer_cot'] = n_df.Jennifer.pct_change() * 100
    n_df.index = n_df.index.astype(int)
    n_df.loc[1960, 'Jennifer_cot'] = 0
    n_df.loc[1960, 'Michael_cot'] = 0
    plt.axhline(y=0, color='grey', linestyle='--')
    plt.axhline(y=20, color='lightgrey', linestyle='--')
    plt.axhline(y=40, color='lightgrey', linestyle='--')
    plt.axhline(y=-20, color='lightgrey', linestyle='--')
    plt.axhline(y=-40, color='lightgrey', linestyle='--')
    plt.plot(n_df.index, n_df.Jennifer_cot, color = 'darkblue')
    plt.plot(n_df.index, n_df.Michael_cot, color = 'orange')
    plt.title('Percent change in popularity of top male \nand female names', fontsize = 18.0)
    legend_info = [Patch(color='darkorange', label='Michael'), 
                Patch(color='darkblue', label='Jennifer')]
    plt.legend(handles=legend_info)
    plt.ylabel('Percent Change', fontsize=14.0)



def main():
    df = get_name_data('AZ')
    figure_1(df)
    plt.figure()
    figure_2(df)
    plt.figure()
    figure_3(df)
    plt.figure()
    figure_4(df)
    plt.show()
    return None

if __name__ == '__main__':
    main()
    






def main():
    pass

if __name__ == '__main__':
    main()
