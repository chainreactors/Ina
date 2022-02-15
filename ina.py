from json import dumps as jsondumps
import click

from core import *


ina_context = click.make_pass_decorator(Ina)
ina_obj = Ina()
front_data = None  # type: InaData


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    ctx.obj = ina_obj
    if ctx.invoked_subcommand is None:
        repl(ctx, {"message": "[none] > "})


@cli.command()
def help():
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))


@cli.command()
@click.argument("code")
@click.option("--source", "-s", help="choice sources: fofa,zoomeye")
@ina_context
def run(ina, code, source):
    global front_data
    front_data = ina.run(code)
    if not ina.idata:
        ina.idata = front_data
    update_prompt(message="[%s] > "%code[:15])


@cli.command()
@ina_context
def history(ina):
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
    input history index id, change current ina_data

    Example:
        history

        choice 1
    """
    global front_data
    front_data, code = ina.get_history(index)
    update_prompt(message="[%s] > "%code.short())


@cli.command()
@ina_context
def root(ina):
    global front_data
    front_data = ina.idata
    update_prompt(message="[root] > ")


@cli.command()
@ina_context
def merge(ina):
    ina.merge(front_data)
    click.get_current_context().invoke(root)


@cli.command()
@click.option("--field", help="output type", default="ip,domain,cidr")
@click.option("-json", help="json format", default=False, is_flag=True)
def output(field, json):
    if json:
        click.echo(jsondumps(front_data.to_dict()))
    else:
        front_data.output(field.split(","), click.echo)


@cli.command()
@click.option("--field", help="output type", default="ip,domain,cidr")
@click.option("--filename", "-f", help="save file name", default="tmp.txt")
@click.option("-json", help="json format", default=False, is_flag=True)
def save(field, filename, json):
    with open(filename, "a+", encoding="utf-8") as f:
        if json:
            f.write(jsondumps(front_data.to_dict()))
        else:
            front_data.output(field.split(","), f.write)


if __name__ == '__main__':
    cli()
