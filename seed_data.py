"""Initial ORIGIN content. Existing rows are never overwritten."""

from psycopg import Connection


DEFAULT_TOURS = [
    ("domestic-kashmir", "domestic", "Kashmir", "NORTH", "", None, "New folder/dal.jpg", "Lakes, mountains, valleys and unforgettable Himalayan landscapes.", [], "Explore Package", False, 1),
    ("domestic-goa", "domestic", "Goa", "WEST", "", None, "New folder/goa1.png", "Beaches, laid-back escapes and vibrant coastal experiences.", [], "Explore Package", False, 2),
    ("domestic-kerala", "domestic", "Kerala", "SOUTH", "", None, "New folder/kerala.jpg", "Backwaters, lush landscapes and peaceful coastal retreats.", [], "Explore Package", False, 3),
    ("domestic-rajasthan", "domestic", "Rajasthan", "NORTH WEST", "", None, "New folder/Rajasthan-Tour-Package.png", "Historic forts, royal cities and rich cultural experiences.", [], "Explore Package", False, 4),
    ("domestic-manali", "domestic", "Manali", "HIMALAYAS", "", None, "New folder/Manali.png", "Mountain scenery, adventure and refreshing Himalayan escapes.", [], "Explore Package", False, 5),
    ("domestic-andaman", "domestic", "Andaman", "ISLANDS", "", None, "New folder/Andaman.png", "Crystal-clear waters, tropical beaches and peaceful island escapes.", [], "Explore Package", False, 6),
    ("international-dubai", "international", "Dubai", "UAE", "", None, "New folder/DubaiFinal.png", "Modern architecture, luxury experiences, desert adventures and vibrant city life.", [], "Explore Package", False, 1),
    ("international-istanbul", "international", "Istanbul", "TURKEY", "", None, "New folder/attractions-in-istanbul.png", "Historic landmarks, vibrant markets and unforgettable experiences across two continents.", [], "Explore Package", False, 2),
    ("international-maldives", "international", "Maldives", "MALDIVES", "", None, "New folder/maldives-tour-package.jpg", "Clear waters, tropical islands and relaxing luxury escapes surrounded by the Indian Ocean.", [], "Explore Package", False, 3),
    ("international-switzerland", "international", "Switzerland", "EUROPE", "", None, "New folder/Switzerlandd.jpg", "Alpine landscapes, charming towns and unforgettable European scenery.", [], "Explore Package", False, 4),
    ("international-paris", "international", "Paris", "FRANCE", "", None, "New folder/Eiffel-Tower.png", "Iconic architecture, art, food and timeless European city experiences.", [], "Explore Package", False, 5),
    ("international-bali", "international", "Bali", "INDONESIA", "", None, "New folder/Bali.png", "Tropical scenery, cultural experiences and peaceful island escapes.", [], "Explore Package", False, 6),
    ("umrah-economy", "umrah", "Economy", "", "8 DAYS", None, "", "A practical package designed for pilgrims looking for a comfortable and well-organized Umrah journey.", ["Accommodation", "Airport transfers", "Guided assistance"], "Enquire Now", False, 1),
    ("umrah-vip-deluxe", "umrah", "VIP Deluxe", "", "8 DAYS", None, "", "A premium Umrah experience with upgraded accommodation and enhanced travel convenience.", ["Premium accommodation", "Private transfers", "Dedicated assistance"], "Enquire Now", True, 2),
    ("umrah-comfort", "umrah", "Comfort", "", "10 DAYS", None, "", "More time for your pilgrimage with a balanced package focused on comfort, convenience and flexibility.", ["Hotel accommodation", "Transfers", "Travel assistance"], "Enquire Now", False, 3),
    ("umrah-extended", "umrah", "Extended Umrah", "", "14 DAYS", None, "", "An extended itinerary for pilgrims who prefer a slower pace and additional time in Makkah and Madinah.", ["Extended stay", "Accommodation", "Transfers"], "Enquire Now", False, 4),
    ("umrah-family", "umrah", "Family Package", "", "10 DAYS", None, "", "A flexible option designed for families travelling together, with convenience prioritized throughout the journey.", ["Family accommodation", "Transfers", "Coordinated assistance"], "Enquire Now", False, 5),
    ("umrah-custom", "umrah", "Custom Package", "", "CUSTOM", None, "", "Tell us your preferred dates, duration, accommodation and travel requirements, and we can help create a package around them.", ["Flexible duration", "Accommodation options", "Personalized planning"], "Build My Package", False, 6),
]


DEFAULT_DESTINATIONS = [
    ("Dubai", "United Arab Emirates", "4 Days", 45000, "New folder/DubaiFinal.png", "Experience desert adventures, city lights, and modern luxury.", "Internationaltours.html"),
    ("Istanbul", "Turkey", "5 Days", 55000, "New folder/attractions-in-istanbul.png", "Discover Istanbul's historic landmarks, markets, and culture.", "Internationaltours.html"),
    ("Kashmir", "India", "5 Days", 25000, "New folder/dal.jpg", "Explore Kashmir's valleys, lakes, and mountain landscapes.", "Domestictours.html"),
    ("Switzerland", "Switzerland", "7 Days", 95000, "New folder/Switzerlandd.jpg", "Travel through alpine villages, lakes, and breathtaking mountain views.", "Internationaltours.html"),
    ("Goa", "India", "4 Days", 22000, "New folder/goa1.png", "Enjoy Goa's beaches, coastal scenery, and vibrant local life.", "Domestictours.html"),
    ("Maldives", "Maldives", "5 Days", 65000, "New folder/maldives-tour-package.jpg", "Relax among turquoise waters, beaches, and island resorts.", "Internationaltours.html"),
    ("Hyderabad", "India", "11 Days", 55000, "New folder/Hyd.jpg", "Enjoy Hyderabad's culture and its culinary", "Domestictours.html"),
]


def seed_default_data(connection: Connection) -> None:
    """Insert starter tours and destinations; preserve any existing content."""
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO tours (
                slug, category, name, region, duration, price, image,
                description, features, cta_label, is_featured, sort_order
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            """,
            DEFAULT_TOURS,
        )

        cursor.execute("SELECT EXISTS (SELECT 1 FROM destinations)")
        destinations_already_exist = cursor.fetchone()["exists"]

        if not destinations_already_exist:
            cursor.executemany(
                """
                INSERT INTO destinations (
                    name, country, duration, price, image, description, link
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                DEFAULT_DESTINATIONS,
            )
