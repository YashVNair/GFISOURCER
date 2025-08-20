import requests
from bs4 import BeautifulSoup

def detect_platform(url):
    """
    Analyzes a URL to detect the e-commerce platform using BeautifulSoup for more reliable parsing.
    Detects BigCommerce, Wix, Squarespace, Shopify, WooCommerce, Magento, or marks as 'custom'.

    Args:
        url (str): The URL of the website to analyze.

    Returns:
        str: The name of the platform ('bigcommerce', 'wix', 'squarespace', 'shopify', 'woocommerce', 'magento', 'custom') or 'error'.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        html_text = response.text

        # BigCommerce: Check for .mybigcommerce.com in the HTML
        if '.mybigcommerce.com' in html_text:
            return 'bigcommerce'

        # Wix: Check for Wix-specific URLs or generator tag
        if any('wix.com' in tag.get('src', '') for tag in soup.find_all('script')) or \
           any('wixstatic.com' in tag.get('src', '') for tag in soup.find_all('script')) or \
           soup.find('meta', attrs={'name': 'generator', 'content': lambda c: c and 'wix.com' in c.lower()}):
            return 'wix'

        # Squarespace: Check for Squarespace-specific URLs or templateId
        if any('static.squarespace.com' in tag.get('src', '') for tag in soup.find_all('script')) or \
           any('static.squarespace.com' in tag.get('href', '') for tag in soup.find_all('link')) or \
           'templateId' in html_text:
            return 'squarespace'

        # Magento: Check for specific script type
        if soup.find('script', type='text/x-magento-init'):
            return 'magento'

        # WooCommerce: Check for WooCommerce body class or plugin paths
        if (soup.body and any('woocommerce' in s for s in soup.body.get('class', []))) or \
           any('/wp-content/plugins/woocommerce/' in tag.get('src', '') for tag in soup.find_all('script')) or \
           any('/wp-content/plugins/woocommerce/' in tag.get('href', '') for tag in soup.find_all('link')):
            return 'woocommerce'

        # Shopify: Check for Shopify-specific script host or variables
        scripts = soup.find_all('script')
        for script in scripts:
            if 'Shopify.theme' in script.text or (script.get('src') and 'cdn.shopify.com' in script.get('src')):
                return 'shopify'
        if '.myshopify.com' in url:
            return 'shopify'

        return 'custom'

    except requests.exceptions.RequestException as e:
        print(f"Could not fetch URL {url}: {e}")
        return 'error'

if __name__ == '__main__':
    # Example usage for testing
    test_urls = {
        "Good Dot (Shopify)": "https://gooddot.in",
        "Blue Tribe (Shopify)": "https://www.bluetribefoods.com",
        "Woostify Demo (WooCommerce)": "https://demo.woostify.com/",
        "Land Rover (Magento)": "https://shop.landrover.com/",
        "Mountain Rose Herbs (BigCommerce)": "https://mountainroseherbs.com/",
        "Copper & Brass (Wix)": "https://www.copperandbrass.net/",
        "silvabokis (Squarespace)": "https://www.silvabokis.com/",
        "Google (Custom)": "https://google.com",
        "Invalid URL": "https://thissitedoesnotexist12345.com"
    }
    print("Running platform detection tests...")
    for name, url in test_urls.items():
        platform = detect_platform(url)
        print(f"The platform for '{name}' ({url}) is: {platform}")
