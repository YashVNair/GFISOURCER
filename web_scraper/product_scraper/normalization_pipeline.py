import re
from itemadapter import ItemAdapter

class NormalizationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        original_item = adapter.asdict()

        # Normalize SKU
        if adapter.get('sku'):
            adapter['sku'] = self.normalize_sku(adapter.get('sku'))

        # Normalize pack_size
        if adapter.get('pack_size'):
            adapter['pack_size'] = self.normalize_pack_size(adapter.get('pack_size'))

        # Normalize claims (sort them alphabetically for consistency)
        if adapter.get('claims'):
            claims_list = sorted([claim.strip() for claim in adapter.get('claims', '').split(',') if claim.strip()])
            adapter['claims'] = ", ".join(claims_list)

        spider.logger.info("--- Normalization Pipeline ---")
        spider.logger.info(f"Original item: {original_item}")
        spider.logger.info(f"Normalized item: {adapter.asdict()}")
        spider.logger.info("------------------------------")

        return item

    def normalize_sku(self, sku_str):
        """
        Normalizes the SKU string.
        - Converts to uppercase
        - Strips leading/trailing whitespace
        """
        if not isinstance(sku_str, str):
            return ""
        return sku_str.strip().upper()

    def normalize_pack_size(self, pack_size_str):
        """
        Normalizes the pack size string to a consistent format.
        e.g., "250g" -> "250 g", "1kg" -> "1 kg", "Pack of 2" -> "2 pack"
        """
        if not isinstance(pack_size_str, str):
            return ""

        pack_size_lower = pack_size_str.lower()

        # Pattern 1: number followed by unit (e.g., "250g", "1.5kg", "500 ml")
        match = re.search(r'(\d+\.?\d*)\s*(g|kg|ml|l)\b', pack_size_lower)
        if match:
            value = match.group(1)
            unit = match.group(2)
            return f"{value} {unit}"

        # Pattern 2: "pack of X" (e.g., "pack of 2")
        match = re.search(r'pack of (\d+)', pack_size_lower)
        if match:
            value = match.group(1)
            return f"{value} pack"

        # Pattern 3: Just a number (assume it's a count)
        match = re.fullmatch(r'\s*(\d+)\s*', pack_size_lower)
        if match:
            return f"{match.group(1)} count"

        # Fallback: return the original string, stripped of whitespace
        return pack_size_str.strip()
