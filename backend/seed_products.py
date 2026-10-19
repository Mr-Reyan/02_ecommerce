import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product, Category, Tag, ProductImage
from inventory.models import Inventory
from carts.models import CartItem
from orders.models import Order, OrderItem
from authen.models import Tenant
from config.redis_client import redis_client

print("--- Step 1: Cleaning Old Products & Dependencies ---")
OrderItem.objects.all().delete()
Order.objects.all().delete()
CartItem.objects.all().delete()
Inventory.objects.all().delete()
ProductImage.objects.all().delete()
Product.objects.all().delete()

# Clear Redis Cache
try:
    for key in redis_client.scan_iter(match="products:*"):
        redis_client.delete(key)
    print("Redis products cache flushed.")
except Exception as e:
    print("Redis flush skipped:", e)

print("Old products and dependencies successfully deleted.")

print("--- Step 2: Setting Up Categories and Tags ---")
category_data = [
    ("T-Shirts", "Classic, graphic, and oversized t-shirts for everyday style."),
    ("Casual Shirts", "Smart casual, button-down, and relaxed resort shirts."),
    ("Cargo & Pants", "Utilitarian cargo pants, relaxed utility trousers, and chinos."),
    ("Baggy Trousers", "Trendy wide-leg, baggy-fit, and pleated streetwear trousers."),
    ("Hoodies & Sweatshirts", "Cozy heavyweight hoodies and crewneck sweatshirts."),
    ("Shorts & Activewear", "Breathable comfort shorts and active streetwear."),
]

categories = {}
for name, desc in category_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
    categories[name] = cat

tag_names = [
    "Casual", "Streetwear", "Summer", "Winter", "Premium",
    "Oversized", "Slim Fit", "Graphic", "Best Seller", "Featured", "Sale"
]
tags = {}
for tname in tag_names:
    t, _ = Tag.objects.get_or_create(name=tname)
    tags[tname] = t

# Available media images in backend/media/products/
media_images = {
    "tshirt_green": "products/adult-tshirt-tail-green.webp",
    "cargo_black": "products/baggy-fit-cargo-pants-black.jpg",
    "baggy_black1": "products/blac-capsule-baggy-pants.webp",
    "baggy_black2": "products/blac-capsule-baggy-pants2.webp",
    "plain_tshirt": "products/classic_plain_t-shirt.webp",
    "graphic_tshirt": "products/mendeez_graphic_black_t-shirt.webp",
    "straight_trouser": "products/straight-leg-baggy-trousers.webp",
    "twill_pants": "products/twill-baggy-pants.webp",
    "shirt1": "products/shirt1.png",
    "shirt2.png": "products/shirt2.png",
    "shirt3.png": "products/shirt3.png",
    "shirt4.png": "products/shirt4.png",
}

image_pools = {
    "T-Shirts": [
        media_images["graphic_tshirt"],
        media_images["plain_tshirt"],
        media_images["tshirt_green"],
        media_images["shirt1"],
        media_images["shirt2.png"],
    ],
    "Casual Shirts": [
        media_images["shirt1"],
        media_images["shirt2.png"],
        media_images["shirt3.png"],
        media_images["shirt4.png"],
    ],
    "Cargo & Pants": [
        media_images["cargo_black"],
        media_images["twill_pants"],
        media_images["baggy_black1"],
    ],
    "Baggy Trousers": [
        media_images["straight_trouser"],
        media_images["baggy_black1"],
        media_images["baggy_black2"],
        media_images["twill_pants"],
    ],
    "Hoodies & Sweatshirts": [
        media_images["graphic_tshirt"],
        media_images["tshirt_green"],
        media_images["shirt3.png"],
    ],
    "Shorts & Activewear": [
        media_images["twill_pants"],
        media_images["plain_tshirt"],
        media_images["shirt4.png"],
    ],
}

falcon_tenant = Tenant.objects.filter(name="Falcon Store").first() or Tenant.objects.first()
top_notch_tenant = Tenant.objects.filter(name="Top Notch").first()

