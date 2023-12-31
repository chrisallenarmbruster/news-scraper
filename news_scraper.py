'''
Scrapes desired news off of AP website
Gives options to view, save as text file, export
to PDF file, export to CSV file and email the news.
'''

import csv
import re
import smtplib
import os
import requests
import bs4
from curtsies import Input
import pdfkit
from dotenv import load_dotenv


load_dotenv()


keys_topic = {
    "U": "us-news",
    "W": "world-news",
    "B": "business",
    "T": "technology",
    "X": "science",
    "S": "sports",
    "H": "health",
    "L": "lifestyle",
    "G": "politics",
    "O": "oddities"
}


def menu():
    '''
        Prints menu, a.k.a. 'help'
    '''
    print(
        "\n NEWS SCRAPER MENU\n\n"
        " Select news topic:\n"
        " --------------"
    )
    print_topics()
    print(
        " --------------\n\n"
        " Select viewing option:\n"
        " --------------\n"
        " A - Save ASCII\n"
        " P - Save PDF\n"
        " C - Save CSV\n"
        " E - Email\n"
        " --------------\n\n"
        " Q - Quit\n"
    )


def print_topics():
    '''
    Prints news topics for menu off of dictionary
    '''
    for key, topic in keys_topic.items():
        print(f" {key} - {topic}")


def get_news(url, topic):
    '''
    Scrapes news from web, depending on URL
    '''
    print("\nRetrieving news, please stand by.\n")
    res = requests.get(url + topic, timeout=15)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    feed_cards = soup.select("div.FeedCard")
    if "news" in topic:
        news_str = topic.upper().replace("-", " ")
    else:
        news_str = topic.upper() + " NEWS"
    hl_list = []
    article_num = 1

    for feed_card in feed_cards:
        soup_headline = bs4.BeautifulSoup(str(feed_card), 'lxml')
        headlines = soup_headline.select("div.CardHeadline > a > h2")
        blurbs = soup_headline.select("a > div > p")
        if blurbs and len(blurbs[0].text) > 100:
            news_str = (
                news_str + "\n\n" + str(article_num) + ")  "
                + headlines[0].text.upper() + ": "
            )
            hl_list.append([article_num, headlines[0].text.upper()])
            article_num += 1
            for blurb in blurbs:
                if len(blurb.text) > 100:
                    news_str = news_str + "\n" + blurb.text
    return news_str, hl_list


def ascii_save(news_str):
    '''
    Writes news buffer to an ASCII text file
    '''
    if news_str == "":
        print("\nNews buffer empty.  Nothing to save.")
    else:
        with open("news.tnr", "w+", encoding='utf-8') as file:
            file.write(news_str)
        print("\nASCII save is complete.")


def csv_save(hl_list):
    '''
    Exports aricle numbers with headlines to a csv file
    '''
    if len(hl_list) == 0:
        print("\nNews buffer empty.  Nothing to export.")
    else:
        with open("news.csv", "w+", newline="", encoding='utf-8') as file:
            csv_writer = csv.writer(file, delimiter=",")
            csv_writer.writerow(["ARTICLE #", "HEADLINE"])
            csv_writer.writerows(hl_list)
        print("\nCSV export is complete.")


def pdf_save(news_str):
    '''
    Writes news buffer to a PDF file
    '''
    if news_str == "":
        print("\nNews buffer empty.  Nothing to convert.")
    else:
        optns = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        html_str = "<div>" + news_str.replace("\n", "<br>") + "</div>"
        pdfkit.from_string(html_str, "news.pdf", options=optns)
        print("PDF export is complete.")


def email(news_str):
    '''
    Sends received string as an email to user spec'd address
    '''
    if len(news_str) == 0:
        print("\nNews buffer empty.  Nothing to email.")
    else:
        smtp_object = smtplib.SMTP(
            os.environ.get('smtp_server'),
            os.environ.get('smtp_port'))
        print(smtp_object.ehlo())
        print(smtp_object.starttls())
        print(
            smtp_object.login(
                os.environ.get('user_account'),
                os.environ.get('user_password')))
        from_address = os.environ.get('user_account')
        email_valid = False
        while email_valid is False:
            to_address = input("Enter the TO email address: \n")
            if validate_email(to_address):
                break
            print(
                f"{to_address} is an improperly formatted email address.  Check and try again.")
        print(f"Sending email FROM {from_address} TO {to_address}...\n")
        subject = "News Scraper Results"
        msg = "Subject: " + subject + '\n' + news_str
        msg = msg.encode('utf-8')
        status = smtp_object.sendmail(from_address, to_address, msg)
        if not status:
            print("\nEmail sent successfully.")
        smtp_object.quit()


def validate_email(email_address):
    '''
    Function that applies a regex mask to an email address to validate it
    '''
    regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,4})+')
    return re.fullmatch(regex, email_address)


def main():
    '''
    Program entry point and primary loop
    '''
    program_on = True
    news_str = ""
    hl_list = []
    url = "https://apnews.com/hub/"

    while program_on:
        os.system('clear')
        menu()

        with Input(keynames='curses') as input_generator:
            for key in input_generator:
                if key.upper() == "Q":
                    program_on = False
                    break
                if key.upper() in keys_topic:
                    news_str, hl_list = get_news(url, keys_topic[key.upper()])
                    print(news_str)
                elif key.upper() == "A":
                    ascii_save(news_str)
                elif key.upper() == "P":
                    pdf_save(news_str)
                elif key.upper() == "C":
                    csv_save(hl_list)
                elif key.upper() == "E":
                    email(news_str)
                elif key.upper() == "M" or key.upper() == "H":
                    menu()
                else:
                    print("\nNot a valid command.")

                print("\n\nEnter command to continue, m for menu or q to quit:\n")


if __name__ == "__main__":
    main()
