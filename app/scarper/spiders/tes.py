import scrapy
import unicodedata


class ProductosObraSpider(scrapy.Spider):
    name = "ProductosObraSpider"
    allowed_domains = ['corona.co',]
    start_urls = ['https://corona.co/productos/c/categories',]
    
    def parse(self, response):
        """Get Liks for each category"""
        category_links = response.xpath('*//div[@class="content-card-4"]/a/@href').extract()
        for link in category_links[0:1]:

            endpoint = response.urljoin(link)
            self.logger.info(f"Category link: {endpoint}")
            print('endpoint: ', endpoint)
            yield scrapy.Request(endpoint, callback=self.parse_category)
    
    
    def parse_category(self, response):
        """Get links of products and call function to parse them"""
        product_links = response.xpath('*//div[contains(@class,"details")]/a/@href').extract()
        for link in product_links[0:2]:
            endpoint = response.urljoin(link)
            yield scrapy.Request(endpoint, callback=self.parse_product)
    
    
    def parse_product(self, response, is_color=False):
        """Get product meta info"""
        name = response.xpath('//h1[@class="name"]/text()')[0].extract()
        reference = response.xpath('//div[@class="sku"]/text()')[0].extract()
        colors_links = response.xpath('*//a[@class="coc-variant-swatch"]/@href').extract()
        colors = response.xpath('*//div[@class="coc-color-swatch"]/@title').extract()
        data = {
            'link':response.request.url, 
            'name':unicodedata.normalize("NFKD", name),
            'reference': reference,
            'colors_data': {
                'links': colors_links,
                'colors': colors
            }
            
        }
        print(data)
        yield data
        
        