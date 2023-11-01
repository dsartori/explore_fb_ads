import requests
import json
import petl
from collections import OrderedDict
import matplotlib.pyplot as plt
import textwrap

# Top 10 issues facing Canadians according to Ipsos data September 2023:

# request parameters
ad_reached_countries='["CA"]'
ad_type='POLITICAL_AND_ISSUE_ADS'
search_terms=['[Cost of living]','[Health care]','[Economy]','["Housing"]', '[Inflation]',  '[Taxes]','[Climate change]','[Poverty]','[Deficit]','[covid]']
ad_active_status='ALL'
ad_delivery_date_min='2023-01-01'
ad_delivery_date_max='2023-9-25'
fields='spend,target_ages,target_gender,page_name,impressions'
access_token = ''


summary_data ={}
term_data ={}

for (i, term) in enumerate(search_terms):

    print ("Getting data for search term: " + term)
    flag = True
    url = f'https://graph.facebook.com/v18.0/ads_archive?fields={fields}&access_token={access_token}&ad_reached_countries={ad_reached_countries}&ad_type={ad_type}&search_terms={term}&ad_active_status={ad_active_status}&ad_delivery_date_min={ad_delivery_date_min}&ad_delivery_date_max={ad_delivery_date_max}'

    output_data = []

    while flag:
        r = requests.get(url)
        ad_data = json.loads(r.text)
        output_data += ad_data['data']
        try:
            url = ad_data['paging']['next']
        except:
            flag = False

    page_data = {}
    for ad in output_data:
        if 'page_name' not in ad:
            continue
        page_name = ad['page_name']
        impressions = 0.0
        if 'upper_bound' not in ad['impressions']:
            impressions = float(ad['impressions']['lower_bound'])
        else:
            if 'lower_bound' not in ad['impressions']:
                impressions = 0.0
            else:
                impressions = float(ad['impressions']['upper_bound'])
        
        spend = 0
        if 'upper_bound' not in ad['spend']:
            spend = float(ad['spend']['lower_bound'])
        else:
            if 'lower_bound' not in ad['spend']:
                spend = 0.0
            else:
                spend = float(ad['spend']['upper_bound'])
        if page_name in page_data:
            page_data[page_name]['impressions'] += impressions
            page_data[page_name]['spend'] += spend
        else:
            page_data[page_name] = {'impressions': impressions, 'spend': spend}

    print(term + "\n\n")
    print (page_data)
    term_data[term] = page_data

    for page in page_data:
        impressions = page_data[page]['impressions']
        spend = page_data[page]['spend']
        if term in summary_data:
            summary_data[term]['impressions'] += impressions
            summary_data[term]['spend'] += spend
        else:
            summary_data[term] = {'impressions': impressions, 'spend': spend}

    print (summary_data)

with open('ad_data.csv', 'w') as f:
    f.write('Search Term, Impressions, Spend\n')
    for term in summary_data:
        f.write(f'{term}, {summary_data[term]["impressions"]}, {summary_data[term]["spend"]}\n')

with open('detail_ad_data.csv', 'w') as f:
    f.write('Search Term, Page Name, Impressions, Spend\n')
    for term in term_data:
        for page in term_data[term]:
            f.write(f'{term}, {page}, {term_data[term][page]["impressions"]}, {term_data[term][page]["spend"]}\n')

    


