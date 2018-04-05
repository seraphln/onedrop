# coding=utf-8


# 百度指数的抓取
# 截图教程：http://www.myexception.cn/web/2040513.html
#
# 登陆百度地址：https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F
# 百度指数地址：http://index.baidu.com

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import pytesseract

from http import get_task, update_task


# 打开浏览器
def openbrowser():
    # https://passport.baidu.com/v2/?login
    url = "https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F"
    # 打开谷歌浏览器
    # Firefox()
    # Chrome()
    browser = webdriver.Chrome()
    # 输入网址
    browser.get(url)
    # 打开浏览器时间
    # print("等待10秒打开浏览器...")
    # time.sleep(10)

    # 这里需要手工输入用户名和密码，因为验证码目前还没有解决
    select = raw_input("请观察浏览器网站是否已经登陆(y/n)：")

    while 1:
        if select == "y" or select == "Y":
            print("登陆成功！")
            print("准备打开新的窗口...")
            break

        elif select == "n" or select == "N":
            selectno = raw_input("账号密码错误请按0，验证码出现请按1...")
            # 账号密码错误则重新输入
            if selectno == "0":

                # 找到id="TANGRAM__PSP_3__userName"的对话框
                # 清空输入框
                browser.find_element_by_id("TANGRAM__PSP_3__userName").clear()
                browser.find_element_by_id("TANGRAM__PSP_3__password").clear()

                # 输入账号密码
                account = []
                try:
                    fileaccount = open("../baidu/account.txt", encoding='UTF-8')
                    accounts = fileaccount.readlines()
                    for acc in accounts:
                        account.append(acc.strip())
                    fileaccount.close()
                except Exception as err:
                    print(err)
                    input("请正确在account.txt里面写入账号密码")
                    exit()

                browser.find_element_by_id("TANGRAM__PSP_3__userName").send_keys(account[0])
                browser.find_element_by_id("TANGRAM__PSP_3__password").send_keys(account[1])
                # 点击登陆sign in
                # id="TANGRAM__PSP_3__submit"
                browser.find_element_by_id("TANGRAM__PSP_3__submit").click()

            elif selectno == "1":
                # 验证码的id为id="ap_captcha_guess"的对话框
                input("请在浏览器中输入验证码并登陆...")
                select = raw_input("请观察浏览器网站是否已经登陆(y/n)：")

        else:
            print("请输入y或者n")
            select = raw_input("请观察浏览器网站是否已经登陆(y/n)：")

    return browser


def get_detail_index(browser, keyword, x_0, y_0, num, day, xoyelement, dtype="all"):
    """
        获取具体分类数据

        Args:
            @param browser: selenium的实例
            @type browser: selenium.webdriver

            @param keyword: 要采集的关键词
            @type keyword: String

            @param x_0: 起始x轴坐标
            @type x_0: Int

            @param y_0: 起始y轴坐标
            @type y_0: Int

            @param num: 请求数量
            @type num: Int

            @param day: 采集的天数
            @type day: Int

            @param xoyelement: 趋势div块
            @type xoyelement: selenium.selector

            @param dtype: 搜索指数趋势类别
            @type dtype: String (all, pc, wise)

        Returns:
            []
    """

    # 储存数字的数组
    # 采集整体趋势、pc趋势、移动端趋势
    index = []
    if dtype != "all":
        # 如果不是全部，则需要先点击指定的分类
        dtype_sbt = browser.find_element_by_xpath("//ul[@class='tab-hd trendtype']/li[@data-value='%s']" % dtype)
        dtype_sbt.click()
    try:
        # webdriver.ActionChains(driver).move_to_element().click().perform()
        # 只有移动位置xoyelement[2]是准确的
        for i in range(day):
            # 坐标偏移量???
            ActionChains(browser).move_to_element_with_offset(xoyelement, x_0, y_0).perform()

            # 构造规则
            if day == 7:
                x_0 = x_0 + 202.33
            elif day == 30:
                x_0 = x_0 + 41.68
            elif day == 90:
                x_0 = x_0 + 13.64
            elif day == 180:
                x_0 = x_0 + 6.78
            elif day == 1000000:
                x_0 = x_0 + 3.37222222
            time.sleep(2)
            # <div class="imgtxt" style="margin-left:-117px;"></div>
            imgelement = browser.find_element_by_xpath('//div[@id="viewbox"]')
            # 找到图片坐标
            locations = imgelement.location
            # 跨浏览器兼容
            scroll = browser.execute_script("return window.scrollY;")
            top = locations['y'] - scroll
            # 找到图片大小
            sizes = imgelement.size
            # 构造关键词长度
            add_length = (len(keyword) - 2) * sizes['width'] / 15
            # 构造指数的位置
            rangle = (int(locations['x'] + sizes['width'] / 4 + add_length), int(top + sizes['height'] / 2),
                      int(locations['x'] + sizes['width'] * 2 / 3), int(top + sizes['height']))
            # 截取当前浏览器
            path = "../baidu/" + str(num)
            browser.save_screenshot(str(path) + ".png")
            # 打开截图切割
            img = Image.open(str(path) + ".png")
            jpg = img.crop(rangle)
            jpg.save(str(path) + ".jpg")

            # 将图片放大一倍
            # 原图大小73.29
            jpgzoom = Image.open(str(path) + ".jpg")
            (x, y) = jpgzoom.size
            x_s = 146
            y_s = 58
            out = jpgzoom.resize((x_s, y_s), Image.ANTIALIAS)
            out.save(path + 'zoom.jpg', 'png', quality=95)

            # 图像识别
            try:
                image = Image.open(str(path) + "zoom.jpg")
                code = pytesseract.image_to_string(image)
                if code:
                    index.append(code)
                else:
                    index.append("")
            except:
                index.append("")
            num = num + 1

    except Exception as err:
        print(err)
        print(num)

    return index


