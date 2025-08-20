import scrapy

class ProductItem(scrapy.Item):
    # Product Info
    title = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    product_format = scrapy.Field()
    animal_product_replicated = scrapy.Field()

    # Status & Availability
    status = scrapy.Field()
    availability = scrapy.Field()
    in_stock = scrapy.Field()
    launch_date = scrapy.Field()
    last_updated = scrapy.Field()

    # Pricing & Physical Details
    price_inr = scrapy.Field()
    unit_price = scrapy.Field()
    price_per_kg_l = scrapy.Field()
    weight = scrapy.Field()
    weight_unit = scrapy.Field()
    pack_size = scrapy.Field()

    # Product Details
    positioning = scrapy.Field()
    segment = scrapy.Field()
    storage_condition = scrapy.Field()
    consumption_format = scrapy.Field()
    shelf_life = scrapy.Field()
    type_of_manufacturing = scrapy.Field()

    # Ingredients & Nutrition
    ingredients_list = scrapy.Field()
    ingredients_summary = scrapy.Field()
    ingredient_count = scrapy.Field()
    protein_sources = scrapy.Field()
    complete_protein = scrapy.Field()
    nutritional_data = scrapy.Field()
    nutritional_claims = scrapy.Field()
    health_claims = scrapy.Field()
    allergen_info = scrapy.Field()

    # Marketing & Claims
    marketing_claims = scrapy.Field()
    certifications = scrapy.Field()

    # Distribution & Sales
    channel = scrapy.Field()
    distribution_channels = scrapy.Field()

    # Company Information
    manufactured_by = scrapy.Field()
    distributed_by = scrapy.Field()
    packaged_by = scrapy.Field()
    marketed_by = scrapy.Field()

    # Digital & Reference
    product_page = scrapy.Field()
    website = scrapy.Field()
    images = scrapy.Field()
    sku_code = scrapy.Field()
    source_name = scrapy.Field()
    source_links = scrapy.Field()
    notes = scrapy.Field()

    # Administrative
    added_by = scrapy.Field()
    update_type = scrapy.Field()
