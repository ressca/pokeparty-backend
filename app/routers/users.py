from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.patch("/update", response_model=schemas.UserResponse)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
    ):
    # Update fields if provided
    if user_update.username is not None:
        # Check if username taken
        existing_user = db.query(models.User).filter(models.User.username == user_update.username).first()
        if existing_user and existing_user.id != current_user.id:
             raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_update.username
        
    if user_update.email is not None:
        # Check if email taken
        existing_email = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_email and existing_email.id != current_user.id:
             raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email

    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    if user_update.profile_pic_pokemon_id is not None:
        current_user.profile_pic_pokemon_id = user_update.profile_pic_pokemon_id

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/current-user", response_model=schemas.UserResponse)
def get_current_user_info(
    current_user: Annotated[models.User, Depends(get_current_user)]
    ):
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()


# Favorite Pokemon Endpoints
@router.post("/favorite-pokemon", response_model=schemas.FavoritePokemon, status_code=status.HTTP_201_CREATED)
def add_favorite_pokemon(
    favorite_pokemon: schemas.FavoritePokemonCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    new_fav = models.favorite_pokemon(
        user_id=current_user.id,
        pokemon_id=favorite_pokemon.pokemon_id
    )
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav


@router.get("/favorite-pokemons", response_model=list[schemas.FavoritePokemon])
def get_favorite_pokemons(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    favs = db.query(models.favorite_pokemon).filter(models.favorite_pokemon.user_id == current_user.id).all()
    return favs


@router.delete("/favorite-pokemon/", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite_pokemon(
    favorite_pokemon: schemas.FavoritePokemonDelete,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    fav = db.query(models.favorite_pokemon).filter(
        models.favorite_pokemon.user_id == current_user.id,
        models.favorite_pokemon.pokemon_id == favorite_pokemon.pokemon_id
    ).first()
    
    if not fav:
        raise HTTPException(status_code=404, detail="Selected Pokemon is not in favorites")
    
    db.delete(fav)
    db.commit()