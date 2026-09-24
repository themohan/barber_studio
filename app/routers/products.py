from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models import Product, Review, User
from app.schemas import (
    ProductCreate, ProductUpdate, ProductOut,
    ReviewCreate, ReviewOut
)
from app.deps import get_current_user, require_admin
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/products", tags=["Products"])

def enrich_product(p: Product) -> ProductOut:
    reviews_list = []
    total_rating = 0
    if p.reviews:
        for r in p.reviews:
            user_name = r.user.name if r.user else "Verified Groomer"
            reviews_list.append(ReviewOut(
                id=r.id,
                product_id=r.product_id,
                user_id=r.user_id,
                user_name=user_name,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at
            ))
            total_rating += r.rating

    avg_rating = round(total_rating / len(reviews_list), 1) if reviews_list else 5.0

    return ProductOut(
        id=p.id,
        name=p.name,
        category=p.category,
        description=p.description,
        price=p.price,
        stock=p.stock,
        image_url=p.image_url,
        is_active=p.is_active,
        created_at=p.created_at,
        average_rating=avg_rating,
        reviews_count=len(reviews_list),
        reviews=reviews_list
    )

@router.get("", response_model=List[ProductOut])
async def list_products(
    category: Optional[str] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Product)
        .options(
            selectinload(Product.reviews).selectinload(Review.user)
        )
    )
    if not include_inactive:
        query = query.where(Product.is_active == True)
    if category and category.lower() != "all":
        query = query.where(Product.category == category)

    query = query.order_by(Product.created_at.desc())
    res = await db.execute(query)
    products = res.scalars().all()
    return [enrich_product(p) for p in products]

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Product)
        .options(
            selectinload(Product.reviews).selectinload(Review.user)
        )
        .where(Product.id == product_id)
    )
    res = await db.execute(query)
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return enrich_product(product)

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    new_product = Product(
        name=product_in.name.strip(),
        category=product_in.category.strip(),
        description=product_in.description.strip(),
        price=product_in.price,
        stock=product_in.stock,
        image_url=product_in.image_url,
        is_active=True
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    query = (
        select(Product)
        .options(
            selectinload(Product.reviews).selectinload(Review.user)
        )
        .where(Product.id == new_product.id)
    )
    res = await db.execute(query)
    full_product = res.scalar_one()

    enriched = enrich_product(full_product)

    await ws_manager.broadcast({
        "type": "PRODUCT_CREATED",
        "product": enriched.model_dump(mode="json")
    })

    return enriched

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Product)
        .options(
            selectinload(Product.reviews).selectinload(Review.user)
        )
        .where(Product.id == product_id)
    )
    res = await db.execute(query)
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    enriched = enrich_product(product)

    await ws_manager.broadcast({
        "type": "PRODUCT_UPDATED",
        "product": enriched.model_dump(mode="json")
    })

    return enriched

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Product).where(Product.id == product_id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product.is_active = False
    await db.commit()

    await ws_manager.broadcast({
        "type": "PRODUCT_DELETED",
        "product_id": product_id
    })

    return {"message": "Product deactivated successfully."}

@router.post("/{product_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_product_review(
    product_id: int,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify product exists
    p_res = await db.execute(select(Product).where(Product.id == product_id))
    product = p_res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    new_review = Review(
        product_id=product.id,
        user_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment.strip()
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)

    review_out = ReviewOut(
        id=new_review.id,
        product_id=new_review.product_id,
        user_id=new_review.user_id,
        user_name=current_user.name,
        rating=new_review.rating,
        comment=new_review.comment,
        created_at=new_review.created_at
    )

    await ws_manager.broadcast({
        "type": "REVIEW_ADDED",
        "product_id": product.id,
        "review": review_out.model_dump(mode="json")
    })

    return review_out
