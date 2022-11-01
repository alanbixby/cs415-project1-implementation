import time
from datetime import datetime
from typing import Any, List, Literal, TypedDict, Union

from typing_extensions import NotRequired

# Based on http://count.reddit-stream.com/api_info/comment and
#          http://count.reddit-stream.com/api_info/thread


class RedditAwards(TypedDict):
    award_sub_type: str
    award_type: str
    awardings_required_to_grant_benefits: NotRequired[int]
    coin_price: int
    coin_reward: int
    count: int
    days_of_drip_extension: NotRequired[int]
    days_of_premium: NotRequired[int]
    description: str
    end_date: None
    giver_coin_reward: NotRequired[int]
    icon_format: str
    icon_height: int
    icon_url: str
    icon_width: int
    id: str
    is_enabled: Literal[True]
    is_new: Literal[False]
    name: str
    penny_donate: NotRequired[int]
    penny_price: NotRequired[int]
    resized_icons: List[Any]
    resized_static_icons: List[Any]
    start_date: None
    static_icon_height: int
    static_icon_url: str
    static_icon_width: int
    sticky_duration_seconds: None
    subreddit_coin_reward: int
    subreddit_id: None
    tiers_by_required_awarding: None


class RedditRichText(TypedDict):
    a: NotRequired[str]
    e: NotRequired[str]
    t: NotRequired[str]
    u: NotRequired[str]


class RedditGildings(TypedDict):
    gid_1: NotRequired[int]
    gid_2: NotRequired[int]
    gid_3: NotRequired[int]


class RedditContent(TypedDict):
    num_reports: None
    mod_note: None
    can_mod_post: bool
    report_reasons: None
    awarders: List[Any]
    author_flair_richtext: NotRequired[List[RedditRichText]]
    distinguished: NotRequired[str]
    can_gild: bool
    banned_at_utc: None
    author_is_blocked: Literal[False]
    name: str
    author_cakeday: NotRequired[Literal[True]]
    id: str
    stickied: bool
    no_follow: bool
    top_awarded_type: str
    locked: bool
    subreddit_id: str
    subreddit_name_prefixed: str
    gilded: int
    subreddit: str
    approved_by: None
    author_premium: bool
    edited: Union[Literal[False], float]
    score: int
    send_replies: bool
    gildings: RedditGildings
    author_flair_text: NotRequired[str]
    treatment_tags: List[str]
    downs: int
    likes: None
    mod_reports: List[Any]
    created: float
    author_flair_template_id: NotRequired[str]
    all_awardings: List[RedditAwards]
    author: str
    author_flair_type: NotRequired[str]
    ups: int
    saved: Literal[False]
    archived: Literal[False]
    author_flair_text_color: NotRequired[str]
    author_fullname: NotRequired[str]
    permalink: str
    subreddit_type: str
    mod_reason_title: None
    author_patreon_flair: Literal[False]
    banned_by: None
    total_awards_received: int
    created_utc: float
    approved_at_utc: None
    mod_reason_by: None
    removal_reason: None
    author_flair_css_class: NotRequired[str]
    media_metadata: NotRequired[Any]
    user_reports: List[Any]
    author_flair_background_color: NotRequired[str]


class RedditComment(RedditContent):
    body: str
    replies: Any  # RedditCommentWrapper
    score_hidden: bool
    body_html: str
    collapsed: bool
    parent_id: str
    controversiality: int
    is_submitter: bool
    comment_type: None
    associated_award: None
    collapsed_reason_code: NotRequired[str]
    unrepliable_reason: None
    collapsed_reason: NotRequired[str]
    collapsed_because_crowd_control: None
    depth: int
    link_id: str


class RedditCollection(TypedDict):
    author_id: str
    author_name: str
    collection_id: str
    created_at_utc: float
    description: str
    display_layout: str
    last_update_utc: float
    link_ids: List[str]
    permalink: str
    sr_detail: NotRequired[Any]
    subreddit_id: str
    title: str


