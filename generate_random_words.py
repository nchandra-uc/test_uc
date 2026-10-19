"""Generate a file of random English words.

Usage:
    python3 generate_random_words.py [count] [output_path] [--seed N]
"""

import argparse
import random

VOCABULARY = """
able about above accept across act add admire adventure afford afraid after
again age agree air alarm alive allow almost alone along amber amount ancient
angle animal answer apple april arch area arm army arrow art ask atom autumn
awake baby back bake balance ball band bank barn basket bath beach bean bear
beauty bed bee begin bell belt bench berry bicycle bird bitter blanket blue
board boat body bold bone book border bottle branch brave bread breeze brick
bridge bright broad brother brush bubble bucket build bundle butter cabin cable
cactus cake calm camel camera candle canyon captain card carpet carry castle
cat cave cedar chain chair chalk change channel charm cheese cherry chess child
circle city clay clean clever cliff climb clock cloud coast coffee coin cold
color comet compass copper coral corner cotton country courage cousin crane
crayon creek crisp crown crystal cup curious curtain cycle daisy dance danger
dawn day deep desert design desk diamond dinner direct distant dog dolphin door
dragon dream drift drum duck dust eager eagle early earth echo edge egg elbow
element elephant ember empty engine enjoy equal escape evening event example
fabric face fair falcon family famous fancy farm feather fence fern festival
field fierce finger fire flag flame flash float flower flute fog follow forest
fork fossil fountain fox fresh friend frost fruit galaxy garden gate gentle
giant gift ginger glacier glass globe glow gold grain grape grass gravel green
guitar habit hammer harbor harvest hat hazel heart heavy helmet hero hill
history hollow honey horizon horse hour humble hunt ice idea island ivory
jacket jade jar jelly jewel journey joy juice jungle kettle key kind king kite
kitten knee knot ladder lake lamp lantern large laugh lava leaf learn lemon
letter level library light lily lion liquid little lizard lobster lock lunar
magic magnet maple marble market meadow melody metal middle mild mirror mist
modern moment monkey moon morning mountain mouse music narrow nature needle
nest network night noble north number oak ocean olive onion open orange orbit
orchard owl paint palace panda paper parade parrot pattern peach pearl pebble
pencil pepper piano picture pilot pine planet plum pocket poem polar pond
potato powder prism puzzle quiet quick quilt rabbit radio rain rainbow rapid
raven record reef ribbon river road robot rocket root rose round ruby saddle
sail salt sand saturn scarf school science season secret seed shadow shell
shore silent silver simple sky slow smile snow soft solar song spark spider
spring square star stone storm stream summer sun sunset swift table tail tea
temple thunder tiger timber toast tomato tower trail travel tree tulip tunnel
turtle umbrella unique valley velvet violet voice volcano voyage wagon walnut
warm water wave wheat whisper wild willow window winter wisdom wolf wonder wood
world yellow young zebra zero zone
""".split()


def generate_words(count, seed=None):
    rng = random.Random(seed)
    return rng.choices(VOCABULARY, k=count)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("count", nargs="?", type=int, default=1000)
    parser.add_argument("output", nargs="?", default="random_words.txt")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    words = generate_words(args.count, args.seed)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(words) + "\n")
    print(f"Wrote {len(words)} words to {args.output}")


if __name__ == "__main__":
    main()
