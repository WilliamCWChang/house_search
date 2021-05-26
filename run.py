import csv
import requests
from bs4 import BeautifulSoup
import toml
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


def get_headers(user_data):

    client = requests.session()
    LOGIN_URL = "https://www.591.com.tw/user-login.html?"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    }
    data = {
        "user.username": user_data["username"],
        "user.pwd": user_data["password"],
        "user.verifyCode": "",
        "cookie": "on",
        "login_sub": "",
        "module": " user",
        "user.bindCode": "",
        "action": " login",
        "redirect": "",
        "isShowCode": "",
    }
    response = client.get(LOGIN_URL)
    response = client.post(LOGIN_URL, data=data, headers=headers, verify=False,)
    assert response.status_code == 200
    headers["cookie"] = "; ".join([x.name + "=" + x.value for x in response.cookies])

    response = client.get(
        "https://www.591.com.tw/index.php?module=userCenter&action=newGuest",
        params={"module": "userCenter", "action": "newGuest"},
        headers=headers,
        verify=False,
    )
    assert response.status_code == 200
    headers["cookie"] = "; ".join([x.name + "=" + x.value for x in response.cookies])

    urls = [
        "https://rent.591.com.tw/home/rent/localStorage",
        "https://sale.591.com.tw/home/sale/localStorage",
        "https://business.591.com.tw/home/business/localStorage",
    ]
    for url in urls:
        response = client.get(url, headers=headers, verify=False)
        assert response.status_code == 200
        headers["cookie"] = "; ".join(
            [x.name + "=" + x.value for x in response.cookies]
        )

    response = requests.get("https://sale.591.com.tw/", headers=headers)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text)
    headers["X-CSRF-TOKEN"] = soup.find("meta", {"name": "csrf-token"})["content"]
    return headers


def get_json(headers, payload):
    TARGET_URL = "https://sale.591.com.tw/home/search/list"
    payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
    response = requests.get(TARGET_URL, headers=headers, params=payload_str)
    assert response.status_code == 200
    return response.json()["data"]["house_list"]


def save_to_csv_file(csv_filename, dict_data):
    csv_columns = [
        "refreshtime",
        "houseage",
        "community_name",
        "unitprice",
        "mainarea",
        "title",
        "has_carport",
        "room",
        "floor",
        "area",
        "address",
        "browsenum",
        "price",
        "tag",
        "section_name",
        "houseid",
        "isnew",
        "filename",
        "type",
        "kind",
        "kind_name",
        "shape_name",
        "region_name",
        "photoNum",
        "carttype",
        "cartmodel",
        "is_video",
        "is_full",
        "photo_url",
        "nick_name",
        "housetype",
        "posttime",
        "showhouseage",
        "unit_price",
        "showprice",
        "is_oversea",
        "is_carport",
        "original_price",
        "is_down_price",
        "down_price_percent",
        "is_combine",
        "isvip",
        "is_hurry_price",
        "saletype",
        "delivery",
        "fci_pai",
        "pc_good_house",
        "good_house",
        "mvip",
        "m_recom",
        "user_id",
        "community_link",
    ]
    with open(csv_filename, "w", newline="", encoding="UTF-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)


def get_total_house(house_data, headers):
    payload = {
        "type": house_data["type"],
        "shType": house_data["shType"],
        "regionid": house_data["regionid"],
        "section": house_data["section"],
        "area": house_data["area"],
        "price": house_data["price"],
        "houseage": house_data["houseage"],
    }

    dict_data = []
    number = 1
    index = 0
    while number:
        payload["firstRow"] = str(index * 30)
        r = get_json(headers, payload)
        number = len(r)
        index += 1
        dict_data.extend(r)
        print(f"index = {index}, number = {number}")
    print(len(dict_data))
    return dict_data


def house_filter(h, prefer_road, not_prefer_community):
    for road in prefer_road:
        if road in h["address"]:
            if h["community_name"] not in not_prefer_community:
                if int(h["mainarea"]) < 1 or int(h["mainarea"]) > 20:
                    return h
    return None


user_data = toml.load("user.toml")
house_data = toml.load("house.toml")
prefer_road = house_data["prefer_road"]
not_prefer_community = house_data["not_prefer_community"]
house_result = get_total_house(house_data, get_headers(user_data))
house_result2 = []
for h in house_result:
    h["houseid"] = f"https://sale.591.com.tw/home/house/detail/2/{h['houseid']}.html"
    if house_filter(h, prefer_road, not_prefer_community):
        house_result2.append(h)

print(f"house after fileter =  {len(house_result2)}")

save_to_csv_file("new.csv", house_result2)
