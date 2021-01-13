
import os
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def main():

    search_key = input('検索ワードを入力してください：')
    try:
        search_max = int(input('最大取得数を設定してください（初期設定100社、50社単位で切り上げ）：'))
    except:
        search_max = 100
    print('キーワード：{}、取得数：{}'.format(search_key, search_max))

    # Chromeを立ち上げて、マイナビにアクセス
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    driver.get('https://tenshoku.mynavi.jp/')
    time.sleep(3)
    print('マイナビをオープン')

    getSearch(search_key, driver)
    print('検索を実施')

    df = collectInfo(search_max, driver)
    print('求人情報を取得')

    df.to_csv('マイナビ_{}.csv'.format(search_key), index=False, encoding='utf-8_sig')
    print('CSVに保存')

def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

def getSearch(search_key, driver):
    # ポップアップを消す
    try:
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(3)
    except:
        pass

    # 検索ワードを検索ボックスに入れる
    searchBox = driver.find_element_by_class_name('topSearch__text')
    searchBox.send_keys(search_key)

    # 検索結果ページを取得
    driver.find_element_by_class_name('topSearch__button').click()

def recruitInfo(driver):
    # 会社名を取得し、データフレームに格納
    company_names = driver.find_elements_by_class_name('cassetteRecruit__name')
    name_list = [name.text for name in company_names]

    df_tmp = pd.DataFrame(name_list).replace(' ', '')
    df_name = df_tmp[0].str.split('|', 1, expand=True)
    df_name.columns = ['会社名', '概要']

    # 求人詳細テーブルを取得し、データフレームに格納
    header = ['仕事内容', '対象となる方', '勤務地', '給与', '初年度年収']
    bodies =[]

    for table in driver.find_elements_by_css_selector('.cassetteRecruit__content .tableCondition'):
        body = [body.text for body in table.find_elements_by_css_selector('td')]
        #初年度年収がない場合はブランクに     
        if len(body) < 5:
            body.append('')
        bodies.append(body)

    df_condition = pd.DataFrame(bodies, columns=header)
    # 会社名DFと求人詳細DFを結合
    df = pd.concat([df_name, df_condition], axis=1)

    return df

def collectInfo(search_max, driver):
    # 全検索結果or取得数上限まで
    df = pd.DataFrame()
    i = 0
    while i < search_max / 50:
        df = pd.concat([df, recruitInfo(driver)], ignore_index=True)

        try:
            driver.find_element_by_css_selector('.pager__item--active + .pager__item').click()
        except:
            break

        i += 1
    return df

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()

