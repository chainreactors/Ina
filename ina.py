from json import dumps as jsondumps
import click
from functools import partial
from prompt_toolkit.history import FileHistory

import settings
from core import *


ina_context = click.make_pass_decorator(Ina)
ina_obj = Ina()
front_data = InaData()  # type: InaData


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    ctx.obj = ina_obj
    if ctx.invoked_subcommand is None:
        prompt_kwargs = {
            'history': FileHistory('./.ina-history'),
            "message": "[none] > "
        }
        repl(ctx, prompt_kwargs=prompt_kwargs)


@cli.command()
def help():
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))


@cli.command()
@click.argument("code")
@click.option("--source", "-s", help="choice sources: fofa, zoomeye, hunter", default="fofa")
@click.option("-cidr", help="collect cidr", is_flag=True, default=False)
@ina_context
def run(ina, code, source, cidr):
    """
    auto running

    example:
        run domain="example.com" --source fofa,zoomeye

        run domain="example.com" --source all
    """
    global front_data
    settings.cidrcollect = cidr
    front_data = ina.run(code, source)
    update_prompt(message="[%s] > " % code[:15])


@cli.command()
@click.argument("code")
@click.option("--source", "-s", help="choice sources: fofa,zoomeye", default="all")
@ina_context
def run_once(ina, code, source):
    "run once code"
    global front_data
    front_data = ina.run_once(code, source)
    update_prompt(message="[%s] > " % code[:15])


@cli.command()
@ina_context
def history(ina):
    "show history"
    if ina.history:
        click.echo("id\tcode\tlen")
        for i, item in enumerate(ina.history.items()):
            click.echo("%s\t%s\t%s" % (i, item[0], len(item[1])))
    else:
        click.echo("no history")


@cli.command()
@click.argument("index")
@ina_context
def choice(ina, index):
    """
    choice history index id, change current ina_data

    Example:
        history

        choice 1
    """
    global front_data
    item = ina.get_history(int(index))
    if item:
        code, front_data = item
        update_prompt(message="[%s] > " % code)
    else:
        click.echo("not found index: %s" %index)


@cli.command()
@ina_context
def root(ina):
    "change current_idata to root"
    global front_data
    front_data = ina.idata
    update_prompt(message="[root] > ")


@cli.command()
@ina_context
def merge(ina):
    "merge current idata to root"
    ina.merge(front_data)
    click.get_current_context().invoke(root)


@cli.command()
@click.option("-field", help="output type: " + ", ".join(InaData.types), default="ip,domain,cidr")
@click.option("-json", help="json format", default=False, is_flag=True)
@click.option("-full", help="full output", is_flag=True)
def output(field, json, full):
    if json:
        click.echo(jsondumps(front_data.to_dict()))
    elif full:
        for asset in front_data.assets:
            click.echo(asset.to_string())
    else:
        front_data.output(field.split(","), click.echo)


@cli.command()
@click.option("-field", help="output type: " + ", ".join(InaData.types), default="ip,domain,cidr")
@click.option("--filename", "-f", help="save file name", default="tmp.txt", required=True)
@click.option("-json", help="json format", default=False, is_flag=True)
@click.option("-full", help="full output", is_flag=True)
def save(field, filename, json, full):
    "save to file"
    with open(filename, "a+", encoding="utf-8") as f:
        if json:
            f.write(jsondumps(front_data.to_dict()))
        elif full:
            for asset in front_data.assets:
                f.write(asset.to_string() + "\n")
        else:
            front_data.output(field.split(","), f.write)


@cli.group(invoke_without_command=True)
@click.pass_context
def clear(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(clear_all)


@clear.command("root")
@ina_context
def clear_root(ina):
    "clear root idata"
    click.echo("root cleared")
    ina.idata = InaData(True, logging.info)


@clear.command("cache")
@ina_context
def clear_cache(ina):
    "clear cache"
    click.echo("cache cleared")
    ina.cache = Code()


@clear.command("history")
@ina_context
def clear_history(ina):
    "clear history"
    click.echo("history cleared")
    ina.history = {}


@clear.command("all")
@ina_context
def clear_all(ina):
    "clear all data"
    click.echo("all cleared")
    ina = Ina()


@cli.command()
def quit():
    click.echo("exit.")
    exit()


if __name__ == '__main__':
    cli()
