from typing import Any, Set
from twitter_typings import TwitterResponse

whitelisted_entities: Set[str] = set(
    [
        "1449025157079519237",  # BetMGM
        "1491824160565174290",  # Betrivers
        "1473287826875686914",  # Caesars Sportsbook
        "10000336840",  # College Baseball
        "10000583723",  # College Basketball
        "10031306963",  # College Basketball
        "10001559323",  # College Basketball Live
        "10023939663",  # College Basketball Live Scoreboard
        "10049297158",  # College Beach Volleyball
        "10043493582",  # College Board
        "1403086701967208449",  # College Bowl
        "10001558617",  # College Bowling
        "10033079849",  # College Football
        "10000611558",  # College Football
        "10000274597",  # College Football Final
        "10000274333",  # College Football Live
        "10041864699",  # College Football Live
        "10000274584",  # College Football Scoreboard
        "10033091048",  # College GameDay
        "10000988702",  # College GameDay (College Basketball)
        "10000274579",  # College GameDay (College Football)
        "10023819145",  # College Golf
        "10001662551",  # College Hockey
        "10001343079",  # College Lacrosse
        "10002734704",  # College Rugby
        "10000458393",  # College Softball
        "10001960300",  # College Swimming & Diving
        "10000462251",  # College Track and Field
        "10001662505",  # College Wrestling
        "10032902339",  # DraftKings
        "10041116731",  # ESPN
        "1382754188824760325",  # ESPN+
        "839544337360801792",  # Esports
        "1288169409228414976",  # Esports casters
        "1491568918174912515",  # Esports events
        "1272667416061861888",  # Esports leagues
        "1288168909422518272",  # Esports players
        "1272667111932878848",  # Esports teams
        "10032902322",  # FanDuel
        "847901256525856769",  # Fantasy sports
        "10040912145",  # FantasyDraft
        "10050757834",  # Fox Sports
        "10050757844",  # Fox Sports 1
        "1478398645430984705",  # FoxBet
        "1288557203075428352",  # Golden State Warriors Stats
        "10032808928",  # Live: College Football
        "10029551948",  # Live: Mutua Madrid Open Tennis
        "10029190505",  # Live: NBA Basketball
        "10042758024",  # NBA
        "10007534154",  # NBA Action
        "10029190557",  # NBA Basketball
        "10000607734",  # NBA Basketball
        "10029304530",  # NBA Basketball
        "10000607731",  # NBA Countdown
        "10051684735",  # NBA G League Basketball
        "10004509128",  # NBA GameTime
        "1248346159833206786",  # NBA HORSE Challenge
        "10028019319",  # NBA Inside Stuff
        "1004423774253375488",  # NBA Live 19
        "10015532381",  # NBA Playoffs Playback
        "10053898244",  # NBA Summer League Basketball
        "1106284725834924032",  # NBA TV
        "10024680075",  # NBA TV Marquee Matchup
        "10042534331",  # NBA Tip-Off
        "10001342984",  # NBA Tip-Off
        "1370413122385629190",  # NBA Top Shot
        "1265692717071265792",  # NBA players
        "1405505346072813572",  # NBC
        "10055847880",  # NCAA Basketball Championship Selection Show
        "10026428668",  # NCAA March Madness Bracket Breakdown
        "10042758256",  # NFL
        "10044080899",  # NFL 360
        "1497319153815867393",  # NFL All Day
        "10028507310",  # NFL America's Game
        "1373999048424759299",  # NFL Draft
        "10003858417",  # NFL Fantasy Live
        "10000490728",  # NFL Films Presents
        "10000612773",  # NFL Football
        "10032425201",  # NFL Football
        "10027594388",  # NFL Football
        "10032937285",  # NFL Game Rewind
        "10027635630",  # NFL GameDay First
        "10004034428",  # NFL GameDay Morning
        "10027351607",  # NFL Insiders
        "10042232767",  # NFL Live
        "10000274336",  # NFL Live
        "10000274604",  # NFL Matchup
        "10054447910",  # NFL Mic'd Up
        "10050897904",  # NFL Power Rankings
        "10000274339",  # NFL PrimeTime
        "10001792867",  # NFL Replay
        "10001795471",  # NFL Total Access
        "10004309915",  # NFL Turning Point
        "1263187885970227200",  # NFL players
        "1290743320252002305",  # New England Patriots Stats
        "1288572665142185984",  # New Orleans Pelicans Stats
        "1290743915620966400",  # New Orleans Saints Stats
        "1290806702309167104",  # New York Giants Stats
        "1290807105855709184",  # New York Jets Stats
        "1288573036480745472",  # New York Knicks Stats
        "1291341477667168256",  # New York Mets Stats
        "1291342199024578561",  # New York Yankees Stats
        "1291802756584321025",  # Newcastle United FC stats
        "1291807045058850816",  # Norwich City FC stats
        "1478398291641450496",  # PointsBet
        "1290808354789453824",  # San Francisco 49ers Stats
        "781974597491040257",  # Sports
        "847900493514891265",  # Sports
        "1491816163713556484",  # Sports Experts
        "10027997188",  # Sports Life Stories
        "10000274619",  # Sports Reporters
        "10046007645",  # Sports Shorts
        "10000379580",  # Sports Stars of Tomorrow
        "1158813612409929728",  # Sports betting
        "1392166833956917251",  # Sports cards
        "1286401121641103360",  # Sports events
        "1285942425861545984",  # Sports figures
        "1491898362609631238",  # Sports games
        "1074755059433463813",  # Sports journalists
        "840160112325021696",  # Sports news
        "1290461311306874880",  # Sports personalities
        "1284101274154053632",  # Sports photography
        "1495103813581115392",  # Sports podcasts
        "1283448166507937792",  # Sports stats
        "1281313213859020806",  # Sports talk
        "781974597176467456",  # Sports/Outdoor
        "781974597428125696",  # Sports/Outdoor
        "10000274304",  # SportsCenter
        "10050757846",  # SportsCenter
        "10000342555",  # SportsCenter Special
        "10029304625",  # SportsCentre
        "10000337517",  # SportsNation
        "1268924967799816198",  # SportsNation
        "10029321417",  # SportsNation
        "890226516914716672",  # SportsTalk 790
        "10033145158",  # Sportscenter
        "10027336602",  # Sportsday
        "10028603627",  # TMZ Sports
        "1443319600863666185",  # UCF Sports
        "10002734734",  # WNBA Basketball
    ]
)


async def custom_eval(tweet: TwitterResponse) -> bool:
    context_annotations: Any = tweet.get("context_annotations", [])
    if len(context_annotations) > 0:
        entity_ids = [annotation["entity"]["id"] for annotation in context_annotations]
        if not whitelisted_entities.isdisjoint(entity_ids):
            return True
        stat_entites = [
            annotation["entity"]["name"]
            for annotation in context_annotations
            if (annotation["entity"]["name"]).lower().rstrip().endswith("stats")
        ]
        if len(stat_entites) > 0:
            return True
    return False
