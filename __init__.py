import scrapy


class DangdangSpider(scrapy.Spider):
    name = "dangdang"
    allowed_domains = ["search.dangdang.com"]
    start_urls = [
        "http://search.dangdang.com/?key=书籍"  # 替换为你的关键词
    ]

    def parse(self, response):
        for item in response.xpath("//ul[@id='component_59']//li"):
            title = item.xpath(".//p[@class='name']/a/@title").get()
            price = item.xpath(".//p[@class='price']/span[@class='search_now_price']/text()").get()

            if title and price:
                yield {
                    "title": title.strip(),
                    "price": price.strip(),
                }
