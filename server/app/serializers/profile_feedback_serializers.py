from typing import Any


def serialize_profile_feedback(feedback: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": feedback["id"],
        "content": feedback["content"],
        "rate": feedback["rate"],
        "commentator": {
            "username": feedback["commentator_username"],
            "photo_link": feedback["commentator_photo_link"],
        },
        "profile_id": feedback["profile_id"],
        "image_link": feedback["image_link"],
    }