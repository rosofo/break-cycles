from enum import Enum
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import networkx as nx
from typer import Typer
import typer

import python_cycles


def evaluation(graph_file, gt_edges_file, method, nodetype=int):
    g = nx.read_edgelist(
        graph_file, create_using=nx.DiGraph(), nodetype=nodetype)
    if method == "dfs":
        from remove_cycle_edges_by_dfs import dfs_performance
        edges_to_be_removed = dfs_performance(
            graph_file, gt_edges_file, nodetype=nodetype)
    elif method == "mfas":
        from remove_cycle_edges_by_minimum_feedback_arc_set_greedy import mfas_to_be_removed
        return mfas_to_be_removed(graph_file, gt_edges_file)
    elif method == "pagerank" or method == "ensembling" or method == "trueskill" or method == "socialagony":
        from remove_cycle_edges_by_hierarchy import breaking_cycles_by_hierarchy_performance
        breaking_cycles_by_hierarchy_performance(
            graph_file, gt_edges_file, method, nodetype=nodetype)


def _break_cycles(graph_file, extra_edges_file=None, algorithm="ensembling", nodetype=int):
    methods = ["dfs", "pagerank", "mfas", "ensembling"]

    if algorithm == "all":
        for method in methods:
            return evaluation(graph_file, extra_edges_file, method, nodetype=nodetype)
    else:
        return evaluation(graph_file, extra_edges_file, algorithm, nodetype=nodetype)


app = Typer()


class Method(Enum):
    Ensembling = "ensembling"
    Mfas = "mfas"


class NodeType(Enum):
    Int = 'int'
    Str = 'str'


@app.command()
def break_cycles(
        graph_file: str = typer.Option(
            None, "-g", "--graph-file", exists=True, dir_okay=False),
        gt_edges_file: str = typer.Option(
            None, "-t", "--gt-edges-file", exists=True, dir_okay=False),
        method: Method = typer.Option('ensembling', "-m", "--method"),
        node_type: NodeType = typer.Option('int', "-n", "--node-type"),
):
    if node_type == 'int':
        return _break_cycles(graph_file, gt_edges_file,
                             method.value, nodetype=int)
    else:
        return _break_cycles(graph_file, gt_edges_file,
                             method.value, nodetype=str)


@app.command()
def break_python_cycles():
    result = subprocess.run('pipdeptree --json',
                            shell=True, capture_output=True)
    tree = json.loads(result.stdout)
    edges = python_cycles.build_edge_set(tree)

    packages = set()
    for edge in edges:
        packages.update(edge)
    packages = list(packages)
    package_numbers = {package: i for i, package in enumerate(packages)}
    number_edges = set()
    for edge in edges:
        number_edges.add(
            (str(package_numbers[edge[0]]), str(package_numbers[edge[1]])))

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tmpfile = tmpdir / 'edges'
        with open(tmpfile, 'w') as file:
            file.write('\n'.join(' '.join(edge) for edge in number_edges))
        to_be_removed = break_cycles(str(tmpfile), gt_edges_file=None,
                                     method=Method.Mfas, node_type=NodeType.Int)

    print(to_be_removed)


if __name__ == '__main__':
    break_python_cycles()