products_catalog = [
    # --- T-SHIRTS (1-12) ---
    {"name": "One Life Graphic Streetwear T-Shirt", "category": "T-Shirts", "price": 45.00, "color": "black", "material": "100% Heavyweight Cotton", "desc": "Premium graphic tee inspired by urban street style with a relaxed boxy cut."},
    {"name": "Tail Green Classic Crewneck T-Shirt", "category": "T-Shirts", "price": 32.00, "color": "green", "material": "100% Combed Cotton", "desc": "Vibrant tail green organic cotton t-shirt engineered for all-day comfort."},
    {"name": "Minimalist Essential Plain White Tee", "category": "T-Shirts", "price": 28.00, "color": "white", "material": "Organic Ring-Spun Cotton", "desc": "Clean, crisp white basic t-shirt made with ultra-soft breathable fabric."},
    {"name": "Mendeez Graphic Anime Oversized Tee", "category": "T-Shirts", "price": 48.50, "color": "black", "material": "240 GSM Cotton", "desc": "Japanese typography and character graphic print across the chest and back."},
    {"name": "Cobalt Blue Vintage Wash Tee", "category": "T-Shirts", "price": 35.00, "color": "blue", "material": "Acid Wash Cotton", "desc": "Washed cobalt blue vintage tee with distressed hem details."},
    {"name": "Crimson Red Boxy Drop-Shoulder Tee", "category": "T-Shirts", "price": 38.00, "color": "red", "material": "100% Bio-Washed Cotton", "desc": "Bold crimson red streetwear t-shirt with signature drop shoulder silhouette."},
    {"name": "Forest Green Heavyweight Skate Tee", "category": "T-Shirts", "price": 42.00, "color": "green", "material": "Heavyweight French Terry", "desc": "Durable heavyweight construction crafted specifically for skate and street wear."},
    {"name": "Monochrome Stripe Detail Tee", "category": "T-Shirts", "price": 36.00, "color": "black", "material": "Cotton Blend", "desc": "Subtle stripe pattern on collar and cuffs for an elevated casual look."},
    {"name": "Midnight Navy Relaxed Pocket Tee", "category": "T-Shirts", "price": 30.00, "color": "blue", "material": "100% Pima Cotton", "desc": "Everyday casual pocket t-shirt in deep navy blue."},
    {"name": "Sunset Ruby Oversized Tee", "category": "T-Shirts", "price": 40.00, "color": "red", "material": "Mercerized Cotton", "desc": "Lustrous ruby red jersey cotton with an exaggerated relaxed drape."},
    {"name": "Pure Snow White Athletic Tee", "category": "T-Shirts", "price": 29.00, "color": "white", "material": "Cotton-Polyester Blend", "desc": "Moisture-wicking athletic cut t-shirt suitable for casual outings and active days."},
    {"name": "Urban Stealth Carbon Graphic Tee", "category": "T-Shirts", "price": 46.00, "color": "black", "material": "Pre-Shrunk Cotton", "desc": "Dark aesthetic graphic design screenprinted on dense pre-shrunk cotton."},

    # --- CASUAL SHIRTS (13-24) ---
    {"name": "Sleeve Striped Relaxed Camp Shirt", "category": "Casual Shirts", "price": 58.00, "color": "white", "material": "100% Linen Blend", "desc": "Breathable camp collar shirt with contrast sleeve piping for breezy summer days."},
    {"name": "Classic Oxford Button-Down Sky Blue", "category": "Casual Shirts", "price": 65.00, "color": "blue", "material": "100% Oxford Weave Cotton", "desc": "Timeless Oxford weave shirt with structured collar and tailored silhouette."},
    {"name": "Noir Utility Overshirt", "category": "Casual Shirts", "price": 75.00, "color": "black", "material": "Heavy Cotton Twill", "desc": "Dual chest pocket utility overshirt perfect for layering in transition seasons."},
    {"name": "Emerald Botanical Resort Shirt", "category": "Casual Shirts", "price": 54.00, "color": "green", "material": "Viscose Rayon", "desc": "Soft draping resort shirt adorned with subtle botanical motifs in rich emerald."},
    {"name": "Brick Red Flannel Check Shirt", "category": "Casual Shirts", "price": 62.00, "color": "red", "material": "Brushed Flannel Cotton", "desc": "Warm brushed flannel shirt with authentic heritage check pattern."},
    {"name": "Modern Minimalist White Poplin Shirt", "category": "Casual Shirts", "price": 60.00, "color": "white", "material": "Crisp Cotton Poplin", "desc": "Sleek hidden-button placket poplin shirt for contemporary styling."},
    {"name": "Indigo Washed Denim Casual Shirt", "category": "Casual Shirts", "price": 68.00, "color": "blue", "material": "100% Rigid Indigo Denim", "desc": "Western yoke details with snap pearl buttons in medium stone wash."},
    {"name": "Olive Green Military Workshirt", "category": "Casual Shirts", "price": 70.00, "color": "green", "material": "Herringbone Cotton", "desc": "Heavyweight military-spec herringbone workshirt with reinforced elbows."},
    {"name": "Crimson Sunset Bowling Shirt", "category": "Casual Shirts", "price": 52.00, "color": "red", "material": "Silky Lyocell Blend", "desc": "Retro 50s inspired bowling shirt featuring two-tone contrast panels."},
    {"name": "Jet Black Linen Blend Short Sleeve", "category": "Casual Shirts", "price": 55.00, "color": "black", "material": "55% Linen, 45% Cotton", "desc": "Lightweight breathable linen blend crafted for warm evenings."},
    {"name": "Ocean Blue Striped Linen Shirt", "category": "Casual Shirts", "price": 59.00, "color": "blue", "material": "Pure European Linen", "desc": "Vertical vertical ticking stripe linen shirt with relaxed silhouette."},
    {"name": "Artisanal Dyed Ruby Camp Shirt", "category": "Casual Shirts", "price": 64.00, "color": "red", "material": "Raw Silk-Cotton Blend", "desc": "Unique garment-dyed shirt with subtle natural slub texture."},

    # --- CARGO & PANTS (25-36) ---
    {"name": "Tactical Multi-Pocket Cargo Pants Black", "category": "Cargo & Pants", "price": 85.00, "color": "black", "material": "Durable Ripstop Cotton", "desc": "Multi-compartment tactical cargo trousers with buckle adjusters and deep bellow pockets."},
    {"name": "Twill Baggy Utility Pants Olive", "category": "Cargo & Pants", "price": 78.00, "color": "green", "material": "Heavyweight Cotton Twill", "desc": "Durable twill cargo pants with ergonomic knee articulation and wide legs."},
    {"name": "Navy Techwear Bungee Cargo Trousers", "category": "Cargo & Pants", "price": 89.00, "color": "blue", "material": "Weather-Resistant Nylon Blend", "desc": "Futuristic techwear trousers equipped with waterproof zips and ankle bungee cords."},
    {"name": "Off-White Relaxed Carpenter Pants", "category": "Cargo & Pants", "price": 76.00, "color": "white", "material": "12oz Duck Canvas", "desc": "Heavy canvas carpenter pants featuring utility loop and reinforced tool pockets."},
    {"name": "Crimson Accent Tactical Track Pants", "category": "Cargo & Pants", "price": 72.00, "color": "red", "material": "Poly-Cotton Matte Weave", "desc": "Comfort track trousers accented with deep red side stripes and zip pockets."},
    {"name": "Shadow Black Relaxed Workwear Chinos", "category": "Cargo & Pants", "price": 68.00, "color": "black", "material": "Stretch Cotton Twill", "desc": "Modern loose-tapered chinos tailored for work and casual weekends."},
    {"name": "Hunter Green Modular Cargo Pants", "category": "Cargo & Pants", "price": 84.00, "color": "green", "material": "Ripstop Cordura", "desc": "Modular cargo pants with detachable pouches and adjustable leg openings."},
    {"name": "Slate Blue Ergonomic Utility Chinos", "category": "Cargo & Pants", "price": 70.00, "color": "blue", "material": "98% Cotton, 2% Elastane", "desc": "Comfort-stretch chinos with angled coin and phone utility pockets."},
    {"name": "Chalk White Skate Chinos", "category": "Cargo & Pants", "price": 65.00, "color": "white", "material": "100% Rugged Cotton Canvas", "desc": "Loose-fitting skate chinos with reinforced double-stitched seams."},
    {"name": "Dark Charcoal Cargo Joggers", "category": "Cargo & Pants", "price": 69.00, "color": "black", "material": "Fleece Backed Twill", "desc": "Fleece-lined cargo joggers combining ultimate loungewear comfort with street aesthetics."},
    {"name": "Military Green Ankle-Cuff Cargos", "category": "Cargo & Pants", "price": 74.00, "color": "green", "material": "Washed Twill", "desc": "Tapered ankle-cuff cargo trousers with elastic drawstring waistband."},
    {"name": "Cobalt Tactical Streetwear Trousers", "category": "Cargo & Pants", "price": 82.00, "color": "blue", "material": "DWR Coated Cotton", "desc": "Water-repellent treated streetwear cargo pants with metal D-ring hardware."},

    # --- BAGGY TROUSERS (37-46) ---
    {"name": "Straight Leg Wide Baggy Trousers Black", "category": "Baggy Trousers", "price": 82.00, "color": "black", "material": "Premium Poly-Viscose Blend", "desc": "Clean straight leg drape trousers inspired by high-end Japanese streetwear."},
    {"name": "Capsule Edition Pleated Baggy Pants", "category": "Baggy Trousers", "price": 95.00, "color": "black", "material": "Double-Woven Gabardine", "desc": "Double pleated front design with voluminous relaxed leg profile."},
    {"name": "Midnight Blue Oversized Tailored Pants", "category": "Baggy Trousers", "price": 88.00, "color": "blue", "material": "Fine Wool-Viscose Blend", "desc": "Relaxed tailored trousers with fluid movement and refined drape."},
    {"name": "Forest Green Wide Skate Slacks", "category": "Baggy Trousers", "price": 75.00, "color": "green", "material": "Heavy Twill Canvas", "desc": "Heavy canvas wide slacks tailored to rest effortlessly over bulky sneakers."},
    {"name": "Vintage Ivory Wide Leg Corduroy Trousers", "category": "Baggy Trousers", "price": 80.00, "color": "white", "material": "8-Wale Chunky Corduroy", "desc": "Chunky wide-rib corduroy pants with a cozy texture and retro 90s fit."},
    {"name": "Burgundy Red Fluid Pleated Trousers", "category": "Baggy Trousers", "price": 92.00, "color": "red", "material": "Flowing Viscose Twill", "desc": "Deep burgundy trousers designed with a high rise and dramatic sweeping leg."},
    {"name": "Raw Umber Relaxed Balloon Trousers", "category": "Baggy Trousers", "price": 79.00, "color": "green", "material": "Cotton Drill", "desc": "Curved balloon fit trousers creating an artistic structural silhouette."},
    {"name": "Washed Indigo Baggy Denim Jeans", "category": "Baggy Trousers", "price": 90.00, "color": "blue", "material": "13.5oz Non-Stretch Denim", "desc": "Authentic 90s skater baggy jeans with vintage fade and stacking cuffs."},
    {"name": "Cream Minimalist Drape Slacks", "category": "Baggy Trousers", "price": 85.00, "color": "white", "material": "Soft Lyocell Weave", "desc": "Elegant and airy wide trousers tailored for effortless summer luxury."},
    {"name": "Pitch Black Oversized Formal Slacks", "category": "Baggy Trousers", "price": 86.00, "color": "black", "material": "Crepe Suiting Fabric", "desc": "Ultra-relaxed formal slacks featuring hidden drawstring and belt loops."},

    # --- HOODIES & SWEATSHIRTS (47-54) ---
    {"name": "Heavyweight 450 GSM Oversized Hoodie Black", "category": "Hoodies & Sweatshirts", "price": 95.00, "color": "black", "material": "100% Organic French Terry", "desc": "Ultra-dense luxury hoodie with seamless double-lined hood and drop shoulders."},
    {"name": "Sage Green Minimalist Crewneck Sweatshirt", "category": "Hoodies & Sweatshirts", "price": 72.00, "color": "green", "material": "Brushed Fleece Cotton", "desc": "Clean-cut crewneck pullover with tonal high-density chest embroidery."},
    {"name": "Navy Blue Classic Zip-Up Street Hoodie", "category": "Hoodies & Sweatshirts", "price": 85.00, "color": "blue", "material": "400 GSM Cotton Fleece", "desc": "Heavy gauge dual zipper hoodie with ribbed side panels and deep pockets."},
    {"name": "Chalk White Vintage Washed Pullover", "category": "Hoodies & Sweatshirts", "price": 78.00, "color": "white", "material": "Loopback Terry Cotton", "desc": "Sun-faded chalk white hoodie with distressed raw hem accents."},
    {"name": "Crimson Arch Logo Heavyweight Hoodie", "category": "Hoodies & Sweatshirts", "price": 90.00, "color": "red", "material": "100% Cotton Fleece", "desc": "Bold collegiate chenille patch lettering across the chest in deep crimson."},
    {"name": "Shadow Charcoal Raglan Sweatshirt", "category": "Hoodies & Sweatshirts", "price": 70.00, "color": "black", "material": "380 GSM Cotton", "desc": "Athletic raglan cut sweatshirt featuring flatlock seam detailing."},
    {"name": "Emerald Green Boxy Fit Hoodie", "category": "Hoodies & Sweatshirts", "price": 88.00, "color": "green", "material": "Organic Cotton Terry", "desc": "Vibrant emerald heavyweight boxy fleece designed for casual layering."},
    {"name": "Atlantic Blue Acid Washed Hoodie", "category": "Hoodies & Sweatshirts", "price": 82.00, "color": "blue", "material": "Acid Wash Cotton", "desc": "Hand-treated acid wash finish giving each garment a unique pattern."},

    # --- SHORTS & ACTIVEWEAR (55-60) ---
    {"name": "Everyday Heavyweight Fleece Shorts Black", "category": "Shorts & Activewear", "price": 45.00, "color": "black", "material": "100% French Terry", "desc": "Above-the-knee lounge shorts with thick ribbed waistband and metal aglets."},
    {"name": "Olive Green Tactical Cargo Shorts", "category": "Shorts & Activewear", "price": 52.00, "color": "green", "material": "Cotton Ripstop", "desc": "Utility cargo shorts with 6 secure pockets and key clip loop."},
    {"name": "Ocean Blue Retro Swim & Trail Shorts", "category": "Shorts & Activewear", "price": 42.00, "color": "blue", "material": "Quick-Dry Taslan Nylon", "desc": "Versatile quick-dry shorts with mesh lining suitable from city to water."},
    {"name": "Oatmeal Relaxed Cotton Sweat Shorts", "category": "Shorts & Activewear", "price": 40.00, "color": "white", "material": "100% Organic Cotton", "desc": "Unbrushed loopback cotton shorts with a relaxed raw-edge hem."},
    {"name": "Scarlet Red Athletic Mesh Shorts", "category": "Shorts & Activewear", "price": 38.00, "color": "red", "material": "Dual Layer Breathable Mesh", "desc": "Breathable double-layer mesh basketball shorts with knit stripe waist."},
    {"name": "Stealth Black Nylon Baggy Shorts", "category": "Shorts & Activewear", "price": 48.00, "color": "black", "material": "Matte Crinkle Nylon", "desc": "Lightweight wide-leg crinkle nylon shorts with deep slash pockets."},
]

