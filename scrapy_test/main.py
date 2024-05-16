import requests
from lxml import etree
import datetime
from loguru import logger
import asyncio

class Base:
    def __init__(self,input_time):
        self.total = 0
        self.page = 1
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.input_time = input_time
        self.task = []
    async def main(self):
        await self.run()
        await asyncio.gather(*self.task)
    async def run(self):
        # 首页数据返回
        index_json = requests.get(url=f'https://www.gd.gov.cn/gkmlpt/api/all/5?page={self.page}&sid=2',headers=self.headers).json()
        self.total = index_json['total']
        articles_list = index_json['articles']
        for info in articles_list:
            # 发布日期
            create_time = datetime.datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d')
            # 判断日期
            if self.check(create_time):
                detail_url = info['url']
                logger.info(f'加入协程:{self.page},successfully')
                self.task.append(self.detail_path(detail_url))
        if self.total <= self.page*100:
            return
        logger.info('当前任务不在日期范围')
        self.page+=1
        await self.run()
    # 日期比较
    def check(self,create_time):
        s = self.input_time.split('-')
        # 将日期字符串转换为 datetime 对象
        create_time_ = datetime.datetime.strptime(create_time, '%Y-%m-%d')
        date1 = datetime.datetime.strptime(s[0], '%Y%m%d')
        date2 = datetime.datetime.strptime(s[1], '%Y%m%d')
        if date1 <= create_time_ <= date2:
            return True
        return False


    # xpath解析
    async def detail_path(self,url):
        res_text = requests.get(url=url,headers=self.headers).text
        three = etree.HTML(res_text)
        # xpath提取所有信息
        text_list = three.xpath("//div[@class='classify']//td/span/text()")
        # 正文文本
        content_text = three.xpath("//div[@class='content']//p//text()")
        # 附件链接
        content_url = three.xpath("//div[@class='article-content']//a/@href")
        content_url = content_url if content_url else '暂无'
        # logger.info(text_list)
        # logger.info(content_text)
        # logger.info(content_url)
        # logger.info('\n')
        infos = {
            '索引号':text_list[0],
            '发布机构':text_list[2],
            '发布日期':text_list[-1],
            '政策标题':text_list[4],
            '政策正文文本':content_text,
            '政策正文附件链接':content_url
        }
        logger.info(infos)

if __name__ == '__main__':
    input_time = input('请输入日期范围从小到大,例(20220101-20230601):')
    x = Base(input_time)
    asyncio.run(x.main())