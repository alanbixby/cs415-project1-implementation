from typing import TypedDict, NotRequired, Literal, List, Union


class TwitterResponse(TypedDict):
    # TODO:
    pass


TwitterParams = TypedDict(
    "TwitterParams",
    {
        "expansions": NotRequired[
            List[
                Literal[
                    "attachments.poll_ids",
                    "attachments.media_keys",
                    "author_id",
                    "edit_history_tweet_ids",
                    "entities.mentions.username",
                    "geo.place_id",
                    "in_reply_to_user_id",
                    "referenced_tweets.id",
                    "referenced_tweets.id.author_id",
                ]
            ]
        ],
        # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media
        "media.fields": NotRequired[
            List[
                Literal[
                    "duration_ms",
                    "height",
                    "media_key",
                    "preview_image_url",
                    "type",
                    "url",
                    "width",
                    "public_metrics",
                    "alt_text",
                    "variants",
                ]
            ]
        ],
        # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/place
        "place.fields": NotRequired[
            List[
                Literal[
                    "contained_within",
                    "country",
                    "country_code",
                    "full_name",
                    "geo",
                    "id",
                    "name",
                    "place_type",
                ]
            ]
        ],
        # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/poll
        "poll.fields": NotRequired[
            List[
                Literal[
                    "duration_minutes", "end_datetime", "id", "options", "voting_status"
                ]
            ]
        ],
        # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
        "tweet.fields": NotRequired[
            List[
                Literal[
                    "attachments",
                    "author_id",
                    "context_annotations",
                    "conversation_id",
                    "created_at",
                    "edit_controls",
                    "entities",
                    "geo",
                    "id",
                    "in_reply_to_user_id",
                    "lang",
                    "public_metrics",
                    "possibly_sensitive",
                    "referenced_tweets",
                    "reply_settings",
                    "source",
                    "text",
                    "withheld",
                ]
            ]
        ],
        # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
        "user.fields": NotRequired[
            List[
                Literal[
                    "created_at",
                    "description",
                    "entities",
                    "id",
                    "location",
                    "name",
                    "pinned_tweet_id",
                    "profile_image_url",
                    "protected",
                    "public_metrics",
                    "url",
                    "username",
                    "verified",
                    "withheld",
                ]
            ]
        ],
        "backfill_minutes": NotRequired[int],  # Academic Access Only
        "start_time": NotRequired[str],  # Enterprise Only
        "end_time": NotRequired[str],  # Enterprise Only
    },
)
