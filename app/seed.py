from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import User, Service, Product, Review, Slot, Booking
from app.security import hash_password

async def seed_database():
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        res = await db.execute(select(User).where(User.email == "admin@privatemillionaires.com"))
        if res.scalar_one_or_none():
            return  # Already seeded

        print("Seeding initial data for Private Millionaires Barber Studio...")

        # 1. Admin User
        admin_user = User(
            name="Master Barber & Owner",
            email="admin@privatemillionaires.com",
            phone="(909) 430-4591",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin_user)

        # 2. Demo Customer
        demo_customer = User(
            name="Marcus Vance",
            email="customer@vip.com",
            phone="(909) 555-0199",
            hashed_password=hash_password("customer123"),
            role="customer"
        )
        db.add(demo_customer)

        await db.flush()

        # 3. Services
        services_data = [
            {
                "title": "Private Millionaire VIP Cut & Facial",
                "category": "VIP Combos",
                "description": "Our flagship signature experience. Precision customized fade or scissor cut, beard sculpt, straight razor lineup, warm ozone steam, hot towel treatment, exfoliating scrub, and scalp massage.",
                "duration_minutes": 60,
                "price": 85.0,
                "image_url": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "Executive Haircut & Razor Lineup",
                "category": "Haircuts",
                "description": "Ultra-sharp precision fade or taper with straight razor perimeter lineup, shears texture work, and premium styling finish.",
                "duration_minutes": 45,
                "price": 45.0,
                "image_url": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "Beard Sculpt, Hot Towel & Straight Razor",
                "category": "Beard Care",
                "description": "Sculpting, fading, razor-sharp cheek and neck definition, hot towel treatment, finished with organic beard elixir oil.",
                "duration_minutes": 30,
                "price": 35.0,
                "image_url": "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "Young Mogul Haircut (Kids 12 & Under)",
                "category": "Haircuts",
                "description": "Patient, stylish precision haircut for young VIPs. Crisp clean lines, custom style, and complimentary finishing pomade.",
                "duration_minutes": 30,
                "price": 35.0,
                "image_url": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "Royal Scalp Therapy & Deep Shampoo",
                "category": "Treatments",
                "description": "Revitalizing tea-tree scalp scrub, deep conditioning wash, warm towel wrap, and pressure point head massage.",
                "duration_minutes": 25,
                "price": 30.0,
                "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "After-Hours VIP Studio Experience",
                "category": "VIP Combos",
                "description": "Exclusive 1-on-1 private studio booking outside standard hours. Full haircut, beard grooming, facial steamer, and private executive lounge.",
                "duration_minutes": 75,
                "price": 120.0,
                "image_url": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=800&q=80"
            }
        ]

        services = []
        for s in services_data:
            svc = Service(
                title=s["title"],
                category=s["category"],
                description=s["description"],
                duration_minutes=s["duration_minutes"],
                price=s["price"],
                image_url=s["image_url"],
                is_active=True
            )
            db.add(svc)
            services.append(svc)

        await db.flush()

        # 4. Products
        products_data = [
            {
                "name": "Millionaires 24K Matte Clay Pomade",
                "category": "Hair Styling",
                "description": "High-hold, zero-shine matte finish crafted with bentonite clay, organic beeswax, and cedarwood oil. Delivers all-day texture without flaking or greasiness.",
                "price": 28.0,
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Royal Oud & Sandalwood Beard Elixir",
                "category": "Beard Care",
                "description": "Nutrient-rich conditioning blend of argan, Moroccan jojoba, and black seed oil infused with deep Arabian oud. Softens coarse hair and prevents beard itch.",
                "price": 32.0,
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1608248597359-009139a0937a?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Ozone Revitalizing Facial Cleanser & Scrub",
                "category": "Skin & Face",
                "description": "Activated charcoal and bamboo micro-exfoliants designed to detoxify pores, prevent ingrown hairs after shaving, and hydrate the skin.",
                "price": 26.0,
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Private Reserve Aftershave Splash & Cologne",
                "category": "Cologne & Fragrance",
                "description": "Cooling witch hazel and aloe vera splash with rich tobacco leaf, amber, and Madagascar vanilla notes that calm irritation instantly.",
                "price": 38.0,
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "24K Gold Plated Master Barber Shavette",
                "category": "Tools",
                "description": "Balanced solid steel razor chassis with mirror 24K gold finish, smooth swing arm blade lock, and 10 complimentary Swedish platinum blades.",
                "price": 48.0,
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1508380702597-707c1b00a35c?auto=format&fit=crop&w=800&q=80"
            }
        ]

        products = []
        for p in products_data:
            prod = Product(
                name=p["name"],
                category=p["category"],
                description=p["description"],
                price=p["price"],
                stock=p["stock"],
                image_url=p["image_url"],
                is_active=True
            )
            db.add(prod)
            products.append(prod)

        await db.flush()

        # 5. Reviews
        reviews_data = [
            (products[0].id, 5, "Best matte clay I have ever used. Holds all day through gym and work, washes out clean with water."),
            (products[0].id, 5, "Leaves my hair looking natural with incredible texture. Definitely barber grade quality."),
            (products[1].id, 5, "The oud fragrance is pure luxury. Softens my beard immediately without feeling greasy."),
            (products[2].id, 5, "Cleanses deep without drying out my face. Zero razor bumps since I started using it!"),
            (products[3].id, 5, "Smells like a million bucks. Get compliments everywhere I go.")
        ]
        for pid, rating, comment in reviews_data:
            rev = Review(
                product_id=pid,
                user_id=demo_customer.id,
                rating=rating,
                comment=comment
            )
            db.add(rev)

        # 6. Generate Upcoming Slots for next 7 days
        today = datetime.now(timezone.utc).date()
        times = [
            ("09:00", "09:45"),
            ("10:00", "10:45"),
            ("11:00", "11:45"),
            ("13:00", "13:45"),
            ("14:00", "14:45"),
            ("15:00", "15:45"),
            ("16:00", "16:45"),
            ("17:00", "17:45"),
        ]

        created_slots = []
        for day_offset in range(0, 7):
            slot_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            # Monday closed
            weekday = (today + timedelta(days=day_offset)).weekday()
            if weekday == 0:  # Monday
                continue

            for start_t, end_t in times:
                s = Slot(
                    date=slot_date,
                    start_time=start_t,
                    end_time=end_t,
                    barber_name="Master Barber Marcus",
                    is_booked=False,
                    is_blocked=False
                )
                db.add(s)
                created_slots.append(s)

        await db.flush()

        # 7. Create a sample confirmed booking for the demo customer
        if created_slots:
            sample_slot = created_slots[1]
            sample_slot.is_booked = True
            sample_booking = Booking(
                user_id=demo_customer.id,
                slot_id=sample_slot.id,
                service_id=services[0].id,
                status="confirmed",
                customer_notes="First time VIP experience. Looking forward to the hot towel & facial!",
                total_price=services[0].price
            )
            db.add(sample_booking)

        await db.commit()
        print("Database seeded successfully with authentic services, products, and slots!")
