import scrapy, json, re, requests
import requests
from scrapy.utils.response import open_in_browser

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
# you can also set number of user agents required by providing `limit` as parameter

software_names = [SoftwareName.CHROME.value]
operating_systems = [
    OperatingSystem.WINDOWS.value,
    OperatingSystem.LINUX.value,
    OperatingSystem.MAC.value,
]

user_agent_rotator = UserAgent(
    software_names=software_names, operating_systems=operating_systems, limit=100
)


# Get Random User Agent String.


class ZumperSpider(scrapy.Spider):
    name = "zumper"
    # allowed_domains = ['zumper.com']

    headers = {
        "authority": "www.zumper.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        # "dnt": "1",
        "origin": "https://www.zumper.com",
        "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        # "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        # "sec-fetch-dest": "empty",
        # "sec-fetch-mode": "cors",
        # "sec-fetch-site": "same-origin",
        # "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    headers2 = {
        "authority": "www.zumper.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.zumper.com",
        "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }
    json_data = {
        "external": True,
        "longTerm": True,
        "minPrice": 0,
        "shortTerm": False,
        "transits": {},
        "url": "ontario-ca",
        "limit": 100,
        "matching": True,
        "excludeGroupIds": [],
        "ignorePopular": True,
        "descriptionLength": 580,
    }
    headers3 = {
        "authority": "www.zumper.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.8",
        "content-type": "application/json",
        # 'cookie': '_pbjs_userid_consent_data=3524755945110770; colorMode=light; _uc_referrer=https://www.google.com/; zumper.sid=s%3AyYxq_ziGs5ms1RbgSObUYxew8-lxnLn3.Nk%2FNmgp%2FUOBRYJfMM6rqpbsMbPNUminfyOerH%2BYTz4M; csrftoken=tO8hywZZ9zXB93XPNz6jnhKEfish9FiY7udDc14uv9YzzXFd8uMKkJplWlgZEBm93u6gTxrARmUtjA4b; optimizely_user_id=1ae3fa32-29d6-4a10-b980-409c6aa64cd5',
        "origin": "https://www.zumper.com",
        # 'referer': 'https://www.zumper.com/apartments-for-rent/ontario-ca',
        "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "x-zumper-xz-token": "t7k6kznmbx9.7m8uzs63g",
    }

    groupids_2_suburl = {}

    handle_httpstatus_list = [451]

    def start_requests(self):
        # proxies setup for requests
        self.proxies = {
            "http": self.settings.get("PROXY"),
            "https": self.settings.get("PROXY"),
        }
        with open(self.settings.get("INPUT_FILE")) as f:
            urls = f.read().strip().splitlines()
        for url in urls:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            if "apartments-for-rent" in url:  # this is a direct listing page
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_listing,
                    headers=self.headers,
                    meta={
                        "proxy": self.settings.get("PROXY"),
                        "province": "",
                        "city": "",
                    },
                )
                continue
            yield scrapy.Request(
                url=url,
                callback=self.parse_province,
                headers=self.headers,
                meta={"proxy": self.settings.get("PROXY")},
            )

    def parse_province(self, response):
        province = response.xpath("//h1/text()").get("").split("Sitemap")[0].strip()

        # Get the list of cities
        cities = response.xpath('//div[contains(@class,"Section_linksContainer")]')[
            0
        ].xpath(".//a")
        for city in cities:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            city_name = (
                city.xpath(".//text()").get("").strip().split("Sitemap")[0].strip()
            )
            city_url = city.xpath(".//@href").get("").strip()
            city_url = response.urljoin(city_url)
            self.logger.info(f"City: {city_name} - {city_url}")
            yield scrapy.Request(
                url=city_url,
                headers=self.headers,
                callback=self.parse_city,
                meta={
                    "province": province,
                    "city": city_name,
                    "proxy": self.settings.get("PROXY"),
                },
            )

        next_pages = response.xpath('//div[contains(@class,"Paginator_container")]//a')
        for next_page in next_pages:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            next_page_url = next_page.xpath(".//@href").get("").strip()
            next_page_url = response.urljoin(next_page_url)
            # self.logger.info(f"Next Page: {next_page_url}")

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_province,
                headers=self.headers,
                meta={
                    # 'province': province,
                    "url": next_page_url,
                    "proxy": self.settings.get("PROXY"),
                },
            )

    def parse_city(self, response):
        listings = response.xpath('//div[contains(@class,"Section_linksContainer")]')
        if listings:
            listings = listings[0].xpath(".//a")

        for listing in listings:
            self.headers2["user-agent"] = user_agent_rotator.get_random_user_agent()
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            listing_url = listing.xpath(".//@href").get("").strip()
            listing_url = response.urljoin(listing_url)
            if (
                "/address/" in listing_url
                or "/apartment-buildings/" in listing_url
                or "/apartments-for-rent/" in listing_url
            ):
                yield scrapy.Request(
                    url=listing_url,
                    callback=self.parse_detail,
                    headers=self.headers2,
                    meta={
                        "province": response.meta.get("province"),
                        "city": response.meta.get("city"),
                        "proxy": self.settings.get("PROXY"),
                    },
                )
                continue

            # listing_url = 'https://www.zumper.com/apartments-for-rent/edmonton-ab' # for testing
            # self.logger.info(f"Listing: {listing_url}")
            yield scrapy.Request(
                url=listing_url,
                callback=self.parse_listing,
                headers=self.headers,
                meta={
                    "province": response.meta.get("province"),
                    "city": response.meta.get("city"),
                    "proxy": self.settings.get("PROXY"),
                },
            )

        next_pages = (
            response.xpath('//div[contains(@class,"Paginator_container")]//a')
            + response.xpath('//a[contains(text(),"Next"))]/@href').getall()
        )
        for next_page in next_pages:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            next_page_url = next_page.xpath(".//@href").get("").strip()
            next_page_url = response.urljoin(next_page_url)
            # self.logger.info(f"Next Page: {next_page_url}")

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_city,
                headers=self.headers,
                meta={
                    # 'province': province,
                    "url": next_page_url,
                    "proxy": self.settings.get("PROXY"),
                },
            )

    def parse_listing(self, response):
        detail_urls = response.xpath(
            '//a[contains(@class,"chakra-link")][@target="_blank"][@aria-hidden="false"]/@href'
        ).getall()

        # "group_id":2122112,
        # get all group_id from response.text using regex
        group_ids = re.findall(r'"group_id":-(\d+),', response.text)
        group_ids = [-int(x) for x in group_ids]

        for detail_url in detail_urls:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            detail_url = response.urljoin(detail_url)
            self.logger.info(f"Detail: {detail_url}")
            # self.logger.info(f"Detail: {detail_url}")

            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                headers=self.headers,
                meta={
                    "province": response.meta.get("province"),
                    "city": response.meta.get("city"),
                    "proxy": self.settings.get("PROXY"),
                },
            )
        next_pages = response.xpath(
            '//div[@data-testid="paginationContainer"]//a/@href'
        ).getall()
        for next_page in next_pages:
            self.headers["user-agent"] = user_agent_rotator.get_random_user_agent()
            next_page_url = response.urljoin(next_page)
            # self.logger.info(f"Next Page: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_listing,
                headers=self.headers,
                meta={
                    "province": response.meta.get("province"),
                    "city": response.meta.get("city"),
                    "proxy": self.settings.get("PROXY"),
                },
            )
        if "?page" not in response.url or True:  # load extra urls for all pages
            sub_url = response.url.split("?")[0].split("/")[-1]
            if sub_url not in self.groupids_2_suburl:
                self.groupids_2_suburl[sub_url] = set(group_ids)
            else:
                self.groupids_2_suburl[sub_url].update(group_ids)
            try:
                # self.headers3['user-agent'] = user_agent_rotator.get_random_user_agent()
                # get cookies from response
                cookies = response.headers.getlist("Set-Cookie")
                # convert cookies to string
                cookies = [cookie.decode("utf-8") for cookie in cookies]

                cookies = [cookie.split(";")[0] for cookie in cookies]
                cookies = "; ".join(cookies)

                headers = self.headers.copy()
                headers[
                    "user-agent"
                ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                headers["referer"] = response.url
                headers["cookie"] = cookies
                # get token
                session = requests.Session()

                resps = session.get(
                    "https://www.zumper.com/api/t/1/bundle",
                    headers=self.headers,
                    proxies=self.proxies,
                )
                xz_token = json.loads(resps.text)["xz_token"]
                csrf_token = json.loads(resps.text)["csrf"]
                headers = self.headers3.copy()
                headers["referer"] = response.url
                headers["x-zumper-xz-token"] = xz_token
                headers["x-csrftoken"] = csrf_token

                json_data = self.json_data.copy()
                json_data["url"] = sub_url
                json_data["excludeGroupIds"] = list(self.groupids_2_suburl[sub_url])
                resp = session.post(
                    "https://www.zumper.com/api/t/1/pages/listables",
                    json=json_data,
                    headers=headers,
                    proxies=self.proxies,
                )
                datas = json.loads(resp.text)
                datas = datas["listables"]
                for item in datas:
                    detail_url = item["url"]
                    # group_id
                    group_id = item["group_id"]
                    self.groupids_2_suburl[sub_url].add(group_id)
                    detail_url = response.urljoin(detail_url)
                    self.logger.info(f"Detail: {detail_url}")

                    yield scrapy.Request(
                        url=detail_url,
                        callback=self.parse_detail,
                        headers=self.headers,
                        meta={
                            "province": response.meta.get("province"),
                            "city": response.meta.get("city"),
                            "proxy": self.settings.get("PROXY"),
                        },
                    )

            except Exception as e:
                self.logger.info(f"Error: {sub_url} {e}")

    def parse_detail(self, response):
        building_name = response.xpath("//h1/text()").get("").strip()
        address_unformat = (
            response.xpath('//span[contains(@class,"Header_headerAddress")]/text()')
            .get("")
            .strip()
        )
        if not address_unformat:
            # '750 Bridge Lake Dr, Winnipeg, MB R3Y 0Y8'
            address_unformat = (
                response.xpath('//*[@data-testid="address"]/h1/text()').get("").strip()
            )

        # get the json data
        # window.__PRELOADED_STATE__
        json_data = json.loads(
            response.xpath(
                '//script[contains(text(),"window.__PRELOADED_STATE__")]/text()'
            )
            .get("")
            .strip(";")
            .strip()
            .split("=")[1]
            .split(";")[0]
        )

        # try to get the neighbourhood
        try:
            neighbourhood = json_data["detail"]["entity"]["data"]["neighborhood"][
                "name"
            ]
        except:
            neighbourhood = ""
        try:
            city = json_data["detail"]["entity"]["data"]["neighborhood"]["city"]
        except:
            # try to get the city from the unformatted address
            try:
                city = address_unformat.split(",")[1].strip()
            except:
                city = ""

        try:
            province = json_data["detail"]["entity"]["data"]["neighborhood"]["state"]
        except:
            try:
                province = address_unformat.split(",")[2].strip().split(" ")[0]
            except:
                province = ""

        try:
            street = json_data["detail"]["entity"]["data"]["street"]
        except:
            try:
                street = address_unformat.split(",")[0].strip()
            except:
                street = ""

        try:
            house_number = json_data["detail"]["entity"]["data"]["house"]
        except:
            # house number is not tricky from unformatted address
            house_number = ""
        try:
            address = json_data["detail"]["entity"]["data"]["formatted_address"]
        except:
            address = ""

        try:
            agent_name = json_data["detail"]["entity"]["data"]["agent_name"]
        except:
            agent_name = ""

        try:
            brokerage_name = json_data["detail"]["entity"]["data"]["brokerage_name"]
        except:
            brokerage_name = ""

        try:
            website = json_data["detail"]["entity"]["data"]["homepage"]
        except:
            website = ""
        building_ameneties = []
        unit_ameneties = []
        try:
            ameneties = json_data["detail"]["entity"]["data"]["amenity_groups"]
        except:
            ameneties = []
        if ameneties:
            for amenety in ameneties:
                amenety_data = ameneties[amenety]
                if amenety_data["group"] == 3:
                    building_ameneties.append(amenety)

            for amenety in ameneties:
                amenety_data = ameneties[amenety]
                if amenety_data["group"] == 1:
                    unit_ameneties.append(amenety)

        try:
            building_id = int(json_data["detail"]["entity"]["data"]["building_id"])
        except:
            try:
                building_id = int(response.text.split('"listing_id":')[1].split(",")[0])
            except:
                building_id = ""
                return  # if no building id, then return because this is a hidden listing

        geo = json.loads(
            response.xpath('//*[@id="schema-json"]/text()').get("").strip()
        )

        try:
            lat = geo["geo"]["latitude"]
        except:
            lat = ""
        try:
            lng = geo["geo"]["longitude"]
        except:
            lng = ""
        try:
            parking = json_data["detail"]["entity"]["data"]["parking"]
        except:
            parking = ""
        try:
            specials = json_data["detail"]["entity"]["data"]["specials"]
        except:
            specials = ""
        if specials:
            specials = ", ".join(specials)
        else:
            specials = ""
        try:
            promotion_type = json_data["detail"]["entity"]["data"]["promotion_type"]
        except:
            promotion_type = ""

        floor_data = []
        floor_plans = response.xpath('//*[@id="floorplans"]/div[@class="css-0"]')
        try:
            floor_plans_json = json_data["detail"]["entity"]["data"][
                "floorplan_listings"
            ]
        except:
            floor_plans_json = []
        for floor_plan in floor_plans_json:
            # price = floor_plan.xpath('.//div[contains(text(),"$")]/text()').getall()[-1]
            price1 = floor_plan["min_price"]
            price2 = floor_plan["max_price"]

            try:
                bedrooms = floor_plan["bedrooms"]
            except:
                bedrooms = ""

            bathrooms = floor_plan["bathrooms"]
            if bedrooms == None:
                continue
            half_bathrooms = floor_plan["half_bathrooms"]
            if half_bathrooms:
                bathrooms = float(bathrooms) + 0.5

            sqft = floor_plan["square_feet"]
            if not bedrooms and not bathrooms and not sqft:
                continue
            floor_data.append(
                {
                    "url": response.url,
                    "price1": price1,
                    "price2": price2,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "area_ave": sqft,
                    "building": building_name,
                    "address": address_unformat,
                    "neighbourhood": neighbourhood,
                    "house_number": house_number,
                    "street": street,
                    "city": city,
                    "province": province,
                    "website": website,
                    "agent_name": agent_name,
                    "brokerage_name": brokerage_name,
                    "building_amenities": ", ".join(building_ameneties),
                    "unit_amenities": " ,".join(unit_ameneties),
                    "building_latitude": lat,
                    "building_longitude": lng,
                    "formatted_address": address,
                    "parking": parking,
                    "specials": specials,
                    "promotion_type": promotion_type,
                }
            )

        if not floor_plans_json:
            # attempt cases like this https://www.zumper.com/address/10534-151-st-nw-edmonton-ab-t5p-1v3-can
            floor_plans = response.xpath(
                '//*[@id="pa-units--tabpanel-0"]/div[@class="css-1j3cjrm"]'
            )

            for floor_plan in floor_plans:
                if (
                    "Occupied" in floor_plan.get()
                ):  ##### COMMENT THESE LINES OUT IF YOU WANT TO SCRAPE OCCUPIED UNITS
                    continue
                try:
                    price1 = (
                        floor_plan.xpath('.//p[contains(text(),"$")]/text()')
                        .getall()[0]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    if price1.isdigit():
                        price1 = int(price1)
                except:
                    price1 = None
                try:
                    price2 = (
                        floor_plan.xpath('.//p[contains(text(),"$")]/text()')
                        .getall()[-1]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    if price2.isdigit():
                        price2 = int(price2)
                except:
                    price2 = None
                try:
                    bedrooms = (
                        floor_plan.xpath('.//p[contains(text(),"Bed")]/text()')
                        .getall()[-1]
                        .replace("Bed", "")
                        .strip()
                        .replace("s", "")
                        .strip()
                    )
                    if bedrooms.isdigit():
                        bedrooms = float(bedrooms)

                    if bedrooms.is_integer():
                        bedrooms = int(bedrooms)
                except:
                    bedrooms = None

                if not bedrooms and (
                    "studio" in floor_plan.get().lower()
                    or "bachelor" in floor_plan.get().lower()
                ):
                    bedrooms = 0
                if bedrooms == None:
                    continue
                try:
                    bathrooms = (
                        floor_plan.xpath('.//p[contains(text(),"Bath")]/text()')
                        .getall()[-1]
                        .replace("Bath", "")
                        .strip()
                        .replace("s", "")
                        .strip()
                    )
                    # 1 Full, 1 Half Bath
                    if "Full" in bathrooms or "Half" in bathrooms:
                        full_bathrooms = 0
                        half_bathrooms = 0
                        if "Full" in bathrooms:
                            # use regex to get the number before Full
                            full_bathrooms = float(
                                re.search(r"(\d+) Full", bathrooms).group(1)
                            )
                        if "Half" in bathrooms:
                            half_bathrooms = float(
                                re.search(r"(\d+) Half", bathrooms).group(1)
                            )
                        bathrooms = str(full_bathrooms + (half_bathrooms * 0.5))
                    if bathrooms.isdigit():
                        bathrooms = float(bathrooms)

                    if bathrooms.is_integer():
                        bathrooms = int(bathrooms)
                except:
                    bathrooms = None

                try:
                    sqft = (
                        floor_plan.xpath('.//p[contains(text(),"sqft")]/text()')
                        .getall()[-1]
                        .replace("sqft", "")
                        .strip()
                        .replace(",", "")
                    )
                    if sqft.isdigit():
                        sqft = int(sqft)
                except:
                    sqft = None
                if not bedrooms and not bathrooms and not sqft:
                    continue
                floor_data.append(
                    {
                        "url": response.url,
                        "price1": price1,
                        "price2": price2,
                        "bedrooms": bedrooms,
                        "bathrooms": bathrooms,
                        "area_ave": sqft,
                        "building": building_name,
                        "address": address_unformat,
                        "neighbourhood": neighbourhood,
                        "house_number": house_number,
                        "street": street,
                        "city": city,
                        "province": province,
                        "website": website,
                        "agent_name": agent_name,
                        "brokerage_name": brokerage_name,
                        "building_amenities": ", ".join(building_ameneties),
                        "unit_amenities": " ,".join(unit_ameneties),
                        "building_latitude": lat,
                        "building_longitude": lng,
                        "formatted_address": address,
                        "parking": parking,
                        "specials": specials,
                        "promotion_type": promotion_type,
                    }
                )
        else:
            floor_plans = ["dont scrape if floor_plans_json is not empty"]
        if not floor_plans:
            # try to get the data from top of page
            try:
                # '4 bed • 3 bath • 2,200 sqft • $2,700'
                subtitle = (
                    response.xpath(
                        '//*[@data-testid="address"]/following-sibling::*//p//text()'
                    )
                    .get("")
                    .strip()
                )
            except:
                subtitle = ""
            try:
                bedrooms = (
                    [x for x in subtitle.split("•") if "bed" in x.lower()][0]
                    .replace("bed", "")
                    .strip()
                )
            except:
                bedrooms = (
                    response.xpath(
                        '//div[contains(@class,"SummaryIcon_summaryText")][contains(text(),"Bed")]/text()'
                    )
                    .get("")
                    .strip()
                    .replace("Beds", "")
                    .replace("Bed", "")
                    .strip()
                )
            try:
                bedrooms = int(bedrooms)
            except:
                bedrooms = None

            try:
                bathrooms = (
                    [x for x in subtitle.split("•") if "bath" in x.lower()][0]
                    .replace("bath", "")
                    .strip()
                )
            except:
                bathrooms = (
                    response.xpath(
                        '//div[contains(@class,"SummaryIcon_summaryText")][contains(text(),"Bathroom")]/text()'
                    )
                    .get("")
                    .strip()
                    .replace("Bathrooms", "")
                    .replace("Bathroom", "")
                    .strip()
                )
                if not bathrooms:
                    bathrooms = (
                        response.xpath(
                            '//div[contains(@class,"SummaryIcon_summaryText")][contains(text(),"Bath")]/text()'
                        )
                        .get("")
                        .strip()
                        .replace("Baths", "")
                        .replace("Bath", "")
                        .strip()
                    )
            try:
                # 1 Full, 1 Half Bath
                if "Full" in bathrooms or "Half" in bathrooms:
                    full_bathrooms = 0
                    half_bathrooms = 0
                    if "Full" in bathrooms:
                        # use regex to get the number before Full
                        full_bathrooms = float(
                            re.search(r"(\d+) Full", bathrooms).group(1)
                        )
                    if "Half" in bathrooms:
                        half_bathrooms = float(
                            re.search(r"(\d+) Half", bathrooms).group(1)
                        )
                    bathrooms = str(full_bathrooms + (half_bathrooms * 0.5))
                if bathrooms.isdigit():
                    bathrooms = float(bathrooms)
                bathrooms = float(bathrooms)
                if bathrooms.is_integer():
                    bathrooms = int(bathrooms)
            except:
                bathrooms = None

            try:
                sqft = (
                    [x for x in subtitle.split("•") if "sqft" in x.lower()][0]
                    .replace("sqft", "")
                    .replace(",", "")
                    .strip()
                )
            except:
                sqft = (
                    response.xpath(
                        '//div[contains(@class,"SummaryIcon_summaryText")][contains(text(),"ft²")]/text()'
                    )
                    .get("")
                    .strip()
                    .replace("ft²", "")
                    .replace(",", "")
                    .strip()
                )
            try:
                sqft = int(sqft)
            except:
                sqft = None
            try:
                price = (
                    [x for x in subtitle.split("•") if "$" in x.lower()][0]
                    .replace("$", "")
                    .replace(",", "")
                    .strip()
                )
            except:
                price = (
                    response.xpath('//div[contains(@class,"Header_price__")]/text()')
                    .get("")
                    .replace("$", "")
                    .replace(",", "")
                    .strip()
                )

            try:
                price = float(price)
                if price.is_integer():
                    price = int(price)
            except:
                price = None
            if not bedrooms and not bathrooms and not sqft:
                return
            if not price:
                return
            floor_data.append(
                {
                    "url": response.url,
                    "price1": price,
                    "price2": price,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "area_ave": sqft,
                    "building": building_name,
                    "address": address_unformat,
                    "neighbourhood": neighbourhood,
                    "house_number": house_number,
                    "street": street,
                    "city": city,
                    "province": province,
                    "website": website,
                    "agent_name": agent_name,
                    "brokerage_name": brokerage_name,
                    "building_amenities": ", ".join(building_ameneties),
                    "unit_amenities": " ,".join(unit_ameneties),
                    "building_latitude": lat,
                    "building_longitude": lng,
                    "formatted_address": address,
                    "parking": parking,
                    "specials": specials,
                    "promotion_type": promotion_type,
                }
            )
        body = (
            '{"group_id":"-'
            + str(building_id)
            + '","lat":'
            + str(lat)
            + ',"lng":'
            + str(lng)
            + "}"
        )
        url = "https://www.zumper.com/api/x/1/location_scores"
        self.headers2["user-agent"] = user_agent_rotator.get_random_user_agent()
        yield scrapy.Request(
            url=url,
            method="POST",
            callback=self.parse_scores,
            headers=self.headers2,
            body=body,
            meta={
                "proxy": self.settings.get("PROXY"),
                "floor_data": floor_data,
            },
        )

    def parse_scores(self, response):
        floor_data = response.meta.get("floor_data")
        try:
            json_data = json.loads(response.body)["scores_json"]
        except:
            json_data = {}

        try:
            pedestrian_friendly = round(
                float(json_data["pedestrian_friendly"]["value"]) * 2
            )
        except:
            pedestrian_friendly = ""
        try:
            car_friendly = round(float(json_data["car_friendly"]["value"]) * 2)
        except:
            car_friendly = ""

        try:
            cycling_friendly = round(float(json_data["cycling_friendly"]["value"]) * 2)
        except:
            cycling_friendly = ""

        try:
            transit_friendly = round(float(json_data["transit_friendly"]["value"]) * 2)
        except:
            transit_friendly = ""

        try:
            groceries = round(float(json_data["groceries"]["value"]) * 2)
        except:
            groceries = ""

        try:
            shopping = round(float(json_data["shopping"]["value"]) * 2)
        except:
            shopping = ""

        try:
            cafes = round(float(json_data["cafes"]["value"]) * 2)
        except:
            cafes = ""

        try:
            restaurants = round(float(json_data["restaurants"]["value"]) * 2)
        except:
            restaurants = ""

        for floor in floor_data:
            # replace all 0 with None
            for key, value in floor.items():
                if value == 0:
                    floor[key] = None
            yield {
                **floor,
                "pedestrian_friendly_score": pedestrian_friendly,
                "car_friendly_score": car_friendly,
                "cycling_friendly_score": cycling_friendly,
                "transit_friendly_score": transit_friendly,
                "groceries_score": groceries,
                "shopping_score": shopping,
                "cafes_score": cafes,
                "restaurants_score": restaurants,
            }
