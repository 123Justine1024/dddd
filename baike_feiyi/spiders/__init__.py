import scrapy
import json


class FeiyiSpider(scrapy.Spider):
    name = "feiyi"
    allowed_domains = ["baike.baidu.com"]
    start_urls = ["https://baike.baidu.com/feiyi"]

    def parse(self, response):
        # 构造 POST 请求的目标 URL 和负载
        post_url = "https://baike.baidu.com/wikitag/api/getlemmas"
        payload = {
            "limit": 20,
            "timeout": 3000,
            "filterTags": '["71377",0]',
            "tagId": 71394,
            "fromLemma": False,
            "contentLength": 40,
            "page": 0
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://baike.baidu.com/feiyi",
            "Origin": "https://baike.baidu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        }

        yield scrapy.FormRequest(
            url=post_url,
            formdata={key: str(value) for key, value in payload.items()},
            headers=headers,
            callback=self.parse_projects
        )

    def parse_projects(self, response):
        # 解析 JSON 响应
        with open("debug_response.json", "w", encoding="utf-8") as f:
            f.write(response.text)  # 保存响应内容以调试
        data = json.loads(response.text)
        projects = data.get("lemmaList", [])  # 根据实际响应结构解析

        for project in projects[:5]:  # 只处理前 5 个项目
            title = project.get("title")
            detail_url = f"https://baike.baidu.com{project.get('lemmaUrl')}"
            yield scrapy.Request(detail_url, callback=self.parse_detail, meta={"title": title})

    def parse_projects(self, response):
        # 解析 JSON 响应
        data = json.loads(response.text)  # 将响应数据转为 Python 字典
        projects = data.get("lemmaList", [])  # 获取包含非遗项目的列表

        # 只处理前 5 个项目
        for project in projects[:5]:
            title = project.get("lemmaTitle")  # 获取词条标题
            description = project.get("lemmaDesc")  # 获取词条简介
            detail_url = project.get("lemmaUrl")  # 获取词条的详情页 URL

            # 调试：打印日志，确保遍历所有项目
            self.log(f"Processing project: {title}")

            # 保存为 txt 文件
            file_name = f"{title}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n\nDescription: {description}\n\nURL: {detail_url}")

            # 打印日志，确保文件保存成功
            self.log(f"Saved project: {title} to {file_name}")

            # 如果你还需要获取更多详细信息，可以继续请求详情页
            yield scrapy.Request(detail_url, callback=self.parse_detail, meta={"title": title})

    def parse_detail(self, response):
        # 获取词条标题
        title = response.meta["title"]

        # 提取词条的主要内容
        content = "".join(response.xpath("//div[@class='lemma-summary']//text()").getall()).strip()

        # 保存每个词条的内容为 txt 文件
        file_name = f"{title}_detail.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"Saved detailed content for project: {title}")
        yield {"title": title, "content": content}