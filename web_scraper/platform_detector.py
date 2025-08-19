import requests

def detect_platform(url):
    """
    Analyzes a URL to detect the e-commerce platform.
    Currently, it only detects Shopify.

    Args:
        url (str): The URL of the website to analyze.

    Returns:
        str: The name of the platform ('shopify') or 'unknown'.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text

        # Simple checks for Shopify fingerprints
        if 'Shopify' in content or 'cdn.shopify.com' in content or '.myshopify.com' in url:
            return 'shopify'

        # Future checks for other platforms can be added here
        # elif 'woocommerce' in content:
        #     return 'woocommerce'

        return 'unknown'

    except requests.exceptions.RequestException as e:
        print(f"Could not fetch URL {url}: {e}")
        return 'error'

if __name__ == '__main__':
    # Example usage for testing
    test_urls = {
        "Good Dot (Shopify)": "https://gooddot.in",
        "Blue Tribe (Shopify)": "https://www.bluetribefoods.com",
        "Google (Unknown)": "https://google.com",
        "Invalid URL": "https://thissitedoesnotexist12345.com"
    }
    for name, url in test_urls.items():
        platform = detect_platform(url)
        print(f"The platform for '{name}' ({url}) is: {platform}")