def getindex(browser, keyword, day):
    """
    采集百度指数

    Args:
        @param browser: 浏览器实例
        @type browser: selenium.webdriver

        @param keyword: 需要采集的关键词
        @type keyword: String

        @param day: 采集的天数
        @type day: Int

    Returns:
        {keyword: index_lst}
    """

    # 进入百度指数页面
    browser.get("http://index.baidu.com")
    time.sleep(5)

    # 写入关键词并搜索
    browser.find_element_by_id("schword").clear()
    # 写入需要搜索的百度指数
    browser.find_element_by_id("schword").send_keys(keyword)

    # 点击搜索
    # <input type="submit" value="" id="searchWords" onclick="searchDemoWords()">
    browser.find_element_by_id("searchWords").click()

    # 等待5s，避免出现由于页面没有加载完毕导致抓取失败
    time.sleep(5)

    # 最大化窗口
    browser.maximize_window()
    time.sleep(2)

    # 构造天数
    sel = '//a[@rel="' + str(day) + '"]'
    browser.find_element_by_xpath(sel).click()

    # 太快了， 点击之后，sleep 2秒，防止太快，被认为是爬虫
    time.sleep(2)

    # 滑动思路：http://blog.sina.com.cn/s/blog_620987bf0102v2r8.html
    # 滑动思路：http://blog.csdn.net/zhouxuan623/article/details/39338511
    # 向上移动鼠标80个像素，水平方向不同
    # xoyelement = browser.find_element_by_xpath('//rect[@stroke="none"]')
    xoyelement = browser.find_elements_by_css_selector("#trend rect")[2]
    num, x_0, y_0 = 0, 1, 0

    dtypes = ["all", "pc", "wise"]

    results = []

    for dtype in dtypes:
        results.append(get_detail_index(browser, keyword, x_0, y_0, num, day, xoyelement, dtype))

    return results


def main():
    """
    1. 加载采集任务
    2. 采集数据
    3. 将数据回传给服务器
    """
    browser = openbrowser()
    time.sleep(2)
    # 这里开始进入百度指数
    # 新开一个窗口，通过执行js来新开一个窗口
    js = 'window.open("http://index.baidu.com");'
    browser.execute_script(js)
    # 新窗口句柄切换，进入百度指数
    # 获得当前打开所有窗口的句柄handles
    # handles为一个数组
    handles = browser.window_handles
    # print(handles)
    # 切换到当前最新打开的窗口
    browser.switch_to_window(handles[-1])

    counter = 0
    while 1:
        task = get_task()

        if not task:
            # 没有任务，则sleep 15s
            # 并且counter + 1，如果counter > 20，则认为没有任务，程序退出
            time.sleep(15)
            counter += 1
            if counter >= 20:
                break

        # 获取采集的关键词和天数
        keyword, day = task.get("keyword", ""), task.get("day", 7)
        results = getindex(browser, keyword, day)
        task["data"] = results

        update_task(task)
        counter = 0


if __name__ == "__main__":
    main()