class RedditTournamentPredictions(TypedDict):
    body: str
    created_at: float
    id: str
    is_nsfw: bool
    is_rtjson: bool
    is_spoiler: bool
    options: List[Any]
    resolved_option_id: None
    status: str
    title: str
    total_stake_amount: int
    total_vote_count: int
    user_selection: None
    user_won_amount: None
    vote_updates_remained: None
    voting_end_timestamp: float


class RedditTournamentData(TypedDict):
    currency: str
    name: str
    predictions: List[RedditTournamentPredictions]
    status: str
    subreddit_id: str
    theme_id: str
    total_participants: int
    tournament_id: str


class RedditImage(TypedDict):
    id: str
    resolutions: List[Any]
    source: Any
    variants: Any


class RedditVideo(TypedDict):
    bitrate_bkps: int
    dash_url: str
    duration: int
    fallback_url: str
    height: int
    hls_url: str
    is_gif: bool
    scrubber_media_url: str
    transcoding_status: str
    width: int


class RedditPreview(TypedDict):
    enabled: bool
    images: List[RedditImage]
    reddit_video_preview: RedditVideo


class RedditOEmbed(TypedDict):
    author_name: NotRequired[str]
    author_url: NotRequired[str]
    cache_age: float
    description: str
    height: int
    html: str
    provider_name: str
    provider_url: str
    thumbnail_height: int
    thumbnail_url: str
    thumbnail_width: int
    title: str
    type: str
    url: str
    version: str
    width: int


class RedditSecureMedia(TypedDict):
    oembed: RedditOEmbed
    reddit_video: RedditVideo
    type: str


class RedditSecureMediaEmbed(TypedDict):
    content: str
    height: int
    media_domain_url: str
    scrolling: bool
    width: int


class RedditSubmission(RedditContent):
    collections: List[RedditCollection]
    tournament_data: RedditTournamentData
    thumbnail: str
    media_only: Literal[False]
    crosspost_parent: NotRequired[str]
    num_comments: int
    link_flair_css_class: NotRequired[str]
    media_embed: NotRequired[RedditSecureMedia]
    post_hint: NotRequired[str]
    thumbnail_height: int
    spoiler: bool
    url: str
    is_self: bool
    hide_score: bool
    is_video: bool
    selftext_html: str
    clicked: Literal[False]
    link_flair_text_color: NotRequired[str]
    hidden: Literal[False]
    visited: bool
    category: str
    event_end: NotRequired[float]
    is_reddit_media_domain: bool
    wls: NotRequired[int]
    link_flair_background_color: NotRequired[str]
    selftext: str
    poll_data: None
    is_gallery: NotRequired[Literal[True]]
    link_flair_richtext: List[RedditRichText]
    discussion_type: None
    preview: RedditPreview
    view_count: None
    secure_media_embed: RedditSecureMediaEmbed
    content_categories: List[str]
    link_flair_template_id: NotRequired[str]
    num_crossposts: int
    suggested_sort: str
    pinned: bool
    contest_mode: bool
    media: NotRequired[RedditSecureMedia]
    is_robot_indexable: bool
    crosspost_parent_list: NotRequired[List[Any]]
    link_flair_type: str
    thumbnail_width: int
    secure_media: RedditSecureMedia
    whitelist_status: str
    parent_whitelist_status: str
    removed_by: None
    is_original_content: bool
    over_18: bool
    quarantine: bool
    is_meta: Literal[False]
    is_created_from_ads_ui: Literal[False]
    title: str
    removed_by_category: None
    pwls: NotRequired[int]
    is_crosspostable: Literal[False]
    link_flair_text: NotRequired[str]
    subreddit_subscribers: int
    upvote_ratio: float
    url_overridden_by_dest: NotRequired[str]


class RedditCommentWrapper(TypedDict):
    kind: Literal["t1"]
    data: RedditComment


class RedditSubmissionWrapper(TypedDict):
    kind: Literal["t3"]
    data: RedditSubmission


class RedditListingData(TypedDict):
    after: str
    dist: int
    modhash: str
    geo_filter: str
    children: Union[List[RedditCommentWrapper], List[RedditSubmissionWrapper]]


class RedditListing(TypedDict):
    kind: Literal["Listing"]
    data: RedditListingData
