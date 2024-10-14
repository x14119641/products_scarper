import scrapy
import unicodedata

class ProductosObra(scrapy.Spider):
    name = "ProductosObra"
    allowed_domains = ['corona.co']
    start_urls = ['https://corona.co/productos/c/categories']
    
    def __init__(self):
        self.category_links = []

    def parse(self, response):
        """Get links for each category"""
        category_links = response.xpath('*//div[@class="content-card-4"]/a/@href').extract()
        category_links = self.remove_first_item_condition(category_links)

        for link in category_links[0:1]:  # Limit for testing
            endpoint = response.urljoin(link)
            self.logger.info(f"Category link: {endpoint}")
            yield scrapy.Request(endpoint, callback=self.parse_category)

    def parse_category(self, response):
        """Get links of products and call function to parse them"""
        subcategories_links = response.xpath('*//div[@class="content-card-4"]/a/@href').extract()

        if subcategories_links:
            subcategories_links = self.remove_first_item_condition(subcategories_links)
            for link in subcategories_links[0:1]:  # Limit for testing
                endpoint = response.urljoin(link)
                self.logger.info(f"SubCategory endpoint: {endpoint}")
                yield scrapy.Request(endpoint, callback=self.parse_category)

        # Extract product links
        product_links = response.xpath('*//div[contains(@class,"details")]/a/@href').extract()
        product_links = list(set(product_links))
        for link in product_links[0:4]:  # Limit for testing
            endpoint = response.urljoin(link)
            yield scrapy.Request(endpoint, callback=self.parse_product)

    def parse_product(self, response):
        """Get product meta info"""
        name = response.xpath('//h1[@class="name"]/text()').get(default='Unknown')
        reference = response.xpath('//div[@class="sku"]/text()').get(default='No Reference')
        description = response.xpath('*//div[@class="description"]/text()').get()
        color = response.xpath('*//span[@class="coc-variant-selected"]/text()').get()
        more_colors_link = response.xpath('*//li[@class="coc-variant-option"]/div/a/@href').extract()
        price = response.xpath('*//div[@class="price"]/span/text()').get()
        price_box = response.xpath('*//div[@class="coc-price-uom"]/text()').get()
        # img_src = response.xpath('*//img[@class="owl-lazy"]/@src').extract()
        # self.logger.info(f'Colors: {more_colors_link}')
        # Log additional colors and crawl them
        if more_colors_link:
            for color_link in more_colors_link:
                self.logger.info(f"Following color variant link: {color_link}")
                yield scrapy.Request(response.urljoin(color_link), callback=self.parse_product)

        # Normalize name
        name = unicodedata.normalize("NFKD", name)
        
        # Collect the product data
        data = {
            'link': response.request.url, 
            'name': name,
            'reference': reference,
            'description': description,
            'color': color,
            'price': price.replace('$', '').strip(),
            'price_box': price_box.split('$')[-1].strip() if price_box else False,
            # 'img_src': img_src
        }

        yield data

    def remove_first_item_condition(self, links):
        """Remove first item if it is 'novedades' or 'lanzamientos'"""
        first_link_text = links[0].lower()
        if 'lanzamientos' in first_link_text or 'novedades' in first_link_text:
            links = links[1:]
        return links