print(f"--- Step 3: Inserting {len(products_catalog)} New Products with Images & Inventory ---")

standard_sizes = ["Small", "Medium", "Large", "X-Large"]
pant_sizes = ["28", "30", "32", "34", "36"]

created_count = 0
for idx, item in enumerate(products_catalog, start=1):
    cat = categories[item["category"]]
    sku = f"SKU-{item['category'][:3].upper()}-{idx:04d}"
    
    # Choose sizes based on clothing type
    # Generate size_stock dictionary with some out-of-stock variations
    size_stock = {}
    for s_idx, s in enumerate(sizes_list):
        if (idx + s_idx) % 4 == 0:
            size_stock[s] = 0
        else:
            size_stock[s] = random.randint(5, 25)

    specs = {
        "color": item["color"],
        "sizes": sizes_list,
        "size_stock": size_stock,
        "material": item["material"],
        "fit": "Relaxed / Oversized" if "Baggy" in item["category"] or "Oversized" in item["name"] else "Regular Fit"
    }

    # Assign tags
    assigned_tags = [tags["Casual"]]
    if "Streetwear" in item["name"] or "Tactical" in item["name"] or "Baggy" in item["category"]:
        assigned_tags.append(tags["Streetwear"])
    if "Graphic" in item["name"]:
        assigned_tags.append(tags["Graphic"])
    if "Oversized" in item["name"] or "Baggy" in item["category"]:
        assigned_tags.append(tags["Oversized"])
    if idx % 4 == 0:
        assigned_tags.append(tags["Best Seller"])
    if idx % 5 == 0:
        assigned_tags.append(tags["Featured"])
    if idx % 7 == 0:
        assigned_tags.append(tags["Sale"])

    # Pick image pool
    pool = image_pools.get(item["category"], [media_images["shirt1"]])
    main_image = pool[idx % len(pool)]

    product = Product.objects.create(
        name=item["name"],
        description=item["desc"],
        price=item["price"],
        tenant=falcon_tenant,
        category=cat,
        image=f"/{main_image}",
        sku=sku,
        is_featured=(idx % 5 == 0),
        is_active=True,
        is_deleted=False,
        specifications=specs
    )
    product.tags.set(assigned_tags)

    # Attach Product Images (1 main + 1-2 gallery images)
    ProductImage.objects.create(
        product=product,
        image=main_image,
        position=0
    )
    # Add an alternate gallery image if available
    alt_image = pool[(idx + 1) % len(pool)]
    if alt_image != main_image:
        ProductImage.objects.create(
            product=product,
            image=alt_image,
            position=1
        )

    # Create Inventory Stock
    stock_qty = random.randint(15, 80)
    Inventory.objects.create(
        product=product,
        stock=stock_qty
    )

    created_count += 1

