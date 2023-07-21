import argparse


def simulate(args):
    from arsim.cli.env import create_scene_from_pyfile

    scene = create_scene_from_pyfile(args.file)
    scene.run()

def test(args):
    print("test")


parser = argparse.ArgumentParser(
    "SoSAirRescue", description="A simple CLI for SoS: AirRescue Simulator."
)

# 执行的命令
# simulate
subparsers = parser.add_subparsers(help="subcommand")

parser_simulate = subparsers.add_parser("simulate", help="simulate help")
parser_simulate.add_argument("file", help="data file to import")
parser_simulate.set_defaults(func=simulate)


# test
parser_test = subparsers.add_parser("test", help="for program test")
parser_test.set_defaults(func=test)

args = parser.parse_args()
args.func(args)
