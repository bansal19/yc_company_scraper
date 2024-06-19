"""
Get a list of all the energy companies from YC's website: https://www.ycombinator.com/companies?industry=Climate&industry=Energy
"""
import requests
from bs4 import BeautifulSoup
import csv
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Scrape YC companies based on industry.")
parser.add_argument('--url', type=str, required=True, help='URL of the YC companies page to scrape')
parser.add_argument('--industry', type=str, required=True, help='Industry to filter by')
parser.add_argument('--xml', type=str, required=True, help='Path to the XML file that has the list of companies. Use inspect element to get the correct div')
args = parser.parse_args()

# URL of the website
url = args.url
industry = args.industry
xml_file = args.xml

# URL of the websites
# url = 'https://www.ycombinator.com/companies?industry=Climate&industry=Energy'
# url = 'https://www.ycombinator.com/companies?industry=Automotive&industry=Agriculture'

def load_xml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_xml_content(content):
    return BeautifulSoup(content, 'lxml')

def find_companies(soup):
    return soup.find_all('a', class_='_company_99gj3_339')

def get_company_page(company_link):
    response = requests.get(company_link)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def get_founders(soup):
    return [img['alt'] for img in soup.find_all('img', class_='h-[75px] w-[75px] object-cover')]

def get_linkedin_links(soup):
    return [a['href'] for a in soup.find_all('a', title='LinkedIn profile')]

def get_company_deets(soup):
    
    founded_span = soup.find('span', string='Founded:')
    if founded_span:
        founded_text = founded_span.find_next_sibling('span').get_text(strip=True)
    team_size_span = soup.find('span', string='Team Size:')
    if team_size_span:
        team_size_text = team_size_span.find_next_sibling('span').get_text(strip=True)
    location_span = soup.find('span', string='Location:')
    if location_span:
        location_text = location_span.find_next_sibling('span').get_text(strip=True)
    return founded_text, team_size_text, location_text

def extract_company_data(companies):
    company_data = []
    for company in companies:
        name = company.find('span', class_='_coName_99gj3_454').text.strip()
        blurb = company.find('span', class_='_coDescription_99gj3_479').text.strip()
        company_link = "https://www.ycombinator.com" + company['href']
        company_page_soup = get_company_page(company_link)

        founders = get_founders(company_page_soup)
        linkedIn_links = get_linkedin_links(company_page_soup)
        founded, team_size, location = get_company_deets(company_page_soup)
        print(f"Company Link: {company_link}, Founded: {founded}, Team Size: {team_size}, Location: {location}")

        company_data.append([name, blurb, company_link, founders, linkedIn_links, founded, team_size, location])
    return company_data

def save_to_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Company Name', 'Blurb', 'Company Link', 'Founders', 'LinkedIn Links', 'Founded', 'Team Size', 'Location'])
        writer.writerows(data)

def main():
    content = load_xml_file(xml_file)
    soup = parse_xml_content(content)
    companies = find_companies(soup)
    
    if len(companies) > 0:
        print(f"Found {len(companies)} companies.")
    
    company_data = extract_company_data(companies)
    save_to_csv('yc_climate_'+ industry + '_companies.csv', company_data)
    print("Data has been successfully scraped and saved to yc_climate_"+industry+"_companies.csv")

if __name__ == "__main__":
    main()