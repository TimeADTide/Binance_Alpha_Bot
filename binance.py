import requests
import time
from decimal import Decimal, ROUND_HALF_UP
import random
import json


# **************[1. 获取购买当前数量 ]**********************
def buy_get_quote(buy_num, headers, cookies):
    print("1.获取预计购买当前数量----开始：")
    json_data = {'fromToken': 'USDC', 'fromContractAddress': '', 'fromBinanceChainId': '56', 'fromCoinAmount': buy_num, 'toToken': 'ZKJ', 'toContractAddress': '0xc71b5f631354be6853efe9c3ab6b9590f8302e81', 'toBinanceChainId': '56', 'priorityMode': 'priorityOnCustom', 'customNetworkFeeMode': 'priorityOnPrice', 'customSlippage': '0.05', }
    response = requests.post('https://www.binance.com/bapi/defi/v1/private/wallet-direct/swap/cex/get-quote', cookies=cookies, headers=headers, json=json_data, )
    # print("1.获取预计购买当前数量----结束：" + response.text)
    response_json = response.json()
    is_success = response_json.get('success', False)
    if not is_success:
        print("1.获取预计购买当前数量失败", response.text)
    coin_amount = response_json.get('data', {}).get('toCoinAmount')
    print("1.获取预计购买当前数量：" + coin_amount)
    extra = response_json.get('data', {}).get('extra')
    return coin_amount, extra


# **************[2. 购买 ]**********************
def buy(buy_num, coin_amount, extra, headers, cookies):
    print("2.购买----开始：")
    json_data = {'fromToken': 'USDC', 'fromBinanceChainId': '56', 'fromCoinAmount': buy_num, 'toToken': 'ZKJ', 'toContractAddress': '0xc71b5f631354be6853efe9c3ab6b9590f8302e81', 'toCoinAmount': str(Decimal(coin_amount)), 'priorityMode': 'priorityOnPrice', 'extra': extra, 'payMethod': 'FUNDING_AND_SPOT', }
    response = requests.post('https://www.binance.com/bapi/defi/v2/private/wallet-direct/swap/cex/buy/pre/payment', cookies=cookies, headers=headers, json=json_data, )
    response_json = response.json()
    is_success = response_json.get('success', False)
    if not is_success:
        print("2.购买失败", response.text)
    token_amount = response_json.get('data', {}).get('orderHistory', {}).get('toTokenAmount', 0)
    token_amount_decimal = Decimal(token_amount)
    buy_count_count = token_amount_decimal.quantize(Decimal("0.0000000000000000"), rounding=ROUND_HALF_UP)
    print("2.购买数量：" + str(buy_count_count))
    return buy_count_count


# **************[3. 获取售卖当前价格 ]**********************
def sell_get_quote(coin_amount, headers, cookies):
    print("3.获取预计售卖当前价格----开始：")
    json_data = {'fromToken': 'ZKJ', 'fromContractAddress': '0xc71b5f631354be6853efe9c3ab6b9590f8302e81', 'fromBinanceChainId': '56', 'fromCoinAmount': str(coin_amount), 'toToken': 'USDC', 'toContractAddress': '', 'toBinanceChainId': '56', 'priorityMode': 'priorityOnCustom', 'customNetworkFeeMode': 'priorityOnPrice', 'customSlippage': '0.05', }
    response = requests.post('https://www.binance.com/bapi/defi/v1/private/wallet-direct/swap/cex/get-quote', cookies=cookies, headers=headers, json=json_data, )
    response_json = response.json()
    is_success = response_json.get('success', False)
    if not is_success:
        print("3.获取预计售卖当前价格失败", response.text)
    coin_price = response_json.get('data', {}).get('toCoinAmount')
    print("3.获取预计售卖当前价格：" + coin_price)
    extra = response_json.get('data', {}).get('extra')
    return coin_price, extra


def sell(from_coin_amount, to_coin_price, extra, headers, cookies):
    print("4.售卖----开始：", from_coin_amount)
    json_data = {'fromToken': 'ZKJ', 'fromContractAddress': '0xc71b5f631354be6853efe9c3ab6b9590f8302e81', 'fromBinanceChainId': '56', 'fromCoinAmount': str(from_coin_amount), 'toToken': 'USDC', 'toBinanceChainId': '56', 'toCoinAmount': str(Decimal(to_coin_price)), 'priorityMode': 'priorityOnCustom', 'extra': extra, }
    response = requests.post('https://www.binance.com/bapi/defi/v2/private/wallet-direct/swap/cex/sell/pre/payment', cookies=cookies, headers=headers, json=json_data, )
    response_json = response.json()
    is_success = response_json.get('success', False)
    if not is_success:
        print("4.售卖失败", response.text)
    token_price = response_json.get('data', {}).get('toTokenAmount', 0)
    print("4.售卖价格：" + token_price)
    return token_price


def extract_headers_simple(text):
    start = text.find('"headers":') + len('"headers":')
    end = text.find('},', start) + 1
    headers_str = text[start:end]
    try:
        header_json = json.loads(headers_str)
        cookie_str = header_json['cookie']
        cookie_split = cookie_str.split(';')
        cookie_dict = {}
        for cookie in cookie_split:
            cookie = cookie.strip()
            if cookie:
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookie_dict[key.strip()] = value.strip()
        del header_json["cookie"]
        return header_json, cookie_dict
    except json.JSONDecodeError:
        print("JSON 解析错误")
    return None


def transaction():
    # 从文件读取文本
    for_num = int(input("请输入循环次数: "))
    buy_price = float(input("请输入购买金额: "))
    file_path = 'header.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.read().strip()
    headers, cookies = (extract_headers_simple(texts))
    i = 0
    while i < for_num:
        print(">>>>>>>>>>>>>>>>>>>第" + str(i + 1) + "笔交易<<<<<<<<<<<<<<<<<<<<")
        one_coin_amount, one_extra = buy_get_quote(buy_price, headers, cookies)
        time_sleep = random.randint(2, 3)
        print("休眠" + str(time_sleep) + "s")
        time.sleep(time_sleep)
        two_buy_coin_count = buy(buy_price, one_coin_amount, one_extra, headers, cookies)
        time_sleep = random.randint(5, 8)
        print("休眠" + str(time_sleep) + "s")
        time.sleep(time_sleep)
        three_coin_price, three_extra = sell_get_quote(two_buy_coin_count, headers, cookies)
        time_sleep = random.randint(2, 3)
        print("休眠" + str(time_sleep) + "s")
        time.sleep(time_sleep)
        sell(two_buy_coin_count, three_coin_price, three_extra, headers, cookies)
        time_sleep = random.randint(10, 15)
        time.sleep(time_sleep)
        i += 1


if __name__ == "__main__":
    transaction()
