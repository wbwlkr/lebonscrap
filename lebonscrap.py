import scrapy
import json
from urllib.parse import urlencode
import requests

# To call the script :
# scrapy runspider lebonscrap.py -o data.json

class LeboncoinSpider(scrapy.Spider):
    name = "leboncoin"
    start_urls = [
        'http://www.leboncoin.fr/li?ca=16_s&c=10&f=p&mre=800&sqs=6&ros=3&ret=1&ret=2&furn=2&location=Toulouse',
    ]

    def parse(self, response_list):
        # follow links to advertissement pages
        for ad_link in response_list.css('a.list_item'):
            description_page = ad_link.css('a::attr("href")').extract_first()
            yield response_list.follow(description_page, self.parse_description)

        # follow pagination link
        next_list = response_list.css('li.next a::attr("href")').extract_first()
        if next_list is not None:
            yield response_list.follow(next_list, self.parse)

    def parse_description(self, response_ad):
        # scrap phone number
        phone = self.get_phone(response_ad)

        # export data
        return {
            'Url': response_ad.url,
            'Titre': response_ad.css("h1::text").extract_first().strip(),
            'Prix': response_ad.css("h2.item_price.clearfix > span.value::text").extract_first().strip(),
            'Surface': response_ad.xpath('//div[9]/h2/span[2]/text()').extract_first().strip('m').strip(),
            'GES': response_ad.xpath('//div[10]/h2/span[2]/a/text()').extract_first(),
            'Classe énergie': response_ad.xpath('//div[10]/h2/span[2]/a/text()').extract_first(),
            'Auteur': response_ad.css('a[data-info*="pseudo_annonceur"]::text').extract_first().strip(),
            'Telephone': phone,
            'Remarques': ''
        }

    def get_phone(self, res_ad):
        # check if the phone button exist then return phone number
        phone_button = res_ad.css('button.button-orange.large.phoneNumber.trackable').extract_first()

        if phone_button is not None:
            list_id = res_ad.css('input[name="id"]::attr(value)').extract_first().strip()
            api_key = res_ad.css('section.adview_main > section > script').re('apiKey = "(.+)"')[0]

            request_phone_body = {
                'list_id': list_id,
                'app_id': 'leboncoin_web_utils',
                'key': api_key,
                'text': '1'
            }

            request_phone_headers = {
                'Host': 'api.leboncoin.fr',
                'Referer': res_ad.url,
                'Origin': 'https://www.leboncoin.fr',
            }

            # TODO: Add POST request to phonenumber API
            # TODO: With url = 'https://api.leboncoin.fr/api/utils/phonenumber.json'
            # TODO: With body = request_phone_body
            # TODO: With headers = request_phone_headers
            # TODO: And parse JSON response with a callback=parse_phone
            return 'Oui'
        else:
            return 'No'

    def parse_phone(self, response_json):
        jsonresponse = json.loads(response_json)
        return jsonresponse['utils']['phonenumber']