print(f"Successfully created {created_count} products for '{falcon_tenant.name}'.")

# Also seed for Top Notch tenant if it exists
if top_notch_tenant:
    for idx, item in enumerate(products_catalog[:15], start=101):
        cat = categories[item["category"]]
        sku = f"TN-{item['category'][:3].upper()}-{idx:04d}"
        pool = image_pools.get(item["category"], [media_images["shirt1"]])
        main_image = pool[idx % len(pool)]
        
        p = Product.objects.create(
            name=f"{item['name']} (TN Edition)",
            description=item["desc"],
            price=item["price"],
            tenant=top_notch_tenant,
            category=cat,
            image=f"/{main_image}",
            sku=sku,
            is_featured=False,
            is_active=True,
            is_deleted=False,
            specifications={
                "color": item["color"],
                "sizes": standard_sizes,
                "material": item["material"],
            }
        )
        p.tags.set([tags["Casual"], tags["Premium"]])
        ProductImage.objects.create(product=p, image=main_image, position=0)
        Inventory.objects.create(product=p, stock=30)
    print(f"Successfully created 15 products for '{top_notch_tenant.name}'.")

print("\n--- Summary Verification ---")
print("Total Products in DB:", Product.objects.count())
print("Total Inventories:", Inventory.objects.count())
print("Total ProductImages:", ProductImage.objects.count())
print("Total Categories:", Category.objects.count())
print("Total Tags:", Tag.objects.count())
